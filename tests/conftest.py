"""Shared fixtures. Expected values are hand-computed (see comments) — CODE SPEC §8."""

from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from retail_targeting.config import Config, REPO_ROOT, validate_config

EXAMPLE_CONFIG = REPO_ROOT / "project_config.example.yaml"
BOUNDARY = pd.Timestamp("2010-12-01")
SHEETS = ["Year 2009-2010", "Year 2010-2011"]

_COLS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]

# id : (Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID)  -> expected handling
_SHEET_A = [
    ("100001", "20001", "MUG", 2, "2010-01-10 10:00", 5.0, 10001.0),     # a1  purchase 10
    ("100001", "20002", "BAG", 1, "2010-01-10 10:00", 3.0, 10001.0),     # a2  purchase 3  -> order 100001 = 13
    ("100001", "POST", "POSTAGE", 1, "2010-01-10 10:00", 10.0, 10001.0), # a3  non_product
    ("100001", "20001", "MUG", 2, "2010-01-10 10:00", 5.0, 10001.0),     # a4  exact duplicate of a1 -> CR-07
    ("C100002", "20001", "MUG", -1, "2010-02-01 09:00", 5.0, 10001.0),   # a5  adjustment -5
    ("100003", "20003", "BOX", 4, "2010-03-05 12:00", 2.5, 10002.0),     # a6  purchase 10
    ("100003", "20004", "CUP", 1, "2010-03-05 12:01", 4.0, 10002.0),     # a7  purchase 4, 2nd timestamp -> order ts 12:00
    ("100004", "20005", "?", -12, "2010-04-01 08:00", 0.0, np.nan),      # a8  excluded stock_adjustment
    ("A100005", "B", "Adjust bad debt", 1, "2010-04-02 08:00", -100.0, np.nan),  # a9 excluded bad_debt_adjustment
    ("100006", "20001", "MUG", 3, "2010-05-01 08:00", 5.0, np.nan),      # a10 excluded missing_customer
    ("100007", "20006", "PEN", 1, "2010-06-01 08:00", 0.0, 10003.0),     # a11 excluded zero_price
    ("100008", "20001", "MUG", 2, "2010-12-02 10:00", 5.0, 10003.0),     # a12 overlap period -> dropped from sheet A (CR-00)
    ("100010", "20002", "BAG", 2, "2010-03-20 15:00", 3.0, 10001.0),     # a13 purchase 6
]
_SHEET_B = [
    ("100008", "20001", "MUG", 2, "2010-12-02 10:00", 5.0, 10003.0),     # b1  kept from sheet B, purchase 10
    ("100009", "20002", "BAG", 5, "2011-01-15 11:00", 3.0, 10001.0),     # b2  purchase 15
]

EXPECTED = {
    "rows_after_combine": 14,          # 12 from A (< boundary) + 2 from B
    "rows_after_dedup": 13,
    "line_type_counts": {"purchase": 7, "adjustment": 1, "non_product": 1, "excluded": 4},
    "exclude_reasons": {"stock_adjustment": 1, "bad_debt_adjustment": 1, "missing_customer": 1, "zero_price": 1},
    "orders": {  # order_id: (customer_id, order_type, order_value, order_ts, n_lines)
        "100001": ("10001", "purchase", 13.0, "2010-01-10 10:00", 2),
        "C100002": ("10001", "adjustment", -5.0, "2010-02-01 09:00", 1),
        "100003": ("10002", "purchase", 14.0, "2010-03-05 12:00", 2),
        "100010": ("10001", "purchase", 6.0, "2010-03-20 15:00", 1),
        "100008": ("10003", "purchase", 10.0, "2010-12-02 10:00", 1),
        "100009": ("10001", "purchase", 15.0, "2011-01-15 11:00", 1),
    },
    # snapshot T0=2010-02-01 (obs [2009-08-05, 2010-02-01), outcome [2010-02-01, 2010-05-02))
    "snap_2010_02_01": {
        "10001": dict(recency_days=21 + 14 / 24, frequency_orders=1, purchase_value=13.0, adjustment_value=0.0,
                      monetary_net=13.0, aov=13.0, repeat_purchase_90d=1, label_future_value_90d=6.0),
    },
    # snapshot T0=2010-06-01 (obs [2009-12-03, 2010-06-01), outcome [2010-06-01, 2010-08-30))
    "snap_2010_06_01": {
        "10001": dict(recency_days=72 + 9 / 24, frequency_orders=2, purchase_value=19.0, adjustment_value=5.0,
                      monetary_net=14.0, aov=7.0, return_rate=5 / 19, avg_interpurchase_days=69 + 5 / 24,
                      active_months=2, unique_products=2, total_units=5, tenure_days=141 + 14 / 24,
                      repeat_purchase_90d=0),
        "10002": dict(recency_days=87.5, frequency_orders=1, monetary_net=14.0, repeat_purchase_90d=0),  # Mar5 12:00 → Jun1
    },
}


def _frame(rows: list[tuple]) -> pd.DataFrame:
    df = pd.DataFrame([(*r[:7], "United Kingdom") for r in rows], columns=_COLS)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Invoice"] = df["Invoice"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["Quantity"] = df["Quantity"].astype("int64")
    df["Price"] = df["Price"].astype("float64")
    df["Customer ID"] = df["Customer ID"].astype("float64")
    return df


@pytest.fixture
def tiny_sheets() -> dict[str, pd.DataFrame]:
    return {SHEETS[0]: _frame(_SHEET_A), SHEETS[1]: _frame(_SHEET_B)}


@pytest.fixture
def raw_config_dict() -> dict:
    with EXAMPLE_CONFIG.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def cfg(raw_config_dict) -> Config:
    validate_config(raw_config_dict)
    return Config(raw=raw_config_dict, root=REPO_ROOT)


@pytest.fixture
def cfg_with_scenarios(raw_config_dict) -> Config:
    raw = copy.deepcopy(raw_config_dict)
    raw["simulation"]["scenarios"] = {
        # Test-only values; NOT project assumptions (D10/D11 still open).
        "conservative": {"discount_rate": 0.05, "incremental_lift": 0.02, "gross_margin": 0.4, "contact_cost": 0.5},
        "base": {"discount_rate": 0.10, "incremental_lift": 0.05, "gross_margin": 0.4, "contact_cost": 0.5},
        "aggressive": {"discount_rate": 0.20, "incremental_lift": 0.10, "gross_margin": 0.4, "contact_cost": 0.5},
    }
    validate_config(raw, require_scenarios=True)
    return Config(raw=raw, root=REPO_ROOT)


@pytest.fixture
def tmp_path_file(tmp_path: Path) -> Path:
    p = tmp_path / "f.bin"
    p.write_bytes(b"abc")
    return p
