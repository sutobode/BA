import numpy as np
import pandas as pd

from helpers import todo
from retail_targeting.decision.policy import (
    capacity_from_fraction, select_policy_a, select_policy_b, select_policy_c, select_policy_d, select_policy_e,
)


def _frame():
    return pd.DataFrame({
        "customer_id": pd.Series(["c1", "c2", "c3", "c4", "c5"], dtype="string"),
        "rfm_score": [15, 12, 12, 5, 3],
        "monetary_net": [100.0, 50.0, 80.0, 10.0, 5.0],
        "eim": [-1.0, 4.0, 4.0, 2.0, 0.0],
        "expected_cost": [5.0, 3.0, 3.0, 1.0, 1.0],
    })


def test_capacity():
    assert capacity_from_fraction(2768, 0.10) == 276 and capacity_from_fraction(3, 0.05) == 1


def test_policy_a_selects_nobody():
    assert not select_policy_a(_frame()).any()


def test_policy_b_reproducible_and_k():
    a, b = select_policy_b(_frame(), 2, seed=7), select_policy_b(_frame(), 2, seed=7)
    assert a.sum() == 2 and np.array_equal(a, b)


def test_policy_c_ties_by_monetary():
    sel = select_policy_c(_frame(), 2)
    assert _frame().loc[sel, "customer_id"].tolist() == ["c1", "c3"]


def test_policy_e_lowest_p():
    f = _frame().assign(p=[0.9, 0.1, 0.1, 0.5, 0.3])
    assert f.loc[select_policy_e(f, 2), "customer_id"].tolist() == ["c2", "c3"]  # tie → customer_id asc


def test_policy_d_positive_eim_tiebreak_and_budget():
    f = _frame()
    sel = select_policy_d(f, 10, budget=None)
    assert f.loc[sel, "customer_id"].tolist() == ["c2", "c3", "c4"]  # eim>0 only; c5 (eim=0) excluded
    sel_k = select_policy_d(f, 1, budget=None)
    assert f.loc[sel_k, "customer_id"].tolist() == ["c2"]  # tie on eim → customer_id asc
    sel_b = select_policy_d(f, 10, budget=6.0)
    assert f.loc[sel_b, "expected_cost"].sum() <= 6.0 and sel_b.sum() == 2
