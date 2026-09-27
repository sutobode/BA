"""Targeting policies A/B/C/D/E and comparison (SPEC §10, CODE SPEC §6.14). Owner: M3.

Selection always uses model probabilities. Evaluation is reported for two value bases
(D24): ``model_p`` (model belief) and ``actual_outcome`` (realized y substituted for p on
validation/test) to avoid scoring policy D with the same numbers used to select it.
All outputs are simulated expected values under stated assumptions — not causal estimates.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from retail_targeting.config import Config
from retail_targeting.decision.simulation import ScenarioParams, compute_eim, incremental_lift

POLICIES = ("A", "B", "C", "D", "E")
VALUE_BASES = ("model_p", "actual_outcome")


def capacity_from_fraction(n_eligible: int, frac: float) -> int:
    """k = max(1, floor(frac * n_eligible))."""
    return max(1, int(np.floor(frac * n_eligible)))


def _ids(frame: pd.DataFrame) -> np.ndarray:
    return frame["customer_id"].astype(str).to_numpy()


def _take(n: int, order: np.ndarray, k: int) -> np.ndarray:
    sel = np.zeros(n, dtype=bool)
    sel[order[:k]] = True
    return sel


def select_policy_a(frame: pd.DataFrame) -> np.ndarray:
    """No promotion: all False."""
    return np.zeros(len(frame), dtype=bool)


def select_policy_b(frame: pd.DataFrame, k: int, seed: int) -> np.ndarray:
    """Random k rows without replacement using numpy.random.default_rng(seed)."""
    sel = np.zeros(len(frame), dtype=bool)
    sel[np.random.default_rng(seed).choice(len(frame), size=min(k, len(frame)), replace=False)] = True
    return sel


def select_policy_c(frame: pd.DataFrame, k: int) -> np.ndarray:
    """Top-k by rfm_score desc, tie monetary_net desc, then customer_id asc. No EIM filter."""
    order = np.lexsort((_ids(frame), -frame["monetary_net"].to_numpy(dtype=float),
                        -frame["rfm_score"].to_numpy(dtype=float)))
    return _take(len(frame), order, k)


def select_policy_d(frame: pd.DataFrame, k: int, budget: float | None) -> np.ndarray:
    """Rows with eim > 0 ranked by eim desc, tie customer_id asc; take while count < k and
    cumulative expected_cost <= budget (if budget is set). ``frame`` must have eim, expected_cost.
    INV-11: count <= k, Σcost <= budget, no selected row with eim <= 0."""
    eim = frame["eim"].to_numpy(dtype=float)
    cost = frame["expected_cost"].to_numpy(dtype=float)
    order = np.lexsort((_ids(frame), -eim))
    order = order[eim[order] > 0][:k]
    if budget is not None:
        order = order[np.cumsum(cost[order]) <= budget]
    sel = np.zeros(len(frame), dtype=bool)
    sel[order] = True
    return sel


def select_policy_e(frame: pd.DataFrame, k: int) -> np.ndarray:
    """D26 baseline: k rows with the lowest ``p`` (asc, tie customer_id asc). No EIM filter.
    Policy D must beat E for value weighting to add anything."""
    order = np.lexsort((_ids(frame), frame["p"].to_numpy(dtype=float)))
    return _take(len(frame), order, k)


def score_frame(scored: pd.DataFrame, scenario: ScenarioParams, structure: str,
                multipliers: dict | None, basis: str) -> pd.DataFrame:
    """Add eim/expected_cost/expected_value/leakage_discount/delta for one scenario.

    Selection columns (``eim``, ``expected_cost``) always use model p; evaluation columns
    (``eval_*``) use p (model_p) or the realized outcome y (actual_outcome).
    """
    f = scored.copy()
    p = f["p"].to_numpy(dtype=float)
    v = f["value"].to_numpy(dtype=float)
    seg = f["customer_segment"].astype(str).to_numpy() if "customer_segment" in f else None
    lift = incremental_lift(p, scenario, structure, seg, multipliers)
    sel = compute_eim(p, v, scenario, lift=lift)
    f["delta"] = sel["delta"].to_numpy()
    f["eim"] = sel["eim"].to_numpy()
    f["expected_cost"] = sel["expected_cost"].to_numpy()
    if basis == "model_p":
        ev = sel
    elif basis == "actual_outcome":
        y = f["y"].to_numpy(dtype=float)
        ev = compute_eim(y, v, scenario, lift=lift)  # same assumed lift, capped at 1 - y
    else:
        raise ValueError(f"unknown value_basis {basis!r}")
    for c in ("eim", "expected_cost", "expected_value", "leakage_discount"):
        f[f"eval_{c}"] = ev[c].to_numpy()
    return f


def summarize_selection(frame: pd.DataFrame, selected: np.ndarray, value_basis: str) -> dict:
    """target_count, expected_future_value, expected_promotion_cost, simulated_eim, eim_per_target,
    discount_leakage_share, actual_repeat_rate_targeted (CODE SPEC §5.6)."""
    s = frame[selected]
    n = int(selected.sum())
    disc = float((s["eval_expected_cost"] - s["contact_cost"]).sum()) if "contact_cost" in s else float("nan")
    eim = float(s["eval_eim"].sum())
    return {
        "target_count": n,
        "expected_future_value": float(s["eval_expected_value"].sum()),
        "expected_promotion_cost": float(s["eval_expected_cost"].sum()),
        "simulated_eim": eim,
        "eim_per_target": eim / n if n else np.nan,
        "discount_leakage_share": float(s["eval_leakage_discount"].sum()) / disc if n and disc > 0 else np.nan,
        "actual_repeat_rate_targeted": float(s["y"].mean()) if n and "y" in s else np.nan,
    }


def run_policies(scored: pd.DataFrame, scenarios: list[ScenarioParams], cfg: Config, *,
                 value_basis: str, lift_structure: str | None = None,
                 capacity_fractions: list[float] | None = None, n_seeds: int | None = None) -> pd.DataFrame:
    """For each decision_date × scenario × capacity_fraction: run A, B (random_baseline_seeds seeds),
    C, D, E on the same customers and k (INV-12), with simulation.lift_structure.
    Returns rows of contract ``scenario_results``.

    ``scored`` needs: customer_id, decision_date, p, y, value, rfm_score, monetary_net, customer_segment.
    """
    sim = cfg.raw["simulation"]
    structure = lift_structure or sim.get("lift_structure", "constant")
    mult = sim.get("segment_lift_multipliers") or {}
    fracs = capacity_fractions or sim["capacity_fractions"]
    seeds = range(cfg.raw["project"]["random_seed"],
                  cfg.raw["project"]["random_seed"] + (n_seeds or sim["random_baseline_seeds"]))
    budget = sim.get("budget")
    rows = []
    for t0, g in scored.groupby("decision_date", sort=True):
        g = g.sort_values("customer_id", kind="mergesort").reset_index(drop=True)
        for sc in scenarios:
            f = score_frame(g, sc, structure, mult, value_basis)
            f["contact_cost"] = sc.contact_cost
            for frac in fracs:
                k = capacity_from_fraction(len(f), frac)
                base = {"scenario": sc.name, "scenario_version": sc.version, "lift_structure": structure,
                        "decision_date": t0, "value_basis": value_basis, "capacity_fraction": float(frac),
                        "capacity_k": k, "budget": np.nan if budget is None else float(budget)}
                selections = {"A": select_policy_a(f), "C": select_policy_c(f, k),
                              "D": select_policy_d(f, k, budget), "E": select_policy_e(f, k)}
                for pol, sel in selections.items():
                    rows.append({**base, "policy": pol, "seed": pd.NA, **summarize_selection(f, sel, value_basis)})
                for seed in seeds:
                    rows.append({**base, "policy": "B", "seed": seed,
                                 **summarize_selection(f, select_policy_b(f, k, seed), value_basis)})
    out = pd.DataFrame(rows)
    for c in ("scenario", "scenario_version", "policy", "lift_structure", "value_basis"):
        out[c] = out[c].astype("string")
    out["seed"] = out["seed"].astype("Int64")
    out["decision_date"] = pd.to_datetime(out["decision_date"]).astype("datetime64[ns]")
    for c in ("capacity_k", "target_count"):
        out[c] = out[c].astype("int64")
    for c in ("budget", "eim_per_target", "discount_leakage_share", "actual_repeat_rate_targeted"):
        out[c] = out[c].astype("float64")
    return out


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    """policy_comparison: mean/p5/p95 of simulated_eim etc. per scenario × policy × capacity × value_basis.
    Snapshots are summed first (total over test/validation T0s), then B is summarized over seeds."""
    keys = ["scenario", "lift_structure", "value_basis", "capacity_fraction", "policy"]
    per_seed = (results.assign(seed=results["seed"].fillna(-1))
                .groupby(keys + ["seed"], observed=True)
                .agg(target_count=("target_count", "sum"), capacity_k=("capacity_k", "sum"),
                     expected_promotion_cost=("expected_promotion_cost", "sum"),
                     expected_future_value=("expected_future_value", "sum"),
                     simulated_eim=("simulated_eim", "sum")).reset_index())
    g = per_seed.groupby(keys, observed=True)
    out = g.agg(n_runs=("seed", "size"), capacity_k=("capacity_k", "mean"), target_count=("target_count", "mean"),
                expected_promotion_cost=("expected_promotion_cost", "mean"),
                expected_future_value=("expected_future_value", "mean"),
                simulated_eim=("simulated_eim", "mean")).reset_index()
    out["simulated_eim_p5"] = g["simulated_eim"].quantile(0.05).to_numpy()
    out["simulated_eim_p95"] = g["simulated_eim"].quantile(0.95).to_numpy()
    out["eim_per_target"] = out["simulated_eim"] / out["target_count"].replace(0, np.nan)
    return out.sort_values(keys).reset_index(drop=True)


def build_targeting_table(scored: pd.DataFrame, selected: np.ndarray, scenario: ScenarioParams,
                          policy: str, cfg: Config) -> pd.DataFrame:
    """Customer-level score table (contract ``customer_targeting_table``).
    ``scored`` must already contain eim/expected_cost from :func:`score_frame` (model_p basis)."""
    f = scored.reset_index(drop=True)
    rank = pd.Series(pd.NA, index=f.index, dtype="Int64")
    if selected.any():
        idx = np.where(selected)[0]
        order = np.lexsort((f.loc[idx, "customer_id"].astype(str).to_numpy(), -f.loc[idx, "eim"].to_numpy()))
        rank.iloc[idx[order]] = np.arange(1, len(idx) + 1)
    out = pd.DataFrame({
        "customer_id": f["customer_id"].astype("string"),
        "decision_date": f["decision_date"].astype("datetime64[ns]"),
        "scenario": pd.Series(scenario.name, index=f.index, dtype="string"),
        "scenario_version": pd.Series(scenario.version, index=f.index, dtype="string"),
        "policy": pd.Series(policy, index=f.index, dtype="string"),
        "customer_segment": f["customer_segment"].astype("string"),
        "recency_days": f["recency_days"].astype(float),
        "frequency_orders": f["frequency_orders"].astype("int64"),
        "monetary_net": f["monetary_net"].astype(float),
        "rfm_score": f["rfm_score"].astype("int64"),
        "repeat_purchase_probability": f["p"].astype(float),
        "customer_value_proxy": f["value"].astype(float),
        "value_is_fallback": f["value_is_fallback"].astype(bool),
        "discount_rate": scenario.discount_rate,
        "incremental_lift_assumption": f["delta"].astype(float),
        "gross_margin": scenario.gross_margin,
        "contact_cost": scenario.contact_cost,
        "expected_promotion_cost": f["expected_cost"].astype(float),
        "simulated_expected_incremental_margin": f["eim"].astype(float),
        "target_rank": rank,
        "recommended_action": pd.Series(np.where(selected, "TARGET", "DO_NOT_TARGET"), index=f.index, dtype="string"),
        "model_version": pd.Series(cfg.raw["versions"]["model_version"], index=f.index, dtype="string"),
    })
    return out
