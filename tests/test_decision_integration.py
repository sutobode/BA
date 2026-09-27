"""Integration-level tests for decision + model modules on small synthetic data."""

import numpy as np
import pandas as pd
import pytest

from retail_targeting.contracts import validate_frame
from retail_targeting.decision.policy import build_targeting_table, run_policies, score_frame, select_policy_d, summarize
from retail_targeting.decision.sensitivity import grid_size, run_grid
from retail_targeting.decision.simulation import ScenarioParams, scenarios_from_config
from retail_targeting.models.train import build_pipeline, feature_matrix, tune_logreg


def _scored(n=200, seed=0):
    rng = np.random.default_rng(seed)
    frames = []
    for t0 in ("2011-08-01", "2011-09-01"):
        p = rng.uniform(0.01, 0.95, n)
        frames.append(pd.DataFrame({
            "customer_id": pd.Series([f"{10000 + i}" for i in range(n)], dtype="string"),
            "decision_date": pd.Timestamp(t0), "p": p, "y": (rng.random(n) < p).astype(float),
            "value": rng.uniform(50, 800, n), "value_uncapped": rng.uniform(50, 2000, n),
            "value_is_fallback": False, "rfm_score": rng.integers(3, 16, n), "monetary_net": rng.uniform(10, 5000, n),
            "recency_days": rng.uniform(1, 180, n), "frequency_orders": rng.integers(1, 10, n),
            "customer_segment": pd.Series(rng.choice(["Dormant", "Developing"], n), dtype="string"),
        }))
    return pd.concat(frames, ignore_index=True)


@pytest.mark.parametrize("basis", ["model_p", "actual_outcome"])
def test_run_policies_invariants(cfg, basis):
    scored = _scored()
    res = run_policies(scored, scenarios_from_config(cfg), cfg, value_basis=basis, n_seeds=5)
    validate_frame(res, "scenario_results")
    assert set(res["policy"]) == {"A", "B", "C", "D", "E"}
    assert (res.loc[res["policy"] == "A", "simulated_eim"] == 0).all()
    assert (res["target_count"] <= res["capacity_k"]).all()                               # INV-11
    for _, g in res.groupby(["scenario", "decision_date", "capacity_fraction"]):           # INV-12
        assert g["capacity_k"].nunique() == 1
        non_d = g[g["policy"].isin(["B", "C", "E"])]
        assert (non_d["target_count"] == non_d["capacity_k"]).all()
    again = run_policies(scored, scenarios_from_config(cfg), cfg, value_basis=basis, n_seeds=5)
    pd.testing.assert_frame_equal(res, again)                                               # reproducible
    comp = summarize(res)
    assert {"simulated_eim_p5", "simulated_eim_p95"} <= set(comp.columns)


def test_policy_d_only_positive_eim_and_targeting_table(cfg):
    scored = _scored()
    sc = ScenarioParams("t", 0.1, 0.2, 0.4, 0.1)
    g = scored[scored["decision_date"] == pd.Timestamp("2011-08-01")].reset_index(drop=True)
    f = score_frame(g, sc, "constant", {}, "model_p")
    sel = select_policy_d(f, 50, None)
    assert (f.loc[sel, "eim"] > 0).all() and sel.sum() <= 50
    tt = build_targeting_table(f, sel, sc, "D", cfg)
    validate_frame(tt, "customer_targeting_table")
    assert (tt["recommended_action"] == "TARGET").sum() == sel.sum()
    ranked = tt.dropna(subset=["target_rank"]).sort_values("target_rank")
    assert ranked["target_rank"].tolist() == list(range(1, int(sel.sum()) + 1))
    assert ranked["simulated_expected_incremental_margin"].is_monotonic_decreasing


def test_actual_outcome_basis_uses_realized_y():
    sc = ScenarioParams("t", 0.1, 0.05, 0.4, 0.1)
    g = pd.DataFrame({"customer_id": pd.Series(["a", "b"], dtype="string"), "p": [0.3, 0.3], "y": [0.0, 1.0],
                      "value": [100.0, 100.0], "customer_segment": pd.Series(["x", "x"], dtype="string")})
    f = score_frame(g, sc, "constant", {}, "actual_outcome")
    # y=0: 0.05*100*0.4 - 0.05*100*0.1 - 0.1 = 1.4 ; y=1: delta=0 -> -100*0.1 - 0.1 = -10.1
    assert f["eval_eim"].tolist() == pytest.approx([1.4, -10.1])
    assert f["eim"].iloc[0] == pytest.approx(f["eim"].iloc[1])  # selection uses model p


def test_sensitivity_grid_row_count(cfg):
    scored = _scored(60)
    base = next(s for s in scenarios_from_config(cfg) if s.name == "base")
    grid = {"discount_rate": [0.05, 0.1], "incremental_lift": [0.05, 0.1], "capacity_fractions": [0.1],
            "lift_structure": ["constant", "persuadable"], "value_cap": [True, False]}
    res = run_grid(scored, base, grid, cfg, n_seeds=3)
    assert len(res) == grid_size(grid) * 4


def test_pipeline_fits_only_train_and_rejects_leaky_features(cfg):
    rng = np.random.default_rng(1)
    feats = cfg.raw["model"]["numeric_features"]
    def frame(split, n):
        df = pd.DataFrame({f: rng.uniform(0, 100, n) for f in feats})
        df["repeat_purchase_90d"] = (rng.random(n) < 0.5).astype("int8")
        df["split"] = split
        df["customer_id"] = [f"c{i}" for i in range(n)]
        return df
    tr, va = frame("train", 300), frame("validation", 100)
    model, grid = tune_logreg(tr, va, cfg)
    assert len(grid) == len(cfg.raw["model"]["C_grid"]) * len(cfg.raw["model"]["class_weight_options"])
    with pytest.raises(ValueError):
        tune_logreg(pd.concat([tr, va]), va, cfg)             # INV-09
    import copy
    from retail_targeting.config import Config
    raw = copy.deepcopy(cfg.raw)
    raw["model"]["numeric_features"] = feats + ["label_future_value_90d"]
    with pytest.raises(ValueError):
        feature_matrix(tr.assign(label_future_value_90d=1.0), Config(raw=raw, root=cfg.root))  # INV-07
    assert build_pipeline(cfg, C=1.0, class_weight=None) is not None
