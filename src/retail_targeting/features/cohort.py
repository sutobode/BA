"""Cohort retention (SPEC §7.2, CODE SPEC §6.8). Owner: M1. Descriptive only."""

from __future__ import annotations

import pandas as pd


def cohort_retention(orders: pd.DataFrame, max_age_months: int = 12) -> pd.DataFrame:
    """Cohort = month of first purchase order. Columns: cohort_month, age_month, n_customers,
    n_active, retention_rate, left_censored (True for the first data month, 2009-12)."""
    raise NotImplementedError("M1 — CODE SPEC §6.8")
