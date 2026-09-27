# Implementation Plan — Topic 1 (6 tuần, Step by Step)

**Project:** Customer Value & Promotion Targeting for an Online Retailer  
**Spec tham chiếu:** `project_specification_topic1.md` (gọi tắt **SPEC**)  
**Decision log:** `decision_log_topic1.md` (mã `Dxx`)  
**Code spec:** `code_specification_topic1.md` — mapping task → module ở §10; con số acceptance trên data thật ở §3.1  
**Owners:** M1 = Data & Customer Analytics · M2 = Predictive Modeling & Validation · M3 = Decision Analytics & Dashboard · ALL = cả nhóm

> Official duration là **6 tuần** (capstone tr.1–2). Plan 4 tuần trong BA (1).pdf được giữ dưới dạng *internal acceleration*: mục tiêu **baseline-complete cuối Week 3**, Weeks 4–6 dành cho decision analytics, robustness, communication và QA — khớp Suggested 6-Week Work Plan của capstone.

---

## 1. Tổng quan milestone

### Trạng thái (cập nhật 2026-09-27 — project hoàn thành)

| Phạm vi | Trạng thái | Evidence |
|---|---|---|
| T1.1–T1.6, T2.1–T2.8 (data, snapshots, split, skeletons) | ✅ Done | Số liệu khớp Code Spec §3.1; `tests/test_ingest|cleaning|snapshots|leakage|split|rfm.py` |
| T3.1–T3.5 (baseline model, RFM, cohort) | ✅ Done | `model_metrics.csv`, `rfm_segments.csv`, `cohort_summary.csv` |
| T4.1–T4.6 (calibration, policy A–E, targeting table) | ✅ Done | `calibration_results.csv`, `policy_comparison.csv`, `customer_targeting_table.csv` |
| T5.1–T5.6 (sensitivity, test once, dashboard, card, brief) | ✅ Done | `sensitivity_*.csv`, `test_access_log.jsonl`, `dashboard/app.py`, `model_analysis_card.md`, `executive_brief.pdf` |
| T6.1–T6.6 (README, clean rerun, tests, claim audit, checklist) | ✅ Done | Docker clean rerun; 79 tests pass; `traceability_matrix_topic1.md` |
| T6.7 Presentation/demo | ⬜ Team (dùng dashboard + brief) | — |

Thay đổi từ review v1 (`review_v1_topic1.md`): T4.4 phải chạy thêm **Policy E** và báo cáo `p*`; T5.1 phải chạy sensitivity theo **lift structure** (`constant` + `persuadable`), value cap và dịch calibration; T4.1 phải báo cáo calibration-in-the-large theo snapshot test (D25–D27).

| Tuần | Trọng tâm | Checkpoint (gate) | Map capstone |
|---|---|---|---|
| 1 | Framing + data readiness | **G1** Problem statement + data readiness review | Week 1 CAP |
| 2 | Canonical data + snapshots + validation plan | **G2** Frozen data/target/split contract | Week 2 CAP (một phần) |
| 3 | Baseline analytics | **G3 Baseline complete** (DoD 1–13) | Week 2–3 CAP |
| 4 | Evaluation + decision logic | **G4** Actionable decision logic | Week 3–4 CAP |
| 5 | Robustness + dashboard + brief draft | **G5** Draft dashboard + recommendations | Week 5 CAP |
| 6 | Integration + final QA | **G6** Final submission package | Week 6 CAP |

**Gate rule:** không bắt đầu stretch (S1–S4) nếu G3 chưa pass. Nếu G3 trễ, Week 4 dùng để hoàn thành baseline trước.

**Nhịp làm việc:** stand-up 15 phút 3 lần/tuần; review gate cuối mỗi tuần (60 phút); mọi thay đổi contract → cập nhật decision log + bump version.

---

## 2. Ownership (RACI)

A = Accountable · R = Responsible · C = Consulted

| Nội dung | M1 | M2 | M3 |
|---|---|---|---|
| Business framing & decision | C | C | **A/R** |
| Source log, license, acquisition | **A/R** | C | C |
| Cleaning rules, data dictionary | **A/R** | C | C |
| Snapshots & feature contract | **A/R** | C | C |
| Target & observation/outcome window | C | **A/R** | C |
| Temporal split & purge | C | **A/R** | C |
| Leakage review | R | **A/R** | C |
| RFM/cohort/segmentation | **A/R** | C | C |
| Model, metrics, calibration, model card | C | **A/R** | C |
| Value proxy & promotion assumptions | C | C | **A/R** |
| Simulation, policy comparison, sensitivity | C | C | **A/R** |
| KPI & guardrails | C | C | **A/R** |
| Dashboard | C | C | **A/R** |
| Executive brief | R | R | **A/R** |
| README & reproducibility | R | **A/R** | R |
| Final QA & claim audit | R | R | R (ALL A) |
| Presentation/demo | R | R | R |

---

## 3. Artifact handoff

| Producer | Artifact | Consumer | Sẵn sàng (prototype → frozen) |
|---|---|---|---|
| M1 | `raw_profile`, schema | ALL | W1 D3 → W1 D5 |
| M1 | `transactions_clean` | M1, M2 | W2 D2 → W2 D5 |
| M1 | `customer_snapshots` | M2, M3 | W2 D4 (prototype) → W3 D3 (frozen v1) |
| M2 | `customer_predictions` | M3 | W3 D4 (val) → W5 D3 (test, final) |
| M3 | `scenario_results`, `policy_comparison`, `sensitivity_results` | Dashboard, brief | W4 → W5 |
| M3 | `customer_targeting_table` | Dashboard, brief | W4 D5 → W5 D4 |

M2 và M3 bắt đầu ngay khi có **prototype** (dữ liệu mẫu đúng schema), không chờ bản frozen.

---

## 4. Task list chi tiết

Định dạng mỗi task: **ID · Objective · Owner · Input · Action · Output · Acceptance · Depends · Risk · Validation**. DoR = Definition of Ready (input có sẵn); DoD task = acceptance đạt + artifact commit + decision log cập nhật nếu có quyết định.

### WEEK 1 — Framing + data readiness

**T1.1 — Repo & environment setup**
- Owner: M2 · Input: SPEC §12 · Depends: —
- Action: tạo cấu trúc repo; `requirements.txt` pinned; `.gitignore` (data/raw); copy `project_config.example.yaml` → `project_config.yaml`; khung `tests/`.
- Output: repo skeleton, `requirements.txt`.
- Acceptance: `pip install -r requirements.txt` thành công trên máy cả 3 người; `pytest` chạy (0 test fail).
- Risk: lệch version → pin exact.
- Validation: log lệnh install + `pytest -q` output.

**T1.2 — Source acquisition & source log**
- Owner: M1 · Input: CAP tr.3, tr.11; <https://archive.ics.uci.edu/dataset/502/online+retail+ii>; SPEC §3.1 (metadata + checksum đã verify 2026-09-27) · Depends: T1.1
- Action: tải lại từ link trên, so SHA-256 với SPEC §3.1; ghi ngày tải chính thức; viết script tải lại.
- Output: `docs/source_log.md`, `retail_targeting.data.ingest.download_raw`, raw file (local).
- Acceptance: mọi field §3.1 SPEC có giá trị (không TBD); script tải lại cho cùng checksum.
- Risk: source không khả dụng → ghi blocker, dùng mirror chính thức nếu có và ghi chú.
- Validation: chạy script lần 2, so checksum.
- Decision: D02, D03.

**T1.3 — Initial profiling**
- Owner: M1 · Input: raw file · Depends: T1.2
- Action: chạy checklist SPEC §3.4 (rows, dates, customers, invoices, missing ID, duplicates, invalid qty/price/date, cancel/return prevalence, volume theo tháng, overlap giữa sheets).
- Output: `notebooks/01_data_understanding`, `outputs/data_quality_report.md` v0.
- Acceptance: mọi check có value + status; schema thực tế được ghi vào data dictionary (raw fields).
- Validation: notebook chạy lại từ đầu không lỗi; số liệu khớp giữa notebook và report.

**T1.4 — Business framing freeze**
- Owner: M3 (A), ALL · Input: SPEC §1 · Depends: —
- Action: review decision, options, criteria, KPIs, guardrails, allowed claims; chọn decision maker; thống nhất 5 KPIs.
- Output: SPEC §1 status = Frozen v1; ghi D01, D15.
- Acceptance: cả 3 người đồng ý (ghi trong decision log).
- Validation: checklist SPEC §15 mục 1 tick.

**T1.5 — Target/window/validation design proposal**
- Owner: M2 · Input: T1.3 volume theo tháng · Depends: T1.3
- Action: tính valid T0 range với 180/90 ngày; đếm số snapshot; ước prevalence sơ bộ; kiểm tra seasonality (Q4); đề xuất split & purge.
- Output: memo 1 trang trong decision log (D05–D07 status Proposed).
- Acceptance: có số snapshot cụ thể, đề xuất ngày split, lý do chọn/đổi window dựa trên data.
- Risk: quá ít snapshot → đổi cadence/window, ghi lý do.

**T1.6 — Scenario parameter draft**
- Owner: M3 · Input: SPEC §9 · Depends: —
- Action: đề xuất khoảng giá trị `m, d, δ, c, K` cho 3 scenarios, kèm lý do/nguồn; skeleton hàm `compute_eim()` + unit test công thức.
- Output: `src/retail_targeting/decision/simulation.py` skeleton, `tests/test_simulation.py`, D09–D11 Proposed.
- Acceptance: test `EIM == M1 − M0`, `δ_i ≤ 1 − p_i`, EIM = −c khi δ=0 & d=0 pass.

**Gate G1 (cuối W1):** source log hoàn chỉnh; profiling report v0; framing frozen; proposal window/split; parameter draft. Evidence: files + decision log.

### WEEK 2 — Canonical data, snapshots, validation plan

**T2.1 — Cleaning rules CR-01…CR-12**
- Owner: M1 · Input: T1.3 · Depends: T1.3
- Action: kiểm chứng từng rule trên data thật; quyết định non-product codes (D04); implement `src/retail_targeting/data/clean.py`.
- Output: `transactions_clean`, bảng reconciliation (rows/customers/revenue trước–sau mỗi rule).
- Acceptance: mỗi rule có count trước/sau; không có row nào bị loại mà không có rule; tổng net revenue reconcile.
- Validation: `tests/test_cleaning.py` (không quantity=0, không price≤0 trong purchase events, không missing customer_id trong customer-level, không duplicate exact).

**T2.2 — Data dictionary v1**
- Owner: M1 · Depends: T2.1
- Action: điền template SPEC §3.3 cho raw + derived fields.
- Output: `docs/data_dictionary.md`.
- Acceptance: 100% field dùng downstream có entry; leakage_risk ghi cho mọi field.

**T2.3 — Customer ID coverage report**
- Owner: M1 · Depends: T2.1
- Action: % dòng/% revenue thiếu ID, theo tháng và country; mô tả bias tiềm năng.
- Output: section trong `data_quality_report.md`; input cho model card (ethics/bias).
- Acceptance: có bảng + 3–5 câu diễn giải.

**T2.4 — Snapshot builder prototype**
- Owner: M1 · Input: SPEC §5 · Depends: T2.1, T1.5
- Action: implement thuật toán SPEC §5 cho RFM + AOV + target; xuất prototype 2–3 snapshot.
- Output: `src/retail_targeting/features/snapshots.py`, `customer_snapshots` prototype.
- Acceptance: đúng schema Code Spec §5.3; assertion `max(hist.ts) < T0` trong code.
- Validation: `tests/test_contracts.py` (schema/dtype/key unique).

**T2.5 — Freeze target, windows, split, purge**
- Owner: M2 (A) · Depends: T1.5, T2.4
- Action: chốt D05–D07 với data thật; ghi exact T0 lists vào `project_config.yaml`.
- Output: config + decision log Frozen.
- Acceptance: split chronological, purge ≥ 90d, test snapshots chưa được dùng.

**T2.6 — Leakage test suite**
- Owner: M2 · Depends: T2.4, T2.5
- Action: implement 6 check SPEC §6 trong `tests/test_leakage.py`.
- Output: test file.
- Acceptance: test pass trên prototype; cố ý chèn 1 transaction post-T0 → test phải fail (negative test).

**T2.7 — Benchmark & modeling skeleton**
- Owner: M2 · Depends: T2.4
- Action: pipeline sklearn + RFM benchmark trên prototype; hàm `evaluate()` trả PR-AUC, ROC-AUC, Brier, top-K.
- Output: `src/retail_targeting/models/train.py`, `src/retail_targeting/models/evaluate.py`.
- Acceptance: chạy end-to-end trên prototype.

**T2.8 — Value proxy & simulator skeleton**
- Owner: M3 · Depends: T2.4, T1.6
- Action: `V_i = aov`, fallback median theo segment fit trên train; policy A–D function dùng `p_i` giả (ví dụ từ RFM benchmark) để test luồng.
- Output: `src/retail_targeting/decision/policy.py`.
- Acceptance: policy không vượt K, không chọn EIM ≤ 0 (D), B tái lập với seed.

**Gate G2:** data dictionary v1; cleaning + tests pass; snapshot prototype; config có split frozen; leakage tests pass (kể cả negative test); skeleton M2/M3 chạy được.

### WEEK 3 — Baseline complete

**T3.1 — Full snapshots + features v1 (frozen)**
- Owner: M1 · Depends: G2
- Action: sinh toàn bộ snapshots; thêm optional features đã duyệt; `feature_version = v1`.
- Output: `customer_snapshots` v1.
- Acceptance: contract + leakage tests pass; bảng eligible count & prevalence theo snapshot.

**T3.2 — RFM scoring & segmentation**
- Owner: M1 · Depends: T3.1
- Action: quintile cutoffs fit trên train, lưu config; gán 5 segments; kiểm tra stability.
- Output: `notebooks/03_rfm_cohort_segmentation`, `rfm_segments.csv`, D12 Frozen.
- Acceptance: 4–6 segments, mỗi segment có interpretation + action gợi ý; cutoffs không đổi giữa splits.

**T3.3 — Cohort analysis**
- Owner: M1 · Depends: T2.1
- Action: cohort theo first valid purchase month; retention heatmap; ghi left-censoring.
- Output: `cohort_summary.csv`, figure.
- Acceptance: heatmap + 3 insight có số liệu.

**T3.4 — Logistic Regression baseline**
- Owner: M2 · Depends: T3.1
- Action: train trên train split; tune `C`, `class_weight` trên validation; so với RFM benchmark.
- Output: `notebooks/05_logistic_baseline`, `model_v1.joblib`, `model_metadata.json`, `model_metrics.csv` (validation).
- Acceptance: PR-AUC, ROC-AUC, Brier, top-K cho LR và benchmark trên validation; prevalence ghi kèm.
- Validation: rerun cùng seed → metric giống hệt.

**T3.5 — Preliminary simulation với p thật**
- Owner: M3 · Depends: T3.4, T2.8
- Action: chạy Base scenario trên validation; policy A–D.
- Output: `scenario_results` v0.
- Acceptance: bảng A–D cùng K; sanity: A = 0; D ≥ 0.

**Gate G3 — Baseline complete:** DoD SPEC §15 mục 1–13 tick với evidence. Nếu fail → không làm stretch; W4 ưu tiên sửa.

### WEEK 4 — Evaluation + decision analytics

**T4.1 — Calibration**
- Owner: M2 · Depends: T3.4
- Action: reliability plot + Brier; nếu lệch → calibrate (sigmoid/isotonic) trên validation; D08.
- Output: `calibration_results`, figure.
- Acceptance: có before/after; quyết định ghi log. (p_i dùng trong EIM phải là calibrated.)

**T4.2 — Threshold/capacity & error analysis**
- Owner: M2 · Depends: T4.1
- Action: precision/recall tại K ∈ {5,10,20}%; metrics theo segment, cohort, snapshot.
- Output: `notebooks/06_evaluation_and_diagnostics`.
- Acceptance: bảng theo 3 chiều; nêu ≥ 2 điểm yếu của model.

**T4.3 — Freeze scenarios**
- Owner: M3 (A), ALL · Depends: T1.6
- Action: chốt giá trị `m, d, δ, c, K/B` cho Conservative/Base/Aggressive; ghi lý do.
- Output: `project_config.yaml` section scenarios, `scenario_version = v1`, D09–D11 Frozen.
- Acceptance: không còn TBD; mỗi giá trị có rationale.

**T4.4 — Policy comparison (validation)**
- Owner: M3 · Depends: T4.1, T4.3
- Action: A–E × 3 scenarios × K grid; B với 100 seeds.
- Output: `policy_comparison.csv`, `notebooks/08_policy_comparison`.
- Acceptance: cùng population/K; B có mean, P5, P95; discount leakage share cho C và D.

**T4.5 — Customer targeting table v0**
- Owner: M3 · Depends: T4.4
- Output: `customer_targeting_table` v0 đúng schema.
- Acceptance: `test_contracts.py` pass; số TARGET ≤ K.

**T4.6 — Model/business consistency review**
- Owner: ALL · Depends: T4.2, T4.4
- Action: review H1–H4 với evidence; check logic segment ↔ EIM (ví dụ high-value active có EIM thấp do leakage discount?).
- Output: ghi chú trong decision log.

**Gate G4:** calibration xong; ≥ 3 scenarios frozen; policy comparison cùng capacity; targeting table v0.

### WEEK 5 — Robustness + dashboard + brief draft

**T5.1 — Sensitivity grid**
- Owner: M3 · Depends: G4
- Action: grid `d × δ × K` (+ m, c nếu kịp); break-even vùng D ≤ B.
- Output: `sensitivity_results.csv`, heatmaps, `notebooks/09_sensitivity_analysis`.
- Acceptance: ≥ 3 giá trị mỗi trục; kết luận robustness bằng lời.

**T5.2 — Final test evaluation (one-shot)**
- Owner: M2 · Depends: G4 (mọi lựa chọn đã frozen)
- Action: chạy model + calibration + policies trên test snapshots **một lần**; ghi timestamp.
- Output: `model_metrics.csv` (test), `customer_predictions` final, `scenario_results` test.
- Acceptance: không thay đổi model/threshold/scenario sau bước này (nếu buộc phải đổi → ghi D-log và report cả hai).

**T5.3 — Dashboard build**
- Owner: M3 · Depends: T5.2 (dùng data validation trước, swap sang test)
- Action: 3 views SPEC §11; 5 KPIs; banner non-causal; controls scenario/K/B.
- Output: `dashboard/`.
- Acceptance: KPIs khớp `scenario_results` (sai số 0); đổi K làm thay đổi target count đúng.

**T5.4 — Model/analysis card**
- Owner: M2 · Depends: T5.2, T2.3
- Output: `docs/model_analysis_card.md` theo SPEC §13 (có ethics/bias).
- Acceptance: đủ mọi mục template.

**T5.5 — Executive brief draft**
- Owner: M3 (A), M1, M2 · Depends: T5.1, T5.2
- Output: `docs/executive_brief.md` → PDF.
- Acceptance: ≤ 2 trang; trả lời 6 câu SPEC §11; có range qua scenarios.

**T5.6 — Source log & data dictionary final**
- Owner: M1 · Output: bản final. Acceptance: khớp code hiện tại.

**Gate G5:** dashboard draft chạy; brief draft; model card; sensitivity; test metrics.

### WEEK 6 — Integration + final QA

**T6.1 — README & run instructions** — Owner M2 · Acceptance: một người ngoài làm theo được; có thứ tự chạy notebook/script, thời gian ước tính, cách tải data.

**T6.2 — Clean-environment rerun** — Owner M1 (người không viết pipeline chính chạy thử) · Action: venv mới → install → download → pipeline → so bảng chính · Acceptance: metrics và `scenario_results` giống bản đã report (seed cố định) · Evidence: rerun log.

**T6.3 — Full test suite** — Owner M2 · `pytest` toàn bộ pass (cleaning, leakage, simulation, contracts).

**T6.4 — Claim audit** — Owner ALL · Action: grep brief/dashboard/notebook markdown cho "ROI", "uplift", "caused", "lift vs control", "increase revenue"; sửa hoặc đặt trong ngữ cảnh phủ định · Acceptance: 0 unsupported claim.

**T6.5 — Output consistency** — Owner M3 · Số liệu trong brief = dashboard = CSV outputs.

**T6.6 — Final checklist** — Owner ALL · Tick SPEC §15 (23 mục) + CAP Final Submission Checklist (10 mục) trong `traceability_matrix_topic1.md` với link evidence.

**T6.7 — Presentation/demo** — Owner ALL · Slide + demo dashboard; mỗi người trình bày workstream của mình.

**Gate G6:** mọi mục DoD tick; package nộp: code/notebooks + README, data dictionary + source log, executive brief ≤ 2 trang, dashboard, model/analysis card, customer-level score table.

---

## 4b. Task register (bảng đầy đủ — nguồn chuẩn cho giao việc)

Bảng này bổ sung đủ các trường cho mọi task ở mục 4. Nếu có khác biệt, bảng này được ưu tiên.

| ID | Owner | Input | Action | Output | Acceptance | Depends | Risk | Validation |
|---|---|---|---|---|---|---|---|---|
| T1.1 | M2 | SPEC §12 | Tạo repo, env pinned, gitignore, config, tests skeleton | Repo skeleton, `requirements.txt` | Install OK trên 3 máy; pytest chạy | — | Lệch version | Log install + `pytest -q` |
| T1.2 | M1 | CAP tr.3, 11; https://archive.ics.uci.edu/dataset/502/online+retail+ii | Tải lại, so SHA-256 với SPEC §3.1, ghi ngày tải chính thức, script tải lại | `source_log.md`, `download.py`, raw | Không còn TBD trong source log | T1.1 | Source down | Chạy lại script, so SHA-256 |
| T1.3 | M1 | Raw file | Profiling theo SPEC §3.4 | Notebook 01, DQ report v0 | Mọi check có value/status | T1.2 | Schema khác dự kiến | Rerun notebook sạch; số khớp report |
| T1.4 | M3 | SPEC §1 | Review & freeze framing, KPIs, claims | SPEC §1 Frozen, D15 | 3/3 đồng ý | — | Scope trôi | DoD mục 1 tick |
| T1.5 | M2 | T1.3 volume/tháng | Tính T0 range, số snapshot, prevalence sơ bộ, seasonality | Memo D05–D07 Proposed | Có số snapshot + ngày split đề xuất | T1.3 | Ít snapshot | Peer review M1 kiểm lại phép tính ngày |
| T1.6 | M3 | SPEC §9 | Draft tham số; skeleton `compute_eim` | `simulation.py`, `test_simulation.py` | 3 unit test công thức pass | T1.1 | Tham số vô căn cứ | `pytest tests/test_simulation.py` |
| T2.1 | M1 | T1.3, SPEC §4 | Kiểm chứng + implement CR-01…12 | `transactions_clean`, reconciliation | Mỗi rule có count trước/sau; revenue reconcile | T1.3 | Cancel/return mơ hồ (D19) | `test_cleaning.py` |
| T2.2 | M1 | T2.1, SPEC §3.3 | Điền data dictionary raw + derived | `data_dictionary.md` v1 | 100% field downstream có entry | T2.1 | Thiếu field | Script so danh sách cột thực tế vs dictionary |
| T2.3 | M1 | T2.1 | Report missing ID theo tháng/country | Section DQ report | Bảng + diễn giải bias | T2.1 | Bias population | M2 review số liệu |
| T2.4 | M1 | T2.1, T1.5, SPEC §5 | Snapshot builder prototype | `snapshots.py`, prototype | Đúng schema; assertion `< T0` | T2.1, T1.5 | Logic window sai | `test_contracts.py` |
| T2.5 | M2 | T1.5, T2.4 | Freeze cadence/window/split/purge | `project_config.yaml`, D05–D07 | Chronological, purge ≥ 90d | T2.4 | Chọn split theo metric | Script kiểm tra ngày split + purge |
| T2.6 | M2 | T2.4, T2.5, SPEC §6 | Implement 6 leakage checks | `test_leakage.py` | Pass + negative test fail đúng | T2.5 | Test không đủ nhạy | Negative test (chèn post-T0 txn) |
| T2.7 | M2 | T2.4 | Pipeline + benchmark + evaluate() | `train.py`, `evaluate.py` | E2E trên prototype | T2.4 | — | Unit test evaluate trên dữ liệu đồ chơi có đáp án |
| T2.8 | M3 | T2.4, T1.6 | Value proxy + policy A–D skeleton | `policy.py` | ≤ K; D không chọn EIM ≤ 0; B tái lập | T1.6, T2.4 | Fallback leakage | `test_simulation.py` mở rộng |
| T3.1 | M1 | G2 | Full snapshots + features v1 | `customer_snapshots` v1 | Contract + leakage pass; bảng prevalence | G2 | Thời gian chạy lâu | `pytest` contracts + leakage |
| T3.2 | M1 | T3.1 | RFM cutoffs (train), 5 segments, stability | `rfm_segments.csv`, D12 | 4–6 segment có interpretation | T3.1 | Segment lệch cỡ | Kiểm tra cutoffs chỉ từ train snapshots |
| T3.3 | M1 | T2.1 | Cohort retention | `cohort_summary.csv`, heatmap | 3 insight có số | T2.1 | Left-censoring | M3 review diễn giải |
| T3.4 | M2 | T3.1 | Train LR, tune trên validation, so benchmark | `model_v1`, metadata, metrics | Đủ metrics cho LR + benchmark | T3.1 | LR ≤ benchmark | Rerun cùng seed → metric giống |
| T3.5 | M3 | T3.4, T2.8 | Base scenario trên validation | `scenario_results` v0 | A = 0; cùng K | T3.4 | — | Sanity assertions trong notebook |
| T4.1 | M2 | T3.4 | Reliability + calibration | `calibration_results` | Before/after + D08 | T3.4 | Overfit calibration | Brier validation before/after |
| T4.2 | M2 | T4.1 | Top-K + error analysis 3 chiều | Notebook 06 | ≥ 2 điểm yếu nêu rõ | T4.1 | — | M1 review theo segment |
| T4.3 | M3 | T1.6, T4.2 | Freeze 3 scenarios | Config scenarios v1 | Không TBD; có rationale | T1.6 | Tranh cãi tham số | ALL sign-off trong D-log |
| T4.4 | M3 | T4.1, T4.3 | A–E × scenarios × K; B 100 seeds; 2 value_basis; báo cáo p* | `policy_comparison.csv` | Cùng population/K; P5–P95 cho B; D vs E báo cáo rõ | T4.3 | So sánh không công bằng | Assert cùng K, cùng population id set |
| T4.5 | M3 | T4.4 | Xuất targeting table | `customer_targeting_table` v0 | Schema đúng; TARGET ≤ K | T4.4 | — | `test_contracts.py` |
| T4.6 | ALL | T4.2, T4.4 | Review H1–H4, logic segment ↔ EIM | Ghi chú D-log | Mỗi H có kết luận + evidence | T4.2, T4.4 | Kết luận quá tay | Claim review theo SPEC §1.10 |
| T5.1 | M3 | G4 | Sensitivity grid × lift structure (constant, persuadable) + value cap on/off + calibration shift; break-even | `sensitivity_results.csv`, heatmaps | ≥ 3 giá trị/trục; kết luận robustness chỉ khi đúng cho cả 2 lift structure | G4 | Grid quá lớn | Số dòng output = tích số giá trị grid |
| T5.2 | M2 | G4 (frozen) | Final test một lần | Test metrics, predictions, scenario test | Không đổi lựa chọn sau đó | G4 | Nhìn test sớm | Log timestamp lần đọc test |
| T5.3 | M3 | T5.2 | Build 3 views, 5 KPIs, banner | `dashboard/` | KPI khớp CSV; đổi K đúng | T5.2 | Tốn thời gian | So KPI dashboard vs `scenario_results` |
| T5.4 | M2 | T5.2, T2.3 | Viết model/analysis card | `model_analysis_card.md` | Đủ mục SPEC §13 | T5.2 | Thiếu ethics/bias | Checklist template |
| T5.5 | M3 | T5.1, T5.2 | Viết executive brief | `executive_brief.pdf` | ≤ 2 trang; 6 câu SPEC §11 | T5.1 | Quá dài/kỹ thuật | Page count; M1 đọc thử như manager |
| T5.6 | M1 | Code hiện tại | Cập nhật source log/dictionary final | Bản final | Khớp code | T3.1 | Lệch code | Script so cột |
| T6.1 | M2 | Toàn bộ pipeline | Viết README, thứ tự chạy | `README.md` | Người ngoài làm theo được | G5 | Thiếu bước | T6.2 |
| T6.2 | M1 | README | Rerun từ venv mới | Rerun log | Bảng/metrics trùng khớp | T6.1 | Phụ thuộc máy | Diff CSV outputs |
| T6.3 | M2 | Tests | Chạy toàn bộ test suite | Test report | 100% pass | T6.2 | Test flaky | `pytest` output lưu file |
| T6.4 | ALL | Brief, dashboard, notebooks | Grep & sửa causal/ROI claims | Claim audit log | 0 unsupported claim | T5.5 | Sót chữ | Grep keyword list SPEC §14 |
| T6.5 | M3 | Brief, dashboard, CSV | So số liệu 3 nguồn | Consistency log | Trùng khớp 100% | T6.2 | Số cũ trong brief | Script/bảng đối chiếu |
| T6.6 | ALL | SPEC §15, traceability matrix | Tick DoD 23 mục + checklist 10 mục kèm evidence | Matrix cập nhật Done | Không mục nào thiếu evidence | T6.3–T6.5 | Tick không evidence | Peer review chéo |
| T6.7 | ALL | Mọi deliverable | Slides + demo | Slide deck, demo | Demo chạy trực tiếp; mỗi người trình bày | T6.6 | Demo lỗi | Dry-run trước 1 ngày |

---

## 5. Stretch backlog (chỉ sau G3, theo thứ tự ưu tiên)

| ID | Việc | Owner | Điều kiện |
|---|---|---|---|
| S3 | Profit curve theo nhiều K / budget | M3 | G4 pass |
| S1 | Gradient boosting + calibration + SHAP, so công bằng với LR | M2 | G3 pass, T4.2 xong |
| S4 | Recommendation layer retain / nurture / no-offer | M3 | S3 hoặc G4 |
| S2 | Future-spend regression (MAE/RMSE holdout) | M2 | Còn ≥ 1 tuần |

---

## 6. Risk register theo thời gian

| Risk | Tuần phát hiện | Trigger | Phản ứng |
|---|---|---|---|
| Không phân biệt được cancellation/return | W1–W2 | CR-01/02 không kiểm chứng được | Gộp "negative adjustments", ghi limitation |
| Quá ít snapshot | W1 | < 8 T0 hợp lệ | Giảm observation window hoặc horizon (D06) |
| M1 trễ | W2 | Snapshot prototype chưa có W2 D4 | M2/M3 dùng sample data đúng schema; M2 hỗ trợ M1 |
| Model kém hơn benchmark | W3 | PR-AUC LR ≤ RFM | Report trung thực; dùng p calibrated từ mô hình tốt hơn trên validation |
| Parameter tranh cãi | W4 | Không đồng thuận scenario | Dùng sensitivity rộng; Base = trung vị |
| Dashboard tốn thời gian | W5 | Chưa có view 3 cuối W5 D3 | Cắt tính năng, giữ 5 KPIs + table |

---

## 7. Validation của chính plan này

- Mỗi task ở mục 4 có owner, input/depends, action, output, acceptance và validation.
- Mọi deliverable CAP (R03–R07, R22) có task tạo ra: README (T6.1), data dictionary/source log (T1.2, T2.2, T5.6), brief (T5.5), dashboard (T5.3), model card (T5.4), score table (T4.5/T5.2).
- Chi tiết mapping: `traceability_matrix_topic1.md`.
