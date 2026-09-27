"""Artifact schemas and validation (CODE SPEC §5, §6.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pandas as pd
from pandas.api import types as pdt


class ContractError(ValueError):
    """Raised when a DataFrame violates its artifact contract."""


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    dtype: str  # string | int | float | datetime | bool | category_or_string
    nullable: bool = False


Check = Callable[[pd.DataFrame], "str | None"]  # returns an error message or None


@dataclass(frozen=True)
class Schema:
    name: str
    columns: tuple[ColumnSpec, ...]
    key: tuple[str, ...] = ()
    strict: bool = False
    checks: tuple[Check, ...] = field(default_factory=tuple)


def _dtype_ok(series: pd.Series, family: str) -> bool:
    if family == "string":
        return pdt.is_string_dtype(series) or pdt.is_object_dtype(series)
    if family == "category_or_string":
        return isinstance(series.dtype, pd.CategoricalDtype) or pdt.is_string_dtype(series) or pdt.is_object_dtype(series)
    if family == "int":
        return pdt.is_integer_dtype(series)
    if family == "float":
        return pdt.is_float_dtype(series)
    if family == "datetime":
        return pdt.is_datetime64_any_dtype(series)
    if family == "bool":
        return pdt.is_bool_dtype(series)
    raise ValueError(f"unknown dtype family {family!r}")


def _c(name: str, dtype: str, nullable: bool = False) -> ColumnSpec:
    return ColumnSpec(name, dtype, nullable)


# ---- custom checks ---------------------------------------------------------

def _lines_purchase_valid(df: pd.DataFrame) -> str | None:
    p = df[df["line_type"] == "purchase"]
    bad = p[(p["quantity"] <= 0) | (p["price"] <= 0) | p["customer_id"].isna()]
    return f"{len(bad)} purchase lines violate quantity>0 & price>0 & customer_id notna" if len(bad) else None


def _lines_types(df: pd.DataFrame) -> str | None:
    allowed = {"purchase", "adjustment", "non_product", "excluded"}
    extra = set(df["line_type"].dropna().unique()) - allowed
    return f"unknown line_type {sorted(extra)}" if extra else None


def _lines_excluded_reason(df: pd.DataFrame) -> str | None:
    bad = df[(df["line_type"] == "excluded") & df["exclude_reason"].isna()]
    return f"{len(bad)} excluded lines without exclude_reason" if len(bad) else None


def _orders_sign(df: pd.DataFrame) -> str | None:
    bad_p = ((df["order_type"] == "purchase") & (df["order_value"] <= 0)).sum()
    bad_a = ((df["order_type"] == "adjustment") & (df["order_value"] >= 0)).sum()
    return f"order_value sign violated: purchase<=0: {bad_p}, adjustment>=0: {bad_a}" if bad_p or bad_a else None


def _snap_target_binary(df: pd.DataFrame) -> str | None:
    col = next((c for c in df.columns if c.startswith("repeat_purchase_")), None)
    if col is None:
        return "missing target column repeat_purchase_*"
    return None if df[col].isin([0, 1]).all() else f"{col} must be 0/1"


def _snap_frequency(df: pd.DataFrame) -> str | None:
    return None if (df["frequency_orders"] >= 1).all() else "frequency_orders must be >= 1 (eligibility)"


def _prob_range(df: pd.DataFrame) -> str | None:
    cols = ["predicted_repeat_probability", "predicted_repeat_probability_raw"]
    bad = [c for c in cols if not df[c].between(0, 1).all()]
    return f"probabilities outside [0,1] in {bad}" if bad else None


def _action_values(df: pd.DataFrame) -> str | None:
    extra = set(df["recommended_action"].unique()) - {"TARGET", "DO_NOT_TARGET"}
    return f"unknown recommended_action {sorted(extra)}" if extra else None


def _policy_d_positive(df: pd.DataFrame) -> str | None:
    bad = df[(df["policy"] == "D") & (df["recommended_action"] == "TARGET")
             & (df["simulated_expected_incremental_margin"] <= 0)]
    return f"{len(bad)} policy-D targets with EIM <= 0" if len(bad) else None


SCHEMAS: dict[str, Schema] = {
    "transactions_raw": Schema(
        "transactions_raw",
        (_c("Invoice", "string"), _c("StockCode", "string"), _c("Description", "string", True),
         _c("Quantity", "int"), _c("InvoiceDate", "datetime"), _c("Price", "float"),
         _c("Customer ID", "float", True), _c("Country", "string"), _c("source_sheet", "string")),
    ),
    "lines": Schema(
        "lines",
        (_c("invoice", "string"), _c("stock_code", "string"), _c("description", "string", True),
         _c("quantity", "int"), _c("invoice_ts", "datetime"), _c("price", "float"),
         _c("customer_id", "string", True), _c("country", "string"), _c("source_sheet", "string"),
         _c("line_value", "float"), _c("line_type", "string"), _c("exclude_reason", "string", True)),
        checks=(_lines_types, _lines_purchase_valid, _lines_excluded_reason),
    ),
    "orders": Schema(
        "orders",
        (_c("order_id", "string"), _c("customer_id", "string"), _c("order_ts", "datetime"),
         _c("order_type", "string"), _c("order_value", "float"), _c("n_lines", "int"),
         _c("n_units", "int"), _c("n_products", "int"), _c("country", "string")),
        key=("order_id",),
        checks=(_orders_sign,),
    ),
    "customer_snapshots": Schema(
        "customer_snapshots",
        (_c("customer_id", "string"), _c("decision_date", "datetime"),
         _c("recency_days", "float"), _c("frequency_orders", "int"), _c("purchase_value", "float"),
         _c("adjustment_value", "float"), _c("monetary_net", "float"), _c("aov", "float"),
         _c("return_rate", "float"), _c("tenure_days", "float"), _c("active_months", "int"),
         _c("avg_interpurchase_days", "float", True), _c("unique_products", "int"),
         _c("total_units", "int"), _c("orders_last_30d", "int"),
         _c("t0_month_sin", "float"), _c("t0_month_cos", "float"),
         _c("cohort_month", "string"), _c("country", "string"),
         _c("repeat_purchase_90d", "int"), _c("label_future_value_90d", "float"),
         _c("feature_version", "string")),
        key=("customer_id", "decision_date"),
        checks=(_snap_target_binary, _snap_frequency),
    ),
    "customer_predictions": Schema(
        "customer_predictions",
        (_c("customer_id", "string"), _c("decision_date", "datetime"), _c("split", "string"),
         _c("actual_repeat_purchase", "int"), _c("rfm_benchmark_score", "float"),
         _c("predicted_repeat_probability_raw", "float"), _c("predicted_repeat_probability", "float"),
         _c("model_version", "string"), _c("feature_version", "string")),
        key=("customer_id", "decision_date"),
        checks=(_prob_range,),
    ),
    "scenario_results": Schema(
        "scenario_results",
        (_c("scenario", "string"), _c("scenario_version", "string"), _c("policy", "string"),
         _c("decision_date", "datetime"), _c("value_basis", "string"), _c("capacity_fraction", "float"),
         _c("capacity_k", "int"), _c("budget", "float", True), _c("seed", "int", True),
         _c("target_count", "int"), _c("expected_future_value", "float"),
         _c("expected_promotion_cost", "float"), _c("simulated_eim", "float"),
         _c("eim_per_target", "float", True), _c("discount_leakage_share", "float", True),
         _c("actual_repeat_rate_targeted", "float", True)),
        key=("scenario", "policy", "decision_date", "capacity_fraction", "seed", "value_basis"),
    ),
    "customer_targeting_table": Schema(
        "customer_targeting_table",
        (_c("customer_id", "string"), _c("decision_date", "datetime"), _c("scenario", "string"),
         _c("scenario_version", "string"), _c("policy", "string"), _c("customer_segment", "string"),
         _c("recency_days", "float"), _c("frequency_orders", "int"), _c("monetary_net", "float"),
         _c("rfm_score", "int"), _c("repeat_purchase_probability", "float"),
         _c("customer_value_proxy", "float"), _c("value_is_fallback", "bool"),
         _c("discount_rate", "float"), _c("incremental_lift_assumption", "float"),
         _c("gross_margin", "float"), _c("contact_cost", "float"),
         _c("expected_promotion_cost", "float"), _c("simulated_expected_incremental_margin", "float"),
         _c("target_rank", "int", True), _c("recommended_action", "string"), _c("model_version", "string")),
        key=("customer_id", "decision_date", "scenario", "policy"),
        checks=(_action_values, _policy_d_positive),
    ),
}


def validate_frame(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Validate ``df`` against ``SCHEMAS[name]``; return ``df`` unchanged or raise ContractError."""
    if name not in SCHEMAS:
        raise ContractError(f"unknown schema {name!r}")
    schema = SCHEMAS[name]
    errors: list[str] = []
    missing = [c.name for c in schema.columns if c.name not in df.columns]
    if missing:
        errors.append(f"missing columns {missing}")
    if schema.strict:
        extra = sorted(set(df.columns) - {c.name for c in schema.columns})
        if extra:
            errors.append(f"unexpected columns {extra}")
    for col in schema.columns:
        if col.name not in df.columns:
            continue
        s = df[col.name]
        if not _dtype_ok(s, col.dtype):
            errors.append(f"{col.name}: dtype {s.dtype} is not {col.dtype}")
        if not col.nullable and s.isna().any():
            errors.append(f"{col.name}: {int(s.isna().sum())} null values")
    if schema.key and not missing:
        dup = int(df.duplicated(list(schema.key)).sum())
        if dup:
            errors.append(f"key {schema.key}: {dup} duplicated rows")
    if not errors:
        for check in schema.checks:
            msg = check(df)
            if msg:
                errors.append(msg)
    if errors:
        raise ContractError(f"[{name}] " + "; ".join(errors))
    return df
