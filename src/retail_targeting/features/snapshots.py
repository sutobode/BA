"""Customer snapshots at decision date T0 (SPEC §5, CODE SPEC §5.3, §6.6). Owner: M1."""

from __future__ import annotations

import pandas as pd

from retail_targeting.config import Config


class LeakageError(AssertionError):
    """Raised when post-T0 information reaches a feature (INV-05/INV-06)."""


def generate_t0_dates(data_start: pd.Timestamp, data_end: pd.Timestamp, cfg: Config) -> list[pd.Timestamp]:
    """First-of-month dates with T0 >= data_start + observation_days and
    T0 + outcome_days <= data_end. Real data (2009-12-01 → 2011-12-09, 180/90) → 16 dates
    2010-06-01 … 2011-09-01."""
    raise NotImplementedError("M1 — CODE SPEC §6.6")


def build_snapshot(orders: pd.DataFrame, lines: pd.DataFrame, t0: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """One row per eligible customer (>= 1 purchase order in [T0-obs, T0)).

    Features use only orders/lines with ts < T0 (assert, raise LeakageError);
    target ``repeat_purchase_{outcome}d`` and ``label_future_value_{outcome}d`` use only
    purchase orders in [T0, T0+outcome). Column formulas: CODE SPEC §5.3.
    Does not add RFM scores, segment or split (added by rfm/split).
    """
    raise NotImplementedError("M1 — CODE SPEC §6.6")


def build_all_snapshots(orders: pd.DataFrame, lines: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Concatenate build_snapshot for every T0 from generate_t0_dates; add feature_version.
    Sorted by (decision_date, customer_id). Satisfies contract ``customer_snapshots``."""
    raise NotImplementedError("M1 — CODE SPEC §6.6")
