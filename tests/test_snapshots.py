import pandas as pd
import pytest

from conftest import BOUNDARY, EXPECTED, SHEETS
from helpers import todo
from retail_targeting.data.clean import build_orders, clean_transactions
from retail_targeting.data.ingest import combine_sheets
from retail_targeting.features.snapshots import build_snapshot, generate_t0_dates


@todo
def test_t0_dates_real_data_range(cfg):
    dates = generate_t0_dates(pd.Timestamp("2009-12-01 07:45"), pd.Timestamp("2011-12-09 12:50"), cfg)
    assert len(dates) == 16
    assert dates[0] == pd.Timestamp("2010-06-01") and dates[-1] == pd.Timestamp("2011-09-01")
    assert all(d.day == 1 for d in dates)


def _prep(tiny_sheets, cfg):
    lines, _ = clean_transactions(combine_sheets(tiny_sheets, BOUNDARY, SHEETS), cfg)
    return build_orders(lines), lines


@todo
@pytest.mark.parametrize("t0, key", [("2010-02-01", "snap_2010_02_01"), ("2010-06-01", "snap_2010_06_01")])
def test_snapshot_values(tiny_sheets, cfg, t0, key):
    orders, lines = _prep(tiny_sheets, cfg)
    snap = build_snapshot(orders, lines, pd.Timestamp(t0), cfg).set_index("customer_id")
    assert set(snap.index) == set(EXPECTED[key])  # 10003 never eligible (only zero-price / later orders)
    for cust, exp in EXPECTED[key].items():
        for col, val in exp.items():
            assert snap.loc[cust, col] == pytest.approx(val), (cust, col)
    assert (snap["decision_date"] == pd.Timestamp(t0)).all()
