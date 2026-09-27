import numpy as np
import pandas as pd
import pytest

from helpers import todo
from retail_targeting.config import ConfigError
from retail_targeting.decision.simulation import (
    ScenarioParams, break_even_p, compute_eim, fit_value_cap, fit_value_fallback, incremental_lift,
    scenarios_from_config, value_proxy,
)


def _params(**kw):
    base = dict(name="t", discount_rate=0.1, incremental_lift=0.05, gross_margin=0.4, contact_cost=0.5)
    base.update(kw)
    return ScenarioParams(**base)


def test_eim_identity_random():
    rng = np.random.default_rng(0)
    for _ in range(1000):
        p = rng.random(5)
        v = rng.uniform(1, 500, 5)
        m = rng.uniform(0.2, 0.8)
        prm = _params(discount_rate=rng.uniform(0, m * 0.99), incremental_lift=rng.random(), gross_margin=m,
                      contact_cost=rng.uniform(0, 2))
        out = compute_eim(p, v, prm)
        closed = out["delta"] * v * m - (p + out["delta"]) * v * prm.discount_rate - prm.contact_cost
        assert np.allclose(out["eim"], out["m1"] - out["m0"], atol=1e-9)
        assert np.allclose(out["eim"], closed, atol=1e-9)
        assert (out["delta"] <= 1 - p + 1e-12).all()


def test_eim_no_offer_effect_costs_contact():
    out = compute_eim([0.3, 0.9], [100, 50], _params(discount_rate=0.0, incremental_lift=0.0))
    assert np.allclose(out["eim"], -0.5)


def test_eim_hand_example():
    # p=0.2, V=100, m=0.4, d=0.1, δ=0.05, c=0.5: 0.05*100*0.4 - 0.25*100*0.1 - 0.5 = 2 - 2.5 - 0.5 = -1.0
    out = compute_eim([0.2], [100.0], _params())
    assert out["eim"].iloc[0] == pytest.approx(-1.0)
    assert out["expected_cost"].iloc[0] == pytest.approx(3.0)
    assert out["leakage_discount"].iloc[0] == pytest.approx(2.0)


def test_eim_delta_capped_for_certain_buyer():
    out = compute_eim([1.0], [100.0], _params())
    assert out["delta"].iloc[0] == 0 and out["eim"].iloc[0] == pytest.approx(-10.5)


@pytest.mark.parametrize("kw", [dict(discount_rate=0.5), dict(incremental_lift=1.5), dict(contact_cost=-1)])
def test_invalid_params(kw):
    with pytest.raises(ValueError):
        _params(**kw).validate()


def test_invalid_inputs():
    with pytest.raises(ValueError):
        compute_eim([1.2], [10.0], _params())
    with pytest.raises(ValueError):
        compute_eim([0.2, 0.3], [10.0], _params())


def test_scenarios_from_config(cfg, raw_config_dict):
    import copy
    from retail_targeting.config import Config, REPO_ROOT
    sc = {s.name: s for s in scenarios_from_config(cfg)}  # frozen values D10/D11
    assert list(sc) == ["conservative", "base", "aggressive"]
    assert (sc["base"].discount_rate, sc["base"].incremental_lift, sc["base"].gross_margin) == (0.10, 0.05, 0.40)
    raw = copy.deepcopy(raw_config_dict)
    raw["simulation"]["scenarios"]["base"]["incremental_lift"] = None
    with pytest.raises(ConfigError):
        scenarios_from_config(Config(raw=raw, root=REPO_ROOT))


def test_value_fallback_train_only():
    df = pd.DataFrame({"split": ["train", "validation"], "customer_segment": ["A", "A"], "aov": [10.0, 20.0]})
    with pytest.raises(ValueError):
        fit_value_fallback(df)
    fb = fit_value_fallback(pd.DataFrame({"split": ["train"] * 3, "customer_segment": ["A", "A", "B"],
                                          "aov": [10.0, 30.0, -5.0]}))
    assert fb["A"] == 20.0 and "__all__" in fb


def test_value_proxy_uses_fallback_for_non_positive_aov():
    df = pd.DataFrame({"customer_segment": ["A", "B"], "aov": [12.0, -3.0]})
    v, is_fb = value_proxy(df, {"A": 20.0, "__all__": 15.0})
    assert list(v) == [12.0, 15.0] and list(is_fb) == [False, True]


def test_value_proxy_cap():
    df = pd.DataFrame({"customer_segment": ["A", "A"], "aov": [12.0, 5000.0]})
    v, _ = value_proxy(df, {"__all__": 15.0}, cap=1000.0)
    assert list(v) == [12.0, 1000.0]


def test_value_cap_train_only():
    tr = pd.DataFrame({"split": ["train"] * 101, "aov": [float(i) for i in range(101)]})
    assert fit_value_cap(tr, 0.99) == pytest.approx(99.01)  # quantile over aov > 0 (1..100): 1 + 0.99*99
    assert fit_value_cap(tr, None) is None
    with pytest.raises(ValueError):
        fit_value_cap(tr.assign(split="test"), 0.99)


def test_incremental_lift_structures():
    p = np.array([0.0, 0.5, 1.0])
    prm = _params(incremental_lift=0.1)
    assert np.allclose(incremental_lift(p, prm, "constant"), 0.1)
    assert np.allclose(incremental_lift(p, prm, "persuadable"), [0.0, 0.1, 0.0])
    seg = incremental_lift(p, prm, "segment", ["Dormant", "X", "High-value at risk"],
                           {"Dormant": 0.5, "High-value at risk": 1.5})
    assert np.allclose(seg, [0.05, 0.1, 0.15])
    with pytest.raises(ValueError):
        incremental_lift(p, prm, "unknown")


def test_compute_eim_with_custom_lift():
    p = np.array([0.2, 0.5])
    prm = _params()
    lift = incremental_lift(p, prm, "persuadable")
    out = compute_eim(p, np.array([100.0, 100.0]), prm, lift=lift)
    assert np.allclose(out["delta"], lift)
    assert np.allclose(out["eim"], out["m1"] - out["m0"])


def test_break_even_p_matches_eim_sign():
    prm = _params()  # d=0.1, δ=0.05, m=0.4, c=0.5
    v = np.array([50.0, 300.0, 1000.0])
    pstar = break_even_p(v, prm)
    # p* = 0.05*0.3/0.1 - 0.5/(0.1*V) = 0.15 - 5/V
    assert np.allclose(pstar, [0.05, 0.15 - 5 / 300, 0.145])
    for vi, ps in zip(v, pstar):
        below = compute_eim([max(ps - 1e-4, 0)], [vi], prm)["eim"].iloc[0]
        above = compute_eim([min(ps + 1e-4, 1)], [vi], prm)["eim"].iloc[0]
        assert below > 0 > above
    with pytest.raises(ValueError):
        break_even_p(v, _params(discount_rate=0.0))
