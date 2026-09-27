# Onboarding — Topic 1: Customer Value & Promotion Targeting

Tài liệu cho người **mới vào dự án**. Đọc xong phần này (khoảng 60 phút), bạn phải trả lời được: dự án giải bài toán gì, dữ liệu ra sao, pipeline gồm những bước nào, mình phụ trách phần nào và bắt đầu code từ đâu.

---

## 1. Dự án trong 5 câu

1. **Câu hỏi nghiệp vụ** (capstone Topic 1): *nên ưu tiên khách nào để gửi promotion/retention, nhằm tăng expected future margin mà không discount lãng phí?*
2. **Dữ liệu**: UCI Online Retail II — khoảng 1 triệu dòng giao dịch 2009–2011 của một online retailer ở UK.
3. **Cách làm**:
   - tại mỗi đầu tháng T0, tạo snapshot khách hàng từ 180 ngày trước T0;
   - dự đoán xác suất khách mua lại trong 90 ngày tới (Logistic Regression, so với benchmark RFM);
   - kết hợp xác suất, giá trị đơn hàng và giả định về discount/lift thành **EIM** (simulated expected incremental margin);
   - chọn khách theo EIM trong giới hạn capacity.
4. **Đánh giá**: temporal split (train/validation/test theo thời gian, có purge 90 ngày), PR-AUC/ROC-AUC/calibration, và so sánh 5 policy (A–E) ở cùng capacity.
5. **Giới hạn quan trọng nhất**: dataset không có thí nghiệm promotion. Mọi con số promotion là **mô phỏng dưới giả định**, không bao giờ được gọi là ROI, causal uplift hay revenue lift.

---

## 2. Thứ tự đọc tài liệu

| # | File | Đọc để biết | Thời gian |
|---|---|---|---|
| 1 | `README.md` | Setup, lệnh chạy | 5' |
| 2 | Tài liệu này | Bức tranh tổng thể, quy trình làm việc | 15' |
| 3 | `docs/project_specification_topic1.md` §1, §5, §9, §10 | Business framing, thiết kế thời gian, công thức EIM, policy | 20' |
| 4 | `docs/data_profile_topic1.md` | Dữ liệu thật trông thế nào | 10' |
| 5 | `docs/code_specification_topic1.md` §1–§3, §10 + mục §6.x của module bạn phụ trách | Quy tắc code, contract, hàm cần viết | 20' |
| 6 | `docs/implementation_plan_topic1.md` §2, §4b | Task của bạn, dependency, acceptance | 10' |
| 7 | `docs/decision_log_topic1.md` | Cái gì đã chốt, cái gì còn mở | 5' |
| — | `docs/review_v1_topic1.md` | Vì sao có Policy E, lift structure, value cap (đọc khi làm phần decision) | — |
| — | `docs/traceability_matrix_topic1.md` | Yêu cầu capstone → evidence (đọc khi làm final QA) | — |
| — | `docs/source_log.md`, `docs/data_dictionary.md` | Nguồn dữ liệu, định nghĩa từng cột | tra cứu |
| — | `docs/archive/` | Tài liệu cũ, đã được thay thế — **không dùng để code** | — |

**Thứ bậc khi có mâu thuẫn (D28):** capstone PDF > SPEC (nghiệp vụ) > Code Spec (kỹ thuật) > các tài liệu khác. Khi thấy hai tài liệu nói khác nhau, **không tự chọn**: báo owner và ghi decision log.

---

## 3. Pipeline tổng thể

```text
UCI zip ──ingest──▶ transactions_raw ──clean──▶ lines ──▶ orders
                                                           │
                                  snapshots (16 T0 × khách eligible)
                                                           │
                         RFM scores + segments (cutoffs fit trên train)
                                                           │
            split: train (8 T0) │ purge │ validation (2) │ purge │ test (2)
                                                           │
                 RFM benchmark ─┬─ Logistic Regression → calibration
                                ▼
                       customer_predictions (p_i)
                                │
              V_i (AOV, fallback, cap) + scenario (m, d, δ, c) → EIM_i
                                │
         Policies A none · B random · C RFM · D EIM · E lowest-p   (cùng K)
                                │
     scenario_results · policy_comparison · sensitivity · customer_targeting_table
                                │
                      dashboard  +  executive brief  +  model card
```

| Stage CLI | Module | Owner | Output chính |
|---|---|---|---|
| `ingest` | `data/ingest.py` | M1 | `data/interim/transactions_raw.parquet` |
| `clean` | `data/clean.py`, `data/quality.py` | M1 | `lines`, `orders`, DQ report |
| `snapshots` | `features/*`, `models/split.py` | M1 (+M2) | `data/processed/customer_snapshots.parquet` |
| `train`, `evaluate` | `models/*` | M2 | model, metrics, `customer_predictions.csv` |
| `simulate`, `sensitivity` | `decision/*` | M3 | các bảng decision |
| (W5) | `dashboard/app.py` | M3 | dashboard |

---

## 4. Glossary

| Thuật ngữ | Nghĩa trong dự án |
|---|---|
| **T0 / decision date** | Ngày ra quyết định (ngày 1 mỗi tháng). Feature chỉ dùng dữ liệu `< T0` |
| **Observation window** | `[T0 − 180d, T0)` — dữ liệu dùng để tạo feature |
| **Outcome window** | `[T0, T0 + 90d)` — dùng để tạo target, **không bao giờ** dùng cho feature |
| **Snapshot** | Một dòng (khách, T0) |
| **Eligible** | Khách có ≥ 1 purchase trong observation window |
| **Target** `repeat_purchase_90d` | 1 nếu khách mua lại trong outcome window |
| **Purge** | Bỏ các T0 ở ranh giới split để outcome không chồng lên split sau |
| **Leakage** | Dùng thông tin của tương lai (≥ T0) khi tạo feature — lỗi nghiêm trọng nhất |
| **Adjustment** | Dòng/order invoice `C` (cancellation hoặc return, không tách được) |
| **Non-product** | StockCode là phí/bưu phí/điều chỉnh, không phải hàng hoá |
| **RFM** | Recency, Frequency, Monetary → score 1–5 → segment |
| **p_i** | Xác suất (đã calibrate) khách tự mua lại khi không có offer |
| **V_i** | Giá trị một đơn hàng của khách (AOV, có fallback và cap) |
| **m, d, δ, c** | Gross margin, discount rate, incremental lift giả định, contact cost |
| **EIM** | Simulated expected incremental margin = M1 − M0 (SPEC §9) |
| **p\*** | Ngưỡng: EIM > 0 ⇔ p < p\* (SPEC §9.4) |
| **Lift structure** | Cách δ thay đổi theo khách: constant / persuadable / segment |
| **Policy A–E** | None / Random / RFM top-K / EIM top-K / lowest-p top-K |
| **value_basis** | `model_p` (đánh giá bằng p) hoặc `actual_outcome` (đánh giá bằng outcome thật — số liệu chính) |
| **K / capacity** | Số khách tối đa được target (5/10/20% eligible) |
| **Contract** | Schema bắt buộc của một artifact (`contracts.py`) |
| **INV-xx** | Invariant phải kiểm tra lúc chạy (Code Spec §7) |
| **Dxx** | Mã quyết định trong decision log |
| **Txx** | Mã task trong implementation plan |

---

## 5. Setup lần đầu

```bash
git clone https://github.com/sutobode/BA.git && cd BA
python -m venv .venv
source .venv/Scripts/activate          # Git Bash; PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt && pip install -e .
pytest                                  # kỳ vọng: 79 passed, 0 failed
python -m retail_targeting validate-config
```

Hoặc dùng Docker (khuyến nghị, cùng môi trường cho mọi người): `docker compose build && docker compose run --rm test` — xem `README.md`.

Tải dữ liệu theo `README.md` → mục *Dữ liệu*. Kiểm tra SHA-256 phải khớp `docs/source_log.md`. Raw data **không** commit (đã có trong `.gitignore`).

---

## 6. Quy trình nhận và làm một task

1. Lấy task trong `implementation_plan_topic1.md` §4b đúng owner và đã đủ dependency (Definition of Ready: input đã có).
2. Đọc mục Code Spec §6.x tương ứng và chạy test của module đó (`pytest tests/test_<module>.py`).
3. Code trong `src/`. Notebook chỉ gọi hàm và vẽ biểu đồ.
4. Viết test cho logic mới (fixture nhỏ, đáp án tính tay) và chạy toàn bộ test. Nếu viết test trước khi code, có thể gắn `@todo` (xem Code Spec §8) rồi gỡ khi hàm xong.
5. Nếu có data thật, so với con số tham chiếu ở Code Spec §3.1.
6. Nếu phải quyết định điều spec chưa nói: thêm dòng vào decision log (status Proposed) → báo owner accountable → rồi mới code.
7. Mở PR (§7).

### Quy tắc bắt buộc

- Không hard-code hằng số nghiệp vụ; mọi thứ đọc từ `project_config.yaml`.
- Không tính lại cột của người khác. Thấy sai thì báo producer (single source of truth).
- Không đọc test split trước T5.2. Mọi lượt đọc phải qua `log_test_access`.
- Mọi fit (scaler, quantile, median, cap) chỉ dùng `split == "train"`.
- Không dùng các từ "ROI", "uplift", "revenue lift", "caused" trong output, trừ khi ở câu phủ định.

---

## 7. Git workflow

- Branch từ `master`: `feat/<task-id>-<ngắn>`, ví dụ `feat/T2.1-cleaning`; sửa lỗi: `fix/<ngắn>`; tài liệu: `docs/<ngắn>`.
- Commit nhỏ, message dạng `T2.1: classify lines per CR rules`.
- Không push thẳng lên `master` sau khi team đã bắt đầu code; mọi thay đổi đi qua PR, ít nhất 1 người review (ưu tiên owner accountable của phần bị ảnh hưởng).
- Không commit `data/`, `.venv/`, model `.joblib`, output tạm.

**PR checklist (Definition of Done cho một PR):**

- [ ] `pytest` 0 failed; đã xoá `@todo` của các test mình làm cho pass.
- [ ] `python -m retail_targeting validate-config` OK.
- [ ] Output đi qua `validate_frame` với contract tương ứng.
- [ ] Không có leakage (feature chỉ từ `< T0`; fit chỉ trên train).
- [ ] Đổi schema/config/quy tắc → cập nhật Code Spec + decision log + test trong **cùng** PR.
- [ ] Mô tả PR: task ID, đã làm gì, đã test gì, con số so với Code Spec §3.1 (nếu có).

---

## 8. FAQ

**Q: Test báo `xfailed` có phải lỗi không?** Hiện không còn test xfail. Nếu thấy, đó là test viết trước cho hàm mới chưa code; chỉ `failed`/`error` mới là lỗi.

**Q: Vì sao không dùng random split?** Cùng một khách xuất hiện ở nhiều T0. Random split sẽ để model học từ tương lai (SPEC §6).

**Q: Vì sao không tách được return với cancellation?** Trong data, mọi điều chỉnh âm có Customer ID đều thuộc invoice `C` (data profile §3, D19).

**Q: Tham số scenario lấy ở đâu?** Đã chốt trong `project_config.yaml → simulation.scenarios` (D10/D11); căn cứ ở decision log §2b.

**Q: Vì sao có Policy E và "persuadable lift"?** Với δ hằng số, EIM luôn ưu tiên khách p thấp. Hai thành phần này kiểm tra xem kết luận có đến từ data hay chỉ từ giả định (`review_v1_topic1.md` R-01).

**Q: Đọc file xlsx mất gần 3 phút?** Đúng như vậy. `load_raw` phải cache parquet (Code Spec §6.3); từ lần thứ hai sẽ mất vài giây.

---

## 9. Trạng thái dự án (cập nhật 2026-09-27)

Pipeline hoàn chỉnh, đã chạy trên data thật trong Docker; test set đã được đánh giá **một lần** (không đánh giá lại). 79 test pass, 0 stub. Deliverables: xem bảng *Deliverables* trong `README.md` và `docs/traceability_matrix_topic1.md`. Kết quả chính: `docs/executive_brief.pdf`, `docs/model_analysis_card.md`.
