# Review v1 — Spec & giải pháp Topic 1 (trước khi vào Plan/Code)

| | |
|---|---|
| Ngày | 2026-09-27 |
| Phạm vi | `project_specification_topic1.md`, `code_specification_topic1.md`, `implementation_plan_topic1.md`, `decision_log_topic1.md`, `traceability_matrix_topic1.md`, `data_profile_topic1.md`, `project_config.yaml`, `src/`, `tests/` |
| Kết luận | **Đủ điều kiện chuyển sang Plan/Code**, với điều kiện team sign-off 4 quyết định mở ở §4 trước các mốc đã ghi |

Mức độ: **S1** = sai phương pháp hoặc có thể làm sai kết luận chính · **S2** = mâu thuẫn giữa các tài liệu hoặc sẽ gây lỗi khi code · **S3** = thiếu sót về tài liệu hoặc onboarding.

---

## 1. Tóm tắt

Giải pháp tổng thể đúng với capstone và đứng vững về mặt phương pháp ở các phần sau:

- decision framing, unit `(customer, T0)`, temporal split có purge;
- baseline RFM + Logistic Regression;
- simulation non-causal có công thức minh bạch;
- policy comparison cùng capacity;
- data contract và test viết trước (đã được kiểm chứng bằng reference implementation trên data thật, xem Code Spec §3.1).

Review tìm ra **3 vấn đề S1** trong phần decision analytics, cùng một số mâu thuẫn S2/S3 giữa SPEC (viết trước profiling) và Code Spec/data thật (viết sau). Tất cả mâu thuẫn tài liệu đã được sửa trong lần review này. Các vấn đề S1 đã được đưa vào spec thành yêu cầu bắt buộc, kèm quyết định mới D25–D28.

---

## 2. Phát hiện S1 — phương pháp

### R-01 · Kết luận "D thắng" có thể do giả định quyết định, không phải do data

**Vấn đề.** Với `δ_i = min(δ, 1 − p_i)` là hằng số, EIM của một khách là:

```text
EIM_i = V_i·[δ(m − d) − p_i·d] − c        (khi p_i ≤ 1 − δ)
EIM_i > 0  ⇔  p_i < p* = δ(m − d)/d − c/(d·V_i)
```

Tức là policy D **luôn** chọn khách có p thấp nhất (và V cao), và mức ngưỡng p* được quyết định hoàn toàn bởi tỷ số `δ/d`.

**Bằng chứng** (tính bằng `compute_eim`, m = 0.40, c = £0.5; bộ tham số thử trong `tests/conftest.py`):

| Scenario (d, δ) | p* khi V = £50 | V = £300 | V = £1000 |
|---|---|---|---|
| Conservative (0.05, 0.02) | không ai | 0.107 | 0.130 |
| Base (0.10, 0.05) | 0.050 | 0.133 | 0.145 |
| Aggressive (0.20, 0.10) | 0.050 | 0.092 | 0.098 |

Prevalence thật là 0.38–0.62 (data profile §5). Vì vậy, với các giá trị "hợp lý", D có thể target rất ít khách, **ít hơn K**. Khi đánh giá theo `actual_outcome`, một khách được target có EIM thực tế:

- `y = 0`: `δ·V·(m − d) − c`
- `y = 1`: `−V·d − c`

Như vậy mọi policy nhắm vào người **không** quay lại đều được thưởng, kể cả khách đã mất hẳn. Policy C (RFM, nhắm khách tốt nhất, y cao) sẽ thua **theo cấu trúc**. Nếu không xử lý, kết luận "model + value targeting tốt hơn" chỉ phản ánh giả định δ hằng số.

**Sửa (đã đưa vào SPEC §9.4, §10, D26):**

1. Thêm baseline **Policy E — lowest-p** (target K khách có p thấp nhất, không dùng value). D chỉ được coi là có giá trị nếu D > E. Khi đó phần đóng góp đến từ value weighting và EIM, không đơn thuần là "chọn người ít mua".
2. Sensitivity bắt buộc theo **cấu trúc δ**, không chỉ theo mức δ:
   - (a) `constant`: δ như hiện tại;
   - (b) `persuadable`: `δ_i = δ·4·p_i·(1 − p_i)` — lift cao nhất với khách ở mức "lưỡng lự" và bằng 0 với khách chắc chắn mua hoặc đã mất;
   - (c) `segment`: hệ số nhân theo segment (ví dụ High-value at risk × 1.5, Dormant × 0.5), ghi rõ là assumption.
   Kết luận chỉ được viết nếu đúng trên cả (a) và (b).
3. Dashboard và executive brief phải hiển thị `p*` và target count thực tế so với K.

### R-02 · Value proxy bị chi phối bởi wholesaler

**Vấn đề.** Trang UCI ghi "nhiều khách là wholesaler". Vì EIM tỷ lệ với `V_i = AOV`, vài khách AOV rất lớn sẽ chiếm phần lớn tổng EIM và gần như toàn bộ top ranking. Data có order đơn lẻ tới 80,995 đơn vị (đã được invoice `C` bù trừ, nhưng vẫn cho thấy phân phối rất lệch).

**Sửa (D27):** `V_i` được **cap tại quantile 99% của AOV trên train**, fit trên train (INV-09). Tham số `simulation.value_cap_quantile: 0.99`. Phải báo cáo tỷ trọng EIM của top 1% khách và chạy sensitivity khi không cap.

### R-03 · Calibration bị lệch phân phối giữa validation và test

**Vấn đề.** EIM dùng giá trị tuyệt đối của `p_i`, không chỉ thứ hạng. Prevalence: train ≈ 0.50, validation (T0 tháng 4–5) ≈ 0.46, test (T0 tháng 8–9) ≈ 0.58. Nếu calibrate trên validation rồi áp cho test, `p_i` sẽ thấp hơn thực tế ở test, khiến EIM bị thổi phồng với khách p thấp.

**Sửa (D25, SPEC §8):**

- Model cuối cho test = fit trên train, calibrate trên validation (MVP; giữ nguyên, không refit trên train + validation).
- Bắt buộc báo cáo **calibration-in-the-large** (mean p so với prevalence) theo từng snapshot test.
- Model card phải ghi rõ đây là rủi ro seasonality.
- Sensitivity bổ sung: EIM với `p` dịch chuyển ± (prevalence_test − mean_p_val).

---

## 3. Phát hiện S2/S3 — nhất quán và tài liệu

| ID | Mức | Vị trí | Vấn đề | Sửa | Trạng thái |
|---|---|---|---|---|---|
| R-04 | S2 | SPEC §4 | Bảng CR viết trước profiling: CR-02 còn tách return, thiếu CR-00 và CR-05b, thứ tự áp rule chưa có | Viết lại theo data thật + tham chiếu Code Spec §6.4 | Đã sửa |
| R-05 | S2 | SPEC §7.1 | Tên và kiểu feature lệch Code Spec (`total_quantity`/`total_units`, recency int/float, thiếu `purchase_value`, `adjustment_value`, `t0_month_*`) | SPEC giữ ý nghĩa nghiệp vụ; Code Spec §5.3 là nguồn chuẩn cho tên/kiểu | Đã sửa |
| R-06 | S2 | SPEC §7.3 và config | Rule segment trong SPEC khác `segmentation.rules` (Developing, Dormant) | Đồng bộ theo config (rule exhaustive, có test) | Đã sửa |
| R-07 | S2 | SPEC §12.2 | Schema lặp và lệch Code Spec §5 (thiếu `split`, `predicted_repeat_probability_raw`, `value_basis`, …) | Bỏ bản lặp, tham chiếu Code Spec §5 | Đã sửa |
| R-08 | S2 | SPEC §3.5, §3.6, §8 | Đường dẫn cũ (`src/data/download.py`, `outputs/model/`, `outputs/data_quality_report.md`) | Cập nhật theo Code Spec §2 | Đã sửa |
| R-09 | S2 | SPEC §10 | Chưa nêu `value_basis` (D24): so sánh bằng EIM do chính model tính là tự đánh giá | Thêm vào SPEC §10 | Đã sửa |
| R-10 | S2 | contracts | `customer_snapshots` hard-code `repeat_purchase_90d`; nếu đổi D06 thì contract gãy | Ghi rõ trong Code Spec §5.3: đổi horizon ⇒ đổi contract + test | Đã ghi |
| R-11 | S3 | SPEC §2.6, §3.1, §3.2, §5 | Assumption A2–A4, "sheets TBD", "phải xác nhận InvoiceDate" đã được profiling giải quyết | Cập nhật trạng thái | Đã sửa |
| R-12 | S3 | Plan/Traceability | Trạng thái task/req vẫn là "Planned" dù T1.1, T1.3 đã xong | Thêm bảng trạng thái | Đã sửa |
| R-13 | S3 | Thiếu file | Plan yêu cầu `docs/source_log.md`, `docs/data_dictionary.md` nhưng chưa có | Tạo `source_log.md` (đủ) + `data_dictionary.md` v0 | Đã tạo |
| R-14 | S3 | Onboarding | Không có tài liệu cho người mới: thứ tự đọc, glossary, git workflow, quy trình nhận task | Tạo `docs/onboarding_topic1.md` | Đã tạo |
| R-15 | S3 | Root repo | `Topic1_Spec_Review_and_Recommendation.md`, `goal_prompt_…md` đã bị thay thế nhưng vẫn nằm ở root, dễ gây nhầm lẫn | Chuyển vào `docs/archive/` | Đã chuyển |
| R-16 | S3 | Decision log | D10/D11 (tham số scenario) còn Open và chặn stage `simulate` | Đề xuất giá trị (Proposed) + phương pháp sign-off | Đề xuất, chờ team |

---

## 4. Quyết định cần team sign-off trước khi code phần liên quan

> **Cập nhật 2026-09-27:** tất cả đã được chốt (Decided) theo benchmark + data. Căn cứ: decision_log_topic1.md §2b. Bảng dưới giữ lại để truy vết.

| ID | Nội dung | Cần trước | Owner |
|---|---|---|---|
| D10/D11 | Giá trị 3 scenarios (đề xuất trong decision log) | T4.3 (W4 D1). M3 dev dùng giá trị test trong `conftest.py` | M3 + ALL |
| D16 | Công cụ dashboard (khuyến nghị Streamlit) | T5.3 (W5) — nên chốt W1 D5 | M3 |
| D22 | Feature mùa vụ sin/cos | T3.4 (W3 D4) | M2 |
| D26 | Cấu trúc δ và Policy E | T4.4 (W4) | M3 |

Các quyết định D05–D07 (window/split) có thể freeze ngay: data thật đã xác nhận 16 T0, prevalence và kích thước từng split (Code Spec §3.1).

---

## 5. Kiểm tra đã thực hiện trong review

- Đối chiếu chéo tên hàm, cột, invariant và file test giữa Code Spec và code (script tự động).
- Tính lại ngưỡng p* bằng công thức và bằng `compute_eim` (bảng R-01, hai cách khớp nhau đến 4 chữ số).
- Rà từng mục SPEC so với data profile và config.
- Sau khi sửa: chạy lại `pytest`, `validate-config` và script kiểm tra tham chiếu chéo (kết quả ở cuối `onboarding_topic1.md` §9).
