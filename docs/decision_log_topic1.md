# Decision Log — Topic 1

**Status values:** `Fact` (từ capstone, không cần quyết định) · `Decided` (đã chốt ở mức spec) · `Proposed` (đề xuất, chờ evidence) · `Open` (chưa có đề xuất đủ căn cứ)  
**Due** tính theo tuần/ngày của `implementation_plan_topic1.md` (W1 D5 = cuối Week 1).  
**Quy tắc:** mọi thay đổi sau khi `Decided`/`Frozen` phải thêm dòng mới (không sửa đè), ghi lý do và bump version liên quan.

## 1. Facts từ capstone (không thay đổi)

| ID | Fact | Nguồn |
|---|---|---|
| F01 | Topic 1 = Customer Value & Promotion Targeting for an Online Retailer | CAP tr.3 |
| F02 | Dataset chính: UCI Online Retail II, ~2 năm giao dịch, UK-based non-store retailer | CAP tr.3 |
| F03 | Team 3–4, duration 6 tuần | CAP tr.1 |
| F04 | Baseline: RFM segmentation + 1 interpretable model; temporal holdout; ≥ 3 scenarios | CAP tr.3 |
| F05 | Metrics: PR-AUC/ROC-AUC + calibration; business metric so với non-targeted | CAP tr.3 |
| F06 | Không causal uplift / revenue lift vs control; promotion effect là assumption | CAP tr.2–3 |
| F07 | Package: code+README, data dictionary+source log, brief ≤ 2 trang, dashboard 3–5 KPIs, model/analysis card | CAP tr.2 |
| F08 | Phải xác minh lại source/terms và ghi download date khi bắt đầu | CAP tr.11 |

## 2. Decisions

| ID | Chủ đề | Quyết định / đề xuất | Status | Evidence cần | Impact nếu chưa quyết | Owner | Due |
|---|---|---|---|---|---|---|---|
| D01 | Duration | Official 6 tuần; plan 4 tuần cũ thành internal acceleration, G3 baseline cuối W3 | Decided | CAP tr.1 | Lệch với yêu cầu chấm | ALL | W1 D1 |
| D02 | Source & license | URL <https://archive.ics.uci.edu/dataset/502/online+retail+ii> (CAP cite tr.3, tr.11); DOI 10.24432/C5CG6D; CC BY 4.0; SHA-256 ghi ở SPEC §3.1 | Decided (verified 2026-09-27) | Trang UCI + checksum | — | M1 | Done |
| D03 | Commit raw data | CC BY 4.0 cho phép chia sẻ kèm ghi nguồn, nhưng file 43.5 MB → mặc định không commit; README ghi link, lệnh tải, checksum | Decided 2026-09-27 (CC BY 4.0 cho phép, nhưng 43 MB; tải lại bằng README + checksum) | Chính sách repo của nhóm | Repo nặng | M1 | W1 D3 |
| D04 | Non-product codes | Danh sách + pattern trong `data_profile_topic1.md` §4 và `cleaning.non_product_*` trong config; loại khỏi purchase events, tính riêng | Decided (profiling 2026-09-27) | 62 mã đặc biệt đã rà | — | M1 | Done |
| D05 | Snapshot cadence | Monthly, T0 = ngày 1 mỗi tháng | Decided 2026-09-27 (16 T0 trên data thật) | Số snapshot hợp lệ | Không build được split | M2 | W2 D3 |
| D06 | Observation / outcome window | 180d / 90d (thiết kế nhóm, không phải yêu cầu GV) | Decided 2026-09-27 (prevalence 0.38-0.62, đủ cân bằng) | Date range, prevalence, seasonality | Target không ổn định | M2 | W2 D3 |
| D07 | Split dates & purge | Train 2010-06→2011-01 (8), Val 2011-04, 2011-05, Test 2011-08, 2011-09; purge 2 snapshot mỗi ranh giới (SPEC §5) | Decided 2026-09-27 (train 23,987 / val 6,346 / test 5,534) | Min/max InvoiceDate thực tế (T1.3) | Leakage / metric ảo | M2 | W2 D5 |
| D08 | Calibration method | **Decided:** Platt/sigmoid trên validation (`model.calibration: sigmoid`); isotonic chỉ là sensitivity (validation ~6.3k dòng, isotonic dễ overfit) | Decided 2026-09-27 | Reliability before/after ở T4.1 | — | M2 | Done |
| D09 | Value unit `V_i` | `V_i = AOV_i`; fallback median AOV theo segment tính trên train | Decided | — (logic) | Over/understate value | M3 | W2 D5 |
| D10 | Incremental lift `δ` | **Decided:** Conservative 0.02 · Base 0.05 · Aggressive 0.10 (điểm phần trăm tuyệt đối); grid 0.02–0.20; cap `1 − p_i` | Decided 2026-09-27 (§2b) | Benchmark §2b | — | M3 | Done |
| D11 | `m`, `d`, `c`, `K`/`B` | **Decided:** m = 0.40 (grid 0.30/0.40/0.50); d = 0.05 / 0.10 / 0.20; c = £0.10/khách (email, chi phí đầy đủ; grid 0.01/0.10/0.50); K = 5/10/20% eligible; budget null | Decided 2026-09-27 (§2b) | Benchmark §2b + data AOV | — | M3 | Done |
| D12 | RFM cutoffs & segments | Quintile fit trên train; 5 segments theo SPEC §7.3 | Decided 2026-09-27 (rule trong config + test_rfm) | Phân phối RFM | Segment không ổn định | M1 | W3 D2 |
| D13 | Random baseline | 100 seeds, list seed trong config | Decided | — | So sánh không tái lập | M3 | W2 D5 |
| D14 | Class imbalance | **Decided:** không re-weight (`class_weight_options: [null]`); prevalence 0.38–0.62, balancing làm lệch xác suất cần cho EIM | Decided 2026-09-27 | data profile §5 | — | M2 | Done |
| D15 | KPIs | 5 KPIs SPEC §1.8 | Decided | — | Dashboard lan man | M3 | W1 D5 |
| D16 | Dashboard tool | **Decided:** Streamlit 1.64.0 trong Docker (`docker compose up dashboard`, chỉ bind 127.0.0.1) — tái lập từ code, không cần license BI | Decided 2026-09-27 | Health check HTTP 200 | — | M3 | Done |
| D17 | Workload split | Theo mô tả Member 1/2/3 trong BA (1).pdf; bảng % bị lỗi trích xuất nên không dùng | Decided | — | — | ALL | W1 D1 |
| D18 | Extreme values | Không xóa; flag; winsorize feature nếu cần, cutoff fit trên train | Decided 2026-09-27 (cap ở simulation, D27) | Phân phối line value | Model nhạy outlier | M1 | W2 D5 |
| D19 | Cancellation vs return | Không phân biệt được trong data: mọi điều chỉnh âm có Customer ID đều là invoice `C`. Gộp thành `adjustment`; quantity âm không có `C` (3,393 dòng, không ID, price 0) → loại; invoice `A` → loại | Decided (profiling 2026-09-27) | `data_profile_topic1.md` §3 | — | M1 | Done |
| D21 | Sheet overlap | CR-00: sheet 2009-2010 cho < 2010-12-01, sheet 2010-2011 cho ≥ 2010-12-01 (22,523 dòng trùng hoàn toàn) | Decided | `data_profile_topic1.md` §2 | Đếm trùng revenue tháng 12/2010 | M1 | Done |
| D22 | Seasonality feature | **Decided:** `t0_month_sin/cos`; T3.4 phải báo cáo ablation có/không (không chặn nếu kém hơn thì bỏ và ghi log) | Decided 2026-09-27 | Tháng validation (4–5) không có trong train → one-hot không dùng được | — | M2 | Done |
| D23 | Value proxy khi aov ≤ 0 | V = aov nếu > 0; ngược lại median aov theo segment fit trên train | Decided | Code Spec §6.13 | EIM âm giả | M3 | Done |
| D24 | Tránh tự đánh giá policy D | Báo cáo `value_basis` = `model_p` và `actual_outcome`; so sánh chính dùng `actual_outcome` | Decided | Code Spec §6.14 | D thắng theo định nghĩa | M3 | Done |
| D25 | Final model protocol & calibration shift | Fit train → tune + calibrate trên validation → test một lần; không refit train+val (MVP). Bắt buộc calibration-in-the-large theo snapshot test + sensitivity dịch p | Decided (review v1 R-03) | Prevalence train 0.50 / val 0.46 / test 0.58 | EIM sai do p lệch | M2 | Done |
| D26 | Cấu trúc incremental lift + Policy E | **Decided:** primary `constant`; `persuadable` là sensitivity **bắt buộc**; thêm Policy E (lowest-p). Với tham số D10/D11, `persuadable` cho EIM ≤ 0 mọi p (lift tối đa δ < ngưỡng hòa vốn) → đây là kết quả phải báo cáo, không phải lỗi | Decided 2026-09-27 | Tính p-range §2b | — | M3 | Done |
| D27 | Cap value proxy | `V_i = min(V_i, quantile 0.99 AOV train)`; báo cáo EIM share top 1% + sensitivity không cap | Decided (review v1 R-02) | UCI: nhiều wholesaler | Vài khách chi phối EIM | M3 | Done |
| D28 | Nguồn chuẩn tài liệu | SPEC = nghiệp vụ/phương pháp; Code Spec = tên cột/kiểu/hàm/đường dẫn; khác biệt phải ghi decision log | Decided | review v1 R-04..R-08 | Lệch schema | ALL | Done |
| D29 | Guardrail net-negative | Loại khách có monetary_net ≤ 0 (trả/huỷ nhiều hơn mua) khỏi population được target cho **mọi** policy (`simulation.exclude_net_negative`) | Decided 2026-09-27 (post-test, báo cáo cả hai kết quả) | Trên test, 4/4 khách D chọn là net-returner dùng value fallback (`outputs/tables/pre_D29/`) | D thưởng cho khách trả hàng | M3 | Done |
| D30 | Scenario minh hoạ | Thêm `illustrative_breakeven` (d = 0.05, δ = 0.10 — một điểm có sẵn trong sensitivity grid) để actionable view cho thấy **điều kiện cần** để targeting có lãi. Không phải scenario kế hoạch; không dùng để chọn model | Decided 2026-09-27 (post-test, chỉ để trình bày) | 3 scenario chính: D không target ai sau D29 | Dashboard không có ví dụ hành động | M3 | Done |
| D20 | Number of incremental orders per horizon | Giả định 1 order (bảo thủ) | Decided | — | EIM phóng đại nếu > 1 | M3 | W2 D5 |

## 2b. Căn cứ chốt tham số (2026-09-27)

Nguyên tắc: tham số promotion **không có trong data** (không có treatment/control), nên chọn theo benchmark công khai + đặc điểm của dataset, rồi phủ bằng sensitivity grid rộng. Mọi số là *team assumption*.

| Tham số | Giá trị chốt | Căn cứ |
|---|---|---|
| Gross margin `m` | 0.40 (grid 0.30–0.50) | Benchmark e-commerce: home goods ~45%, brand $1M–$10M ~42% (eightx.co 2026); wholesale 15–50% (BusinessDojo). Dataset bán giftware, **nhiều khách là wholesaler** (UCI) → chọn thấp hơn DTC |
| Discount `d` | 5% / 10% / 20% | Mức coupon phổ biến trong bán lẻ; điều kiện `d < m` luôn thỏa |
| Incremental lift `δ` | 2 / 5 / 10 điểm phần trăm | Holdout test là chuẩn đo incrementality (attribuly, measured.com); lift tương đối ≥ 20% đã được coi là đáng kể (improvado). Với baseline repeat ~0.50, 2–10 pp ≈ 4–20% tương đối |
| Contact cost `c` | £0.10/khách (grid £0.01–£0.50) | Kênh email cho online retailer. Chi phí gửi thuần chỉ ~$0.10–0.90 / 1,000 email (AWS SES, tools.town); £0.10 đã gồm creative/nhân sự; £0.50 = kênh đắt hơn (SMS/direct mail) |
| Capacity K | 5 / 10 / 20% eligible | ≈ 140–550 khách mỗi T0 test (2,766–2,768 eligible) |
| Value `V_i` | AOV, cap q0.99 train | Data: AOV khách (train) median £284, p90 £661, p99 £1,946; top 1% khách chiếm **28.5%** giá trị → cap là cần thiết (D27) |

**Hệ quả đã tính** (`compute_eim`, V = AOV p10/p50/p90): với `constant`, EIM > 0 chỉ khi p < ~0.10–0.15 (Aggressive ~0.10, Base ~0.146, Conservative ~0.133). Với `persuadable`, không có khách nào EIM > 0 ở cả 3 scenario. Diễn giải cho báo cáo: *nếu lift tập trung ở nhóm lưỡng lự, discount đại trà ở các mức này không sinh lời — cần lift lớn hơn hoặc discount nhỏ hơn*. Sensitivity grid (δ tới 0.20, d từ 0.05) sẽ chỉ ra vùng hòa vốn.

## 3. Câu hỏi mở cần hỏi giảng viên (nếu cần)

1. Có chấp nhận internal plan hoàn tất baseline sớm (W3) trong khung 6 tuần không? (không bắt buộc hỏi)
2. Dashboard có cần deploy online hay chạy local là đủ?
3. Có yêu cầu định dạng executive brief (PDF/Word)?

## 4. Change history

| Ngày | ID | Thay đổi | Lý do | Người |
|---|---|---|---|---|
| 2026-09-27 | D01–D20 | Tạo log ban đầu từ review BA.pdf, BA (1).pdf và capstone | Khởi tạo Spec v1.0 | Team |
| 2026-09-27 | D02, D03, D07, D19 | Điền source URL (lấy từ hyperlink trong CAP), license CC BY 4.0, checksum; split cụ thể theo coverage của UCI; quy tắc cancellation theo UCI | Đã verify trang UCI và tải file | Team |
| 2026-09-27 | D04, D19, D21–D24 | Chốt cleaning theo profiling thật; thêm quyết định kỹ thuật của Code Spec | `data_profile_topic1.md` | Team |
| 2026-09-27 | D29 | Guardrail net-negative sau khi xem test; kết quả trước giữ ở outputs/tables/pre_D29 | Khách D chọn đều là net-returner | Team |
| 2026-09-27 | D08, D10, D11, D14, D16, D22, D26 | Chốt theo benchmark + data (§2b) | Yêu cầu user: tự chốt theo chuẩn | Team |
| 2026-09-27 | D10, D11, D25–D28 | Review v1: đề xuất giá trị scenario; calibration protocol; lift structure + Policy E; cap value; nguồn chuẩn tài liệu | `review_v1_topic1.md` | Team |
