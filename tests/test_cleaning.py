import pandas as pd
import pytest

from conftest import BOUNDARY, EXPECTED, SHEETS
from helpers import todo
from retail_targeting.contracts import validate_frame
from retail_targeting.data.clean import build_orders, clean_transactions, is_non_product, standardize_columns
from retail_targeting.data.ingest import combine_sheets


def _lines(tiny_sheets, cfg):
    raw = combine_sheets(tiny_sheets, BOUNDARY, SHEETS)
    return clean_transactions(raw, cfg)


@todo
def test_standardize_columns(tiny_sheets):
    raw = pd.concat(tiny_sheets.values()).assign(source_sheet="x")
    out = standardize_columns(raw)
    assert {"invoice", "stock_code", "invoice_ts", "price", "customer_id"} <= set(out.columns)
    ids = out["customer_id"].dropna().unique().tolist()
    assert "10001" in ids and all("." not in i for i in ids)


@todo
def test_is_non_product():
    s = pd.Series(["POST", "20001", "ADJUST2", "gift_0001_20", "DCGS0058", "M", "m", "85123A"])
    out = is_non_product(s, ["POST", "M", "m"], ["ADJUST", "gift_"])
    assert out.tolist() == [True, False, True, True, False, True, True, False]


@todo
def test_line_types_and_reasons(tiny_sheets, cfg):
    lines, log = _lines(tiny_sheets, cfg)
    validate_frame(lines, "lines")
    assert len(lines) == EXPECTED["rows_after_dedup"]
    assert lines["line_type"].value_counts().to_dict() == EXPECTED["line_type_counts"]
    assert lines["exclude_reason"].value_counts().to_dict() == EXPECTED["exclude_reasons"]
    assert {"rule_id", "rows_before", "rows_after", "rows_affected"} <= set(log.columns)


@todo
def test_bad_debt_precedes_non_product(tiny_sheets, cfg):
    lines, _ = _lines(tiny_sheets, cfg)
    row = lines[lines["invoice"] == "A100005"].iloc[0]
    assert row["line_type"] == "excluded" and row["exclude_reason"] == "bad_debt_adjustment"


@todo
def test_build_orders(tiny_sheets, cfg):
    lines, _ = _lines(tiny_sheets, cfg)
    orders = validate_frame(build_orders(lines), "orders").set_index("order_id")
    assert set(orders.index) == set(EXPECTED["orders"])
    for oid, (cust, otype, value, ts, n_lines) in EXPECTED["orders"].items():
        o = orders.loc[oid]
        assert (o["customer_id"], o["order_type"], o["n_lines"]) == (cust, otype, n_lines)
        assert o["order_value"] == pytest.approx(value)
        assert o["order_ts"] == pd.Timestamp(ts)  # min timestamp for invoice 100003
