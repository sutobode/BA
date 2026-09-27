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
| D03 | Commit raw data | CC BY 4.0 cho phép chia sẻ kèm ghi nguồn, nhưng file 43.5 MB → mặc định không commit; README ghi link, lệnh tải, checksum | Proposed | Chính sách repo của nhóm | Repo nặng | M1 | W1 D3 |
| D04 | Non-product codes | Danh sách + pattern trong `data_profile_topic1.md` §4 và `cleaning.non_product_*` trong config; loại khỏi purchase events, tính riêng | Decided (profiling 2026-09-27) | 62 mã đặc biệt đã rà | — | M1 | Done |
| D05 | Snapshot cadence | Monthly, T0 = ngày 1 mỗi tháng | Proposed | Số snapshot hợp lệ | Không build được split | M2 | W2 D3 |
| D06 | Observation / outcome window | 180d / 90d (thiết kế nhóm, không phải yêu cầu GV) | Proposed | Date range, prevalence, seasonality | Target không ổn định | M2 | W2 D3 |
| D07 | Split dates & purge | Train 2010-06→2011-01 (8), Val 2011-04, 2011-05, Test 2011-08, 2011-09; purge 2 snapshot mỗi ranh giới (SPEC §5) | Proposed | Min/max InvoiceDate thực tế (T1.3) | Leakage / metric ảo | M2 | W2 D5 |
| D08 | Calibration method | Chỉ calibrate nếu reliability lệch; sigmoid mặc định, isotonic nếu đủ dữ liệu | Proposed | Reliability plot validation | p_i sai → EIM sai | M2 | W4 D2 |
| D09 | Value unit `V_i` | `V_i = AOV_i`; fallback median AOV theo segment tính trên train | Decided | — (logic) | Over/understate value | M3 | W2 D5 |
| D10 | Incremental lift `δ` | Hằng số theo scenario, cap `1 − p_i`; giá trị TBD | Open | Rationale/benchmark tham khảo | Không chạy được scenario | M3 | W4 D1 |
| D11 | `m`, `d`, `c`, `K`/`B` | Giá trị cho 3 scenarios TBD; K mặc định thử 5/10/20% eligible | Open | Business rationale | Không có business metric | M3 | W4 D1 |
| D12 | RFM cutoffs & segments | Quintile fit trên train; 5 segments theo SPEC §7.3 | Proposed | Phân phối RFM | Segment không ổn định | M1 | W3 D2 |
| D13 | Random baseline | 100 seeds, list seed trong config | Decided | — | So sánh không tái lập | M3 | W2 D5 |
| D14 | Class imbalance | So `class_weight` None vs balanced trên validation, chọn theo PR-AUC + calibration | Proposed | Prevalence thực tế | Probability lệch | M2 | W3 D4 |
| D15 | KPIs | 5 KPIs SPEC §1.8 | Decided | — | Dashboard lan man | M3 | W1 D5 |
| D16 | Dashboard tool | Streamlit (ưu tiên reproducibility) hoặc Power BI/Tableau | Open | Kỹ năng nhóm, yêu cầu interactive | Trễ W5 | M3 | W1 D5 |
| D17 | Workload split | Theo mô tả Member 1/2/3 trong BA (1).pdf; bảng % bị lỗi trích xuất nên không dùng | Decided | — | — | ALL | W1 D1 |
| D18 | Extreme values | Không xóa; flag; winsorize feature nếu cần, cutoff fit trên train | Proposed | Phân phối line value | Model nhạy outlier | M1 | W2 D5 |
| D19 | Cancellation vs return | Không phân biệt được trong data: mọi điều chỉnh âm có Customer ID đều là invoice `C`. Gộp thành `adjustment`; quantity âm không có `C` (3,393 dòng, không ID, price 0) → loại; invoice `A` → loại | Decided (profiling 2026-09-27) | `data_profile_topic1.md` §3 | — | M1 | Done |
| D21 | Sheet overlap | CR-00: sheet 2009-2010 cho < 2010-12-01, sheet 2010-2011 cho ≥ 2010-12-01 (22,523 dòng trùng hoàn toàn) | Decided | `data_profile_topic1.md` §2 | Đếm trùng revenue tháng 12/2010 | M1 | Done |
| D22 | Seasonality feature | `t0_month_sin/cos` (không one-hot: tháng T0 của validation 4–5 không có trong train) | Proposed | So PR-AUC/calibration validation có/không feature | Calibration test lệch | M2 | W3 D4 |
| D23 | Value proxy khi aov ≤ 0 | V = aov nếu > 0; ngược lại median aov theo segment fit trên train | Decided | CODE SPEC §6.13 | EIM âm giả | M3 | Done |
| D24 | Tránh tự đánh giá policy D | Báo cáo `value_basis` = `model_p` và `actual_outcome`; so sánh chính dùng `actual_outcome` | Decided | CODE SPEC §6.14 | D thắng theo định nghĩa | M3 | Done |
| D20 | Number of incremental orders per horizon | Giả định 1 order (bảo thủ) | Decided | — | EIM phóng đại nếu > 1 | M3 | W2 D5 |

## 3. Câu hỏi mở cần hỏi giảng viên (nếu cần)

1. Có chấp nhận internal plan hoàn tất baseline sớm (W3) trong khung 6 tuần không? (không bắt buộc hỏi)
2. Dashboard có cần deploy online hay chạy local là đủ?
3. Có yêu cầu định dạng executive brief (PDF/Word)?

## 4. Change history

| Ngày | ID | Thay đổi | Lý do | Người |
|---|---|---|---|---|
| 2026-09-27 | D01–D20 | Tạo log ban đầu từ review BA.pdf, BA (1).pdf và capstone | Khởi tạo Spec v1.0 | Team |
| 2026-09-27 | D02, D03, D07, D19 | Điền source URL (lấy từ hyperlink trong CAP), license CC BY 4.0, checksum; split cụ thể theo coverage của UCI; quy tắc cancellation theo UCI | Đã verify trang UCI và tải file | Team |
