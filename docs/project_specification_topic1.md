# Project Specification v1.0 — Topic 1

**Customer Value & Promotion Targeting for an Online Retailer**

| Metadata | Giá trị |
|---|---|
| Version | 1.0 (thay thế BA.pdf — Project Specification v0.1) |
| Trạng thái | Draft for team review — các mục `TBD` phải freeze theo `decision_log_topic1.md` |
| Team | 3 thành viên (M1 Data, M2 Modeling, M3 Decision/Dashboard) |
| Official duration | **6 tuần** (capstone, trang 1–2) |
| Primary dataset | UCI Machine Learning Repository — Online Retail II |
| Tài liệu đi kèm | `implementation_plan_topic1.md`, `decision_log_topic1.md`, `traceability_matrix_topic1.md`, `../project_config.example.yaml` |

**Quy ước nhãn thông tin** (dùng xuyên suốt tài liệu):

- `[FACT]` — lấy trực tiếp từ PDF capstone (`BA_Capstone_Topics_2026_MSc class (1).pdf`, gọi tắt **CAP**).
- `[DESIGN]` — thiết kế của nhóm (một phần kế thừa BA.pdf v0.1 hoặc BA (1).pdf).
- `[ASSUME]` — giả định phải kiểm chứng bằng EDA/business review trước khi freeze.
- `TBD` — chưa có giá trị; không được thay bằng số tự bịa.

---

## 0. Input sources và source traceability

### 0.1 File nguồn đã đọc

| File | Loại | Kích thước | Số trang | Trạng thái đọc | Vai trò |
|---|---|---|---|---|---|
| `BA_Capstone_Topics_2026_MSc class (1).pdf` | PDF | 207,744 bytes | 11 | Đọc được qua `pdftotext -layout` | **Source of truth** cho yêu cầu môn học |
| `BA.pdf` | PDF | 381,340 bytes | 27 | Đọc được; một số ký tự tiếng Việt bị lỗi font khi trích xuất, nội dung kỹ thuật đọc được | Project Specification v0.1 cần review |
| `BA (1).pdf` | PDF | 256,341 bytes | 14 | Đọc được; lỗi font tương tự | Phân chia công việc + plan 4 tuần |
| `Topic1_Spec_Review_and_Recommendation.md` | Markdown | ~29.8 KB | — | Đọc được | Review trước đó; đã đối chiếu lại với PDF |
| Trang dataset UCI (hyperlink trong CAP tr.3 và tr.11) | Web | — | — | Truy cập 2026-09-27 | Source metadata, license, schema documentation |

**Link dataset do capstone cite `[FACT]`:** hyperlink "UCI Online Retail II" ở CAP tr.3 (Topic 1) và tr.11 (Data Sources – Quick Reference) trỏ tới <https://archive.ics.uci.edu/dataset/502/online+retail+ii> (trích xuất bằng PyMuPDF và pypdf, hai thư viện cho cùng kết quả).

### 0.2 Yêu cầu capstone áp dụng cho Topic 1 `[FACT]`

| Mã | Yêu cầu | Nguồn |
|---|---|---|
| R01 | Team 3–4 sinh viên, project duration 6 tuần | CAP tr.1 |
| R02 | Bắt đầu từ business decision, không từ algorithm; recommendation truy vết được từ data → assumptions → analysis → validation | CAP tr.2 (Format & Expectations) |
| R03 | Reproducible code/notebook + README + run instructions | CAP tr.2 (Required Project Package) |
| R04 | Data dictionary + source log (source URL, download date, filters, joins, cleaning decisions) | CAP tr.2 |
| R05 | Executive brief tối đa 2 trang cho manager | CAP tr.2 |
| R06 | Interactive dashboard nhỏ, 3–5 decision KPIs + 1 actionable view | CAP tr.2 |
| R07 | Model/analysis card: target, features, validation, assumptions, risks, ethics/bias, limitations | CAP tr.2 |
| R08 | Định nghĩa unit of analysis, target, prediction horizon, business decision **trước** modeling | CAP tr.2 (Mandatory Rules) |
| R09 | Validation khớp data-generating process; temporal holdout/rolling; random split không đủ nếu gây leakage | CAP tr.2 |
| R10 | Chỉ dùng thông tin có tại decision time; xác định và loại target leakage | CAP tr.2 |
| R11 | Baseline bắt buộc; stretch chỉ sau baseline + validation + business interpretation | CAP tr.2 |
| R12 | Không claim causal uplift/ROI/cost savings; scenario phải nêu assumptions + sensitivity | CAP tr.2 |
| R13 | Quantify business impact bằng decision rule/budget/threshold/capacity/scenario | CAP tr.2 |
| R14 | Clean transactions, identify cancellations/returns, customer-level behavioral features | CAP tr.3 (Core Tasks) |
| R15 | RFM/cohort views + customer value segmentation | CAP tr.3 |
| R16 | Predict repeat purchase và/hoặc future value trên holdout horizon | CAP tr.3 |
| R17 | Promotion-targeting rule + simulate expected margin dưới response-rate và discount assumptions | CAP tr.3 |
| R18 | Baseline: RFM segmentation + 1 interpretable model | CAP tr.3 (Baseline) |
| R19 | Temporal holdout; features chỉ từ observation window | CAP tr.3 |
| R20 | Promotion scenario table ≥ 3 discount/response assumptions | CAP tr.3 |
| R21 | Metrics: PR-AUC/ROC-AUC + calibration; MAE/RMSE nếu future-value; expected incremental margin vs non-targeted | CAP tr.3 (Success Metrics) |
| R22 | Deliverables: notebook/pipeline + customer-level score table; executive brief; dashboard (segment size/value, retention risk, scenario outcomes) | CAP tr.3 |
| R23 | Guardrails: không report causal uplift / "revenue lift vs control"; promotion effect là assumption; không merge complaint datasets không liên quan | CAP tr.3 |
| R24 | Final Submission Checklist (10 mục) | CAP tr.11 |
| R25 | Xác minh lại source/terms khi bắt đầu; ghi access/download date | CAP tr.11 |

Stretch được phép `[FACT]` (CAP tr.3): gradient boosting + calibration + SHAP; budget-constrained optimization hoặc robust sensitivity; recommendation layer retain/nurture/no-offer.

### 0.3 Mâu thuẫn và cách xử lý

| # | Mâu thuẫn | Quyết định | Log |
|---|---|---|---|
| C1 | CAP: 6 tuần; BA.pdf/BA (1).pdf: 4 tuần | Official plan = 6 tuần. Plan 4 tuần cũ được giữ như *internal acceleration*: baseline-complete cuối Week 3 | D01 |
| C2 | BA v0.1 đề xuất 180/90 ngày như thiết kế nhóm (chính BA.pdf đã ghi không phải yêu cầu giảng viên) | Giữ là `[DESIGN]`, freeze sau EDA | D06 |
| C3 | BA v0.1 dùng ký hiệu `u` (response) và `v_i` (value) chưa định nghĩa đơn vị | Chuẩn hóa `δ_i` = assumed incremental lift, `V_i` = value của một order (AOV) | D09, D10 |
| C4 | BA v0.1 chưa quy định cadence/purge cho snapshot | Monthly cadence + purge ≥ horizon | D05, D07 |
| C5 | BA (1).pdf bảng workload bị vỡ khi trích xuất, không đọc được tỷ lệ chính xác | Dùng ownership theo mô tả chữ (Member 1/2/3) — không dựa vào bảng % | D17 |

### 0.4 Review BA.pdf và BA (1).pdf — tóm tắt

**Đạt (giữ lại):** business question đúng Topic 1; decision framing Decision–Options–Criteria; modeling unit `(customer, T0)`; RFM + Logistic Regression; không random split; 3 scenarios; Policy A/B/C/D; over-discounting được mô hình hóa; guardrails non-causal; DoD bao phủ checklist; phân chia 3 workstream với RACI và artifact interface.

**Gap (đã sửa trong v1.0):** duration; cadence/purge; định nghĩa `V_i`, `δ_i`; cùng capacity cho mọi policy; Frequency là distinct orders; fallback value không leakage; license/terms trong source log; class prevalence; ethics/bias trong model card (CAP R07 yêu cầu, BA v0.1 thiếu); final test chỉ dùng một lần; owner accountable cho từng artifact.

---

## 1. Business framing

### 1.1 Value proposition

Giúp CRM/marketing manager của một online retailer quyết định **ai nên nhận promotion** trong giới hạn ngân sách/năng lực campaign, để tăng expected future margin mà không lãng phí discount cho khách vốn sẽ tự mua lại.

### 1.2 Business context và pain point

Online retailer (UK-based, non-store — CAP tr.3) có tập khách rất khác nhau: mua thường xuyên giá trị cao; từng giá trị cao nhưng lâu chưa quay lại; mới hoặc không thường xuyên; và khách sẽ tự quay lại không cần incentive. Gửi promotion cho tất cả làm tăng chi phí discount và gây **over-discounting**. Câu hỏi thật không phải "ai sẽ mua?" mà "với ngân sách hữu hạn, ưu tiên ai để tạo expected incremental margin cao nhất dưới giả định minh bạch?".

### 1.3 Decision maker `[DESIGN]`

CRM/Marketing Manager, có campaign capacity `K` (số khách) hoặc budget `B` cho mỗi đợt.

### 1.4 Business question `[FACT]`

> Which customers should the retailer prioritize for retention or promotion to increase expected future margin without over-discounting?

### 1.5 Primary decision

Tại mỗi decision date `T0`: *với capacity `K`/budget `B` cố định, khách nào nhận offer (`TARGET`) và khách nào không (`DO_NOT_TARGET`)?*

### 1.6 Decision options

| Option | Mô tả |
|---|---|
| A — No promotion | Không gửi offer |
| B — Non-targeted | Gửi cho `K` khách chọn ngẫu nhiên trong eligible population |
| C — RFM targeting | Gửi cho top-`K` theo RFM score đã freeze |
| D — Model + value | Gửi cho top-`K` khách có `EIM_i > 0` cao nhất |

### 1.7 Decision criteria

| Criterion | Ý nghĩa | Nguồn trong pipeline |
|---|---|---|
| Expected future value | Giá trị kinh tế dự kiến của khách | `V_i`, `p_i` |
| Promotion cost / discount exposure | Discount + contact cost | `d`, `c` |
| Simulated expected incremental margin | Kết quả kinh doanh chính (mô phỏng) | `EIM_i` |
| Campaign capacity/budget | Ràng buộc | `K`, `B` |
| Technical predictive quality | Độ tin cậy của `p_i` | PR-AUC, ROC-AUC, calibration |
| Risk/limitations | Độ nhạy với giả định | Sensitivity grid |

### 1.8 North-star và decision KPIs

**North-star:** *Simulated Expected Incremental Margin* (tổng `EIM` của policy được chọn, dưới scenario đã nêu).

**Decision KPIs (đúng 5, CAP R06):**

| # | KPI | Công thức | Mục đích |
|---|---|---|---|
| K1 | Targeted customers | `count(recommended_action = TARGET)` | Quy mô campaign |
| K2 | Expected future value addressed | `Σ (p_i + δ_i) × V_i` trên targeted | Value được tác động (không phải realized revenue) |
| K3 | Expected promotion cost | `Σ [(p_i + δ_i) × V_i × d + c]` trên targeted | Discount/contact exposure |
| K4 | Simulated expected incremental margin | `Σ EIM_i` trên targeted | Outcome chính |
| K5 | Margin per targeted customer | `K4 / K1` | Hiệu quả targeting |

### 1.9 Business guardrails

- Không vượt `K`/`B`.
- Không target khách có `EIM_i ≤ 0`.
- Theo dõi *discount leakage share* = discount chi cho natural buyers / tổng discount (`Σ p_i V_i d / Σ (p_i+δ_i) V_i d`).
- Mọi parameter hiển thị công khai trong dashboard/brief.

### 1.10 Claim được phép / không được phép

| Được phép | Không được phép |
|---|---|
| "Simulated expected incremental margin under Base scenario is X (range Y–Z across scenarios)" | "Promotion increases revenue by X" |
| "Model-based targeting yields higher simulated margin than random targeting at the same capacity" | "Causal uplift", "ROI", "revenue lift vs control" |
| "Recency is associated with higher repeat probability" | "Recency causes repeat purchase" |
| "Assumed incremental lift δ = TBD" | Ẩn giá trị δ, d, m, c |

---

## 2. Scope, objectives, Definition of Done

### 2.1 Primary objective

Xây một reproducible customer analytics pipeline: (1) mô tả/phân khúc khách bằng RFM + cohort; (2) ước lượng repeat-purchase probability; (3) kết hợp probability + value + promotion assumptions; (4) tạo customer-level targeting score; (5) đề xuất policy trong capacity/budget; (6) so với non-targeted policy.

### 2.2 Secondary objectives (stretch — chỉ sau DoD MVP, CAP R11)

S1 Gradient boosting + calibration + SHAP. S2 Future-spend regression (MAE/RMSE trên holdout). S3 Robust sensitivity/profit curve theo nhiều capacity. S4 Recommendation layer retain / nurture / no-offer.

### 2.3 MVP bắt buộc

```text
Online Retail II → cleaning + cancellation/return treatment → customer snapshots
→ RFM / cohort / segmentation → repeat-purchase target → RFM benchmark
→ Logistic Regression → temporal holdout → calibration + capacity threshold analysis
→ customer value proxy → ≥3 promotion scenarios → same-capacity policy comparison
→ customer-level targeting table → dashboard 3–5 KPIs
→ README / data dictionary / source log / model card / executive brief
```

### 2.4 In scope

Online Retail II; transaction cleaning; cancellation/return handling; customer-ID coverage; customer snapshots; RFM; cohort; segmentation 4–6 nhóm; repeat-purchase classification; value proxy; temporal validation; targeting rule; scenario simulation; sensitivity; customer score table; decision dashboard; reproducible pipeline.

### 2.5 Out of scope

Production API/real-time system; deep learning; product recommender; personalized coupon optimization; external datasets không cần thiết (đặc biệt complaint datasets — CAP R23); causal uplift modeling; claim realized ROI/lift.

### 2.6 Assumptions `[ASSUME]`

A1 ~~Online Retail II tải được, terms cho phép dùng~~ → **đã xác minh 2026-09-27**: tải được, license CC BY 4.0. A2 Coverage 01/12/2009–09/12/2011 (theo UCI) cho 16 monthly snapshots với 180/90 ngày; phải xác nhận bằng InvoiceDate thực tế. A3 Có trường cho phép nhận diện cancellation/return. A4 Tỷ lệ missing Customer ID chấp nhận được cho phân tích customer-level. A5 Gross margin, discount, incremental lift, contact cost không có trong data → do nhóm giả định.

### 2.7 Dependencies

Truy cập UCI; môi trường Python (pandas, scikit-learn, matplotlib; dashboard: Streamlit **hoặc** Power BI/Tableau — D16); M2/M3 phụ thuộc artifact contract của M1 (§12).

### 2.8 Risks và mitigation

| Risk | Hậu quả | Mitigation | Owner |
|---|---|---|---|
| Return/cancellation xử lý sai | Thổi phồng RFM/value | Canonical rule + reconciliation trước/sau | M1 |
| Temporal leakage | Metric ảo | Feature `< T0`, purge, leakage audit tự động | M2 |
| Seasonality (Q4 bán lẻ) | Generalize kém | Cohort/time error analysis, nhiều snapshot | M2 |
| Missing Customer ID | Population bias | Report coverage, mô tả bias trong model card | M1 |
| Class imbalance | Accuracy gây hiểu lầm | PR-AUC, prevalence, top-K | M2 |
| Promotion effect không quan sát được | Kết luận sai | Scenario + sensitivity, ngôn ngữ non-causal | M3 |
| Over-scope | Không kịp | MVP trước, stretch sau checkpoint Week 3 | Cả nhóm |
| Over-discounting | Mất margin | EIM phạt discount trên natural buyers | M3 |
| Schema drift giữa workstreams | Kết quả không khớp | Artifact contract + version field | Cả nhóm |

### 2.9 Definition of Done — xem §15.

---

## 3. Data source và data understanding

### 3.1 Source log (đã xác minh 2026-09-27)

| Field | Giá trị | Nguồn xác minh |
|---|---|---|
| `source_name` | UCI Machine Learning Repository — Online Retail II | Trang UCI |
| `source_url` | <https://archive.ics.uci.edu/dataset/502/online+retail+ii> | Hyperlink trong CAP tr.3, tr.11 |
| `download_url` | <https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip> | Nút Download trên trang UCI |
| `alt_access` | `ucimlrepo`: `fetch_ucirepo(id=502)` | Trang UCI |
| `doi` / citation | 10.24432/C5CG6D — Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository | Trang UCI |
| `donated` | 2019-09-20 | Trang UCI |
| `license_or_terms` | Creative Commons Attribution 4.0 International (CC BY 4.0): được chia sẻ và chỉnh sửa, chỉ cần ghi nguồn đúng | Trang UCI |
| `coverage_period` | 01/12/2009 – 09/12/2011 (UK-based, registered non-store online retailer; nhiều khách là wholesaler) | Trang UCI |
| `instances` | 1,067,371 | Trang UCI |
| `raw_filename` | `online_retail_II.xlsx` (43.5 MB) trong `online_retail_ii.zip` | Trang UCI + file đã tải |
| `access_download_datetime` | 2026-09-27 (+07:00) — lần tải kiểm chứng | Lệnh tải |
| `sha256_zip` | `572E36277C2390FBFDE10664750731E0A86F55E33470D91919085F0408E67BFB` (45,622,418 bytes) | `Get-FileHash` |
| `sha256_xlsx` | `BCBE73B35F5B7BABF197FB0CB983A11F5D9FF929078D4AA53D171B1F2DF2E980` (45,622,278 bytes) | `Get-FileHash` |
| `sheets_or_parts` | `TBD` — xác minh ở T1.3 (thường chia theo giai đoạn năm; phải kiểm tra overlap giữa các sheet) | Chưa profiling |
| `filters` | Ghi mọi filter, kèm số dòng trước/sau | T2.1 |
| `joins` | MVP: không join external data | Thiết kế |
| `cleaning_decisions` | Tham chiếu `CR-xx` trong §4 | T2.1 |

Nếu tải lại cho checksum khác, phải ghi version mới vào log, không ghi đè.

### 3.2 Raw-data unit và expected fields `[ASSUME]`

Raw unit: một **transaction line** (một sản phẩm trong một invoice). Trang UCI mô tả 8 biến `[FACT]`:

| Biến (theo trang UCI) | Mô tả UCI |
|---|---|
| InvoiceNo | Mã invoice 6 chữ số; **bắt đầu bằng chữ "c" là cancellation** |
| StockCode | Mã sản phẩm 5 chữ số |
| Description | Tên sản phẩm |
| Quantity | Số lượng mỗi sản phẩm trong giao dịch |
| InvoiceDate | Ngày giờ giao dịch |
| UnitPrice | Đơn giá, đơn vị sterling (£) |
| CustomerID | Mã khách hàng 5 chữ số |
| Country | Quốc gia của khách |

`[ASSUME]` Tên cột trong file Excel có thể khác tên trên trang (ví dụ `Invoice`, `Price`, `Customer ID`), và có mã StockCode không phải 5 chữ số (phí, bưu phí, điều chỉnh). Trang UCI có "Has Missing Values? Yes" nhưng bảng biến lại ghi "no" cho mọi dòng, nên missingness phải đo trực tiếp. Tên cột chính xác chỉ được ghi vào data dictionary sau T1.3 (profiling).

### 3.3 Data dictionary template

| field_name | data_type | meaning | allowed_values | missing_rate | cleaning_rule | leakage_risk | downstream_use |
|---|---|---|---|---|---|---|---|
| `TBD` | `TBD` | `TBD` | `TBD` | `TBD` | `CR-xx` | none / post-T0 / target | feature / key / target / excluded |

Data dictionary gồm hai phần: (a) raw fields; (b) derived fields (net_value, is_cancellation, is_return, order_id, features RFM, target).

### 3.4 Initial profiling checklist

Row count (theo sheet/năm) · date range · unique customers · unique invoices · missing Customer ID (dòng và % revenue) · duplicate rows exact · invalid quantity (0, âm) · invalid price (0, âm) · invalid/missing date · cancellation prevalence · return prevalence · transaction volume theo tháng · phân phối line value (outliers) · số dòng/invoice · country distribution · overlap giữa các sheet (nếu có).

### 3.5 Data-quality report format

`outputs/data_quality_report.md` (+ CSV): mỗi check có `check_id, description, metric, value, threshold, status(PASS/WARN/FAIL), action`.

### 3.6 Reproducible acquisition

`src/data/download.py` (hoặc notebook 01) tải từ `source_url` trong config, tính SHA-256, so với giá trị đã log; fail nếu khác mà không có ghi chú version mới.

### 3.7 Raw-data commit policy

Mặc định **không commit raw data** vào repo (`data/raw/` trong `.gitignore`); README hướng dẫn tải + checksum. Nếu license cho phép và kích thước hợp lý, có thể commit — ghi quyết định vào D03.

---

## 4. Canonical transaction cleaning contract

Mọi rule có mã `CR-xx`, phải được xác nhận bằng EDA (T1.2–T2.1) trước khi freeze. Ghi số dòng/khách/revenue trước và sau mỗi rule.

| Rule | Nội dung đề xuất `[DESIGN]` | Cần xác nhận |
|---|---|---|
| CR-01 Cancellation | Invoice code bắt đầu bằng "C"/"c" là cancellation (theo documentation UCI) | Kiểm tra trên data: mọi dòng invoice "C" có quantity âm không; có prefix chữ khác không (ví dụ adjustment) |
| CR-02 Return | Dòng quantity âm không phải cancellation toàn invoice được coi là return; giữ lại để tính net value và `return_rate` | Có phân biệt được cancellation vs return không; nếu không → gộp "negative adjustments" và ghi limitation |
| CR-03 Line value | `line_value = quantity × unit_price`; `net_value` = tổng có dấu | Đơn vị tiền tệ |
| CR-04 Quantity | Quantity = 0 → loại; âm → theo CR-01/02 | |
| CR-05 Price | Price ≤ 0 → loại khỏi purchase events, log riêng (có thể là adjustment/fee) | Có mã non-product (postage, fee, manual…)? → quyết định giữ/loại (D04) |
| CR-06 Missing Customer ID | Loại khỏi customer-level dataset; **không suy diễn danh tính**; report % dòng, % revenue | |
| CR-07 Duplicates | Exact duplicate rows → giữ 1, log số lượng | Duplicate giữa các sheet năm |
| CR-08 Dates | Missing/invalid datetime → loại; kiểm tra timezone/format | |
| CR-09 Order unit | `order_id` = invoice identifier; một order = tập dòng cùng invoice | |
| CR-10 Valid purchase event | Order có customer ID hợp lệ, không phải cancellation, tổng net value > 0 sau khi áp CR-02..08 | |
| CR-11 Extreme values | Không xóa mặc định; flag top 0.1% line value; phân tích ảnh hưởng; winsorize **chỉ feature** nếu cần, cutoff fit trên train | |
| CR-12 Temporal safety | Cleaning chỉ là rule theo dòng (row-wise), không dùng aggregate toàn dataset → không leakage. Mọi aggregate (quantile, median) nằm ở bước feature/modeling và fit trên train | |

Nguyên tắc: Frequency = **distinct valid orders**; Monetary = net value trong observation window (purchases − returns); `AOV = Monetary / Frequency` khi Frequency > 0. Không âm thầm xóa return (return behavior là feature).

---

## 5. Analytical unit, temporal design, target

| Mục | Định nghĩa |
|---|---|
| Raw unit | Transaction line |
| Modeling unit | `(customer_id, T0)` — customer snapshot tại decision date |
| Snapshot cadence `[DESIGN]` | Monthly, `T0` = ngày đầu tháng (00:00) |
| Observation window `[DESIGN]` | `[T0 − 180d, T0)` |
| Outcome window `[DESIGN]` | `[T0, T0 + 90d)` |
| Eligible population | Customer ID hợp lệ **và** ≥ 1 valid purchase trong observation window |
| Target | `repeat_purchase_90d = 1` nếu ≥ 1 valid purchase trong outcome window, ngược lại 0 |

**Valid T0 range:** `T0_min ≥ data_start + 180d`; `T0_max + 90d ≤ data_end`. Dùng coverage period trên trang UCI (01/12/2009 – 09/12/2011):

- `data_start + 180d` = 2010-05-30 → T0 đầu tiên là **2010-06-01**
- `data_end − 90d` = 2011-09-10 → T0 cuối cùng là **2011-09-01**
- Như vậy có **16 monthly snapshots** (2010-06-01 … 2011-09-01). Con số này phải được xác nhận lại bằng min/max `InvoiceDate` thực tế ở T1.3.

Đề xuất split `[DESIGN]` (freeze tại D07, sau T1.3):

| Split | T0 | Số snapshot | Kiểm tra purge 90 ngày |
|---|---|---|---|
| Train | 2010-06-01 … 2011-01-01 | 8 | Snapshot train cuối + 90d = 2011-04-01 |
| (purge) | 2011-02-01, 2011-03-01 | 2 bị bỏ | — |
| Validation | 2011-04-01, 2011-05-01 | 2 | Snapshot val cuối + 90d = 2011-07-30 |
| (purge) | 2011-06-01, 2011-07-01 | 2 bị bỏ | — |
| Test | 2011-08-01, 2011-09-01 | 2 | Outcome kết thúc 2011-11-30 ≤ 2011-12-09 |

Lưu ý seasonality: outcome window của test rơi vào Q4 (mùa cao điểm quà tặng), nên prevalence của test có thể cao hơn của train. Phải báo cáo prevalence theo từng snapshot và nêu điểm này trong model card.

**Snapshot generation algorithm:**

```text
for T0 in monthly_dates(T0_min, T0_max):
    hist = valid_txn[ts < T0 and ts >= T0 - 180d]
    fut  = valid_orders[ts >= T0 and ts < T0 + 90d]
    eligible = customers with ≥1 valid order in hist
    features = aggregate(hist)            # chỉ hist
    target   = eligible ∈ customers(fut)
    assert max(hist.ts) < T0 <= min(fut.ts)
    write rows (customer_id, T0, features, target, feature_version)
```

Một khách xuất hiện ở nhiều snapshot là chủ ý (mô phỏng deployment hàng tháng). Report theo từng snapshot: eligible count, positive prevalence, % khách mới.

Tên target gắn với horizon; nếu đổi horizon (D06) → đổi tên (`repeat_purchase_60d`…) và cập nhật mọi artifact.

---

## 6. Temporal train / validation / test

`[DESIGN]` (exact dates freeze tại D07, trước khi train final model):

| Split | Snapshots | Dùng cho |
|---|---|---|
| Train | Các `T0` sớm nhất | Fit preprocessing, RFM cutoffs, fallback, model |
| Validation | `T0` kế tiếp, sau purge | Chọn hyperparameter (C của LR), calibration method, capacity threshold |
| Test | `T0` muộn nhất có outcome đầy đủ | Report **một lần** ở cuối |

**Purge/embargo:** snapshot cuối cùng của train phải có `T0_train_last + 90d ≤ T0_val_first` (outcome window của train không chồng lên thời điểm quyết định của validation); tương tự giữa validation và test. Với monthly cadence và horizon 90 ngày ⇒ bỏ khoảng 2 snapshot ở mỗi ranh giới.

**Tại sao không random split:** cùng một khách xuất hiện ở nhiều snapshot có feature gần như giống nhau; random split đặt snapshot tương lai vào train → model học hành vi tương lai → metric ảo, không phản ánh deployment (CAP R09).

**Rolling backtest (khuyến nghị nếu còn thời gian):** expanding window 2–3 fold trên train+validation để kiểm tra độ ổn định metric.

**Leak audit checklist (tự động hóa trong `tests/test_leakage.py`):**

1. `max(feature_source_ts) < T0` cho mọi snapshot.
2. Target chỉ dùng orders trong `[T0, T0+90d)`.
3. Không có cột post-T0 trong feature matrix (whitelist feature).
4. Scaler/imputer/quantile cutoffs fit chỉ trên train (kiểm tra object fit trong pipeline).
5. Split dates tăng dần và purge đúng.
6. Test set không được đọc trước bước final report (log timestamp lần đọc).

---

## 7. Features, RFM, cohort, segmentation

### 7.1 Feature specification

| Feature | Công thức (trên observation window, `< T0`) | Type | Bắt buộc |
|---|---|---|---|
| `recency_days` | `T0 − last_valid_order_ts` (ngày) | int | Có |
| `frequency_orders` | `count distinct valid order_id` | int | Có |
| `monetary_net` | `Σ net_value` (purchase − return) | float | Có |
| `aov` | `monetary_net / frequency_orders` | float | Có (dùng cho `V_i`) |
| `tenure_days` | `T0 − first_valid_order_ts` (toàn bộ lịch sử `< T0`) | int | Tùy chọn |
| `active_months` | số tháng có ≥1 order | int | Tùy chọn |
| `avg_interpurchase_days` | trung bình khoảng cách giữa các order; NaN nếu 1 order | float | Tùy chọn |
| `return_rate` | `|return value| / gross purchase value` | float | Tùy chọn |
| `unique_products` | distinct product codes | int | Tùy chọn |
| `total_quantity` | Σ quantity dương | int | Tùy chọn |
| `orders_last_30d` | orders trong `[T0−30d, T0)` | int | Tùy chọn |

Missing/fallback: `avg_interpurchase_days` NaN → impute bằng median train + cờ `single_order_flag`. Giá trị lệch (monetary, aov) → `log1p` trong pipeline LR. `feature_version` tăng mỗi khi đổi công thức.

### 7.2 Cohort

`cohort_month` = tháng của first valid order (trong toàn bộ lịch sử có sẵn). Lưu ý: khách có order đầu tiên sát `data_start` bị *left-censored* — ghi limitation. Metrics: cohort size, retention theo tháng thứ k, repeat rate, AOV theo cohort. Output: cohort retention heatmap + `cohort_summary.csv`. Cohort là descriptive; nếu dùng làm feature thì chỉ dùng thông tin `< T0`.

### 7.3 RFM scoring và segmentation

R, F, M → quintile score 1–5 (R đảo chiều). **Cutoffs fit trên train snapshots, freeze** vào `project_config` rồi áp cho validation/test. Frequency có nhiều giá trị trùng → dùng rank-based quantile hoặc cutoffs cố định; ghi phương pháp.

Segments `[DESIGN]` (5 nhóm, rule cụ thể freeze sau EDA — D12):

| Segment | Rule khởi tạo | Hành động gợi ý |
|---|---|---|
| High-value active | R ≥ 4, F ≥ 4, M ≥ 4 | Thường tự mua → cẩn trọng discount |
| High-value at risk | R ≤ 2, M ≥ 4 | Ứng viên retention |
| Developing | R ≥ 3, F 2–3 | Nurture |
| Low-value active | R ≥ 3, M ≤ 2 | Offer chi phí thấp |
| Dormant | R ≤ 2, F ≤ 2 | Thường không target |

Kiểm tra stability: tỷ trọng segment và repeat rate theo segment qua các snapshot.

---

## 8. Predictive modeling

| Mục | Spec |
|---|---|
| Target | `repeat_purchase_90d` |
| Benchmark | `rfm_score` (tổng R+F+M hoặc ranking RFM) dùng làm score; cùng metrics |
| Baseline | Logistic Regression (L2), `class_weight` so sánh None vs balanced trên validation |
| Preprocessing | `Pipeline([log1p cho skewed, SimpleImputer(median), StandardScaler, LR])`; fit chỉ trên train |
| Hyperparameter | `C` ∈ grid log-scale, chọn theo PR-AUC validation |
| Calibration | Reliability plot + Brier trên validation; nếu lệch → `CalibratedClassifierCV` (sigmoid/isotonic) fit trên validation, report test |
| Seed | `random_seed` trong config |
| Artifact | `outputs/model/model_v{n}.joblib` + `model_metadata.json` (features, C, train dates, metrics) |
| Explainability | Hệ số chuẩn hóa + odds ratio; SHAP chỉ với stretch model |
| Hypotheses | H1 recency ↔ repeat; H2 frequency/value ↔ repeat; H3 khách `p_i` rất cao là target kém (discount leakage); H4 model+value > non-targeted ở cùng capacity (simulation only) |

**Metrics bắt buộc:** PR-AUC (so với prevalence baseline), ROC-AUC, Brier score, reliability plot (10 bins), precision/recall tại top-K cho K ∈ {5%, 10%, 20%} eligible, positive prevalence theo snapshot, error analysis theo segment/cohort/snapshot. Accuracy **không** là metric chính.

**Advanced model (stretch):** chỉ sau DoD MVP; phải so công bằng với LR trên cùng split; nếu không cải thiện PR-AUC/calibration/EIM thì LR vẫn là model được recommend.

---

## 9. Customer value và promotion simulation

### 9.1 Notation

| Ký hiệu | Ý nghĩa | Nguồn |
|---|---|---|
| `p_i` | Predicted natural repeat probability (không offer) trong outcome window | Model (calibrated) |
| `V_i` | Expected net value của **một** order = `aov_i` | Feature; fallback = median AOV của segment tính trên **train** |
| `m` | Gross-margin rate, `0 ≤ m ≤ 1` | `[ASSUME]` `TBD` |
| `d` | Discount rate của offer, `0 ≤ d < m` | Scenario |
| `δ_i` | Assumed incremental probability lift do offer, `0 ≤ δ_i ≤ 1 − p_i` | Scenario — **không phải causal estimate** |
| `c` | Contact/campaign cost trên mỗi khách được target | `[ASSUME]` |
| `K` / `B` | Capacity / budget | Scenario/dashboard input |

MVP: `δ_i = min(δ, 1 − p_i)` với `δ` là hằng số theo scenario (có thể mở rộng theo segment ở sensitivity).

### 9.2 Công thức

```text
M0_i  = p_i × V_i × m                                  # không offer
M1_i  = (p_i + δ_i) × V_i × (m − d) − c                # có offer
EIM_i = M1_i − M0_i
      = δ_i × V_i × m  −  (p_i + δ_i) × V_i × d  −  c
Cost_i = (p_i + δ_i) × V_i × d + c
```

Diễn giải: khoản `p_i × V_i × d` là discount trao cho khách vốn sẽ tự mua → phạt over-discounting (H3). Giả định MVP: discount chỉ phát sinh khi khách mua; một order trong horizon (bảo thủ — ghi limitation). Unit test phải kiểm tra `EIM_i == M1_i − M0_i`.

### 9.3 Scenarios (≥ 3, CAP R20)

Giá trị cụ thể `TBD` tới D10/D11; phải là giá trị hiển thị, không hidden constants.

| Scenario | `d` | `δ` | `m` | `c` | Mục đích |
|---|---|---|---|---|---|
| Conservative | thấp `TBD` | thấp `TBD` | `TBD` | `TBD` | Downside |
| Base | trung bình `TBD` | trung bình `TBD` | `TBD` | `TBD` | Planning |
| Aggressive | cao `TBD` | cao `TBD` | `TBD` | `TBD` | Upside / high cost |

Sensitivity grid: `d × δ × K` (tối thiểu), thêm `m`, `c` nếu kịp. Output: heatmap EIM và vùng tham số làm `EIM` của Policy D ≤ Policy B (break-even).

Mỗi scenario có `scenario_version`, owner (M3), nguồn lý do chọn giá trị (ví dụ benchmark ngành trích dẫn được, hoặc "team assumption").

---

## 10. Targeting policy và policy comparison

**Policy D algorithm:**

```text
for scenario s, snapshot T0 (test):
    compute p_i, V_i, δ_i, EIM_i
    candidates = {i : EIM_i > 0}
    rank candidates by EIM_i desc
    select while count < K and Σ Cost_i ≤ B
    action = TARGET if selected else DO_NOT_TARGET
```

**So sánh công bằng:** cùng eligible population, cùng test snapshot(s), cùng scenario, cùng `K`/`B`, cùng định nghĩa value/cost, cùng metric.

| Policy | Chọn | Ghi chú |
|---|---|---|
| A | ∅ | EIM = 0, cost = 0 (mốc tham chiếu) |
| B | Random K | 100 seeds (seed list trong config); report mean, P5–P95 |
| C | Top-K theo RFM score | Không lọc EIM |
| D | Top positive EIM ≤ K | Có thể target < K nếu ít khách có EIM > 0 — report rõ |

**Business metrics per policy:** total EIM (K4), EIM/target (K5), expected cost (K3), target count (K1), value addressed (K2), discount leakage share, top-K capture của actual repeaters (dùng outcome test — chỉ để đánh giá, không dùng để chọn).

**Kết luận chỉ được rút ra** nếu D > B và D ≥ C ổn định trên phần lớn sensitivity grid; nếu không, report trung thực.

---

## 11. Dashboard và executive communication

**Công cụ:** `TBD` (D16) — Streamlit (khuyến nghị: tái lập từ code) hoặc Power BI/Tableau đọc CSV outputs.

**Views:**

1. **Overview** — customer count, segment size/value, RFM distribution, repeat-risk profile (CAP R22: segment size/value, retention risk).
2. **Promotion Scenario** — input: scenario, `d`, `δ`, `K`/`B`; output: 5 KPIs, policy comparison A–D, sensitivity heatmap.
3. **Actionable Customer/Segment View** — scatter `p_i` × `V_i` tô màu theo action; bảng lọc được: `customer_id, segment, p, V, cost, EIM, rank, recommended_action`; export CSV.

Banner cố định: *"Results are scenario-based simulations under stated assumptions. Online Retail II contains no promotion treatment/control; figures are not causal uplift or ROI."*

**Executive brief (≤ 2 trang):** (1) Recommendation: target ai, rule gì; (2) expected simulated impact + range qua scenarios; (3) campaign size/cost; (4) 3 assumptions quan trọng nhất; (5) risks & limitations; (6) next step: A/B test thật để đo δ.

---

## 12. Artifact contracts và repository structure

### 12.1 Repository

```text
README.md
project_config.yaml            # từ project_config.example.yaml
requirements.txt               # pinned versions
data/raw/ (gitignored)  data/processed/
docs/  project_specification_topic1.md  implementation_plan_topic1.md
       decision_log_topic1.md  traceability_matrix_topic1.md
       data_dictionary.md  source_log.md  model_analysis_card.md  executive_brief.md
src/   data/ features/ models/ decision/     # hàm dùng chung, notebooks gọi vào
notebooks/ 01_data_understanding … 09_sensitivity_analysis
tests/ test_cleaning.py test_leakage.py test_simulation.py test_contracts.py
outputs/ (tables, figures, model/)
dashboard/
```

### 12.2 Schemas

**`customer_snapshots`** (producer M1 → M2, M3) — key `(customer_id, decision_date)`

```text
customer_id:str, decision_date:date, recency_days:int, frequency_orders:int,
monetary_net:float, aov:float, tenure_days:int, return_rate:float,
[optional features], r_score:int, f_score:int, m_score:int, rfm_score:int,
customer_segment:str, cohort_month:str, repeat_purchase_90d:int, feature_version:str
```

**`customer_predictions`** (M2 → M3)

```text
customer_id, decision_date, split{train,val,test}, actual_repeat_purchase:int,
predicted_repeat_probability:float, model_version, feature_version
```

**`scenario_results`** (M3)

```text
scenario, scenario_version, policy{A,B,C,D}, decision_date, capacity_k, budget_b,
target_count, expected_future_value, expected_promotion_cost, simulated_eim,
eim_per_target, discount_leakage_share, seed(nullable), n_seeds(nullable)
```

**`policy_comparison`** (M3) — aggregate của `scenario_results` theo scenario × policy × K: mean, p5, p95.

**`sensitivity_results`** (M3)

```text
scenario_version, discount_rate, incremental_lift, gross_margin, contact_cost,
capacity_k, policy, simulated_eim, eim_per_target, target_count
```

**`customer_targeting_table`** (M3 → dashboard, brief) — deliverable "customer-level score table" (CAP R22)

```text
customer_id, decision_date, scenario, policy, customer_segment, recency_days,
frequency_orders, monetary_net, rfm_score, repeat_purchase_probability,
customer_value_proxy, discount_rate, incremental_lift_assumption,
expected_promotion_cost, simulated_expected_incremental_margin, target_rank,
recommended_action{TARGET,DO_NOT_TARGET}, model_version, scenario_version
```

**Quy tắc single source of truth:** M2 không tính lại Monetary; M3 không train lại model; mọi sửa logic phải sửa tại producer và bump version. `tests/test_contracts.py` kiểm tra cột, dtype, key unique, không null ở cột bắt buộc.

---

## 13. Model/analysis card (template)

Target · Unit · Decision time · Population & coverage (missing-ID %) · Features · Train/val/test dates + purge · Metrics (PR-AUC, ROC-AUC, Brier, top-K; business EIM theo scenario) · Assumptions (m, d, δ, c, K) · **Ethics/bias** (population chỉ gồm khách có ID → bias; phân bố theo country; rủi ro loại trừ khách giá trị thấp khỏi ưu đãi; không dùng thuộc tính nhạy cảm) · Risks (seasonality, returns, value proxy, promotion effect không quan sát) · Limitations (observational, không randomized treatment, kết quả không causal, left-censoring cohort, một order/horizon).

---

## 14. Validation và QA requirements

| Lớp | Check | Công cụ/evidence |
|---|---|---|
| Data | schema, rows, date range, missing, duplicates, ID coverage, cancel/return count, invalid values, reconciliation trước/sau | `data_quality_report`, `test_cleaning.py` |
| Temporal/leakage | 6 check §6 | `test_leakage.py` |
| Model | baseline tồn tại; pipeline rerun; PR/ROC-AUC; calibration; prevalence; top-K; metrics theo segment/cohort/time | `model_metrics.csv`, figures |
| Decision | parameters visible; `EIM = M1 − M0`; không target EIM ≤ 0; không vượt K/B; cùng population & K; random baseline tái lập; sensitivity chạy | `test_simulation.py`, `scenario_results` |
| Communication | 3–5 KPIs; actionable view; brief ≤ 2 trang; banner non-causal; grep report không có "ROI"/"uplift"/"caused" ngoài ngữ cảnh phủ định | dashboard screenshot, `claim_audit` |
| Reproducibility | Clean env → `pip install -r requirements.txt` → chạy pipeline theo README → tái tạo bảng/metrics chính (sai số 0 với seed cố định) | Rerun log Week 6 |

---

## 15. Definition of Done / acceptance checklist

Baseline-complete (cuối Week 3) cần mục 1–13; final (Week 6) cần tất cả.

1. [ ] Business question, decision maker, decision rule, guardrails viết rõ (§1).
2. [ ] Source URL, download date, version/checksum, license/terms ghi trong `source_log.md`.
3. [ ] Raw unit, modeling unit, T0, windows, eligible population ghi (§5).
4. [ ] Missing-ID rate, coverage, data-quality report xuất ra.
5. [ ] CR-01…CR-12 được xác nhận và ghi trong data dictionary.
6. [ ] Frequency = distinct valid orders; Monetary/AOV canonical.
7. [ ] Snapshots chỉ dùng dữ liệu `< T0`; `test_leakage.py` pass.
8. [ ] Cadence, split dates, purge lưu trong config.
9. [ ] RFM, cohort view, 4–6 segments tái lập; cutoffs fit trên train.
10. [ ] Target executable, không dùng post-outcome data.
11. [ ] RFM benchmark + Logistic Regression hoàn tất.
12. [ ] Preprocessing fit trên train only.
13. [ ] PR-AUC, ROC-AUC, Brier/reliability, top-K report trên validation.
14. [ ] Error analysis theo segment/cohort/time.
15. [ ] `V_i, m, d, δ, c, K/B` và công thức EIM công khai; `test_simulation.py` pass.
16. [ ] ≥ 3 scenarios + sensitivity grid.
17. [ ] Policy A/B/C/D so sánh ở cùng population và capacity; B có ≥ 100 seeds.
18. [ ] `customer_targeting_table` đúng schema, `test_contracts.py` pass.
19. [ ] Dashboard 3–5 KPIs + actionable view + banner non-causal.
20. [ ] Executive brief ≤ 2 trang.
21. [ ] Model/analysis card đủ mục, gồm ethics/bias.
22. [ ] Test metrics report một lần; README rerun thành công từ môi trường sạch.
23. [ ] Claim audit: không causal uplift/ROI/revenue-lift-vs-control.
