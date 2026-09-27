# GOAL PROMPT — Build hoàn chỉnh Topic 1 (vibe-coding end-to-end)

> **Cách dùng:** copy toàn bộ từ `BEGIN AGENT TASK` đến `END AGENT TASK`, dán cho AI coding agent có quyền đọc/ghi repo và chạy lệnh (Docker Desktop phải đang chạy). Nếu agent dừng giữa chừng, dán lại prompt: agent sẽ tự đọc §0 (trạng thái) và làm tiếp.

---

## BEGIN AGENT TASK

### 0. Vai trò, mục tiêu, cách tiếp tục

Bạn là **Lead Data Scientist + Python engineer**. Nhiệm vụ: implement **toàn bộ** project capstone *Topic 1 — Customer Value & Promotion Targeting for an Online Retailer* trong repo hiện tại. Kết quả cuối phải là một pipeline chạy được từ raw data đến dashboard, kèm đủ deliverables mà capstone yêu cầu. **Không thay đổi thiết kế.** Thiết kế đã được chốt trong tài liệu (28/28 quyết định ở trạng thái Decided).

**Bắt đầu mỗi phiên bằng việc xác định trạng thái** (không dựa vào trí nhớ):

```bash
git status && git log --oneline -5
docker compose run --rm test          # đếm passed / xfailed / failed
grep -rn "raise NotImplementedError" src/ | wc -l
```

Sau đó làm tiếp phase đầu tiên chưa đạt Definition of Done (§4).

### 1. Đọc trước khi code (bắt buộc, theo thứ tự)

1. `docs/onboarding_topic1.md`: bức tranh tổng thể, glossary, quy tắc bắt buộc, git workflow.
2. `docs/code_specification_topic1.md`: **nguồn chuẩn kỹ thuật** (tên hàm, signature, cột, kiểu, invariant, thứ tự code §10, **con số tham chiếu trên data thật §3.1**).
3. `docs/project_specification_topic1.md`: nghiệp vụ và phương pháp (§5 temporal, §8 model, §9 EIM, §9.4 p*, §10 policy A–E, §11 dashboard, §13 model card, §15 DoD).
4. `docs/decision_log_topic1.md`: quyết định D01–D28 và căn cứ tham số (§2b).
5. `docs/review_v1_topic1.md`: lý do có Policy E, lift structure, value cap, calibration protocol.
6. `docs/implementation_plan_topic1.md` §4b: task register (acceptance từng task).
7. `project_config.yaml`, `src/retail_targeting/**`, `tests/**`.

**Thứ bậc khi mâu thuẫn:** capstone PDF > SPEC (nghiệp vụ) > Code Spec (kỹ thuật) > các tài liệu khác. Nếu thấy mâu thuẫn hoặc spec thiếu: ghi một dòng mới vào `docs/decision_log_topic1.md` (status Decided, kèm lý do và evidence), chọn phương án bảo thủ nhất, rồi mới code.

### 2. Môi trường — dùng Docker

```bash
docker compose build                                         # sau khi đổi requirements*.txt
docker compose run --rm test                                 # toàn bộ test
docker compose run --rm test python -m pytest tests/test_cleaning.py -q   # một file
docker compose run --rm pipeline run <stage>                 # ingest|clean|snapshots|train|evaluate|simulate|sensitivity|all
docker compose run --rm pipeline run evaluate --include-test # chỉ ở Phase 7 (đánh giá test một lần)
docker compose up dashboard                                  # http://localhost:8501
docker compose --profile dev up notebook                     # JupyterLab (notebooks/)
```

- `src/`, `tests/`, `dashboard/`, config, `data/`, `outputs/` được bind-mount: sửa trên host là container thấy ngay, không cần rebuild.
- Chỉ rebuild khi đổi `requirements*.txt` hoặc `Dockerfile`. Thêm dependency thì pin version chính xác, và chỉ dùng package phổ biến.
- Raw data nằm ở `data/raw/online_retail_II.xlsx` (SHA-256 trong `project_config.yaml`). Nếu thiếu, tải bằng lệnh trong `README.md`, hoặc implement `download_raw` trước.
- Có thể dùng `.venv` local để chạy nhanh, nhưng **kết quả nghiệm thu phải chạy bằng Docker**.

### 3. Quy tắc code (vi phạm là fail)

1. **TDD theo test có sẵn.** Mỗi hàm stub có test gắn `@todo` (xfail strict). Implement xong thì test báo `XPASS(strict)` = fail. **Xoá `@todo`** của test đó rồi chạy lại cho pass. **Không sửa assertion/đáp án của test có sẵn**: chúng đã được kiểm chứng bằng reference implementation trên data thật. Nếu tin chắc một test sai, ghi decision log kèm chứng minh tính tay trước khi sửa.
2. Mỗi hàm mới/logic mới phải có test mới (fixture nhỏ, đáp án tính tay).
3. Logic nằm trong `src/retail_targeting/`; notebook và dashboard **chỉ gọi hàm và đọc output**.
4. Không hard-code hằng số nghiệp vụ; mọi thứ đọc từ `project_config.yaml`.
5. **Leakage:** feature chỉ dùng `ts < T0`; target chỉ dùng `[T0, T0+90d)`; mọi fit (scaler, imputer, RFM cutoffs, value fallback, value cap, calibration) chỉ dùng `split == "train"` (calibration dùng `validation`). Không đọc test split trước Phase 7; mọi lượt đọc test phải gọi `log_test_access`.
6. Mọi artifact ghi ra đĩa phải qua `validate_frame(df, <schema>)` (INV-xx trong Code Spec §7).
7. Deterministic: seed từ config; tie-break luôn kết thúc bằng `customer_id`; CSV sort theo key, `float_format="%.6f"`.
8. Ngôn ngữ output: **không** dùng "ROI", "causal", "uplift", "revenue lift", "caused/causes" trừ trong câu phủ định/disclaimer. Luôn dùng "simulated", "expected", "under stated assumptions".
9. Hiệu năng: vectorized pandas/numpy; không `iterrows`/`apply` theo dòng trên ~1M dòng. Nếu snapshot stage chạy > 3 phút thì tối ưu.
10. Git: branch `feat/<phase>-<ngắn>`, commit nhỏ `T<id>: <mô tả>`. Merge vào `master` sau khi phase đạt DoD. Không commit `data/`, `.venv/`, `*.joblib`. Không force-push, không rewrite history.

### 4. Phases (làm tuần tự; mỗi phase phải đạt DoD trước khi sang phase sau)

Mỗi phase ghi rõ: module (Code Spec §6.x), task plan, con số nghiệm thu. "Numbers" = so với Code Spec §3.1; phải **khớp chính xác**.

#### Phase 1 — Ingest & cleaning (M1 · T1.2, T2.1–T2.3 · Code Spec §6.3–6.5)

- `data/ingest.py`: `verify_checksum`, `download_raw`, `read_raw_excel`, `combine_sheets` (CR-00), `load_raw` (cache parquet có key theo sha256[:12]).
- `data/clean.py`: `standardize_columns`, `is_non_product`, `classify_lines` (đúng thứ tự rule §6.4), `clean_transactions` (+ `cleaning_log` đầy đủ các rule), `build_orders`.
- `data/quality.py`: `profile_raw`, `customer_coverage`, `reconcile`, `write_quality_report`.
- `io.py`: `read_parquet`, `write_parquet`, `write_csv`, `write_manifest`.
- `pipeline.stage_ingest`, `stage_clean`; CLI `check`.
- **DoD:**
  - `test_ingest.py`, `test_cleaning.py` pass (không còn `@todo`).
  - `run ingest && run clean` chạy được.
  - Numbers: 1,044,848 → 1,033,036 dòng; line types và exclude reasons khớp; reconcile diff = 0.0; orders purchase 36,594 / adjustment 7,283.
  - Có `outputs/reports/data_quality_report.md` và `cleaning_log.csv`.
  - `docs/data_dictionary.md` điền `missing_rate` thực tế.

#### Phase 2 — Snapshots, split, RFM, cohort (M1+M2 · T2.4–T2.6, T3.1–T3.3 · §6.6–6.9)

- `features/snapshots.py` (`generate_t0_dates`, `build_snapshot`, `build_all_snapshots`) — vectorized, có `LeakageError`.
- `models/split.py` (`check_split_config`, `assign_split`).
- `features/rfm.py` (cutoffs fit train, lưu `outputs/models/rfm_cutoffs.json`; scores; segments theo config).
- `features/cohort.py`.
- `pipeline.stage_snapshots` → `data/processed/customer_snapshots.parquet` (có `split`, RFM, segment), `outputs/tables/cohort_summary.csv`, `rfm_segments.csv`.
- **DoD:**
  - `test_snapshots.py`, `test_leakage.py`, `test_split.py`, `test_rfm.py` pass.
  - Numbers: 16 T0; 47,933 dòng; train 23,987 / validation 6,346 / test 5,534 / purged 12,066; prevalence theo T0 khớp `data_profile_topic1.md` §5; `aov ≤ 0` = 149; `monetary_net < 0` = 34.
  - Thêm test tích hợp: T0 bất kỳ trên data thật có `max(feature ts) < T0`.

#### Phase 3 — Baseline model (M2 · T2.7, T3.4, T4.1, T4.2 · §6.10–6.12)

- `models/evaluate.py` (metrics, top-K, reliability, by-group, `log_test_access`), `models/train.py` (feature_matrix, benchmark, pipeline signed-log1p → median impute → scaler → LR, `tune_logreg` theo PR-AUC validation), `models/calibrate.py` (sigmoid, `FrozenEstimator`).
- `stage_train`, `stage_evaluate` (không kèm test). Output: `outputs/tables/model_metrics.csv` (validation, LR và RFM benchmark), `calibration_results.csv`, `metrics_by_group.csv`, reliability plot trong `outputs/figures/`, `customer_predictions.csv` (train + validation), `outputs/models/model_v1.joblib` + metadata.
- Ablation D22: có và không có `t0_month_sin/cos`; ghi kết quả vào decision log.
- **DoD:**
  - `test_evaluate.py` pass; thêm test cho `build_pipeline` (fit chỉ trên train) và `feature_matrix` (INV-07).
  - LR và benchmark đều có PR-AUC, ROC-AUC, Brier, precision/recall/lift@5/10/20%, prevalence.
  - Rerun cùng seed cho metric giống hệt.
  - Không có dòng test nào trong predictions.

#### Phase 4 — Decision simulation (M3 · T2.8, T4.3–T4.5 · §6.13–6.14)

- `decision/simulation.py`: `fit_value_fallback`, `fit_value_cap`, `value_proxy`.
- `decision/policy.py`: A, B (100 seeds), C, D, **E**; `summarize_selection`, `run_policies` (hai `value_basis`, `lift_structure` từ config), `summarize`, `build_targeting_table`.
- `stage_simulate` trên **validation** → `scenario_results.csv`, `policy_comparison.csv`, `customer_targeting_table.csv`. Thêm bảng `break_even.csv` (p* theo scenario × V quantiles) và "EIM share of top 1% customers".
- **DoD:**
  - `test_policy.py`, `test_simulation.py` pass; thêm test cho `run_policies`: INV-11, INV-12, B reproducible, A = 0, D ≤ K và chỉ EIM > 0, hai value_basis.
  - Contract của 3 bảng pass.

#### Phase 5 — Sensitivity (M3 · T5.1 · §6.15)

- `decision/sensitivity.py`: `run_grid` trên grid của `simulation.sensitivity_grid` (gồm `lift_structure` constant/persuadable, value cap on/off) + calibration shift ± (prevalence − mean p); `break_even`.
- **DoD:**
  - Số dòng output bằng tích số giá trị grid × số policy (có test).
  - `sensitivity_results.csv` + heatmap trong `outputs/figures/`.
  - Kết luận robustness viết bằng số: D so với B, C, E trên basis `actual_outcome`, cho **cả hai** lift structure.
  - Kết quả đã biết trước: với `persuadable` và 3 scenario chính, D không target ai (EIM ≤ 0). Phải báo cáo điều này, **không che giấu, không chỉnh tham số để làm đẹp kết quả**.

#### Phase 6 — Dashboard (M3 · T5.3 · SPEC §11)

- `dashboard/app.py`: 3 view (Overview · Promotion Scenario · Actionable Customer/Segment).
  - Đúng 5 KPI (SPEC §1.8).
  - Control: scenario, lift structure, capacity, value basis.
  - Hiển thị p* và target count của D so với K.
  - Bảng khách lọc được + export CSV.
  - Banner non-causal cố định.
  - Chỉ đọc `outputs/tables/`.
- **DoD:**
  - `docker compose up dashboard` → `/_stcore/health` trả 200.
  - Một test đọc output và đối chiếu KPI với `scenario_results.csv` (sai số 0).
  - Screenshot mỗi view lưu ở `outputs/figures/dashboard_*.png` (dùng streamlit AppTest hoặc chụp thủ công; nếu không chụp được thì ghi rõ).

#### Phase 7 — Final test evaluation, một lần (M2+M3 · T5.2)

- Trước khi chạy: freeze toàn bộ lựa chọn (model, calibration, scenario, grid) và commit.
- `run evaluate --include-test` và `run simulate/sensitivity` trên test snapshots, log vào `test_access_log.jsonl`.
- Báo cáo calibration-in-the-large theo từng T0 test (D25).
- **DoD:** test metrics + test policy comparison được ghi; **không** được thay đổi model/tham số sau bước này. Nếu buộc phải đổi, ghi decision log và báo cáo **cả hai** kết quả.

#### Phase 8 — Notebooks & deliverables (ALL · T5.4–T5.6, T6.x)

- `notebooks/01…09_*.ipynb` theo Code Spec §2: mỗi notebook chạy từ đầu đến cuối, chỉ gọi `retail_targeting.*`, có markdown giải thích và biểu đồ. Chạy bằng `jupyter nbconvert --execute` trong container dev.
- `docs/model_analysis_card.md` theo SPEC §13: target, unit, decision time, population/coverage, features, dates + purge, metrics (validation và test), assumptions, **ethics/bias** (missing ID 22.76%, UK chiếm đa số, wholesaler, không dùng country làm feature), risks, limitations.
- `docs/executive_brief.md` → PDF **≤ 2 trang**: recommendation (target ai, theo rule gì), simulated impact kèm range qua các scenario và lift structure, campaign size/cost, 3 assumption quan trọng nhất, risks/limitations, next step (A/B test thật để đo δ). Viết cho manager, không dùng thuật ngữ kỹ thuật.
- Cập nhật `docs/source_log.md` (bảng filter bằng số thật từ pipeline), `docs/data_dictionary.md` (bản final), `README.md` (run instructions đầy đủ, thời gian chạy).
- Cập nhật trạng thái `docs/implementation_plan_topic1.md` và `docs/traceability_matrix_topic1.md` (Status = Done kèm link evidence cho từng R01–R25 và 10 mục checklist).

#### Phase 9 — Final QA (T6.1–T6.6)

1. **Clean rerun:**
   ```bash
   docker compose build --no-cache
   # rồi xoá data/interim, data/processed, outputs/* (trừ .gitkeep)
   docker compose run --rm pipeline run all
   docker compose run --rm pipeline run evaluate --include-test
   ```
   Các bảng chính phải giống bản đã report (diff CSV).
2. `docker compose run --rm test` cho **0 failed, 0 xfailed**; `grep -rn NotImplementedError src/` rỗng.
3. **Claim audit:** grep `ROI|causal|uplift|revenue lift|caused` trong `docs/executive_brief.md`, `docs/model_analysis_card.md`, `dashboard/`, `notebooks/`. Mọi kết quả khớp phải là câu phủ định/disclaimer.
4. **Consistency:** số liệu trong brief = dashboard = CSV.
5. Tick SPEC §15 (23 mục) và CAP Final Submission Checklist (10 mục) trong traceability matrix, mỗi mục có evidence.

### 5. Deliverables cuối cùng (checklist nộp)

- [ ] Code/notebooks tái lập được + `README.md` (Docker + local)
- [ ] `docs/data_dictionary.md` + `docs/source_log.md` (URL, ngày tải, license CC BY 4.0, filters, joins, cleaning)
- [ ] `outputs/tables/customer_targeting_table.csv` (customer-level score table)
- [ ] `docs/executive_brief.pdf` ≤ 2 trang
- [ ] Dashboard Streamlit: 3–5 KPI + actionable view
- [ ] `docs/model_analysis_card.md` (có ethics/bias)
- [ ] Assumptions + sensitivity results (`sensitivity_results.csv`, heatmap, break-even)
- [ ] Traceability matrix: tất cả Done kèm evidence

### 6. Được phép / không được phép

**Được:** tối ưu code; thêm test; thêm helper nội bộ; thêm dependency pinned; thêm cột **phụ** vào artifact (contract cho phép cột thừa); ghi decision log.

**Không được:**
- đổi window/split/cleaning rules/scenario values/segment rules/feature list mà không ghi decision log kèm evidence;
- dùng random split;
- tune trên test;
- xoá hoặc làm yếu test có sẵn;
- claim causal/ROI;
- thêm dataset ngoài;
- deep learning;
- làm stretch (XGBoost/SHAP/future-spend regression) **trước khi** Phase 1–9 đạt DoD. Stretch chỉ làm sau đó, trên branch riêng, so công bằng với LR trên cùng split.

### 7. Báo cáo cuối mỗi phiên

Ngắn gọn, gồm:

1. Phase đã xong (kèm evidence: số test pass/xfail, con số so với Code Spec §3.1, file output).
2. Phase đang làm và phần còn dở.
3. Quyết định mới ghi vào decision log.
4. Blocker (nếu có) và cách xử lý.
5. Lệnh để người khác tái hiện kết quả.

## END AGENT TASK
