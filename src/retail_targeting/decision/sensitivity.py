"""Sensitivity analysis (SPEC §9.3, §9.4, CODE SPEC §6.15). Owner: M3.

Every grid point is a simulation under stated assumptions; nothing here is a causal estimate.
"""

from __future__ import annotations

import dataclasses
import itertools

import numpy as np
import pandas as pd

from retail_targeting.config import Config
from retail_targeting.decision.policy import (
    capacity_from_fraction, score_frame, select_policy_b, select_policy_c, select_policy_d, select_policy_e,
    summarize_selection,
)
from retail_targeting.decision.simulation import ScenarioParams

GRID_POLICIES = ("B", "C", "D", "E")


def grid_size(grid: dict[str, list]) -> int:
    return int(np.prod([len(v) for v in grid.values()]))


def run_grid(scored: pd.DataFrame, base: ScenarioParams, grid: dict[str, list[float]], cfg: Config,
             *, value_basis: str = "actual_outcome", n_seeds: int | None = None) -> pd.DataFrame:
    """Cartesian product of grid values (discount_rate × incremental_lift × capacity_fractions, plus
    gross_margin/contact_cost/lift_structure/value_cap if given); policies B (mean, p5, p95 over seeds), C, D, E;
    value_basis="actual_outcome". Row count must equal the product of grid sizes × policies.

    Metrics are totals over all decision dates in ``scored``. ``value_cap=False`` uses column
    ``value_uncapped`` (must exist in ``scored``).
    """
    sim = cfg.raw["simulation"]
    mult = sim.get("segment_lift_multipliers") or {}
    seeds = list(range(cfg.raw["project"]["random_seed"],
                       cfg.raw["project"]["random_seed"] + (n_seeds or sim["random_baseline_seeds"])))
    grid = dict(grid)
    grid.setdefault("lift_structure", [sim.get("lift_structure", "constant")])
    grid.setdefault("value_cap", [True])
    keys = list(grid)
    groups = [g.sort_values("customer_id", kind="mergesort").reset_index(drop=True)
              for _, g in scored.groupby("decision_date", sort=True)]
    rows = []
    for combo in itertools.product(*(grid[k] for k in keys)):
        point = dict(zip(keys, combo))
        params = dataclasses.replace(base, **{k: float(point[k]) for k in
                                              ("discount_rate", "incremental_lift", "gross_margin", "contact_cost")
                                              if k in point})
        if not (0 <= params.discount_rate < params.gross_margin):
            for pol in GRID_POLICIES:
                rows.append({**point, "policy": pol, "valid": False})
            continue
        acc = {pol: [] for pol in GRID_POLICIES}
        b_runs = np.zeros(len(seeds))
        for g in groups:
            gg = g if point["value_cap"] else g.assign(value=g["value_uncapped"])
            f = score_frame(gg, params, point["lift_structure"], mult, value_basis)
            f["contact_cost"] = params.contact_cost
            k = capacity_from_fraction(len(f), point["capacity_fractions"])
            for pol, sel in (("C", select_policy_c(f, k)), ("D", select_policy_d(f, k, None)), ("E", select_policy_e(f, k))):
                acc[pol].append(summarize_selection(f, sel, value_basis))
            ev = f["eval_eim"].to_numpy()
            for i, seed in enumerate(seeds):
                b_runs[i] += float(ev[select_policy_b(f, k, seed)].sum())
        for pol in ("C", "D", "E"):
            eim = sum(a["simulated_eim"] for a in acc[pol])
            n = sum(a["target_count"] for a in acc[pol])
            rows.append({**point, "policy": pol, "valid": True, "target_count": n, "simulated_eim": eim,
                         "eim_per_target": eim / n if n else np.nan,
                         "simulated_eim_p5": eim, "simulated_eim_p95": eim})
        rows.append({**point, "policy": "B", "valid": True,
                     "target_count": sum(capacity_from_fraction(len(g), point["capacity_fractions"]) for g in groups),
                     "simulated_eim": float(b_runs.mean()), "eim_per_target": np.nan,
                     "simulated_eim_p5": float(np.quantile(b_runs, 0.05)),
                     "simulated_eim_p95": float(np.quantile(b_runs, 0.95))})
    out = pd.DataFrame(rows)
    out["value_basis"] = value_basis
    return out


def break_even(grid_df: pd.DataFrame) -> pd.DataFrame:
    """Grid points where simulated_eim(D) <= mean simulated_eim(B)."""
    params = [c for c in grid_df.columns if c not in
              ("policy", "valid", "target_count", "simulated_eim", "eim_per_target", "simulated_eim_p5",
               "simulated_eim_p95", "value_basis")]
    v = grid_df[grid_df["valid"]]
    wide = v.pivot_table(index=params, columns="policy", values="simulated_eim", aggfunc="first").reset_index()
    wide["d_minus_b"] = wide["D"] - wide["B"]
    wide["d_minus_e"] = wide["D"] - wide["E"]
    wide["d_minus_c"] = wide["D"] - wide["C"]
    return wide[wide["D"] <= wide["B"]].reset_index(drop=True)


def dominance_summary(grid_df: pd.DataFrame) -> pd.DataFrame:
    """Share of valid grid points where D beats B, C, E (by lift structure)."""
    params = [c for c in grid_df.columns if c not in
              ("policy", "valid", "target_count", "simulated_eim", "eim_per_target", "simulated_eim_p5",
               "simulated_eim_p95", "value_basis")]
    v = grid_df[grid_df["valid"]]
    wide = v.pivot_table(index=params, columns="policy", values="simulated_eim", aggfunc="first").reset_index()
    rows = []
    for ls, g in wide.groupby("lift_structure"):
        rows.append({"lift_structure": ls, "n_points": len(g),
                     "share_D_gt_B": float((g["D"] > g["B"]).mean()),
                     "share_D_ge_C": float((g["D"] >= g["C"]).mean()),
                     "share_D_gt_E": float((g["D"] > g["E"]).mean()),
                     "share_D_positive": float((g["D"] > 0).mean()),
                     "share_D_targets_nobody": float((g["D"] == 0).mean())})
    return pd.DataFrame(rows)
