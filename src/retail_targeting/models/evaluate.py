"""Model evaluation (SPEC §8, CODE SPEC §6.12). Owner: M2."""

from __future__ import annotations

import numpy as np
import pandas as pd

from retail_targeting.config import Config


def top_k_count(n: int, fraction: float) -> int:
    """k = max(1, floor(fraction * n))."""
    raise NotImplementedError("M2 — CODE SPEC §6.12")


def classification_metrics(y: np.ndarray, score: np.ndarray, top_k_fractions: list[float],
                           ids: np.ndarray | None = None) -> dict:
    """prevalence, pr_auc (average_precision), roc_auc; brier and log_loss only if score ∈ [0,1];
    for each fraction f: precision_at_{f}, recall_at_{f}, lift_at_{f}.
    Ranking: score desc, tie-break by ids asc (or position if ids is None)."""
    raise NotImplementedError("M2 — CODE SPEC §6.12")


def reliability_table(y: np.ndarray, p: np.ndarray, n_bins: int = 10, strategy: str = "quantile") -> pd.DataFrame:
    """Columns: bin, n, mean_predicted, observed_rate."""
    raise NotImplementedError("M2 — CODE SPEC §6.12")


def metrics_by_group(df: pd.DataFrame, score_col: str, group_col: str, cfg: Config) -> pd.DataFrame:
    """classification_metrics per value of group_col (customer_segment, cohort_month, decision_date)."""
    raise NotImplementedError("M2 — CODE SPEC §6.12")


def log_test_access(cfg: Config, what: str) -> None:
    """Append {timestamp, what, config_hash} to reports_dir/test_access_log.jsonl."""
    raise NotImplementedError("M2 — CODE SPEC §6.12")
