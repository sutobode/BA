# Topic 1 — Review plan và Project Specification v1.0

**Project:** Customer Value & Promotion Targeting for an Online Retailer  
**Dataset đề xuất:** UCI Machine Learning Repository — Online Retail II  
**Đối tượng review:** `BA.pdf` (Project Specification v0.1) và `BA (1).pdf` (phân chia công việc/kế hoạch nhóm)  
**Căn cứ chính:** `BA_Capstone_Topics_2026_MSc class (1).pdf`, đặc biệt Format & Expectations, Topic 1, Final Submission Checklist.

> Tài liệu này là bản đề xuất đã chỉnh sửa, không phải cam kết causal uplift. Mọi kết quả promotion trong project phải được gọi là **simulated/expected impact under stated assumptions**.

---

## 1. Executive review

### 1.1 Kết luận

Plan hiện tại **đúng hướng và đã bao phủ phần lớn yêu cầu bắt buộc của Topic 1**. BA v0.1 có business question đúng, RFM/cohort/segmentation, customer snapshot tại `T0`, đề xuất temporal holdout, Logistic Regression, scenario simulation, policy comparison, dashboard, model card và Definition of Done. BA(1) cũng đã phân chia ownership theo ba workstream tương đối hợp lý.

Tuy nhiên, plan chưa nên dùng nguyên trạng để triển khai. Có bốn điểm P0 cần sửa trước khi nhóm coding/modeling:

1. **Thời lượng:** capstone quy định project duration **6 tuần**, trong khi BA v0.1 và BA(1) ghi **4 tuần**. Có thể dùng 4 tuần như kế hoạch hoàn thành baseline nội bộ, nhưng không được ghi đó là project duration chính thức.
2. **Temporal design:** đã nói temporal holdout nhưng chưa khóa snapshot cadence, quy tắc purge/embargo và xử lý outcome window chồng lấn. Đây là rủi ro leakage hoặc đánh giá quá lạc quan.
3. **Business simulation:** công thức margin có ý tưởng tốt nhưng phải định nghĩa chính xác `V` là value của một incremental order, `u` là incremental response/lift chứ không phải response quan sát được, và cùng một capacity phải được dùng cho mọi policy.
4. **Data contract:** cần khóa source/license/schema/return rules và schema của các artifact trước khi chia việc; nếu không, mỗi workstream có thể dùng một cách tính Monetary, customer value hoặc target khác nhau.

Sau khi sửa bốn điểm này, Topic 1 có scope phù hợp cho nhóm 3 người và đáp ứng được baseline bắt buộc mà không cần phụ thuộc vào XGBoost, SHAP hay optimization phức tạp.

### 1.2 Những phần nên giữ lại

- Business question và decision framing của BA v0.1 bám đúng Topic 1.
- Customer snapshot `(customer_id, T0)` là modeling unit phù hợp.
- RFM + Logistic Regression là baseline interpretable đúng yêu cầu.
- Không dùng random split làm đánh giá chính.
- Có ít nhất ba promotion scenarios và sensitivity analysis.
- Có Policy A/B/C/D để so sánh no-promotion, non-targeted, RFM và model+value.
- Có customer-level score table, dashboard decision-oriented, README, data dictionary, source log, model/analysis card và acceptance criteria.
- BA(1) đã phân biệt Data, Predictive Modeling và Decision Analytics thay vì giao Dashboard cho một người làm riêng lẻ.

---

## 2. Traceability: yêu cầu capstone và mức đáp ứng của plan

| Yêu cầu trong capstone | Bằng chứng trong plan hiện tại | Đánh giá / hành động |
|---|---|---|
| Project bắt đầu từ business decision, không bắt đầu từ algorithm | BA §2: “Which customers should receive a promotion…” | **Đạt**; giữ nguyên |
| Team 3–4 người, duration 6 tuần | BA v0.1 và BA(1) ghi 3 người, **4 tuần** | **P0 gap**; đổi lịch chính thức thành 6 tuần, có thể giữ 4 tuần như baseline checkpoint |
| Online Retail II; observation và future outcome window | BA §5–§7; đề xuất 180 ngày/90 ngày | **Đạt có điều kiện**; freeze sau EDA và ghi rõ lý do |
| Clean transactions, cancellations/returns, customer aggregation | BA §8 và BA(1) Member 1 | **Đạt có điều kiện**; phải có canonical transaction rule, schema log và coverage report |
| RFM/cohort/value segmentation | BA §9–§11 | **Đạt**; Frequency nên khóa là distinct valid orders, không phải số dòng |
| Predict repeat purchase và/hoặc future value | BA §13–§15 | **Đạt**; repeat purchase là MVP, future-spend regression là extension |
| RFM + interpretable model baseline | RFM + Logistic Regression | **Đạt** |
| Temporal holdout, predictor chỉ dùng thông tin trước decision time | BA §7, §21, BA(1) Member 2 | **Chưa đủ chi tiết**; thêm cadence, purge/embargo, fit preprocessing trên train |
| Ít nhất 3 discount/response assumptions | BA §17, BA(1) Member 3 | **Đạt có điều kiện**; định nghĩa response là incremental lift và công khai parameter |
| Technical metrics và business metric | BA §15, §20 | **Đạt**; thêm class-imbalance reporting và cùng-capacity comparison |
| So sánh với simple non-targeted policy | BA §19 | **Chưa đủ reproducible**; khóa same capacity, same population, same scenario, random seed/repeated random baseline |
| Không claim causal uplift/ROI | BA §4.2, §21, §26 | **Đạt**; phải áp dụng thống nhất trong report/dashboard/executive brief |
| Dashboard 3–5 KPIs và một actionable view | BA §23 | **Đạt**; khóa semantics và filter behavior |
| README, source log, data dictionary, executive brief ≤2 trang, model/analysis card | BA §24–§26 | **Đạt**; bổ sung license/terms, checksum/version và rerun smoke test |

**Kết luận traceability:** không cần đổi đề tài hoặc đổi algorithm. Cần làm rõ các contract và lịch triển khai để biến plan thành một project có thể audit/reproduce.

---

## 3. Feedback ưu tiên cho plan hiện tại

### P0 — phải chốt trước khi bắt đầu modeling

#### P0.1. Sửa mismatch 6 tuần và đặt baseline checkpoint

Capstone ghi project duration 6 tuần. Đề xuất:

- Ghi trong project metadata: `official_duration = 6 weeks`.
- Dùng **cuối Week 3** làm baseline-complete checkpoint: có clean data, customer snapshots, target, RFM benchmark, Logistic Regression, temporal evaluation sơ bộ.
- Weeks 4–6 dành cho policy/simulation, robustness, dashboard, executive brief, integration và final QA.
- Nếu nhóm chỉ có 4 tuần thực tế, phải nói rõ đó là **internal execution plan** và vẫn map deliverables vào tuần 5–6 của capstone; không được đổi duration trong Spec.

#### P0.2. Khóa temporal snapshot design

Đề xuất MVP:

- `T0` theo **monthly cadence** sau khi EDA xác nhận đủ số snapshot.
- Observation window: `[T0 − 180 days, T0)`.
- Outcome window: `[T0, T0 + 90 days)`.
- Eligible population: customer có `Customer ID` hợp lệ và ít nhất một valid purchase trong observation window; report coverage so với toàn bộ customer ID quan sát được.
- Feature chỉ dùng transaction có timestamp `< T0`; outcome chỉ dùng timestamp `>= T0` và `< T0 + 90 days`.
- Chọn chronological train/validation/final-test snapshots. Split dates phải được ghi vào config/README, không chọn sau khi xem metric test.
- Dùng **purge/embargo tối thiểu 90 ngày tại ranh giới split**, để outcome của snapshot train không chồng lên observation/outcome logic của validation/test. Không dùng random split làm final evaluation.
- Cùng một customer có thể xuất hiện ở nhiều snapshot chronological; đây là mô phỏng deployment. Không được để một transaction sau `T0` đi vào feature của snapshot đó. Nếu nhóm chọn group-by-customer split thay vì time split, phải giải thích vì sao; đó không thay thế temporal holdout.

Nếu EDA cho thấy 180/90 không phù hợp, nhóm được đổi window nhưng phải ghi lý do bằng data evidence trước khi train final model.

#### P0.3. Khóa canonical transaction và customer-value unit

Không hard-code cleaning rule trước khi kiểm tra schema thực tế. Data dictionary phải ghi:

- record/line/order unit;
- date field dùng cho decision time;
- field nhận diện cancellation/return;
- quantity/price rule;
- duplicate rule;
- missing customer-ID treatment;
- invalid date/price/quantity treatment;
- net transaction value và valid purchase event.

Để tránh line-item inflation:

- `Frequency` = số **distinct valid orders/invoices**, không phải số dòng sản phẩm.
- `Monetary` = tổng net order value trong observation window.
- `AOV` = `Monetary / Frequency` khi Frequency > 0.
- `V_i` trong simulation là **expected value của một incremental order** của customer i, MVP dùng `AOV_i`; không dùng toàn bộ historical Monetary làm value của một order.
- Fallback AOV (nếu customer không có AOV hợp lệ) phải là một giá trị training-only đã quy định, ví dụ median theo segment/cohort; fallback không được fit bằng dữ liệu tương lai.

#### P0.4. Sửa định nghĩa promotion response và formula

Vì Online Retail II không có randomized promotion treatment/control, `u_i` không phải response đã quan sát. Định nghĩa:

- `p_i`: predicted probability customer i có natural repeat purchase trong outcome window nếu không có offer.
- `δ_i`: assumed **incremental probability lift** do offer, không phải causal estimate. Cần bảo đảm `0 ≤ δ_i ≤ 1 − p_i`.
- `V_i`: expected net order value của một incremental order.
- `m`: assumed gross-margin rate, `0 ≤ m ≤ 1`.
- `d`: discount rate của scenario, `0 ≤ d ≤ 1`.
- `c`: contact/campaign cost trên targeted customer, nếu dùng.

Expected margin không offer:

```text
M0_i = p_i × V_i × m
```

Expected margin có offer:

```text
M1_i = (p_i + δ_i) × V_i × (m − d) − c
```

Simulated expected incremental margin:

```text
EIM_i = M1_i − M0_i
      = δ_i × V_i × m − (p_i + δ_i) × V_i × d − c
```

Thành phần discount trên `(p_i + δ_i)` phản ánh rằng natural buyers cũng có thể được giảm giá. Nếu business rule là chỉ discount khi customer mua, phải ghi rõ; nếu contact cost áp dụng cho mọi người được target, phải trừ `c` cho mọi targeted customer.

Không gọi `δ_i` là uplift quan sát được, không gọi `EIM` là actual ROI/revenue lift. Report phải dùng cụm “scenario-based simulated expected margin”.

#### P0.5. Chuẩn hóa policy baseline

Mọi policy phải dùng cùng:

- eligible population;
- decision snapshot và test period;
- scenario parameters;
- campaign capacity `K` hoặc budget `B`;
- cost/value definition;
- evaluation metric.

Policy đề xuất:

- **A — No promotion:** không target, EIM và cost bằng 0.
- **B — Non-targeted:** chọn ngẫu nhiên cùng `K` customer từ eligible population, fixed seed; chạy nhiều seed hoặc bootstrap và báo mean/range.
- **C — RFM:** rank theo RFM rule đã freeze, chọn cùng `K`.
- **D — Model + value:** rank theo `EIM_i`, loại `EIM_i ≤ 0`, chọn top positive tối đa `K` hoặc đến khi hết budget.

Nếu budget không đủ cho K customer, dùng budget làm constraint chính và phải report số customer được target. Không so D với B ở capacity khác nhau.

### P1 — nên hoàn thành trong Weeks 2–5

- Báo cáo positive-class prevalence theo snapshot; không dùng accuracy làm metric chính khi imbalance.
- Logistic Regression cần preprocessing nằm trong pipeline; scaler/encoder/imputer chỉ fit trên training snapshots.
- Báo cáo ROC-AUC, PR-AUC, Brier score và reliability/calibration plot trên validation và final test nếu có đủ dữ liệu.
- Không chọn threshold chỉ theo Youden/accuracy; báo cáo top-K/capacity curve và precision/recall tại campaign threshold.
- Thực hiện error analysis theo segment, cohort và snapshot period.
- Report missing Customer-ID rate, excluded transaction rate và customer coverage sau cleaning.
- Sensitivity grid tối thiểu thay đổi discount, incremental lift/response assumption và capacity; nếu có thể thêm gross-margin rate/contact cost.
- Tạo một owner accountable cho mỗi artifact; “cả nhóm cùng chịu trách nhiệm” chỉ dùng cho integration/final QA, không thay cho owner.
- Dashboard phải phân biệt rõ `Expected future value`, `Expected promotion cost`, `Simulated EIM` và không hiển thị “ROI”, “uplift”, “revenue lift” nếu không có causal design.

### P2 — chỉ làm sau khi baseline đạt DoD

- Gradient boosting, calibration nâng cao, SHAP.
- Future-spend regression.
- Budget optimization phức tạp hoặc recommendation layer nhiều action.
- Bất kỳ external dataset nào không cần thiết cho Topic 1.

---

## 4. Project Specification v1.0 đề xuất

### 4.1 Purpose và business decision

**Business question:** Which customers should the retailer prioritize for retention or promotion to increase expected future margin without over-discounting?

**Primary decision tại mỗi `T0`:** trong fixed campaign capacity/budget, customer nào được target promotion và customer nào không được target?

**Decision output:** mỗi eligible customer nhận một action:

- `TARGET` — positive simulated EIM và nằm trong capacity/budget;
- `DO_NOT_TARGET` — EIM không dương hoặc không nằm trong top capacity;
- optional `REVIEW` — chỉ dùng nếu nhóm cần đánh dấu missing/low-confidence data, không thay thế hai action MVP.

**Decision maker giả định:** retail CRM/marketing manager có campaign capacity giới hạn.

### 4.2 Scope

**In scope:**

1. Online Retail II source acquisition và source/data-quality log.
2. Transaction cleaning, cancellation/return identification, customer-ID coverage.
3. Customer snapshots tại T0.
4. RFM, cohort và 4–6 business-readable segments.
5. Repeat-purchase target trong future outcome window.
6. RFM benchmark và Logistic Regression baseline.
7. Temporal holdout, leakage audit, calibration và error analysis.
8. Customer value proxy và scenario-based expected-margin simulation.
9. Ba promotion scenarios trở lên, sensitivity analysis.
10. Policy comparison ở cùng capacity/budget.
11. Customer-level targeting output và decision dashboard.
12. README, data dictionary, source log, model/analysis card, executive brief tối đa 2 trang.

**Out of scope:**

- causal uplift/treatment-effect estimation;
- actual ROI, observed revenue lift hoặc avoided cost claim;
- production API/real-time campaign system;
- deep learning và complex recommender system;
- product-level personalized coupon optimization;
- merge complaint/external dataset chỉ để tăng feature count;
- full production deployment.

### 4.3 Data source và governance

Source log bắt buộc có:

| Field | Nội dung |
|---|---|
| `source_name` | UCI Online Retail II |
| `source_url` | URL tải chính thức tại thời điểm project bắt đầu |
| `access/download_date` | Ngày giờ tải |
| `version_or_snapshot` | File/version/hash nếu có |
| `license_or_terms` | License/terms và giới hạn sử dụng đã kiểm tra |
| `raw_filename` | Tên file raw đã lưu |
| `filters` | Filter dùng hoặc không dùng |
| `joins` | Join; MVP nên là không join external table |
| `cleaning_decisions` | Quy tắc duplicate, return, cancellation, invalid values, missing IDs |

Nhóm phải kiểm tra lại availability và terms khi bắt đầu project; không giả định metadata trong PDF luôn không đổi.

### 4.4 Unit, population, target và time design

**Raw-data unit:** transaction line theo schema thực tế của Online Retail II.

**Modeling unit:** `(customer_id, decision_date=T0)`.

**Candidate design:** observation 180 ngày, outcome 90 ngày, monthly snapshots. Thiết kế chỉ được freeze sau initial EDA.

**Eligible customer:** có customer identifier hợp lệ và ít nhất một valid purchase trong observation window. Báo cáo:

- số customer ID tổng;
- tỷ lệ missing ID;
- số customer đủ điều kiện;
- coverage theo từng snapshot;
- số customer bị loại do cleaning/eligibility.

**Valid purchase event:** event còn lại sau canonical cleaning, không phải cancellation/return bị loại, có customer ID hợp lệ và giá trị/quantity hợp lệ theo data rule. Quy tắc cụ thể phải dựa trên schema thực tế và xuất hiện trong data dictionary.

**Target:**

```text
repeat_purchase_90d_i = 1
nếu customer i có ít nhất một valid purchase trong [T0, T0 + 90 days)
ngược lại = 0
```

Nếu chọn horizon khác sau EDA, phải đổi tên target và update mọi artifact; không giữ tên `repeat_purchase_90d` cho horizon khác.

### 4.5 Leakage-safe feature rules

Tất cả feature của snapshot phải satisfy:

```text
transaction_datetime < T0
```

Không được dùng outcome window, post-T0 transaction, realized response, future customer value hoặc aggregate fit trên toàn bộ dataset để tạo predictor.

Preprocessing cho model phải là một pipeline có `fit` trên train snapshots; validation/test chỉ được `transform`. RFM quantile cutoffs, imputation values, scaling và category encoding nếu có phải được freeze từ training data hoặc được ghi rõ là descriptive-only.

### 4.6 Feature specification

**Required RFM:**

- `recency_days = T0 − latest_valid_purchase_date`;
- `frequency_orders = count(distinct valid order/invoice IDs)`;
- `monetary_net = sum(net valid order value)`.

**Optional historical features nếu data support:** `AOV`, total quantity, unique products, purchase frequency per active month, tenure, average interpurchase time, return rate, recent order count. Chỉ giữ feature có business interpretation và availability tại T0.

**Segmentation:** RFM percentile/quantile scores và tối đa 4–6 segments, ví dụ High-value active, High-value at risk, Developing, Low-value active, Dormant. Cutoffs phải được lưu trong config và không thay đổi tùy ý theo dashboard filter.

**Cohort:** first valid purchase month/period; dùng để xem retention/repeat behavior, seasonality và stability, không được dùng future information.

### 4.7 Modeling baseline

**Benchmark:** RFM-based rank/probability rule, được đánh giá trên cùng temporal test period.

**Required model:** Logistic Regression cho `repeat_purchase_*`.

**Reporting:**

- PR-AUC;
- ROC-AUC;
- Brier score/calibration;
- reliability plot;
- precision/recall tại top-K hoặc campaign capacity;
- prevalence của positive class;
- error analysis theo segment/cohort/time.

**Advanced model:** chỉ chạy sau khi benchmark, Logistic Regression, temporal evaluation và business interpretation hoàn tất. Nếu advanced model không cải thiện decision quality hoặc calibration, baseline interpretable vẫn là model được recommend.

### 4.8 Temporal validation

Config phải chứa danh sách snapshot dates và nhãn split, ví dụ:

```text
train_snapshots      = earlier chronological T0 values
validation_snapshots = later chronological T0 values
test_snapshots       = latest usable T0 values
purge_days           = 90
```

Exact dates chỉ freeze sau data audit nhưng trước final model fitting. Final test chỉ dùng để report một lần ở cuối; không dùng test để chọn hyperparameter, scenario hoặc threshold.

### 4.9 Promotion scenario model

Mỗi scenario phải công khai ít nhất:

- discount rate `d`;
- assumed incremental lift `δ` hoặc quy tắc tạo `δ_i`;
- gross-margin rate `m`;
- contact cost `c`;
- campaign capacity `K` hoặc budget `B`;
- value unit `V_i`;
- random seed nếu có non-targeted selection.

Named scenarios:

| Scenario | Mục đích |
|---|---|
| Conservative | discount thấp, incremental lift thấp; downside |
| Base | parameter planning chính |
| Aggressive | discount/lift cao hơn nhưng chi phí và rủi ro over-discount cao hơn |

Không bắt buộc khóa số phần trăm trong Spec trước EDA/business review, nhưng final config/dashboard phải có số cụ thể và sensitivity table.

### 4.10 Targeting policy

Với mỗi scenario và snapshot:

1. tạo `p_i` từ model;
2. tạo `V_i` từ customer value proxy;
3. tạo `EIM_i` theo formula §3 P0.4;
4. loại `EIM_i ≤ 0`;
5. rank giảm dần theo EIM;
6. chọn top positive trong capacity/budget;
7. assign `TARGET`/`DO_NOT_TARGET`.

**Primary recommendation:** Model + value targeting chỉ được recommend nếu nó cải thiện simulated business metric một cách ổn định so với non-targeted và RFM baseline trong các scenario hợp lý; không chỉ dựa vào một scenario tốt nhất.

### 4.11 Dashboard và KPIs

Dashboard có tối đa 5 KPI chính:

1. `Targeted customers` — campaign scale;
2. `Expected future value` — value addressed, không phải realized revenue;
3. `Expected promotion cost` — discount/contact exposure;
4. `Simulated expected incremental margin` — scenario-based business outcome;
5. `Margin per targeted customer` — efficiency.

Có ít nhất một actionable view:

- customer/segment table với `recommended_action`, rank, segment, p, value, cost, EIM;
- scenario selector;
- capacity/budget control;
- policy comparison view.

UI label và executive brief phải dùng “simulated”, “expected”, “assumed”, “scenario” khi phù hợp; không dùng “caused”, “uplift”, “ROI” hoặc “revenue lift vs control”.

### 4.12 Output contracts

**`customer_snapshots`** — producer M1, consumers M2/M3:

```text
customer_id, decision_date, recency_days, frequency_orders,
monetary_net, aov, rfm_score, customer_segment, feature_version
```

**`customer_predictions`** — producer M2, consumer M3:

```text
customer_id, decision_date, split, actual_repeat_purchase,
predicted_repeat_probability, model_version, feature_version
```

**`scenario_results`** — producer M3:

```text
policy, scenario, decision_date, capacity_or_budget,
target_count, expected_promotion_cost, expected_future_value,
simulated_eim, eim_per_target, random_seed
```

**`customer_targeting_table`** — producer M3, consumer dashboard/final report:

```text
customer_id, decision_date, scenario, policy, customer_segment,
repeat_purchase_probability, customer_value_proxy, discount_rate,
incremental_lift_assumption, expected_promotion_cost,
simulated_expected_incremental_margin, target_rank, recommended_action
```

M2 không tự tính lại Monetary; M3 không train lại model trong simulation notebook. Mỗi artifact phải có `feature_version`, `model_version` hoặc `scenario_version` để trace.

### 4.13 Required artifacts

```text
README.md
project_config.(yaml/json)
data/
  raw/                         # hoặc hướng dẫn tải lại, tùy policy dữ liệu
  processed/
  data_dictionary.md
  source_log.md
notebooks/
  01_data_understanding
  02_cleaning_and_snapshots
  03_rfm_cohort_segmentation
  04_target_and_temporal_split
  05_logistic_baseline
  06_evaluation_and_diagnostics
  07_promotion_simulation
  08_policy_comparison
  09_sensitivity_analysis
outputs/
  data_quality_report
  customer_snapshots
  rfm_segments
  customer_predictions
  model_metrics
  calibration_results
  scenario_results
  policy_comparison
  sensitivity_results
  customer_targeting_table
  model_analysis_card.md
dashboard/
executive_brief.pdf       # tối đa 2 trang
```

Nếu source không được phép commit raw data, README phải có run instructions, URL, download date, checksum/version và expected schema.

---

## 5. Kế hoạch 6 tuần và ownership đề xuất

| Tuần | M1 — Data & Customer Analytics | M2 — Modeling & Validation | M3 — Decision Analytics & Dashboard | Checkpoint nhóm |
|---|---|---|---|---|
| 1 | Source, schema, profiling, cleaning hypotheses | Target/window/validation design | Decision rule, KPI, scenario parameter draft | Problem statement + data readiness |
| 2 | Canonical cleaning, customer coverage, snapshot prototype | Leakage audit và benchmark skeleton | Value proxy + simulator skeleton | Frozen data/target contract |
| 3 | RFM, cohort, segmentation, feature export | Logistic Regression + temporal baseline | Preliminary policy/simulation | **Baseline complete** |
| 4 | Data-quality/segment diagnostics | PR-AUC/ROC-AUC, calibration, threshold, error analysis | 3+ scenarios, policy comparison, sensitivity grid | End-to-end result |
| 5 | Final source log/data dictionary | Model card, robustness and final test | Dashboard, actionable table, executive recommendation | Draft final package |
| 6 | Re-run and data QA | Metric/table consistency QA | Dashboard/brief/demo integration | Final QA + submission |

**Accountability:**

- M1 accountable cho source, cleaning rule, data dictionary, snapshot contract.
- M2 accountable cho target, temporal split, leakage audit, model metrics và model card.
- M3 accountable cho assumptions, simulation, policy comparison, dashboard và executive decision view.
- Cả nhóm accountable cho business framing, review assumptions, README integration, final rerun và claim review.

Mỗi tuần phải có artifact versioned; không chờ M1 hoàn tất mọi thứ mới cho M2/M3 bắt đầu. Sau khi có schema và snapshot prototype, các workstream chạy song song với interface cố định.

---

## 6. Definition of Done / acceptance checklist

Project chỉ được gọi là baseline-complete khi tất cả mục sau có evidence trong output:

- [ ] Business question, decision maker, decision rule và guardrails được viết rõ.
- [ ] Dataset source URL, download date, version/checksum và license/terms được ghi.
- [ ] Raw unit, modeling unit, `T0`, observation window, outcome horizon và eligible population được ghi.
- [ ] Missing-ID rate, excluded-row/customer coverage và data-quality report được xuất.
- [ ] Cancellation/return/duplicate/invalid quantity-price-date rules được data dictionary hóa.
- [ ] `Frequency` là distinct valid orders và `Monetary/AOV` có định nghĩa canonical.
- [ ] Customer snapshots chỉ dùng transaction trước `T0`; có feature audit.
- [ ] Snapshot cadence, split dates và purge/embargo được lưu trong config.
- [ ] RFM, cohort view và tối đa 4–6 actionable segments được tái lập.
- [ ] Repeat-purchase target có định nghĩa executable và không dùng post-outcome data.
- [ ] RFM benchmark và Logistic Regression baseline hoàn tất.
- [ ] Preprocessing fit trên train only.
- [ ] PR-AUC, ROC-AUC, Brier/calibration và threshold/capacity results được report.
- [ ] Error analysis theo segment/cohort/time được thực hiện hoặc limitation được ghi rõ.
- [ ] `V_i`, `m`, `d`, `δ_i`, `c`, capacity/budget và formula EIM được công khai.
- [ ] Ít nhất 3 scenarios và sensitivity analysis được chạy.
- [ ] No-promotion, same-capacity non-targeted và RFM baselines được so sánh công bằng.
- [ ] Customer-level score/targeting table có schema cố định và action rule.
- [ ] Dashboard có 3–5 KPIs và một actionable view.
- [ ] Executive brief tối đa 2 trang nêu recommendation, simulated range, assumptions, risk và limitation.
- [ ] Model/analysis card có target, features, unit, validation, metrics, assumptions, ethics/bias considerations, risks và limitations.
- [ ] README cho phép người khác rerun core analysis; có smoke test hoặc rerun evidence.
- [ ] Không có causal uplift/actual ROI/observed control-lift claim.

---

## 7. Các quyết định nhóm phải freeze tại kickoff

1. Source URL, download date, file/version và license/terms.
2. Exact transaction fields sau schema inspection.
3. Canonical return/cancellation rule.
4. Missing Customer-ID eligibility và coverage threshold.
5. Snapshot cadence; mặc định monthly.
6. Observation/outcome window; mặc định 180/90 ngày.
7. Exact chronological split dates và 90-day purge/embargo.
8. Value unit `V_i`; mặc định AOV per expected order.
9. Gross-margin, discount, incremental-lift và contact-cost parameter ranges.
10. Capacity/budget dùng trong comparison.
11. Seed/repetition count cho non-targeted baseline.
12. KPI names/definitions và câu chữ không-causal trong dashboard.
13. Artifact schemas, version fields và owner.

Nếu một trong các mục trên chưa được freeze, nhóm vẫn có thể làm exploratory analysis nhưng chưa được gọi là final baseline/model result.

---

## 8. Kết luận review

BA v0.1 là nền tảng tốt và không cần đổi Topic 1. BA(1) có cách chia workstream hợp lý, nhưng kế hoạch 4 tuần nên được xem là lịch nội bộ rút gọn chứ không phải duration của capstone. Bản Spec này giữ nguyên MVP: clean Online Retail II → customer snapshots → RFM/cohort/segmentation → Logistic Regression temporal baseline → scenario-based targeting → policy comparison → dashboard.

Thứ tự thực hiện được khuyến nghị là: **freeze data/temporal/business contracts → hoàn thành baseline → validate/calibrate → simulation cùng capacity → dashboard/brief → final rerun**. Không làm advanced model trước khi toàn bộ checklist baseline và business interpretation hoàn tất.
