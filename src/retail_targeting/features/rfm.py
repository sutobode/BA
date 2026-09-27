"""RFM scoring and segmentation (SPEC §7.3, CODE SPEC §6.7). Owner: M1."""

from __future__ import annotations

import numpy as np
import pandas as pd

RFM_SOURCE_COLUMNS = {"r": "recency_days", "f": "frequency_orders", "m": "monetary_net"}


def fit_rfm_cutoffs(train: pd.DataFrame, n_bins: int = 5) -> dict[str, list[float]]:
    """Interior quantile edges per dimension from TRAIN rows only (INV-09).

    Raise ValueError if any row has split != "train". Duplicate edges removed (np.unique).
    Returns {"r": [...], "f": [...], "m": [...]} (edges on the raw source columns).
    """
    if "split" not in train or (train["split"] != "train").any():
        raise ValueError("fit_rfm_cutoffs: only split == 'train' rows are allowed (INV-09)")
    qs = np.linspace(0, 1, n_bins + 1)[1:-1]
    return {k: [float(x) for x in np.unique(np.quantile(train[c].to_numpy(dtype=float), qs))]
            for k, c in RFM_SOURCE_COLUMNS.items()}


def apply_rfm_scores(df: pd.DataFrame, cutoffs: dict[str, list[float]], n_bins: int = 5) -> pd.DataFrame:
    """Add r_score, f_score, m_score (int8, 1..n_bins) and rfm_score = r+f+m.

    score = 1 + searchsorted(edges, x, side="right"), clipped to [1, n_bins];
    recency is reversed: r_score = n_bins + 1 - score(recency_days).
    """
    out = df.copy()
    for k, col in RFM_SOURCE_COLUMNS.items():
        s = np.clip(1 + np.searchsorted(np.asarray(cutoffs[k]), out[col].to_numpy(dtype=float), side="right"), 1, n_bins)
        if k == "r":
            s = n_bins + 1 - s
        out[f"{k}_score"] = s.astype("int8")
    out["rfm_score"] = (out["r_score"].astype("int16") + out["f_score"] + out["m_score"]).astype("int8")
    return out


def assign_segments(df: pd.DataFrame, rules: list[dict]) -> pd.Series:
    """Evaluate ``rules`` (config segmentation.rules) in order; first match wins;
    rule with when == "default" matches all remaining rows. Returns string Series."""
    out = pd.Series(pd.NA, index=df.index, dtype="string")
    scores = df[["r_score", "f_score", "m_score"]].astype(int)
    for rule in rules:
        mask = (pd.Series(True, index=df.index) if rule["when"] == "default"
                else scores.eval(rule["when"]).astype(bool))
        out[mask & out.isna()] = rule["name"]
    return out
