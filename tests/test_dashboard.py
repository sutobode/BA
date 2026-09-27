"""Dashboard tests (goal prompt Phase 6): KPIs must equal scenario_results exactly."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dashboard" / "app.py"
RESULTS = ROOT / "outputs" / "tables" / "scenario_results.csv"


def _app():
    spec = importlib.util.spec_from_file_location("dashboard_app", APP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_kpis_on_synthetic_results():
    app = _app()
    res = pd.DataFrame({
        "scenario": ["base"] * 4, "lift_structure": ["constant"] * 4, "value_basis": ["actual_outcome"] * 4,
        "capacity_fraction": [0.1] * 4, "policy": ["D", "D", "B", "B"], "seed": [None, None, 1, 2],
        "target_count": [3, 2, 10, 10], "capacity_k": [10, 10, 10, 10], "expected_future_value": [100.0, 50.0, 1, 3],
        "expected_promotion_cost": [10.0, 5.0, 1, 3], "simulated_eim": [6.0, 4.0, -2.0, -4.0],
    })
    k = app.kpis(res, "base", "constant", "actual_outcome", 0.1, "D")
    assert k["Targeted customers"] == 5 and k["Simulated incremental margin (£)"] == 10.0
    assert k["Margin per targeted customer (£)"] == 2.0
    kb = app.kpis(res, "base", "constant", "actual_outcome", 0.1, "B")
    assert kb["Simulated incremental margin (£)"] == -3.0


@pytest.mark.skipif(not RESULTS.exists(), reason="pipeline outputs not generated")
def test_kpis_match_pipeline_outputs():
    app = _app()
    res = pd.read_csv(RESULTS)
    sub = res[(res.scenario == "base") & (res.lift_structure == "constant") & (res.value_basis == "actual_outcome")
              & (res.capacity_fraction == 0.1) & (res.policy == "D")]
    k = app.kpis(res, "base", "constant", "actual_outcome", 0.1, "D")
    assert k["Simulated incremental margin (£)"] == pytest.approx(sub.simulated_eim.sum(), abs=0)
    assert k["Targeted customers"] == sub.target_count.sum()


@pytest.mark.skipif(not RESULTS.exists(), reason="pipeline outputs not generated")
def test_dashboard_renders_without_exceptions():
    st_testing = pytest.importorskip("streamlit.testing.v1")
    at = st_testing.AppTest.from_file(str(APP), default_timeout=60)
    at.run()
    assert not at.exception
    assert len(at.tabs) == 3
    assert len(at.metric) >= 5
