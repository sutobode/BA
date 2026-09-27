# Traceability Matrix — Topic 1

Mapping: **Capstone requirement → Spec section → Implementation task → Artifact → Validation evidence**.  
CAP = `BA_Capstone_Topics_2026_MSc class (1).pdf`; SPEC = `project_specification_topic1.md`; tasks theo `implementation_plan_topic1.md`.  
Dataset (hyperlink trong CAP tr.3, tr.11): <https://archive.ics.uci.edu/dataset/502/online+retail+ii>.  
Cột **Status** cập nhật trong quá trình làm: `Planned` → `In progress` → `Done (link evidence)`.

## 1. Yêu cầu chung và Topic 1

| Req | Yêu cầu (CAP) | Trang | SPEC | Task | Artifact | Validation evidence | Status |
|---|---|---|---|---|---|---|---|
| R01 | Team 3–4, 6 tuần | 1 | Metadata, §0.3 | Plan §1 | Plan 6 tuần | Gate G1–G6 | Planned |
| R02 | Bắt đầu từ business decision; truy vết được | 2 | §1 | T1.4 | SPEC §1 frozen | D-log D15; brief nêu rule | Planned |
| R03 | Reproducible code + README | 2 | §12, §14 | T1.1, T6.1, T6.2 | `README.md`, `src/`, notebooks | Clean-env rerun log | Planned |
| R04 | Data dictionary + source log | 2 | §3 | T1.2, T2.2, T5.6 | `docs/data_dictionary.md`, `docs/source_log.md` | Không còn TBD; checksum khớp | In progress (source log xong; dictionary v0) |
| R05 | Executive brief ≤ 2 trang | 2 | §11 | T5.5 | `executive_brief.pdf` | Page count ≤ 2 | Planned |
| R06 | Dashboard 3–5 KPIs + actionable view | 2 | §1.8, §11 | T5.3 | `dashboard/` | KPI = `scenario_results`; screenshot | Planned |
| R07 | Model/analysis card (gồm ethics/bias) | 2 | §13 | T5.4 | `docs/model_analysis_card.md` | Đủ mục template | Planned |
| R08 | Unit, target, horizon, decision trước modeling | 2 | §5 | T2.5 | `project_config.yaml` | D05–D07 Frozen trước T3.4 | In progress (số liệu thật đã xác nhận; chờ freeze) |
| R09 | Temporal validation, không random split | 2 | §6 | T2.5, T2.6 | config split | `test_leakage.py` pass | Planned |
| R10 | Chỉ thông tin tại decision time; loại leakage | 2 | §5, §6 | T2.4, T2.6 | snapshot builder | Negative leakage test fail đúng | Planned |
| R11 | Baseline trước stretch | 2 | §2.2, §8 | T3.4, Gate G3 | `model_v1` | G3 checklist trước S1–S4 | Planned |
| R12 | Không causal/ROI claim; assumptions + sensitivity | 2 | §1.10, §9 | T5.1, T6.4 | `sensitivity_results.csv` | Claim audit 0 lỗi | Planned |
| R13 | Business impact qua rule/budget/capacity/scenario | 2 | §10 | T4.4 | `policy_comparison.csv` | Cùng K cho A–D | Planned |
| R14 | Clean txn, cancellations/returns, behavioral features | 3 | §4, §7.1 | T2.1, T3.1 | `transactions_clean`, `customer_snapshots` | `test_cleaning.py`, reconciliation | Planned |
| R15 | RFM/cohort + value segmentation | 3 | §7.2, §7.3 | T3.2, T3.3 | `rfm_segments.csv`, `cohort_summary.csv` | Cutoffs fit trên train | Planned |
| R16 | Predict repeat purchase trên holdout horizon | 3 | §5, §8 | T3.4, T5.2 | `customer_predictions` | Test metrics report 1 lần | Planned |
| R17 | Targeting rule + simulate margin (response, discount) | 3 | §9, §10 | T1.6, T4.3, T4.4 | `src/retail_targeting/decision/` | `test_simulation.py` | Planned |
| R18 | RFM + interpretable model baseline | 3 | §8 | T2.7, T3.4 | benchmark + LR | `model_metrics.csv` có cả 2 | Planned |
| R19 | Features chỉ từ observation window | 3 | §5, §6 | T2.4, T2.6 | snapshots | assertion + test | Planned |
| R20 | Scenario table ≥ 3 assumptions | 3 | §9.3 | T4.3 | config scenarios | 3 scenario không TBD | Planned |
| R21 | PR-AUC/ROC-AUC + calibration; EIM vs non-targeted | 3 | §8, §10 | T3.4, T4.1, T4.4 | metrics, calibration, comparison | Bảng D vs B (100 seeds) | Planned |
| R22 | Pipeline + customer-level score table; brief; dashboard | 3 | §11, §12.2 | T4.5, T5.2–T5.5 | `customer_targeting_table` | `test_contracts.py` | Planned |
| R23 | Không merge complaint datasets; effect là assumption | 3 | §2.5 | T1.2 | source log (joins = none) | Source log | Planned |
| R25 | Xác minh source, ghi download date | 11 | §3.1 | T1.2 | source log | URL từ hyperlink CAP tr.3/tr.11, license CC BY 4.0, SHA-256 | In progress (verified 2026-09-27; ghi lại ngày tải chính thức ở T1.2) |

Stretch (CAP tr.3) → SPEC §2.2 → Plan §5 (S1–S4), chỉ sau G3.

## 2. Final Submission Checklist (CAP tr.11)

| # | Checklist item | SPEC | Task | Evidence | Status |
|---|---|---|---|---|---|
| 1 | Business decision, unit, target, evaluation period defined | §1, §5, §6 | T1.4, T2.5 | SPEC + config | Planned |
| 2 | Source, download date, license/terms, filters/joins documented | §3, §4 | T1.2, T2.1, T5.6 | source log, data dictionary | Planned |
| 3 | No target leakage | §6 | T2.6 | `test_leakage.py` | Planned |
| 4 | Baseline complete, fair comparison with advanced model | §8 | T3.4, S1 | metrics cùng split | Planned |
| 5 | Validation matches temporal structure | §6 | T2.5 | config split + purge | Planned |
| 6 | Technical + business metric reported | §8, §10 | T4.1, T4.4 | metrics + policy comparison | Planned |
| 7 | Scenario assumptions visible + sensitivity | §9 | T4.3, T5.1 | config + sensitivity | Planned |
| 8 | Dashboard supports a concrete decision | §11 | T5.3 | Actionable view | Planned |
| 9 | Brief: recommendation, impact range, risks, limitations | §11 | T5.5 | brief | Planned |
| 10 | Third party can rerun from README | §14 | T6.1, T6.2 | rerun log | Planned |

## 3. Coverage check

- 24/24 yêu cầu R01–R25 (R24 = checklist ở mục 2) có SPEC section, task và evidence.
- 10/10 mục Final Submission Checklist có task và evidence.
- Mỗi deliverable bắt buộc có đúng một task tạo ra và một owner accountable (RACI trong plan §2).
