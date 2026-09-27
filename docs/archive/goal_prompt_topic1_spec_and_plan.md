# GOAL PROMPT — Viết Project Specification và Implementation Plan đầy đủ cho Topic 1

> **Cách sử dụng:** Copy toàn bộ nội dung từ phần `BEGIN AGENT TASK` đến `END AGENT TASK` và đưa cho AI Agent có quyền đọc/ghi file trong project. Agent phải làm việc trực tiếp với các file nguồn, tạo các tài liệu đầu ra và kiểm tra lại trước khi kết thúc.

---

## BEGIN AGENT TASK

### 1. Vai trò

Bạn là một Senior Business Analyst, Data Product Manager và Lead Data Scientist phụ trách xây dựng một kế hoạch capstone Business Analytics có thể triển khai và đánh giá được.

Bạn phải:

- đọc và hiểu toàn bộ tài liệu nguồn trước khi đề xuất;
- ưu tiên business decision, measurable impact và reproducibility thay vì model complexity;
- phân biệt rõ fact lấy từ tài liệu, design decision của nhóm và assumption cần xác nhận;
- tạo một Project Specification đầy đủ và một Implementation Plan Step by Step có thể giao việc cho team 3 người;
- không tự bịa dữ liệu, metric, schema hoặc kết quả model chưa được kiểm chứng;
- làm việc autonomous, không dừng ở việc mô tả ý tưởng chung chung.

### 2. Mục tiêu tổng thể

Hãy đọc các file nguồn trong project và viết đầy đủ specification và kế hoạch triển khai cho:

> **Topic 1 — Customer Value & Promotion Targeting for an Online Retailer**

Business question chính:

> Which customers should the retailer prioritize for retention or promotion to increase expected future margin without over-discounting?

Project phải biến business question trên thành một pipeline có thể chạy lại:

```text
Business decision
→ Data source and data understanding
→ Transaction cleaning
→ Customer snapshots at T0
→ RFM/cohort/segmentation
→ Repeat-purchase target
→ Temporal validation
→ RFM benchmark + interpretable baseline model
→ Customer value proxy
→ Promotion scenario simulation
→ Capacity-constrained targeting policy
→ Policy comparison
→ Dashboard and executive recommendation
→ Reproducibility and final QA
```

### 3. File nguồn bắt buộc

Làm việc trong thư mục project hiện tại. Đọc các file sau trước khi viết tài liệu:

1. `C:\Users\X1\Master_Course\BA\BA_Capstone_Topics_2026_MSc class (1).pdf`
2. `C:\Users\X1\Master_Course\BA\BA.pdf`
3. `C:\Users\X1\Master_Course\BA\BA (1).pdf`

Nếu có file sau thì dùng để tham khảo, nhưng phải kiểm tra lại với PDF gốc:

4. `C:\Users\X1\Master_Course\BA\Topic1_Spec_Review_and_Recommendation.md`

Quy tắc đọc tài liệu:

- PDF capstone là source of truth cho yêu cầu môn học, Topic 1, deliverables, duration và checklist đánh giá.
- `BA.pdf` là Project Specification v0.1 cần được review và cải thiện.
- `BA (1).pdf` là plan phân chia công việc và ownership cần được review.
- Nếu các file mâu thuẫn, tạo một decision log, nêu rõ mâu thuẫn và chọn phương án dựa trên capstone.
- Không coi assumption trong BA v0.1, ví dụ observation 180 ngày hoặc outcome 90 ngày, là yêu cầu bắt buộc của giảng viên. Phải ghi chúng là proposed design cho đến khi được xác nhận bằng EDA.

Nếu PDF không thể đọc trực tiếp, hãy dùng công cụ trích xuất PDF khả dụng trong môi trường. Không bỏ qua phần Topic 1, Final Submission Checklist, Format & Expectations hoặc các yêu cầu về validation/leakage.

### 4. Context cần giữ nhất quán

- Topic: Customer Value & Promotion Targeting for an Online Retailer.
- Primary dataset: UCI Machine Learning Repository — Online Retail II.
- Team size: 3 students, có thể mở rộng thành 4 nếu tài liệu capstone yêu cầu.
- Official capstone duration: **6 weeks**. Nếu nhóm có kế hoạch nội bộ 4 tuần, phải ghi rõ đó là internal baseline schedule, không thay thế duration chính thức.
- MVP phải hoàn thành trước advanced/stretch work.
- Kết quả promotion không có causal treatment/control trong dataset; chỉ được trình bày là scenario-based simulated/expected impact.

### 5. Nhiệm vụ chính

Thực hiện lần lượt tất cả các bước bên dưới. Không chỉ viết outline; hãy điền nội dung, quyết định, bảng, acceptance criteria và artifact schema cụ thể.

---

## PHASE 0 — Kiểm tra đầu vào và source traceability

1. Liệt kê tất cả file nguồn đã tìm thấy, đường dẫn, loại file, kích thước và trạng thái đọc được.
2. Trích xuất các yêu cầu của capstone thành bảng traceability:
   - requirement;
   - source file/section/page nếu xác định được;
   - cách Topic 1 đáp ứng;
   - artifact dùng để chứng minh;
   - gap hoặc risk.
3. Tách riêng ba loại thông tin:
   - `FACT_FROM_SOURCE`;
   - `PROJECT_DESIGN_PROPOSAL`;
   - `ASSUMPTION_TO_VALIDATE`.
4. Liệt kê các mâu thuẫn giữa capstone và BA/BA(1), đặc biệt duration 6 tuần versus 4 tuần.
5. Tạo một decision log có owner, due date, impact nếu chưa quyết định và cách validation.

---

## PHASE 1 — Business framing

Viết rõ các nội dung sau:

1. Project title và one-sentence value proposition.
2. Business context và pain point của online retailer.
3. Decision maker giả định.
4. Business question.
5. Primary decision tại mỗi decision time `T0`.
6. Decision options:
   - no promotion;
   - non-targeted promotion;
   - RFM-based targeting;
   - model + customer-value targeting.
7. Decision criteria:
   - expected future value;
   - promotion cost/discount exposure;
   - simulated expected incremental margin;
   - campaign capacity/budget;
   - technical predictive quality;
   - risk/limitations.
8. North-star metric và 3–5 decision KPIs.
9. Business guardrails.
10. Những claim được phép và không được phép trong report.

Business framing phải chứng minh project bắt đầu từ decision, không bắt đầu từ việc chọn Logistic Regression hay XGBoost.

---

## PHASE 2 — Scope, objectives và Definition of Done

Viết:

1. Primary objective.
2. Secondary objectives.
3. MVP bắt buộc trong 6 tuần.
4. Stretch objectives chỉ làm sau khi MVP đạt DoD.
5. In-scope items.
6. Explicitly out-of-scope items.
7. Assumptions.
8. Dependencies.
9. Risks và mitigation.
10. Definition of Done dạng checklist có thể kiểm chứng.

MVP tối thiểu phải gồm:

```text
Online Retail II
→ cleaning và return/cancellation treatment
→ customer snapshots
→ RFM/cohort/segmentation
→ repeat purchase target
→ RFM benchmark
→ Logistic Regression baseline
→ temporal holdout
→ calibration and business threshold analysis
→ customer value proxy
→ ít nhất 3 promotion scenarios
→ same-capacity policy comparison
→ customer-level targeting table
→ dashboard 3–5 KPIs
→ README/data dictionary/source log/model card/executive brief
```

---

## PHASE 3 — Data source và data understanding specification

Viết data specification chưa phụ thuộc vào việc đoán schema. Bắt buộc có:

1. Source name, official URL, access/download date, version/snapshot, license/terms.
2. Raw-data unit và expected fields.
3. Data dictionary template gồm:
   - field name;
   - data type;
   - meaning;
   - allowed values;
   - missingness;
   - cleaning rule;
   - leakage risk;
   - downstream use.
4. Initial profiling checklist:
   - row count;
   - date range;
   - unique customers;
   - missing Customer ID;
   - duplicates;
   - invalid quantity/price/date;
   - cancellation/return prevalence;
   - transaction volume over time;
   - negative values;
   - order/invoice structure.
5. Source log format.
6. Data-quality report format.
7. Reproducible raw-data acquisition instructions.
8. Policy nếu raw data không được commit vào repository.

Không được hard-code rằng một cột là cancellation/return trước khi kiểm tra schema và documentation thực tế.

---

## PHASE 4 — Canonical transaction cleaning

Thiết kế một canonical cleaning contract, trong đó Agent phải yêu cầu team xác nhận bằng EDA:

1. Cách nhận diện cancellation.
2. Cách nhận diện returns.
3. Cách tính gross line value và net value.
4. Cách xử lý quantity âm/dương.
5. Cách xử lý price bằng 0 hoặc âm.
6. Cách xử lý missing Customer ID.
7. Cách xử lý duplicate rows và duplicate orders.
8. Cách xử lý invalid/missing date.
9. Cách phân biệt transaction line và order/invoice.
10. Cách định nghĩa valid purchase event.
11. Cách ghi lại số dòng/số customer trước và sau mỗi filter.
12. Cách kiểm tra rằng cleaning không dùng thông tin sau `T0`.

Khóa nguyên tắc MVP:

- `Frequency` nên là số distinct valid orders/invoices, không phải số transaction lines.
- `Monetary` là net monetary value theo observation window.
- `AOV = Monetary / Frequency` nếu Frequency > 0.
- Mọi quyết định cleaning phải xuất hiện trong data dictionary/source log.

---

## PHASE 5 — Analytical unit, temporal design và target

Viết specification chính xác cho:

1. Raw-data unit.
2. Modeling unit: `(customer_id, T0)`.
3. Eligible population.
4. Snapshot cadence; đề xuất monthly nhưng phải validate bằng EDA.
5. Observation window.
6. Outcome window.
7. Decision time `T0`.
8. Target definition.
9. Customer inclusion/exclusion.
10. Snapshot generation algorithm.
11. Expected number of snapshots và coverage check.
12. Các trường hợp customer xuất hiện ở nhiều snapshots.

Có thể dùng proposal ban đầu:

```text
Observation window = [T0 - 180 days, T0)
Outcome window    = [T0, T0 + 90 days)
target            = valid purchase within outcome window
```

Nhưng phải ghi rõ đây là design proposal, được freeze sau initial EDA và business review.

Bắt buộc yêu cầu:

- feature transaction timestamp phải `< T0`;
- outcome transaction timestamp phải `>= T0` và `< T0 + horizon`;
- không dùng post-outcome information;
- nếu đổi horizon thì phải đổi tên target và update mọi artifact;
- báo cáo coverage và class prevalence theo snapshot.

---

## PHASE 6 — Temporal train/validation/test plan

Thiết kế temporal validation có thể thực hiện được:

1. Chronological train snapshots.
2. Later validation snapshots.
3. Latest usable final-test snapshots.
4. Exact split-date freeze process.
5. Purge/embargo rule; mặc định xem xét tối thiểu bằng outcome horizon.
6. Cách xử lý outcome window chồng lấn ở ranh giới split.
7. Preprocessing fit chỉ trên train.
8. RFM quantile cutoffs chỉ fit/freeze theo đúng design.
9. Hyperparameter/threshold selection chỉ dùng train/validation.
10. Final test chỉ report ở cuối.
11. Leak audit checklist.
12. Temporal backtest hoặc rolling validation nếu dữ liệu cho phép.

Phải giải thích rõ vì sao random train/test split không phù hợp với transaction-time data.

---

## PHASE 7 — Feature engineering, RFM, cohort và segmentation

Viết đầy đủ:

1. Required RFM features:
   - Recency;
   - Frequency;
   - Monetary.
2. Optional features chỉ nếu data support:
   - AOV;
   - total quantity;
   - unique products;
   - active months;
   - tenure;
   - interpurchase time;
   - return rate;
   - recent order count.
3. Feature availability tại T0.
4. Feature formula và data type.
5. Missing/fallback strategy.
6. Feature versioning.
7. Cohort definition từ first valid purchase.
8. Cohort metrics.
9. RFM scoring method.
10. Tối đa 4–6 business-readable segments.
11. Segment cutoff freeze process.
12. Segment stability checks theo snapshot/cohort.
13. Business interpretation cho từng segment.

Không được tạo quá nhiều segments chỉ để làm dashboard đẹp.

---

## PHASE 8 — Predictive modeling specification

Thiết kế baseline theo thứ tự:

1. Simple RFM benchmark/ranking.
2. Logistic Regression baseline.
3. Optional advanced model sau khi MVP đạt DoD.

Viết:

- target;
- feature set;
- categorical/numeric preprocessing;
- class imbalance treatment;
- random seed;
- model pipeline;
- training protocol;
- calibration protocol;
- model artifact format;
- explainability method;
- model card fields.

Metrics bắt buộc:

- PR-AUC;
- ROC-AUC;
- Brier score hoặc calibration metric;
- reliability/calibration plot;
- precision/recall tại top-K hoặc campaign capacity;
- positive-class prevalence;
- error analysis theo segment/cohort/time.

Không dùng accuracy làm business success metric chính khi class imbalance.

---

## PHASE 9 — Customer value và promotion simulation

Thiết kế customer value proxy thật rõ:

1. Value unit của một expected/incremental order.
2. MVP value proxy, đề xuất AOV thay vì toàn bộ historical Monetary.
3. Fallback value và cách fit fallback không leakage.
4. Gross-margin assumption.
5. Discount assumption.
6. Incremental response/lift assumption.
7. Contact/campaign cost.
8. Campaign capacity hoặc budget.
9. Conservative/Base/Aggressive scenarios.
10. Sensitivity grid.
11. Parameter source/owner/version.

Dùng notation rõ ràng:

- `p_i`: predicted natural repeat probability;
- `δ_i`: assumed incremental probability lift, không phải causal estimate;
- `V_i`: expected net value của một incremental order;
- `m`: gross-margin rate;
- `d`: discount rate;
- `c`: contact cost.

Công thức đề xuất:

```text
M0_i = p_i × V_i × m
M1_i = (p_i + δ_i) × V_i × (m − d) − c
EIM_i = M1_i − M0_i
      = δ_i × V_i × m − (p_i + δ_i) × V_i × d − c
```

Phải giải thích:

- `0 ≤ δ_i ≤ 1 − p_i`;
- natural repeat buyers có thể vẫn bị discount;
- các parameter là assumptions;
- EIM là scenario-based simulated expected margin;
- không được gọi EIM là actual ROI, revenue lift hoặc causal uplift.

---

## PHASE 10 — Targeting policy và policy comparison

Thiết kế policy algorithm:

1. Tính `p_i`.
2. Tính `V_i`.
3. Tính `EIM_i` cho từng scenario.
4. Loại customer có `EIM_i <= 0`.
5. Rank theo EIM giảm dần.
6. Chọn top positive trong capacity/budget.
7. Gán `TARGET` hoặc `DO_NOT_TARGET`.

So sánh tối thiểu:

- Policy A: No promotion.
- Policy B: Non-targeted/random cùng capacity.
- Policy C: RFM targeting cùng capacity.
- Policy D: Model + value targeting cùng capacity.

Mọi policy phải dùng cùng:

- eligible population;
- decision/test period;
- scenario assumptions;
- budget/capacity;
- value/cost definition;
- evaluation metric.

Non-targeted baseline phải có fixed seed và nên chạy nhiều seeds/bootstrap để báo mean/range. Không so sánh một policy ở K=100 với policy khác ở K=500.

Business metrics cần có:

- total simulated EIM;
- EIM per targeted customer;
- expected promotion cost;
- target count;
- expected value addressed;
- top-K capture/coverage nếu phù hợp;
- sensitivity theo scenario và capacity.

---

## PHASE 11 — Dashboard và executive communication

Thiết kế dashboard decision-oriented, không phải chỉ là EDA dashboard.

Bắt buộc có 3–5 KPIs, đề xuất:

1. Targeted customers.
2. Expected future value.
3. Expected promotion cost.
4. Simulated expected incremental margin.
5. Margin per targeted customer.

Có actionable view gồm:

- scenario selector;
- capacity/budget input;
- policy selector/comparison;
- segment/customer table;
- recommended action;
- probability, value, cost, EIM và rank;
- warnings về assumptions và non-causal interpretation.

Executive brief tối đa 2 trang phải trả lời:

1. Nên target ai?
2. Target theo rule nào?
3. Expected/simulated impact là bao nhiêu dưới các scenario?
4. Campaign cost/capacity là gì?
5. Assumptions nào quan trọng nhất?
6. Risks, limitations và điều gì cần kiểm chứng bằng experiment thật?

---

## PHASE 12 — Team structure và work breakdown

Thiết kế ownership cho team 3 người:

### Member 1 — Data & Customer Analytics

- source acquisition;
- profiling;
- cleaning;
- returns/cancellations;
- missing IDs;
- snapshots;
- RFM;
- cohort;
- segmentation;
- data dictionary;
- customer feature handoff.

### Member 2 — Predictive Modeling & Validation

- target construction;
- temporal split;
- purge/embargo;
- leakage audit;
- RFM benchmark;
- Logistic Regression;
- evaluation;
- calibration;
- threshold/capacity analysis;
- error analysis;
- model card.

### Member 3 — Decision Analytics & Dashboard

- customer value proxy;
- assumptions;
- scenario simulation;
- targeting rule;
- same-capacity policy comparison;
- sensitivity analysis;
- customer targeting table;
- dashboard;
- executive decision view.

Tạo RACI/ownership matrix cho:

- business framing;
- data definitions;
- target/window;
- leakage review;
- KPI/guardrails;
- assumptions;
- README;
- final QA;
- presentation.

Thiết kế artifact handoff contracts để mỗi workstream không tự tính lại logic của workstream khác.

---

## PHASE 13 — Implementation plan 6 tuần

Viết kế hoạch theo tuần, theo ngày hoặc milestone. Mỗi task phải có:

- task ID;
- objective;
- owner;
- input;
- action;
- output artifact;
- acceptance criteria;
- dependency;
- risk;
- validation command/check;
- definition of ready/done.

Kế hoạch tối thiểu:

### Week 1 — Framing và data readiness

- source/terms;
- business decision;
- schema/profiling;
- initial cleaning hypotheses;
- target/window proposal;
- KPI/guardrail draft;
- scenario parameter draft.

### Week 2 — Canonical data và snapshots

- cleaning pipeline;
- missing ID report;
- return/cancellation rule;
- data dictionary;
- snapshot prototype;
- feature contract;
- temporal split skeleton.

### Week 3 — Baseline complete

- RFM/cohort/segmentation;
- repeat-purchase target;
- RFM benchmark;
- Logistic Regression;
- initial temporal evaluation;
- baseline checkpoint.

### Week 4 — Evaluation và decision analytics

- PR-AUC/ROC-AUC;
- calibration;
- error analysis;
- customer value proxy;
- three scenarios;
- first policy comparison.

### Week 5 — Robustness và communication

- sensitivity grid;
- capacity analysis;
- policy stability;
- dashboard;
- customer targeting table;
- model card;
- executive brief draft.

### Week 6 — Integration và final QA

- rerun from clean environment;
- output consistency;
- leakage/claim audit;
- dashboard QA;
- README QA;
- final brief/presentation;
- final submission checklist.

Nếu đề xuất plan 4 tuần, chỉ được trình bày như internal acceleration plan và phải map đầy đủ vào official 6-week deliverables.

---

## PHASE 14 — Repository structure và artifact contracts

Đề xuất repository structure có thể dùng được, ví dụ:

```text
README.md
project_config.yaml
data/
  raw/
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
dashboards/
docs/
  project_specification.md
  implementation_plan.md
  executive_brief.md
```

Định nghĩa schema cho ít nhất:

- `customer_snapshots`;
- `customer_predictions`;
- `scenario_results`;
- `policy_comparison`;
- `sensitivity_results`;
- `customer_targeting_table`.

Mỗi artifact cần có version hoặc metadata phù hợp:

- `feature_version`;
- `model_version`;
- `scenario_version`;
- `decision_date`;
- `split`;
- `seed` nếu có random baseline.

---

## PHASE 15 — Validation và QA requirements

Tạo validation plan gồm các lớp sau:

### Data QA

- schema check;
- row count;
- date range;
- missingness;
- duplicate rate;
- customer-ID coverage;
- cancellation/return counts;
- invalid value counts;
- before/after cleaning reconciliation.

### Temporal/leakage QA

- mọi feature timestamp `< T0`;
- target chỉ lấy trong outcome window;
- no post-T0 columns;
- preprocessing fit train only;
- split dates chronological;
- purge/embargo applied;
- no test-based tuning;
- feature audit report.

### Model QA

- baseline exists;
- model pipeline reruns;
- PR-AUC/ROC-AUC available;
- calibration available;
- class prevalence reported;
- threshold/capacity results available;
- metrics segmented by time/cohort/segment.

### Decision QA

- scenario parameters visible;
- EIM formula reconciles with M1−M0;
- negative EIM not targeted;
- capacity/budget not exceeded;
- same population and capacity across policies;
- non-targeted random baseline reproducible;
- sensitivity results generated.

### Communication QA

- dashboard has 3–5 decision KPIs;
- actionable customer/segment view exists;
- executive brief ≤2 pages;
- assumptions and limitations visible;
- no causal/ROI/uplift claim unsupported by data;
- README contains run instructions;
- clean-environment smoke test completed.

Nếu project code đã tồn tại, chạy targeted tests, lint/type check, pipeline smoke test và build dashboard phù hợp. Nếu code chưa tồn tại, validation của deliverable này phải là document lint/structure check và review checklist; không được giả vờ có model result.

---

## PHASE 16 — Required output files

Sau khi hoàn thành, tạo hoặc cập nhật các file sau:

1. `docs/project_specification_topic1.md`
   - full specification;
   - traceability;
   - business/data/model/decision requirements;
   - assumptions;
   - guardrails;
   - acceptance criteria.

2. `docs/implementation_plan_topic1.md`
   - 6-week plan;
   - step-by-step tasks;
   - owners;
   - dependencies;
   - artifacts;
   - validation per step;
   - risks and mitigations.

3. `docs/decision_log_topic1.md`
   - facts;
   - proposed decisions;
   - unresolved questions;
   - evidence needed;
   - owner and due date.

4. `docs/traceability_matrix_topic1.md`
   - capstone requirement → specification section → implementation task → artifact → validation evidence.

5. Nếu cần, tạo `project_config.example.yaml` chứa các parameter chưa freeze, nhưng không chèn giá trị giả làm kết quả thực tế.

Nếu thư mục `docs/` chưa có, tạo thư mục. Không xóa hoặc overwrite file quan trọng mà không đọc trước. Nếu file đã tồn tại, giữ nội dung có giá trị và cập nhật có kiểm soát.

---

## 6. Quy tắc chất lượng và guardrails bắt buộc

1. Không tự nhận rằng promotion tạo ra causal uplift, ROI hoặc revenue lift vì Online Retail II không có randomized treatment/control.
2. Không dùng random train/test split làm final evaluation cho temporal transaction data.
3. Không dùng transaction sau `T0` để tạo feature cho snapshot tại `T0`.
4. Không để preprocessing, quantile cutoffs hoặc fallback value học từ validation/test một cách leakage-prone.
5. Không chọn advanced model trước baseline.
6. Không report accuracy như metric duy nhất.
7. Không sử dụng hidden constants cho discount, response/lift, margin, contact cost hoặc capacity.
8. Không so sánh policies ở capacity khác nhau.
9. Không mở rộng scope bằng external data nếu không chứng minh cần thiết và reproducible.
10. Không viết exact schema dựa trên giả định chưa kiểm tra source.
11. Mọi số liệu chưa chạy phải ghi là `TBD`, `proposed`, hoặc `to be validated`.
12. Nếu thiếu input hoặc gặp hard blocker, ghi rõ blocker, thử cách đọc/kiểm tra thay thế và chỉ hỏi user khi không thể tiếp tục hợp lý.
13. Không kết thúc chỉ bằng kế hoạch; phải tạo các output files và đọc/kiểm tra lại chúng.

---

## 7. Tiêu chí nghiệm thu cuối cùng cho Agent

Agent chỉ được báo hoàn thành khi tất cả điều kiện sau có bằng chứng từ file/output:

- [ ] Đã đọc ba PDF nguồn và ghi source traceability.
- [ ] Đã xác nhận đây là Topic 1.
- [ ] Đã review BA.pdf và BA (1).pdf, chỉ ra phần đạt và gap.
- [ ] Đã giải quyết hoặc ghi rõ mọi conflict 4 tuần/6 tuần.
- [ ] Có full Project Specification, không chỉ outline.
- [ ] Có implementation plan 6 tuần Step by Step.
- [ ] Mỗi step có owner, input, action, output và validation.
- [ ] Có data, temporal, leakage, model, business simulation và dashboard requirements.
- [ ] Có công thức EIM và định nghĩa của mọi parameter.
- [ ] Có ít nhất 3 scenarios.
- [ ] Có same-capacity policy comparison.
- [ ] Có artifact schemas và repository structure.
- [ ] Có acceptance criteria/Definition of Done.
- [ ] Có traceability matrix từ yêu cầu capstone đến validation evidence.
- [ ] Có decision log cho assumption chưa freeze.
- [ ] Đã đọc lại các output files sau khi ghi.
- [ ] Báo cáo rõ validation nào đã chạy và validation nào chưa thể chạy.
- [ ] Không có unsupported causal/ROI/uplift claim.

### Format báo cáo cuối của Agent

Trả lời ngắn gọn nhưng phải có:

1. Files đã tạo/cập nhật.
2. Tóm tắt nội dung từng file.
3. Các quyết định quan trọng đã chốt.
4. Các assumption còn TBD.
5. Các gap/blocker còn lại.
6. Validation đã thực hiện và evidence cụ thể.
7. Bước tiếp theo được đề xuất để bắt đầu implementation.

## END AGENT TASK
