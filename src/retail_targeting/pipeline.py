"""Stage orchestration (CODE SPEC §6.16). Each stage reads inputs from disk, writes outputs,
validates contracts and records a manifest."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Callable

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from retail_targeting.config import Config, config_hash, resolve_path, split_dates  # noqa: E402
from retail_targeting.contracts import validate_frame  # noqa: E402
from retail_targeting.io import read_csv_artifact, read_parquet, write_csv, write_manifest, write_parquet  # noqa: E402

log = logging.getLogger(__name__)


def _p(cfg: Config, key: str, name: str) -> Path:
    return resolve_path(cfg, key) / name


# ---------------------------------------------------------------- data stages

def stage_ingest(cfg: Config) -> None:
    """download_raw → load_raw → data/interim/transactions_raw.parquet."""
    from retail_targeting.data.ingest import download_raw, load_raw

    download_raw(cfg)
    raw = load_raw(cfg)
    out = write_parquet(raw, _p(cfg, "interim_dir", "transactions_raw.parquet"), schema="transactions_raw")
    write_manifest(cfg, "ingest", [out])


def stage_clean(cfg: Config) -> None:
    """clean_transactions → lines.parquet, cleaning_log.csv; build_orders → orders.parquet;
    quality report + reconcile (INV-03)."""
    from retail_targeting.data.clean import build_orders, clean_transactions
    from retail_targeting.data.quality import customer_coverage, profile_raw, reconcile, write_quality_report

    raw = read_parquet(_p(cfg, "interim_dir", "transactions_raw.parquet"))
    lines, cleaning_log = clean_transactions(raw, cfg)
    orders = build_orders(lines)
    rec = reconcile(raw, lines, orders)
    if (rec["status"] != "PASS").any():
        raise AssertionError(f"INV-03 reconciliation failed:\n{rec}")
    outs = [write_parquet(lines, _p(cfg, "interim_dir", "lines.parquet"), schema="lines"),
            write_parquet(orders, _p(cfg, "interim_dir", "orders.parquet"), schema="orders")]
    report = _p(cfg, "reports_dir", "data_quality_report.md")
    write_quality_report(profile_raw(raw), customer_coverage(lines), cleaning_log, report, rec)
    rec.to_csv(_p(cfg, "reports_dir", "reconciliation.csv"), index=False)
    write_manifest(cfg, "clean", outs + [report])


def stage_snapshots(cfg: Config) -> None:
    """build_all_snapshots → assign_split → fit_rfm_cutoffs(train) → apply scores/segments
    → data/processed/customer_snapshots.parquet; cohort_summary.csv."""
    from retail_targeting.features.cohort import cohort_retention
    from retail_targeting.features.rfm import apply_rfm_scores, assign_segments, fit_rfm_cutoffs
    from retail_targeting.features.snapshots import build_all_snapshots
    from retail_targeting.models.split import assign_split, check_split_config

    check_split_config(cfg)
    lines = read_parquet(_p(cfg, "interim_dir", "lines.parquet"))
    orders = read_parquet(_p(cfg, "interim_dir", "orders.parquet"))
    snaps = build_all_snapshots(orders, lines, cfg)
    snaps["split"] = assign_split(snaps, cfg)
    seg_cfg = cfg.raw["segmentation"]
    cutoffs = fit_rfm_cutoffs(snaps[snaps["split"] == "train"], seg_cfg["n_bins"])
    snaps = apply_rfm_scores(snaps, cutoffs, seg_cfg["n_bins"])
    snaps["customer_segment"] = assign_segments(snaps, seg_cfg["rules"])
    cut_path = _p(cfg, "models_dir", "rfm_cutoffs.json")
    cut_path.parent.mkdir(parents=True, exist_ok=True)
    cut_path.write_text(json.dumps({"fit_on": "split == train", "cutoffs": cutoffs}, indent=1), encoding="utf-8")
    out = write_parquet(snaps, _p(cfg, "processed_dir", "customer_snapshots.parquet"), schema="customer_snapshots")

    target = cfg.raw["temporal"]["target_name"]
    by_t0 = (snaps.groupby(["decision_date", "split"], observed=True)
             .agg(eligible=("customer_id", "size"), prevalence=(target, "mean"),
                  median_aov=("aov", "median")).reset_index())
    t1 = write_csv(by_t0, _p(cfg, "tables_dir", "snapshot_summary.csv"))
    seg = (snaps[snaps["split"] != "purged"].groupby(["split", "customer_segment"], observed=True)
           .agg(customers=("customer_id", "size"), repeat_rate=(target, "mean"),
                median_monetary=("monetary_net", "median"), median_aov=("aov", "median"),
                median_recency=("recency_days", "median")).reset_index())
    t2 = write_csv(seg, _p(cfg, "tables_dir", "rfm_segments.csv"))
    cohort = cohort_retention(orders)
    t3 = write_csv(cohort, _p(cfg, "tables_dir", "cohort_summary.csv"))
    _plot_cohort(cohort, _p(cfg, "figures_dir", "cohort_retention.png"))
    write_manifest(cfg, "snapshots", [out, t1, t2, t3, cut_path])


# ---------------------------------------------------------------- model stages

def _load_snaps(cfg: Config) -> pd.DataFrame:
    return read_parquet(_p(cfg, "processed_dir", "customer_snapshots.parquet"))


def _predict_frame(snaps: pd.DataFrame, model, raw_model, cfg: Config) -> pd.DataFrame:
    from retail_targeting.models.train import feature_matrix, rfm_benchmark_score

    target = cfg.raw["temporal"]["target_name"]
    X = feature_matrix(snaps, cfg)
    return pd.DataFrame({
        "customer_id": snaps["customer_id"].astype("string"),
        "decision_date": snaps["decision_date"].astype("datetime64[ns]"),
        "split": snaps["split"].astype("string"),
        "actual_repeat_purchase": snaps[target].astype("int8"),
        "rfm_benchmark_score": rfm_benchmark_score(snaps).astype(float).to_numpy(),
        "predicted_repeat_probability_raw": raw_model.predict_proba(X)[:, 1],
        "predicted_repeat_probability": model.predict_proba(X)[:, 1],
        "model_version": pd.Series(cfg.raw["versions"]["model_version"], index=snaps.index, dtype="string"),
        "feature_version": snaps["feature_version"].astype("string"),
    })


def stage_train(cfg: Config) -> None:
    """tune_logreg on train/validation → calibrate → save_model; model_metrics (validation)."""
    from retail_targeting.models.calibrate import calibrate
    from retail_targeting.models.evaluate import classification_metrics, reliability_table
    from retail_targeting.models.train import coefficients, feature_names, save_model, tune_logreg

    snaps = _load_snaps(cfg)
    train, val = snaps[snaps["split"] == "train"], snaps[snaps["split"] == "validation"]
    target = cfg.raw["temporal"]["target_name"]
    fracs = cfg.raw["model"]["top_k_fractions"]
    best, grid = tune_logreg(train, val, cfg)
    write_csv(grid, _p(cfg, "tables_dir", "model_tuning.csv"))
    cal = calibrate(best, val, cfg)

    # D22 ablation: seasonality features
    import copy
    from retail_targeting.config import Config as _C
    raw2 = copy.deepcopy(cfg.raw)
    raw2["model"]["numeric_features"] = [f for f in raw2["model"]["numeric_features"] if not f.startswith("t0_month")]
    raw2["model"]["log1p_features"] = [f for f in raw2["model"]["log1p_features"] if not f.startswith("t0_month")]
    cfg2 = _C(raw=raw2, root=cfg.root)
    best2, _ = tune_logreg(train, val, cfg2)

    from retail_targeting.models.train import feature_matrix, rfm_benchmark_score
    yv = val[target].to_numpy()
    ids = val["customer_id"].to_numpy()
    rows = [
        {"model": "rfm_benchmark", "split": "validation",
         **classification_metrics(yv, rfm_benchmark_score(val).to_numpy(), fracs, ids)},
        {"model": "logreg_raw", "split": "validation",
         **classification_metrics(yv, best.predict_proba(feature_matrix(val, cfg))[:, 1], fracs, ids)},
        {"model": "logreg_calibrated", "split": "validation (in-sample for calibration)",
         **classification_metrics(yv, cal.predict_proba(feature_matrix(val, cfg))[:, 1], fracs, ids)},
        {"model": "logreg_raw_no_seasonality (D22 ablation)", "split": "validation",
         **classification_metrics(yv, best2.predict_proba(feature_matrix(val, cfg2))[:, 1], fracs, ids)},
        {"model": "logreg_raw", "split": "train",
         **classification_metrics(train[target].to_numpy(), best.predict_proba(feature_matrix(train, cfg))[:, 1],
                                  fracs, train["customer_id"].to_numpy())},
    ]
    metrics = pd.DataFrame(rows)
    t_metrics = write_csv(metrics, _p(cfg, "tables_dir", "model_metrics.csv"))
    coef = coefficients(best)
    t_coef = write_csv(coef, _p(cfg, "tables_dir", "model_coefficients.csv"))
    rel = pd.concat([reliability_table(yv, best.predict_proba(feature_matrix(val, cfg))[:, 1]).assign(model="raw"),
                     reliability_table(yv, cal.predict_proba(feature_matrix(val, cfg))[:, 1]).assign(model="calibrated")])
    t_rel = write_csv(rel, _p(cfg, "tables_dir", "calibration_results.csv"))
    _plot_reliability(rel, _p(cfg, "figures_dir", "reliability_validation.png"), "Validation reliability")
    meta = {"target": target, "features": feature_names(cfg), "C": float(best.named_steps["lr"].C),
            "class_weight": best.named_steps["lr"].class_weight, "calibration": cfg.raw["model"]["calibration"],
            "train_dates": [str(d) for d in split_dates(cfg)["train"]],
            "validation_dates": [str(d) for d in split_dates(cfg)["validation"]],
            "config_hash": config_hash(cfg), "validation_metrics": rows[1], "n_train": len(train), "n_val": len(val)}
    model_path = save_model({"calibrated": cal, "raw": best}, meta, cfg)
    write_manifest(cfg, "train", [t_metrics, t_coef, t_rel, model_path])


def _load_model(cfg: Config):
    obj = joblib.load(_p(cfg, "models_dir", f"model_{cfg.raw['versions']['model_version']}.joblib"))
    return obj["calibrated"], obj["raw"]


def stage_evaluate(cfg: Config, *, include_test: bool = False) -> None:
    """customer_predictions.csv; metrics by group; test only if include_test (log_test_access)."""
    from retail_targeting.models.evaluate import (
        classification_metrics, log_test_access, metrics_by_group, reliability_table,
    )

    snaps = _load_snaps(cfg)
    splits = ["train", "validation"] + (["test"] if include_test else [])
    if include_test:
        log_test_access(cfg, "stage_evaluate: predictions + metrics on test snapshots")
    snaps = snaps[snaps["split"].isin(splits)].reset_index(drop=True)
    model, raw_model = _load_model(cfg)
    pred = validate_frame(_predict_frame(snaps, model, raw_model, cfg), "customer_predictions")
    outs = [write_csv(pred, _p(cfg, "tables_dir", "customer_predictions.csv"), schema="customer_predictions")]
    merged = pred.merge(snaps[["customer_id", "decision_date", "customer_segment", "cohort_month"]],
                        on=["customer_id", "decision_date"])
    eval_split = "test" if include_test else "validation"
    ev = merged[merged["split"] == eval_split]
    by = []
    for col in ("customer_segment", "decision_date"):
        by.append(metrics_by_group(ev, "predicted_repeat_probability", col, cfg).assign(split=eval_split, group=col)
                  .rename(columns={col: "group_value"}))
    ev2 = ev.assign(cohort_year=ev["cohort_month"].str[:4])
    by.append(metrics_by_group(ev2, "predicted_repeat_probability", "cohort_year", cfg)
              .assign(split=eval_split, group="cohort_year").rename(columns={"cohort_year": "group_value"}))
    byg = pd.concat(by, ignore_index=True)
    byg["group_value"] = byg["group_value"].astype(str)
    outs.append(write_csv(byg, _p(cfg, "tables_dir", f"metrics_by_group_{eval_split}.csv")))
    if include_test:
        fracs = cfg.raw["model"]["top_k_fractions"]
        rows = []
        for name, col in (("rfm_benchmark", "rfm_benchmark_score"), ("logreg_raw", "predicted_repeat_probability_raw"),
                          ("logreg_calibrated", "predicted_repeat_probability")):
            rows.append({"model": name, "split": "test",
                         **classification_metrics(ev["actual_repeat_purchase"].to_numpy(), ev[col].to_numpy(), fracs,
                                                  ev["customer_id"].to_numpy())})
        outs.append(write_csv(pd.DataFrame(rows), _p(cfg, "tables_dir", "model_metrics_test.csv")))
        cil = (ev.groupby("decision_date").agg(n=("customer_id", "size"),
                                                prevalence=("actual_repeat_purchase", "mean"),
                                                mean_p_calibrated=("predicted_repeat_probability", "mean"),
                                                mean_p_raw=("predicted_repeat_probability_raw", "mean")).reset_index())
        cil["calibration_in_the_large"] = cil["prevalence"] - cil["mean_p_calibrated"]
        outs.append(write_csv(cil, _p(cfg, "tables_dir", "calibration_in_the_large_test.csv")))
        rel = reliability_table(ev["actual_repeat_purchase"].to_numpy(), ev["predicted_repeat_probability"].to_numpy())
        _plot_reliability(rel.assign(model="calibrated"), _p(cfg, "figures_dir", "reliability_test.png"), "Test reliability")
    write_manifest(cfg, "evaluate_test" if include_test else "evaluate", outs)


# ---------------------------------------------------------------- decision stages

def _scored_frame(cfg: Config, split: str) -> pd.DataFrame:
    from retail_targeting.decision.simulation import fit_value_cap, fit_value_fallback, value_proxy

    snaps = _load_snaps(cfg)
    pred = read_csv_artifact(_p(cfg, "tables_dir", "customer_predictions.csv"))
    if split not in set(pred["split"]):
        raise RuntimeError(f"no predictions for split {split!r}; run evaluate first"
                           + (" with --include-test" if split == "test" else ""))
    train = snaps[snaps["split"] == "train"]
    fallback = fit_value_fallback(train)
    cap = fit_value_cap(train, cfg.raw["simulation"].get("value_cap_quantile"))
    s = snaps[snaps["split"] == split].merge(
        pred[["customer_id", "decision_date", "predicted_repeat_probability"]], on=["customer_id", "decision_date"])
    if cfg.raw["simulation"].get("exclude_net_negative", False):
        # D29 guardrail: customers whose returns/cancellations exceed purchases are never promotion targets
        n0 = len(s)
        s = s[s["monetary_net"] > 0].reset_index(drop=True)
        log.info("D29: excluded %d net-negative customer-snapshots from the targeting population", n0 - len(s))
    value, is_fb = value_proxy(s, fallback, cap)
    uncapped, _ = value_proxy(s, fallback, None)
    target = cfg.raw["temporal"]["target_name"]
    s = s.assign(p=s["predicted_repeat_probability"].clip(0, 1), y=s[target].astype(float),
                 value=value.to_numpy(), value_uncapped=uncapped.to_numpy(), value_is_fallback=is_fb.to_numpy())
    s.attrs["value_cap"] = cap
    return s


def _decision_split(cfg: Config) -> str:
    pred = read_csv_artifact(_p(cfg, "tables_dir", "customer_predictions.csv"))
    return "test" if "test" in set(pred["split"]) else "validation"


def stage_simulate(cfg: Config) -> None:
    """scenarios_from_config (require values) → run_policies for both value bases →
    scenario_results.csv, policy_comparison.csv, customer_targeting_table.csv."""
    from retail_targeting.decision.policy import (
        build_targeting_table, capacity_from_fraction, run_policies, score_frame, select_policy_d, summarize,
    )
    from retail_targeting.decision.simulation import break_even_p, scenarios_from_config

    split = _decision_split(cfg)
    if split == "test":
        from retail_targeting.models.evaluate import log_test_access
        log_test_access(cfg, "stage_simulate: policies on test snapshots")
    scored = _scored_frame(cfg, split)
    scenarios = scenarios_from_config(cfg)
    sim = cfg.raw["simulation"]
    results = []
    for basis in sim["value_bases"]:
        for ls in ("constant", "persuadable"):
            results.append(run_policies(scored, scenarios, cfg, value_basis=basis, lift_structure=ls))
    res = pd.concat(results, ignore_index=True)
    outs = [write_csv(res, _p(cfg, "tables_dir", "scenario_results.csv"), schema="scenario_results")]
    comp = summarize(res).assign(evaluation_split=split)
    outs.append(write_csv(comp, _p(cfg, "tables_dir", "policy_comparison.csv")))

    # customer-level score table: primary lift structure, policy D, capacity 10% (and all scenarios)
    tables = []
    primary = sim.get("lift_structure", "constant")
    frac = 0.10 if 0.10 in sim["capacity_fractions"] else sim["capacity_fractions"][0]
    for sc in scenarios:
        for t0, g in scored.groupby("decision_date", sort=True):
            g = g.sort_values("customer_id", kind="mergesort").reset_index(drop=True)
            f = score_frame(g, sc, primary, sim.get("segment_lift_multipliers"), "model_p")
            sel = select_policy_d(f, capacity_from_fraction(len(f), frac), sim.get("budget"))
            tables.append(build_targeting_table(f, sel, sc, "D", cfg))
    tt = validate_frame(pd.concat(tables, ignore_index=True), "customer_targeting_table")
    outs.append(write_csv(tt, _p(cfg, "tables_dir", "customer_targeting_table.csv"), schema="customer_targeting_table"))

    # break-even p* by scenario and value quantile (SPEC §9.4) + value concentration (R-02)
    qs = scored["value"].quantile([0.1, 0.5, 0.9]).to_dict()
    be = pd.DataFrame([{"scenario": sc.name, "value_quantile": q, "value": v,
                        "p_star": float(break_even_p([v], sc)[0])} for sc in scenarios for q, v in qs.items()])
    outs.append(write_csv(be, _p(cfg, "tables_dir", "break_even.csv")))
    tot = scored.groupby("customer_id")["value"].first().sort_values(ascending=False)
    conc = pd.DataFrame([{"evaluation_split": split, "value_cap": scored.attrs.get("value_cap"),
                          "top1pct_share_of_value_capped": float(tot.iloc[:max(1, len(tot) // 100)].sum() / tot.sum()),
                          "customers": len(tot)}])
    outs.append(write_csv(conc, _p(cfg, "tables_dir", "value_concentration.csv")))
    write_manifest(cfg, f"simulate_{split}", outs)


def stage_sensitivity(cfg: Config) -> None:
    """run_grid → sensitivity_results.csv; break_even; dominance summary; calibration-shift check."""
    from retail_targeting.decision.policy import run_policies, summarize
    from retail_targeting.decision.sensitivity import break_even, dominance_summary, run_grid
    from retail_targeting.decision.simulation import scenarios_from_config

    split = _decision_split(cfg)
    if split == "test":
        from retail_targeting.models.evaluate import log_test_access
        log_test_access(cfg, "stage_sensitivity: grid on test snapshots")
    scored = _scored_frame(cfg, split)
    base = next(s for s in scenarios_from_config(cfg) if s.name == "base")
    grid = {k: list(v) for k, v in cfg.raw["simulation"]["sensitivity_grid"].items()}
    res = run_grid(scored, base, grid, cfg, n_seeds=20).assign(evaluation_split=split)
    outs = [write_csv(res, _p(cfg, "tables_dir", "sensitivity_results.csv"))]
    outs.append(write_csv(break_even(res), _p(cfg, "tables_dir", "sensitivity_break_even.csv")))
    dom = dominance_summary(res).assign(evaluation_split=split)
    outs.append(write_csv(dom, _p(cfg, "tables_dir", "sensitivity_dominance.csv")))
    _plot_sensitivity(res, _p(cfg, "figures_dir", "sensitivity_heatmap.png"))

    # D25: calibration shift — move p by ± (prevalence − mean p)
    shift = float(scored["y"].mean() - scored["p"].mean())
    rows = []
    for delta_p in (-abs(shift), 0.0, abs(shift)):
        s2 = scored.assign(p=(scored["p"] + delta_p).clip(0, 1))
        r = run_policies(s2, [base], cfg, value_basis="actual_outcome", n_seeds=20)
        rows.append(summarize(r).assign(p_shift=delta_p))
    outs.append(write_csv(pd.concat(rows, ignore_index=True).assign(evaluation_split=split),
                          _p(cfg, "tables_dir", "sensitivity_calibration_shift.csv")))
    write_manifest(cfg, f"sensitivity_{split}", outs)


# ---------------------------------------------------------------- plots

def _save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def _plot_reliability(rel: pd.DataFrame, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="perfect")
    for name, g in rel.groupby("model"):
        ax.plot(g["mean_predicted"], g["observed_rate"], "o-", label=name)
    ax.set(xlabel="mean predicted probability", ylabel="observed repeat rate", title=title, xlim=(0, 1), ylim=(0, 1))
    ax.legend()
    _save(fig, path)


def _plot_cohort(cohort: pd.DataFrame, path: Path) -> None:
    piv = cohort.pivot(index="cohort_month", columns="age_month", values="retention_rate")
    fig, ax = plt.subplots(figsize=(10, 7))
    im = ax.imshow(piv.to_numpy(), aspect="auto", cmap="viridis", vmin=0, vmax=0.6)
    ax.set_yticks(range(len(piv.index)), piv.index, fontsize=7)
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set(xlabel="months since first purchase", ylabel="cohort (first purchase month)",
           title="Cohort retention (share of cohort purchasing)")
    fig.colorbar(im, ax=ax)
    _save(fig, path)


def _plot_sensitivity(res: pd.DataFrame, path: Path) -> None:
    v = res[res["valid"] & (res["policy"] == "D")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, ls in zip(axes, ("constant", "persuadable")):
        sub = v[(v["lift_structure"] == ls) & np.isclose(v["gross_margin"], 0.40) & np.isclose(v["contact_cost"], 0.10)
                & np.isclose(v["capacity_fractions"], 0.10) & (v["value_cap"].astype(bool))]
        piv = sub.pivot_table(index="incremental_lift", columns="discount_rate", values="simulated_eim")
        im = ax.imshow(piv.to_numpy(), cmap="RdYlGn", origin="lower", aspect="auto")
        ax.set_xticks(range(len(piv.columns)), [f"{c:.2f}" for c in piv.columns])
        ax.set_yticks(range(len(piv.index)), [f"{c:.2f}" for c in piv.index])
        for (i, j), val in np.ndenumerate(piv.to_numpy()):
            ax.text(j, i, f"{val:,.0f}", ha="center", va="center", fontsize=7)
        ax.set(xlabel="discount rate d", ylabel="assumed incremental lift δ",
               title=f"Policy D simulated EIM (£), lift={ls}\nm=0.40, c=£0.10, K=10%")
        fig.colorbar(im, ax=ax)
    _save(fig, path)


STAGES: dict[str, Callable[..., None]] = {
    "ingest": stage_ingest,
    "clean": stage_clean,
    "snapshots": stage_snapshots,
    "train": stage_train,
    "evaluate": stage_evaluate,
    "simulate": stage_simulate,
    "sensitivity": stage_sensitivity,
}
