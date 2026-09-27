"""Leakage tests (SPEC §6, INV-05/06). Independent of cleaning: orders/lines are built by hand."""

import pandas as pd
import pytest

from helpers import todo
from retail_targeting.features.snapshots import build_snapshot

T0 = pd.Timestamp("2010-06-01")
FEATURES = ["recency_days", "frequency_orders", "purchase_value", "adjustment_value", "monetary_net", "aov",
            "return_rate", "tenure_days", "active_months", "unique_products", "total_units", "orders_last_30d"]


def _frames(extra_orders=()):
    rows = [("o1", "10001", "2010-03-01 10:00", "purchase", 20.0, "20001", 2),
            ("o2", "10001", "2010-05-15 10:00", "purchase", 30.0, "20002", 3),
            *extra_orders]
    orders = pd.DataFrame({
        "order_id": pd.Series([r[0] for r in rows], dtype="string"),
        "customer_id": pd.Series([r[1] for r in rows], dtype="string"),
        "order_ts": pd.to_datetime([r[2] for r in rows]),
        "order_type": pd.Series([r[3] for r in rows], dtype="string"),
        "order_value": [r[4] for r in rows],
        "n_lines": 1, "n_units": [abs(r[6]) for r in rows], "n_products": 1,
        "country": pd.Series(["United Kingdom"] * len(rows), dtype="string"),
    })
    lines = pd.DataFrame({
        "invoice": orders["order_id"], "stock_code": pd.Series([r[5] for r in rows], dtype="string"),
        "description": pd.Series(["x"] * len(rows), dtype="string"), "quantity": [r[6] for r in rows],
        "invoice_ts": orders["order_ts"], "price": [abs(r[4] / r[6]) for r in rows],
        "customer_id": orders["customer_id"], "country": orders["country"],
        "source_sheet": pd.Series(["s"] * len(rows), dtype="string"), "line_value": orders["order_value"],
        "line_type": orders["order_type"], "exclude_reason": pd.Series([None] * len(rows), dtype="string"),
    })
    return orders, lines


@todo
def test_future_orders_do_not_change_features(cfg):
    base = build_snapshot(*_frames(), T0, cfg).set_index("customer_id")
    future = [("o3", "10001", "2010-06-01 00:00", "purchase", 500.0, "20009", 50),   # exactly at T0 → outcome
              ("C4", "10001", "2010-06-10 00:00", "adjustment", -30.0, "20002", -3)]
    with_future = build_snapshot(*_frames(future), T0, cfg).set_index("customer_id")
    pd.testing.assert_frame_equal(base[FEATURES], with_future[FEATURES])
    assert base.loc["10001", "repeat_purchase_90d"] == 0
    assert with_future.loc["10001", "repeat_purchase_90d"] == 1
    assert with_future.loc["10001", "label_future_value_90d"] == pytest.approx(500.0)


@todo
def test_order_after_outcome_window_is_ignored(cfg):
    late = [("o5", "10001", "2010-08-30 00:00", "purchase", 50.0, "20001", 5)]  # T0 + 90d → excluded
    snap = build_snapshot(*_frames(late), T0, cfg).set_index("customer_id")
    assert snap.loc["10001", "repeat_purchase_90d"] == 0
