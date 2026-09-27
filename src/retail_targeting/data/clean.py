"""Canonical transaction cleaning (SPEC §4, CODE SPEC §6.4). Owner: M1."""

from __future__ import annotations

import logging

import pandas as pd

from retail_targeting.config import Config

log = logging.getLogger(__name__)

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

# (rule_id, description, line_type, exclude_reason) in application order (CODE SPEC §6.4)
_RULES = (
    ("CR-08", "missing/invalid invoice date", "excluded", "invalid_date"),
    ("CR-05", "bad-debt adjustment invoice (prefix A)", "excluded", "bad_debt_adjustment"),
    ("CR-05b", "non-product stock code (postage, fees, manual, vouchers ...)", "non_product", None),
    ("CR-01/02", "cancellation invoice with positive quantity", "excluded", "invalid_quantity"),
    ("CR-01/02", "cancellation/return invoice (prefix C)", "adjustment", None),
    ("CR-04", "negative quantity without cancellation (stock adjustment)", "excluded", "stock_adjustment"),
    ("CR-05c", "price <= 0", "excluded", "zero_price"),
    ("CR-06", "missing customer id", "excluded", "missing_customer"),
    ("CR-10", "valid purchase line", "purchase", None),
)


def standardize_columns(raw: pd.DataFrame) -> pd.DataFrame:
    """Rename via RAW_TO_CANONICAL and cast (CODE SPEC §4.2).

    customer_id: float 12346.0 -> string "12346"; missing -> <NA>. stock_code stripped.
    Keeps ``source_sheet``.
    """
    df = raw.rename(columns=RAW_TO_CANONICAL).copy()
    for col in ("invoice", "stock_code", "description", "country"):
        df[col] = df[col].astype("string")
    df["source_sheet"] = df["source_sheet"].astype("string") if "source_sheet" in df else pd.Series(
        "unknown", index=df.index, dtype="string")
    df["stock_code"] = df["stock_code"].str.strip()
    df["invoice"] = df["invoice"].str.strip()
    df["customer_id"] = df["customer_id"].astype("Float64").astype("Int64").astype("string")
    df["quantity"] = df["quantity"].astype("int64")
    df["price"] = df["price"].astype("float64")
    df["invoice_ts"] = pd.to_datetime(df["invoice_ts"], errors="coerce").astype("datetime64[ns]")
    return df


def is_non_product(stock_code: pd.Series, codes: list[str], prefixes: list[str]) -> pd.Series:
    """True where stock_code is in ``codes`` (exact, case-sensitive) or starts with a prefix."""
    s = stock_code.astype("string").fillna("")
    out = s.isin(list(codes))
    for prefix in prefixes:
        out = out | s.str.startswith(prefix)
    return out.astype(bool)


def _rule_masks(df: pd.DataFrame, cfg: Config) -> list[pd.Series]:
    cl = cfg.raw["cleaning"]
    inv = df["invoice"].fillna("")
    is_cancel = inv.str.startswith(cl["cancellation_prefix"]).astype(bool)
    return [
        df["invoice_ts"].isna(),
        inv.str.startswith(cl["bad_debt_prefix"]).astype(bool),
        is_non_product(df["stock_code"], cl["non_product_codes"], cl["non_product_prefixes"]),
        is_cancel & (df["quantity"] > 0),
        is_cancel,
        df["quantity"] < 0,
        df["price"] <= 0,
        df["customer_id"].isna(),
        pd.Series(True, index=df.index),
    ]


def classify_lines(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Add line_value, line_type, exclude_reason applying rules in the order of CODE SPEC §6.4
    (CR-08 → bad debt → non-product → cancellation → negative qty → price<=0 → missing id → purchase).
    Input: standardized, de-duplicated frame.
    """
    df = df.copy()
    df["line_value"] = (df["quantity"] * df["price"]).astype("float64")
    line_type = pd.Series(pd.NA, index=df.index, dtype="string")
    reason = pd.Series(pd.NA, index=df.index, dtype="string")
    for (_, _, ltype, why), mask in zip(_RULES, _rule_masks(df, cfg)):
        m = mask.to_numpy(dtype=bool) & line_type.isna().to_numpy()
        line_type[m] = ltype
        if why is not None:
            reason[m] = why
    df["line_type"] = line_type
    df["exclude_reason"] = reason
    return df


def clean_transactions(raw: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """standardize → CR-07 drop exact duplicates → classify_lines.

    Returns (lines, cleaning_log). cleaning_log columns: rule_id, description, rows_before,
    rows_after, rows_affected, value_affected, customers_affected.
    ``lines`` satisfies contract ``lines``.
    """
    from retail_targeting.contracts import validate_frame

    n0 = len(raw)
    dedup = raw.drop_duplicates()
    dup_rows = raw[raw.duplicated()]
    log_rows = [{
        "rule_id": "CR-07", "description": "exact duplicate rows removed", "rows_before": n0,
        "rows_after": len(dedup), "rows_affected": n0 - len(dedup),
        "value_affected": float((dup_rows["Quantity"] * dup_rows["Price"]).sum()),
        "customers_affected": int(dup_rows["Customer ID"].nunique()),
    }]
    lines = classify_lines(standardize_columns(dedup), cfg).reset_index(drop=True)
    remaining = len(lines)
    seen: set[tuple[str, str]] = set()
    for rule_id, desc, ltype, why in _RULES:
        key = (ltype, why or "")
        if key in seen:
            continue
        seen.add(key)
        m = (lines["line_type"] == ltype) & (
            lines["exclude_reason"].isna() if why is None else lines["exclude_reason"] == why)
        m = m.fillna(False).astype(bool)
        n = int(m.sum())
        log_rows.append({
            "rule_id": rule_id, "description": f"{desc} -> {ltype}" + (f"/{why}" if why else ""),
            "rows_before": remaining, "rows_after": remaining - n, "rows_affected": n,
            "value_affected": float(lines.loc[m, "line_value"].sum()),
            "customers_affected": int(lines.loc[m, "customer_id"].nunique()),
        })
        remaining -= n
    cleaning_log = pd.DataFrame(log_rows)
    log.info("clean_transactions: %d rows -> %d lines; %s", n0, len(lines),
             lines["line_type"].value_counts().to_dict())
    return validate_frame(lines, "lines"), cleaning_log


def build_orders(lines: pd.DataFrame) -> pd.DataFrame:
    """Aggregate purchase/adjustment lines WITH customer_id to one row per invoice (CODE SPEC §5.2).

    order_ts = min(invoice_ts); order_type = "adjustment" if line_type == adjustment else "purchase";
    drop purchase orders with order_value <= 0 (log count). Assert one customer per order (INV-04).
    Output satisfies contract ``orders``.
    """
    from retail_targeting.contracts import validate_frame

    sel = lines[lines["line_type"].isin(["purchase", "adjustment"]) & lines["customer_id"].notna()].copy()
    sel["abs_qty"] = sel["quantity"].abs()
    g = sel.groupby("invoice", sort=True, observed=True)
    n_cust = g["customer_id"].nunique()
    if (n_cust > 1).any():
        raise AssertionError(f"INV-04 violated: {int((n_cust > 1).sum())} orders with >1 customer")
    country = (sel.groupby(["invoice", "country"], observed=True).size()
               .reset_index(name="n").sort_values(["invoice", "n", "country"], ascending=[True, False, True])
               .drop_duplicates("invoice").set_index("invoice")["country"])
    orders = pd.DataFrame({
        "customer_id": g["customer_id"].first(),
        "order_ts": g["invoice_ts"].min(),
        "order_type": g["line_type"].first(),
        "order_value": g["line_value"].sum(),
        "n_lines": g.size(),
        "n_units": g["abs_qty"].sum(),
        "n_products": g["stock_code"].nunique(),
    })
    orders["country"] = country.reindex(orders.index)
    orders = orders.reset_index().rename(columns={"invoice": "order_id"})
    bad = (orders["order_type"] == "purchase") & (orders["order_value"] <= 0)
    if bad.any():
        log.warning("build_orders: dropping %d purchase orders with value <= 0", int(bad.sum()))
    orders = orders[~bad].reset_index(drop=True)
    for col in ("order_id", "customer_id", "order_type", "country"):
        orders[col] = orders[col].astype("string")
    for col in ("n_lines", "n_units", "n_products"):
        orders[col] = orders[col].astype("int64")
    orders["order_value"] = orders["order_value"].astype("float64")
    return validate_frame(orders, "orders")
