# Data Dictionary — Topic 1 (v0)

Trạng thái: **v1 (final, 2026-09-27)**. Missing rate đo từ output pipeline (`data/interim/lines.parquet`, `data/processed/customer_snapshots.parquet`). Nguồn chuẩn cho tên và kiểu: `src/retail_targeting/contracts.py`.

Missing rate thực tế sau cleaning: `description` 0.41% dòng; `customer_id` 22.76% dòng (giữ ở line level, loại khỏi orders/snapshots); trong `customer_snapshots` chỉ có `avg_interpurchase_days` thiếu (45.66% — khách có 1 order trong cửa sổ, được impute median train trong pipeline model), mọi cột khác 0%.

`leakage_risk`: **none** = có trước T0 · **target** = nhãn/outcome · **post-T0** = chỉ được dùng cho outcome.

## 1. Raw fields (`online_retail_II.xlsx`, cả 2 sheet)

| Raw field | Canonical | Type | Ý nghĩa | Giá trị / đặc điểm (profiling) | Missing | Cleaning rule | Downstream |
|---|---|---|---|---|---|---|---|
| `Invoice` | `invoice` | string | Mã hoá đơn | 6 chữ số; prefix `C` = cancellation/return (19,104 dòng); prefix `A` = bad debt (6 dòng) | 0 | CR-01/02, CR-05, CR-09 | key order |
| `StockCode` | `stock_code` | string | Mã sản phẩm | `^\d{5}[A-Za-z]{0,2}$`; 62 mã đặc biệt (POST, DOT, M, …) | 0 | CR-05b | `unique_products` |
| `Description` | `description` | string | Tên sản phẩm | — | 4,275 dòng | không dùng làm feature | mô tả |
| `Quantity` | `quantity` | int | Số lượng | Không có 0; âm ở invoice `C` và 3,393 dòng điều chỉnh kho | 0 | CR-04 | `total_units`, `line_value` |
| `InvoiceDate` | `invoice_ts` | datetime | Thời điểm giao dịch | 2009-12-01 07:45 → 2011-12-09 12:50; độ chính xác phút | 0 | CR-08; `order_ts = min` | T0 windows |
| `Price` | `price` | float (£) | Đơn giá | 6,014 dòng = 0; 5 dòng < 0 (invoice `A`) | 0 | CR-05c | `line_value` |
| `Customer ID` | `customer_id` | string | Mã khách | float trong file → string 5 chữ số; 5,942 khách | 22.76% dòng | CR-06 | key snapshot |
| `Country` | `country` | string | Quốc gia khách | 43 nước; UK 948,321 dòng | 0 | — | mô tả (không phải feature) |
| *(thêm)* | `source_sheet` | string | Sheet gốc | `Year 2009-2010` / `Year 2010-2011` | 0 | CR-00 | trace |

## 2. Derived — line/order level

| Field | Type | Định nghĩa | Leakage | Nguồn |
|---|---|---|---|---|
| `line_value` | float | `quantity × price` | none | Code Spec §5.1 |
| `line_type` | string | purchase / adjustment / non_product / excluded | none | §6.4 |
| `exclude_reason` | string | missing_customer / zero_price / stock_adjustment / bad_debt_adjustment / invalid_quantity / invalid_date | none | §6.4 |
| `order_id`, `order_ts`, `order_type`, `order_value`, `n_lines`, `n_units`, `n_products` | — | Tổng hợp theo invoice | none | §5.2 |

## 3. Derived — `customer_snapshots` (một dòng / khách / T0)

| Field | Type | Định nghĩa ngắn | Leakage | Dùng làm |
|---|---|---|---|---|
| `recency_days` | float | Số ngày từ lần mua gần nhất đến T0 | none | feature, RFM-R |
| `frequency_orders` | int | Số purchase order trong 180 ngày | none | feature, RFM-F |
| `purchase_value` / `adjustment_value` | float | Tổng mua / tổng huỷ-trả (≥ 0) | none | feature |
| `monetary_net` | float | purchase − adjustment (có thể âm: 34 dòng) | none | feature, RFM-M |
| `aov` | float | monetary_net / frequency_orders | none | feature, `V_i` |
| `return_rate` | float | adjustment / purchase, cap 1 | none | feature |
| `tenure_days` | float | Ngày từ lần mua đầu tiên (toàn lịch sử < T0) | none | feature |
| `active_months`, `avg_interpurchase_days`, `unique_products`, `total_units`, `orders_last_30d` | — | Xem Code Spec §5.3 | none | feature |
| `t0_month_sin`, `t0_month_cos` | float | Mã hoá tháng của T0 | none | feature (D22) |
| `cohort_month` | string | Tháng mua đầu tiên | none | cohort |
| `country` | string | Country của order gần nhất | none | mô tả |
| `repeat_purchase_90d` | int (0/1) | Có purchase trong [T0, T0+90d) | **target** | target |
| `label_future_value_90d` | float | Tổng purchase trong [T0, T0+90d) | **target** | đánh giá / stretch S2 |
| `r_score`, `f_score`, `m_score`, `rfm_score`, `customer_segment` | int / string | RFM (cutoffs fit train) | none | benchmark, segment |
| `split` | string | train / validation / test / purged / unused | — | M2 |
| `feature_version` | string | Version công thức | — | trace |

## 4. Derived — decision outputs

Xem Code Spec §5.4–§5.6 (`customer_predictions`, `customer_targeting_table`, `scenario_results`). Mọi cột tiền tệ đều tính bằng £ (GBP).
