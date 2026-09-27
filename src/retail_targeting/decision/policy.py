"""Targeting policies A/B/C/D and comparison (SPEC §10, CODE SPEC §6.14). Owner: M3.

Selection always uses model probabilities. Evaluation is reported for two value bases
(D24): ``model_p`` (model belief) and ``actual_outcome`` (realized y substituted for p on
validation/test) to avoid scoring policy D with the same numbers used to select it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from retail_targeting.config import Config
from retail_targeting.decision.simulation import ScenarioParams

POLICIES = ("A", "B", "C", "D", "E")
VALUE_BASES = ("model_p", "actual_outcome")


def capacity_from_fraction(n_eligible: int, frac: float) -> int:
    """k = max(1, floor(frac * n_eligible))."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def select_policy_a(frame: pd.DataFrame) -> np.ndarray:
    """No promotion: all False."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def select_policy_b(frame: pd.DataFrame, k: int, seed: int) -> np.ndarray:
    """Random k rows without replacement using numpy.random.default_rng(seed)."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def select_policy_c(frame: pd.DataFrame, k: int) -> np.ndarray:
    """Top-k by rfm_score desc, tie monetary_net desc, then customer_id asc. No EIM filter."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def select_policy_d(frame: pd.DataFrame, k: int, budget: float | None) -> np.ndarray:
    """Rows with eim > 0 ranked by eim desc, tie customer_id asc; take while count < k and
    cumulative expected_cost <= budget (if budget is set). ``frame`` must have eim, expected_cost.
    INV-11: count <= k, Σcost <= budget, no selected row with eim <= 0."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def select_policy_e(frame: pd.DataFrame, k: int) -> np.ndarray:
    """D26 baseline: k rows with the lowest ``p`` (asc, tie customer_id asc). No EIM filter.
    Policy D must beat E for value weighting to add anything."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def summarize_selection(frame: pd.DataFrame, selected: np.ndarray, value_basis: str) -> dict:
    """target_count, expected_future_value, expected_promotion_cost, simulated_eim, eim_per_target,
    discount_leakage_share, actual_repeat_rate_targeted (CODE SPEC §5.6)."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def run_policies(scored: pd.DataFrame, scenarios: list[ScenarioParams], cfg: Config, *,
                 value_basis: str) -> pd.DataFrame:
    """For each decision_date × scenario × capacity_fraction: run A, B (random_baseline_seeds seeds),
    C, D, E on the same customers and k (INV-12), with simulation.lift_structure.
    Returns rows of contract ``scenario_results``."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    """policy_comparison: mean/p5/p95 of simulated_eim etc. per scenario × policy × capacity × value_basis."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")


def build_targeting_table(scored: pd.DataFrame, selected: np.ndarray, scenario: ScenarioParams,
                          policy: str, cfg: Config) -> pd.DataFrame:
    """Customer-level score table (contract ``customer_targeting_table``)."""
    raise NotImplementedError("M3 — CODE SPEC §6.14")
