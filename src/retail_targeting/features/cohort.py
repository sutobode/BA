"""Cohort retention (SPEC §7.2, CODE SPEC §6.8). Owner: M1. Descriptive only."""

from __future__ import annotations

import pandas as pd


def cohort_retention(orders: pd.DataFrame, max_age_months: int = 12) -> pd.DataFrame:
    """Cohort = month of first purchase order. Columns: cohort_month, age_month, n_customers,
    n_active, retention_rate, left_censored (True for the first data month, 2009-12)."""
    p = orders[orders["order_type"] == "purchase"][["customer_id", "order_ts"]].copy()
    p["month"] = p["order_ts"].dt.to_period("M")
    first = p.groupby("customer_id", observed=True)["month"].min().rename("cohort")
    p = p.join(first, on="customer_id")
    p["age_month"] = (p["month"] - p["cohort"]).apply(lambda x: x.n).astype(int)
    p = p[p["age_month"] <= max_age_months]
    active = p.groupby(["cohort", "age_month"], observed=True)["customer_id"].nunique().rename("n_active").reset_index()
    size = first.value_counts().rename("n_customers")
    active = active.join(size, on="cohort")
    active["retention_rate"] = active["n_active"] / active["n_customers"]
    first_month = p["month"].min()
    active["left_censored"] = active["cohort"] == first_month
    active["cohort_month"] = active["cohort"].astype(str)
    return active[["cohort_month", "age_month", "n_customers", "n_active", "retention_rate", "left_censored"]] \
        .sort_values(["cohort_month", "age_month"]).reset_index(drop=True)
