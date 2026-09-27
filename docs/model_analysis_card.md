# Model & Analysis Card — Topic 1: Repeat-purchase model and promotion-targeting rule

| | |
|---|---|
| Version | model `v0` (config `versions.model_version`), features `v1`, scenarios `v1` |
| Date | 2026-09-27 |
| Owner | M2 (model), M3 (decision rule) |
| Evidence | `outputs/tables/*.csv`, `outputs/figures/*.png`, `outputs/reports/run_manifest.json`, `outputs/reports/test_access_log.jsonl` |

> Promotion results are **scenario-based simulations under stated assumptions**. The dataset has no promotion treatment/control, so no figure here is a causal uplift, ROI or observed revenue lift.

## 1. Purpose and decision

- **Decision supported:** at each monthly decision date T0, which customers should receive a promotion under a fixed capacity K (5/10/20% of eligible customers), so that simulated expected incremental margin is maximised without over-discounting.
- **Intended user:** CRM/marketing manager of an online retailer.
- **Not intended for:** estimating the causal effect of promotions; individual-level credit/pricing decisions; production use without an A/B test.

## 2. Data, unit and population

| Item | Value |
|---|---|
| Source | UCI Online Retail II (CC BY 4.0, DOI 10.24432/C5CG6D), 01/12/2009–09/12/2011 |
| Raw → clean | 1,067,371 rows → 1,044,848 after sheet-overlap removal → 1,033,036 after exact duplicates |
| Unit | Customer snapshot `(customer_id, T0)`, T0 = first day of each month |
| Population | Customers with a Customer ID and ≥ 1 valid purchase in `[T0 − 180d, T0)` |
| Coverage | 22.76% of lines (15.15% of positive revenue) have no Customer ID and are excluded from customer-level analysis |
| Snapshots | 16 T0 (2010-06-01 … 2011-09-01), 47,933 rows |

## 3. Target and features

- **Target:** `repeat_purchase_90d` = 1 if the customer places ≥ 1 valid purchase order in `[T0, T0 + 90d)`.
- **Features** (only data before T0): recency, frequency (distinct orders), net monetary value, AOV, return rate, tenure, active months, average inter-purchase days, unique products, total units, orders in the last 30 days, month-of-T0 (sin/cos).
- **Not used as features:** country (ethics, §8), description, anything from the outcome window.

## 4. Validation design

| Split | T0 | Rows | Prevalence |
|---|---|---|---|
| Train | 2010-06 … 2011-01 (8) | 23,987 | 0.498 |
| (purged) | 2011-02, 2011-03 | — | — |
| Validation | 2011-04, 2011-05 | 6,346 | 0.458 |
| (purged) | 2011-06, 2011-07 | — | — |
| Test | 2011-08, 2011-09 | 5,534 | 0.582 |

The split is chronological with ≥ 90-day purge at each boundary. Preprocessing, RFM cutoffs, value fallback and value cap are fitted on train only. Hyperparameters and sigmoid calibration are fitted on validation. **The test set was evaluated once**; accesses are logged in `test_access_log.jsonl`. Leakage tests: `tests/test_leakage.py`.

## 5. Model

- **Benchmark:** RFM score (R + F + M quintiles).
- **Baseline:** Logistic Regression (L2, C selected by validation PR-AUC), signed-log1p + median impute + standardise; no class re-weighting (prevalence 0.38–0.62). Sigmoid calibration on validation.
- **Main associations** (standardised coefficients, `model_coefficients.csv`): active months (odds ×1.80 per SD), tenure (×1.18), frequency (×1.16), recency (×0.87). These are associations, not causes.

## 6. Metrics

| Split | Model | PR-AUC | ROC-AUC | Brier | Precision@10% | Lift@10% |
|---|---|---|---|---|---|---|
| Validation | RFM benchmark | 0.718 | 0.744 | — | — | — |
| Validation | Logistic Regression | **0.745** | 0.745 | 0.204 | — | — |
| Validation | LR without seasonality (D22 ablation) | 0.743 | 0.743 | 0.201 | — | — |
| Test | RFM benchmark | 0.786 | 0.725 | — | 0.902 | 1.55 |
| Test | Logistic Regression (raw) | **0.816** | **0.744** | **0.201** | 0.951 | 1.63 |
| Test | Logistic Regression (calibrated) | 0.816 | 0.744 | 0.216 | 0.951 | 1.63 |

Prevalence is the PR-AUC of a random ranking: 0.458 on validation and 0.582 on test.

**Calibration.** Calibration-in-the-large on test (prevalence − mean calibrated p) is −0.142 (T0 2011-08) and −0.093 (T0 2011-09). The calibrator was fitted on validation (spring T0s, prevalence 0.46) and **over-predicts** on autumn T0s. The raw model is closer (mean p 0.62 vs prevalence 0.58). Following the one-shot test rule, the model was **not** re-fitted; the effect on decisions is covered by the calibration-shift sensitivity, where shifting p by ±0.12 leaves the decision unchanged (`sensitivity_calibration_shift.csv`).

**By segment (test, ROC-AUC):** High-value active 0.77 · Developing 0.67 · High-value at risk 0.67 · Dormant 0.63 · Low-value active **0.50** (no ranking power inside this segment).

## 7. Decision rule, assumptions and business metric

- **Rule (policy D):** target customer *i* if `EIM_i = δ_i·V_i·m − (p_i + δ_i)·V_i·d − c > 0`, ranked by EIM, up to K. Net-returners (`monetary_net ≤ 0`) are never targeted (D29).
- **Assumptions (team, benchmark-based — decision log §2b):** gross margin m = 40%; discount d = 5 / 10 / 20%; incremental lift δ = 2 / 5 / 10 percentage points; contact cost c = £0.10; V = customer AOV capped at the train 99th percentile (£1,951).
- **Baselines:** A no offer · B random (100 seeds) · C RFM top-K · E lowest-p top-K; all use the same customers and K.
- **Business metric:** simulated expected incremental margin evaluated with the realised outcome (`value_basis = actual_outcome`).

**Result (test, K = 10%, constant lift):**

| Scenario | B random | C RFM | D model + value | E lowest-p |
|---|---|---|---|---|
| Conservative (5%, 2 pp) | −£5,685 | −£14,023 | £0 (targets 0) | −£734 |
| Base (10%, 5 pp) | −£11,245 (5–95%: −12,394 … −10,348) | −£27,968 | £0 (targets 0) | −£1,362 |
| Aggressive (20%, 10 pp) | −£23,146 | −£56,118 | £0 (targets 0) | −£3,173 |
| Illustrative (5%, 10 pp) | −£3,691 | −£13,361 | **+£276** (551 targets) | +£681 |

**Sensitivity** (1,080 grid points per lift structure, test): D ≥ B and D ≥ C in 100% of points; D > E in 84% (constant lift) and 88% (persuadable lift) of points; D targets nobody in 67% / 73% of points. See the break-even heatmap in `outputs/figures/sensitivity_heatmap.png`.

## 8. Ethics, bias and fairness

- **Population bias:** 22.8% of transaction lines (guest or unidentified buyers) are excluded; conclusions apply only to identified customers.
- **Geography:** about 92% of lines are from the UK; results may not transfer to other countries. Country is deliberately not a feature, to avoid geography-based differential treatment.
- **Wholesale mix:** many customers are wholesalers. Value is capped at p99 so that a few large accounts do not dominate targeting (top 1% share after the cap: 5.4%).
- **Exclusion from offers:** the rule withholds discounts from customers likely to buy anyway. That is a commercial choice, but it means loyal customers receive fewer offers; teams should monitor customer-experience effects.
- **No sensitive attributes** (age, gender, ethnicity) exist in or are inferred from the data. No personal data beyond pseudonymous IDs is used.

## 9. Risks and limitations

1. **Promotion effect is not observed.** δ is an assumption, and every business figure depends on it. The only valid way to measure δ is a randomised holdout test.
2. **Seasonality:** repeat rates vary 0.38–0.62 by month, and the calibration fitted on spring over-predicts in autumn.
3. **Cancellations and returns** cannot be separated in the data; both are treated as adjustments.
4. **Value proxy:** one order of AOV per 90 days is a conservative simplification; wholesaler behaviour is lumpy.
5. **Observational, historical data (2009–2011)** from a single retailer; external validity is limited.
6. **Low-value active segment:** the model has no discriminative power there (ROC ≈ 0.50).
7. **Decisions D29/D30 were added after viewing the test set** (a guardrail and a presentation scenario, not model changes). Results before D29 are kept in `outputs/tables/pre_D29/`.
