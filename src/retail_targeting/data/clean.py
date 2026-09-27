"""Canonical transaction cleaning (SPEC §4, CODE SPEC §6.4). Owner: M1."""

from __future__ import annotations

import pandas as pd

from retail_targeting.config import Config

RAW_TO_CANONICAL: dict[str, str] = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_ts",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}

LINE_TYPES = ("purchase", "adjustment", "non_product", "excluded")
EXCLUDE_REASONS = (
    "missing_customer", "zero_price", "stock_adjustment",
    "bad_debt_adjustment", "invalid_quantity", "invalid_date",
)


def standardize_columns(raw: pd.DataFrame) -> pd.DataFrame:
    """Rename via RAW_TO_CANONICAL and cast (CODE SPEC §4.2).

    customer_id: float 12346.0 -> string "12346"; missing -> <NA>. stock_code stripped.
    Keeps ``source_sheet``.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.4")


def is_non_product(stock_code: pd.Series, codes: list[str], prefixes: list[str]) -> pd.Series:
    """True where stock_code is in ``codes`` (exact, case-sensitive) or starts with a prefix."""
    raise NotImplementedError("M1 — CODE SPEC §6.4")


def classify_lines(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Add line_value, line_type, exclude_reason applying rules in the order of CODE SPEC §6.4
    (CR-08 → bad debt → non-product → cancellation → negative qty → price<=0 → missing id → purchase).
    Input: standardized, de-duplicated frame.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.4")


def clean_transactions(raw: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """standardize → CR-07 drop exact duplicates → classify_lines.

    Returns (lines, cleaning_log). cleaning_log columns: rule_id, description, rows_before,
    rows_after, rows_affected, value_affected, customers_affected.
    ``lines`` satisfies contract ``lines``.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.4")


def build_orders(lines: pd.DataFrame) -> pd.DataFrame:
    """Aggregate purchase/adjustment lines WITH customer_id to one row per invoice (CODE SPEC §5.2).

    order_ts = min(invoice_ts); order_type = "adjustment" if line_type == adjustment else "purchase";
    drop purchase orders with order_value <= 0 (log count). Assert one customer per order (INV-04).
    Output satisfies contract ``orders``.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.4")
