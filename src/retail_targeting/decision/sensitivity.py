"""Sensitivity analysis (SPEC §9.3, CODE SPEC §6.15). Owner: M3."""

from __future__ import annotations

import pandas as pd

from retail_targeting.config import Config
from retail_targeting.decision.simulation import ScenarioParams


def run_grid(scored: pd.DataFrame, base: ScenarioParams, grid: dict[str, list[float]], cfg: Config) -> pd.DataFrame:
    """Cartesian product of grid values (discount_rate × incremental_lift × capacity_fractions, plus
    gross_margin/contact_cost if given); policies B (mean, p5, p95 over seeds), C, D;
    value_basis="actual_outcome". Row count must equal the product of grid sizes × policies."""
    raise NotImplementedError("M3 — CODE SPEC §6.15")


def break_even(grid_df: pd.DataFrame) -> pd.DataFrame:
    """Grid points where simulated_eim(D) <= mean simulated_eim(B)."""
    raise NotImplementedError("M3 — CODE SPEC §6.15")
