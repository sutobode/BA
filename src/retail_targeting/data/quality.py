"""Profiling, coverage and reconciliation (CODE SPEC §6.5). Owner: M1."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def profile_raw(raw: pd.DataFrame) -> dict:
    """Metrics of docs/data_profile_topic1.md §1–§5 (rows, date range, missing id %, prefixes,
    negative qty, zero/negative price, special stock codes, invoices per month)."""
    raise NotImplementedError("M1 — CODE SPEC §6.5")


def customer_coverage(lines: pd.DataFrame) -> pd.DataFrame:
    """Per month and country: rows, pct_missing_customer, pct_positive_revenue_missing_customer."""
    raise NotImplementedError("M1 — CODE SPEC §6.5")


def reconcile(raw: pd.DataFrame, lines: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
    """INV-03: Σ raw line value == Σ over line_type (after CR-07), and
    Σ orders.order_value == Σ lines (purchase + adjustment with customer id, minus dropped orders).
    Returns a table of check, expected, actual, abs_diff, status (tolerance 0.01)."""
    raise NotImplementedError("M1 — CODE SPEC §6.5")


def write_quality_report(profile: dict, coverage: pd.DataFrame, cleaning_log: pd.DataFrame,
                         path: Path) -> None:
    """Write outputs/reports/data_quality_report.md (+ CSV siblings)."""
    raise NotImplementedError("M1 — CODE SPEC §6.5")
