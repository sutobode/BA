"""Promotion scenario model (SPEC §9, CODE SPEC §6.13).

EIM is a scenario-based *simulated* expected incremental margin under stated
assumptions. It is not a causal estimate, ROI or observed revenue lift.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike

from retail_targeting.config import Config, ConfigError, SCENARIO_KEYS


@dataclass(frozen=True)
class ScenarioParams:
    name: str
    discount_rate: float      # d
    incremental_lift: float   # δ — assumed, not estimated
    gross_margin: float       # m
    contact_cost: float       # c (per targeted customer)
    version: str = "v0"

    def validate(self) -> None:
        if not (0 <= self.discount_rate < self.gross_margin <= 1):
            raise ValueError(f"{self.name}: require 0 <= discount_rate < gross_margin <= 1")
        if not (0 <= self.incremental_lift <= 1):
            raise ValueError(f"{self.name}: incremental_lift must be in [0, 1]")
        if self.contact_cost < 0:
            raise ValueError(f"{self.name}: contact_cost must be >= 0")


def scenarios_from_config(cfg: Config) -> list[ScenarioParams]:
    """Build validated scenarios; raise ConfigError if any value is still null (D10/D11)."""
    sim = cfg.raw["simulation"]
    version = cfg.raw["versions"]["scenario_version"]
    out: list[ScenarioParams] = []
    for name, params in sim["scenarios"].items():
        if any(params.get(k) is None for k in SCENARIO_KEYS):
            raise ConfigError(f"simulation.scenarios.{name} has null values; freeze D10/D11 first")
        sp = ScenarioParams(name=name, version=version, **{k: float(params[k]) for k in SCENARIO_KEYS})
        sp.validate()
        out.append(sp)
    return out


def compute_eim(p: ArrayLike, value: ArrayLike, params: ScenarioParams) -> pd.DataFrame:
    """Per-customer expected margins under one scenario.

    ``p`` is the natural repeat probability (model output, or the realized 0/1
    outcome when ``value_basis == "actual_outcome"``); ``value`` is V_i, the
    expected net value of one order.

    Returns columns: delta, m0, m1, eim, expected_cost, expected_value, leakage_discount.
    Invariant (INV-10): eim == m1 - m0.
    """
    params.validate()
    p_arr = np.asarray(p, dtype=float)
    v_arr = np.asarray(value, dtype=float)
    if p_arr.shape != v_arr.shape:
        raise ValueError("p and value must have the same shape")
    if np.any((p_arr < 0) | (p_arr > 1)) or np.isnan(p_arr).any():
        raise ValueError("p must be in [0, 1] with no NaN")
    if np.isnan(v_arr).any():
        raise ValueError("value must not contain NaN")

    d, m, c = params.discount_rate, params.gross_margin, params.contact_cost
    delta = np.minimum(params.incremental_lift, 1.0 - p_arr)
    m0 = p_arr * v_arr * m
    m1 = (p_arr + delta) * v_arr * (m - d) - c
    eim = m1 - m0
    return pd.DataFrame({
        "delta": delta,
        "m0": m0,
        "m1": m1,
        "eim": eim,
        "expected_cost": (p_arr + delta) * v_arr * d + c,
        "expected_value": (p_arr + delta) * v_arr,
        "leakage_discount": p_arr * v_arr * d,
    })


def fit_value_fallback(train: pd.DataFrame) -> dict[str, float]:
    """Median positive ``aov`` per ``customer_segment`` on TRAIN rows only, plus key '__all__' (D23).

    Must raise ValueError if ``train`` contains rows whose ``split`` != "train" (INV-09).
    """
    raise NotImplementedError("M3 — CODE SPEC §6.13")


def value_proxy(df: pd.DataFrame, fallback: dict[str, float]) -> tuple[pd.Series, pd.Series]:
    """V_i = aov if aov > 0 else fallback[segment] (or fallback['__all__']).

    Returns (value, value_is_fallback) aligned with ``df.index``.
    """
    raise NotImplementedError("M3 — CODE SPEC §6.13")
