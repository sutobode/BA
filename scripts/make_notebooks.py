"""Generate the 9 analysis notebooks (CODE SPEC §2). Notebooks only call retail_targeting.* and read
pipeline outputs — no logic lives here. Execute with:

    docker compose --profile dev run --rm notebook python scripts/make_notebooks.py --execute
"""

from __future__ import annotations

import argparse
import pathlib

import nbformat as nbf

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"

SETUP = """import os, pathlib
os.chdir(pathlib.Path.cwd().parent if pathlib.Path.cwd().name == "notebooks" else pathlib.Path.cwd())
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from IPython.display import Image, display
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
from retail_targeting.config import load_config
cfg = load_config()
T = lambda name: pd.read_csv(f"outputs/tables/{name}")"""

BANNER = ("> All promotion results are **scenario-based simulations under stated assumptions**. Online Retail II has "
          "no promotion treatment/control, so nothing here is a causal uplift, ROI or observed revenue lift.")

NOTEBOOKS = {
    "01_data_understanding": [
        ("md", "# 01 · Data understanding\nSource: UCI Online Retail II (CC BY 4.0, DOI 10.24432/C5CG6D). "
               "See `docs/source_log.md` and `docs/data_profile_topic1.md`."),
        ("code", SETUP),
        ("code", "from retail_targeting.io import read_parquet\nfrom retail_targeting.data.quality import profile_raw\n"
                 "raw = read_parquet('data/interim/transactions_raw.parquet')\nprof = profile_raw(raw)\n"
                 "{k: v for k, v in prof.items() if k != 'invoices_per_month'}"),
        ("code", "s = pd.Series(prof['invoices_per_month']); ax = s.plot(figsize=(10,3), title='Invoices per month')\n"
                 "ax.set_ylabel('invoices'); plt.show()"),
        ("md", "**Takeaways:** two sheets overlap on 2010-12-01…09 (removed by CR-00); 22.8% of lines have no Customer ID "
               "(15.2% of positive revenue); strong November peaks (Q4 seasonality)."),
    ],
    "02_cleaning_and_snapshots": [
        ("md", "# 02 · Cleaning and customer snapshots\nRules CR-00…CR-12 (SPEC §4); snapshot design SPEC §5."),
        ("code", SETUP),
        ("code", "pd.read_csv('outputs/reports/cleaning_log.csv')"),
        ("code", "pd.read_csv('outputs/reports/reconciliation.csv')"),
        ("code", "T('snapshot_summary.csv')"),
        ("md", "Each row of `customer_snapshots` is (customer, T0) with features from [T0−180d, T0) and the target from "
               "[T0, T0+90d). Purged T0s separate train / validation / test by ≥ 90 days."),
    ],
    "03_rfm_cohort_segmentation": [
        ("md", "# 03 · RFM, cohorts and segmentation\nRFM quintile cutoffs are fitted on train snapshots only."),
        ("code", SETUP),
        ("code", "import json; json.load(open('outputs/models/rfm_cutoffs.json'))"),
        ("code", "seg = T('rfm_segments.csv'); seg"),
        ("code", "seg.pivot(index='customer_segment', columns='split', values='repeat_rate').plot.bar(figsize=(8,3), "
                 "title='90-day repeat rate by segment'); plt.show()"),
        ("code", "display(Image('outputs/figures/cohort_retention.png'))"),
    ],
    "04_target_and_temporal_split": [
        ("md", "# 04 · Target and temporal split\nWhy not random split: the same customer appears at many T0s; a random "
               "split would train on the future (SPEC §6)."),
        ("code", SETUP),
        ("code", "from retail_targeting.config import split_dates\nsplit_dates(cfg)"),
        ("code", "s = T('snapshot_summary.csv'); s.pivot_table(index='decision_date', columns='split', values='prevalence')"),
        ("md", "Prevalence varies 0.38–0.62 with season: T0s whose outcome window covers Q4 have higher repeat rates. "
               "Test (T0 = Aug/Sep 2011) has prevalence 0.58 vs ~0.50 in train."),
    ],
    "05_logistic_baseline": [
        ("md", "# 05 · RFM benchmark and Logistic Regression baseline"),
        ("code", SETUP),
        ("code", "T('model_tuning.csv')[['C','class_weight','pr_auc','roc_auc','brier']]"),
        ("code", "T('model_coefficients.csv')"),
        ("md", "Interpretation: more active months, longer tenure and more orders raise the odds of a repeat purchase; "
               "longer recency lowers them (H1, H2 — associations, not causes)."),
    ],
    "06_evaluation_and_diagnostics": [
        ("md", "# 06 · Evaluation and diagnostics\nValidation is used for model selection and calibration; the test set "
               "was evaluated once (see `outputs/reports/test_access_log.jsonl`)."),
        ("code", SETUP),
        ("code", "T('model_metrics.csv')[['model','split','prevalence','pr_auc','roc_auc','brier','precision_at_0.1','lift_at_0.1']]"),
        ("code", "T('model_metrics_test.csv')[['model','prevalence','pr_auc','roc_auc','brier','mean_predicted','precision_at_0.1','lift_at_0.1']]"),
        ("code", "T('calibration_in_the_large_test.csv')"),
        ("code", "display(Image('outputs/figures/reliability_validation.png')); display(Image('outputs/figures/reliability_test.png'))"),
        ("code", "T('metrics_by_group_test.csv')[['group','group_value','n','prevalence','pr_auc','roc_auc']]"),
        ("md", "**Findings:** LR beats the RFM benchmark on PR-AUC on validation and test. Sigmoid calibration fitted on "
               "validation (prevalence 0.46) over-predicts on test (prevalence 0.58 → mean p 0.70): a seasonal shift, "
               "reported in the model card. The model is weak inside the Low-value active segment (ROC ≈ 0.50)."),
    ],
    "07_promotion_simulation": [
        ("md", "# 07 · Promotion simulation\n" + BANNER + "\n\nEIM = δ·V·m − (p+δ)·V·d − c (SPEC §9)."),
        ("code", SETUP),
        ("code", "from retail_targeting.decision.simulation import scenarios_from_config\n"
                 "pd.DataFrame([s.__dict__ for s in scenarios_from_config(cfg)])"),
        ("code", "T('break_even.csv')"),
        ("code", "tt = T('customer_targeting_table.csv'); tt.groupby(['scenario','recommended_action']).size().unstack(fill_value=0)"),
        ("md", "Under the three planning scenarios the break-even probability p* is 0.10–0.15, far below observed repeat "
               "rates, so the model + value rule recommends **no offer** for every eligible customer."),
    ],
    "08_policy_comparison": [
        ("md", "# 08 · Policy comparison (same customers, same capacity)\n" + BANNER),
        ("code", SETUP),
        ("code", "c = T('policy_comparison.csv'); c = c[(c.value_basis=='actual_outcome') & (c.capacity_fraction==0.1)]\n"
                 "c.pivot_table(index=['scenario','lift_structure'], columns='policy', values='simulated_eim').round(0)"),
        ("code", "c.pivot_table(index=['scenario','lift_structure'], columns='policy', values='target_count')"),
        ("md", "A = no offer, B = random, C = RFM top-K, D = model + value (EIM), E = lowest probability. "
               "Blanket (B) and RFM (C) campaigns lose simulated margin in every planning scenario because most "
               "targeted customers would have bought anyway."),
    ],
    "09_sensitivity_analysis": [
        ("md", "# 09 · Sensitivity analysis\n" + BANNER),
        ("code", SETUP),
        ("code", "T('sensitivity_dominance.csv')"),
        ("code", "display(Image('outputs/figures/sensitivity_heatmap.png'))"),
        ("code", "r = T('sensitivity_results.csv'); d = r[r.valid & (r.policy=='D') & r.value_cap & (r.capacity_fractions==0.1) "
                 "& (r.gross_margin==0.4) & (r.contact_cost==0.1)]\n"
                 "d.pivot_table(index=['lift_structure','incremental_lift'], columns='discount_rate', values='target_count')"),
        ("code", "T('sensitivity_calibration_shift.csv').query('capacity_fraction==0.1')[['p_shift','lift_structure','policy','target_count','simulated_eim']]"),
        ("md", "Targeting becomes profitable only when the assumed lift is large relative to the discount "
               "(e.g. δ ≥ 10 pp with d = 5%). The rule never loses more than random or RFM targeting in any grid point."),
    ],
}


def build(execute: bool) -> None:
    NB.mkdir(exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        nb = nbf.v4.new_notebook()
        nb.cells = [nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src) for kind, src in cells]
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        path = NB / f"{name}.ipynb"
        if execute:
            from nbconvert.preprocessors import ExecutePreprocessor
            ExecutePreprocessor(timeout=600, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(ROOT)}})
        nbf.write(nb, path)
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    build(ap.parse_args().execute)
