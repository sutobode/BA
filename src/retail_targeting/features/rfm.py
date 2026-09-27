"""RFM scoring and segmentation (SPEC §7.3, CODE SPEC §6.7). Owner: M1."""

from __future__ import annotations

import pandas as pd

RFM_SOURCE_COLUMNS = {"r": "recency_days", "f": "frequency_orders", "m": "monetary_net"}


def fit_rfm_cutoffs(train: pd.DataFrame, n_bins: int = 5) -> dict[str, list[float]]:
    """Interior quantile edges per dimension from TRAIN rows only (INV-09).

    Raise ValueError if any row has split != "train". Duplicate edges removed (np.unique).
    Returns {"r": [...], "f": [...], "m": [...]} (edges on the raw source columns).
    """
    raise NotImplementedError("M1 — CODE SPEC §6.7")


def apply_rfm_scores(df: pd.DataFrame, cutoffs: dict[str, list[float]], n_bins: int = 5) -> pd.DataFrame:
    """Add r_score, f_score, m_score (int8, 1..n_bins) and rfm_score = r+f+m.

    score = 1 + searchsorted(edges, x, side="right"), clipped to [1, n_bins];
    recency is reversed: r_score = n_bins + 1 - score(recency_days).
    """
    raise NotImplementedError("M1 — CODE SPEC §6.7")


def assign_segments(df: pd.DataFrame, rules: list[dict]) -> pd.Series:
    """Evaluate ``rules`` (config segmentation.rules) in order; first match wins;
    rule with when == "default" matches all remaining rows. Returns string Series."""
    raise NotImplementedError("M1 — CODE SPEC §6.7")
