"""Model evaluation (SPEC §8, CODE SPEC §6.12). Owner: M2."""

from __future__ import annotations

import datetime as dt
import json

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

from retail_targeting.config import Config, config_hash, resolve_path


def top_k_count(n: int, fraction: float) -> int:
    """k = max(1, floor(fraction * n))."""
    return max(1, int(np.floor(fraction * n)))


def _rank_order(score: np.ndarray, ids: np.ndarray | None) -> np.ndarray:
    tie = np.arange(len(score)) if ids is None else np.asarray(ids).astype(str)
    return np.lexsort((tie, -score))


def classification_metrics(y: np.ndarray, score: np.ndarray, top_k_fractions: list[float],
                           ids: np.ndarray | None = None) -> dict:
    """prevalence, pr_auc (average_precision), roc_auc; brier and log_loss only if score ∈ [0,1];
    for each fraction f: precision_at_{f}, recall_at_{f}, lift_at_{f}.
    Ranking: score desc, tie-break by ids asc (or position if ids is None)."""
    y = np.asarray(y).astype(int)
    s = np.asarray(score, dtype=float)
    prev = float(y.mean())
    out: dict = {"n": int(len(y)), "prevalence": prev,
                 "pr_auc": float(average_precision_score(y, s)), "roc_auc": float(roc_auc_score(y, s))}
    if s.min() >= 0 and s.max() <= 1:
        out["brier"] = float(brier_score_loss(y, s))
        out["log_loss"] = float(log_loss(y, np.clip(s, 1e-12, 1 - 1e-12), labels=[0, 1]))
        out["mean_predicted"] = float(s.mean())
    order = _rank_order(s, ids)
    for f in top_k_fractions:
        k = top_k_count(len(y), f)
        hits = float(y[order[:k]].sum())
        out[f"precision_at_{f}"] = hits / k
        out[f"recall_at_{f}"] = hits / y.sum() if y.sum() else float("nan")
        out[f"lift_at_{f}"] = (hits / k) / prev if prev else float("nan")
    return out


def reliability_table(y: np.ndarray, p: np.ndarray, n_bins: int = 10, strategy: str = "quantile") -> pd.DataFrame:
    """Columns: bin, n, mean_predicted, observed_rate."""
    y = np.asarray(y).astype(int)
    p = np.asarray(p, dtype=float)
    if strategy == "quantile":
        edges = np.unique(np.quantile(p, np.linspace(0, 1, n_bins + 1)))
    else:
        edges = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    df = pd.DataFrame({"bin": idx, "y": y, "p": p})
    g = df.groupby("bin")
    return pd.DataFrame({"n": g.size(), "mean_predicted": g["p"].mean(), "observed_rate": g["y"].mean()}).reset_index()


def metrics_by_group(df: pd.DataFrame, score_col: str, group_col: str, cfg: Config,
                     target_col: str = "actual_repeat_purchase") -> pd.DataFrame:
    """classification_metrics per value of group_col (customer_segment, cohort_month, decision_date)."""
    fracs = cfg.raw["model"]["top_k_fractions"]
    rows = []
    for key, g in df.groupby(group_col, observed=True):
        y = g[target_col].to_numpy()
        if len(np.unique(y)) < 2 or len(g) < 20:
            rows.append({group_col: key, "n": len(g), "prevalence": float(y.mean())})
            continue
        m = classification_metrics(y, g[score_col].to_numpy(), fracs, g["customer_id"].to_numpy())
        rows.append({group_col: key, **m})
    return pd.DataFrame(rows)


def log_test_access(cfg: Config, what: str) -> None:
    """Append {timestamp, what, config_hash} to reports_dir/test_access_log.jsonl."""
    path = resolve_path(cfg, "reports_dir") / "test_access_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "what": what, "config_hash": config_hash(cfg)}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
