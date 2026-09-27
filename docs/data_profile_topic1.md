# Data Profile — Online Retail II (T1.3, chạy 2026-09-27)

Nguồn: `data/raw/online_retail_II.xlsx` (SHA-256 `BCBE73B3…F2DF2E980`, khớp SPEC §3.1).  
Script: `data/raw/_profile.py`, `_profile2.py` (tạm, sẽ được thay bằng `retail_targeting.data.quality`). Output gốc: `data/raw/_profile.json`, `_profile2.json`.

## 1. Schema thực tế

File có **2 sheet**, cùng 8 cột. Tên cột **khác** trang UCI:

| Cột trong file | Tên trên trang UCI | dtype đọc được | Ghi chú |
|---|---|---|---|
| `Invoice` | InvoiceNo | str | Prefix `C` = cancellation (19,104 dòng); prefix `A` = "Adjust bad debt" (6 dòng) |
| `StockCode` | StockCode | str | Phần lớn `^\d{5}[A-Za-z]{0,2}$`; có 62 mã đặc biệt (§4) |
| `Description` | Description | str | 4,275 dòng thiếu |
| `Quantity` | Quantity | int64 | Không có giá trị 0 |
| `InvoiceDate` | InvoiceDate | datetime | Độ chính xác phút |
| `Price` | UnitPrice | float64 | £; 6,014 dòng = 0; 5 dòng < 0 (đều là invoice `A`) |
| `Customer ID` | CustomerID | float64 | Giá trị đều là số nguyên → ép sang string 5 chữ số |
| `Country` | Country | str | 43 quốc gia; UK chiếm 948,321 dòng |

| Sheet | Rows | Min InvoiceDate | Max InvoiceDate |
|---|---|---|---|
| `Year 2009-2010` | 525,461 | 2009-12-01 07:45 | 2010-12-09 20:01 |
| `Year 2010-2011` | 541,910 | 2010-12-01 08:26 | 2011-12-09 12:50 |
| Tổng | 1,067,371 (= số instances trên UCI) | 2009-12-01 | 2011-12-09 |

## 2. Overlap giữa 2 sheet

- Giai đoạn 2010-12-01 → 2010-12-09 có ở **cả hai sheet**: mỗi bên 22,523 dòng, tập invoice trùng nhau và **multiset dòng giống hệt**.
- Quy tắc CR-00: lấy sheet 2009-2010 cho `InvoiceDate < 2010-12-01` và sheet 2010-2011 cho `InvoiceDate ≥ 2010-12-01`. Sau bước này còn 1,044,848 dòng.
- Duplicate exact **trong** từng sheet: 6,865 và 5,268 dòng. Sau khi áp CR-00 còn 11,812 dòng duplicate → CR-07 bỏ, còn **1,033,036 dòng**.

## 3. Customer ID, cancellation, giá trị âm

| Chỉ số | Giá trị |
|---|---|
| Dòng thiếu Customer ID | 22.76% |
| Revenue dương của các dòng thiếu Customer ID | 15.15% |
| Unique customers / invoices | 5,942 / 53,628 |
| Invoice có > 1 customer | 0 |
| Invoice có > 1 timestamp | 83 → order_ts = min(InvoiceDate) |
| Dòng invoice `C` | 19,104 (1 dòng có quantity > 0) |
| Dòng invoice `C` có Customer ID | 18,390; tổng value −£1,084,813 (≈ 6.2% so với £17.37M revenue dương có ID) |
| Quantity < 0 nhưng không phải `C` | 3,393 — **tất cả** không có Customer ID và price = 0 (điều chỉnh kho) |
| Dòng `C` xảy ra trước lần mua đầu tiên trong data (hoặc khách không có lần mua nào) | 727 |
| Giao dịch cực lớn | 80,995 và 74,215 đơn vị, mỗi dòng bị huỷ bằng một invoice `C` tương ứng |

**Kết luận D19:** trong dataset, cancellation và return **không phân biệt được**. Mọi điều chỉnh âm có Customer ID đều nằm trong invoice `C`. Code gộp chúng thành một loại `adjustment` (hiểu là cancellation/return); `return_rate` được tính từ các invoice `C`.

## 4. Stock code đặc biệt (non-product)

Mã không phải sản phẩm, loại khỏi purchase events và tính riêng:

`POST` (POSTAGE), `DOT` (DOTCOM POSTAGE), `C2` (CARRIAGE), `C3`, `M`/`m` (Manual), `D` (Discount), `S` (SAMPLES), `BANK CHARGES`, `AMAZONFEE`, `CRUK` (Commission), `B` (Adjust bad debt), `ADJUST*`, `TEST*`, `GIFT`, `gift_0001_*` (gift voucher).

Giữ lại như sản phẩm: `DCGS*` (sản phẩm dotcom giftshop), `SP1002`, `PADS` (price 0.001, vẫn > 0), `47503J`.

## 5. Volume theo thời gian và snapshots

- Số invoice mỗi tháng dao động 1,393–3,669, đạt đỉnh vào tháng 11 cả hai năm (mùa Q4).
- Valid orders (có Customer ID, không phải `C`/`A`, qty > 0, price > 0, là sản phẩm): **36,594**.

Eligible customers và prevalence của `repeat_purchase_90d` theo T0 (cửa sổ 180/90 ngày):

| T0 | Eligible | Prevalence | | T0 | Eligible | Prevalence |
|---|---|---|---|---|---|---|
| 2010-06-01 | 2,652 | 0.500 | | 2011-02-01 | 3,348 | 0.397 |
| 2010-07-01 | 2,737 | 0.509 | | 2011-03-01 | 3,338 | 0.424 |
| 2010-08-01 | 2,813 | 0.570 | | 2011-04-01 | 3,299 | 0.439 |
| 2010-09-01 | 2,822 | 0.620 | | 2011-05-01 | 3,047 | 0.478 |
| 2010-10-01 | 2,899 | 0.580 | | 2011-06-01 | 2,658 | 0.500 |
| 2010-11-01 | 3,196 | 0.493 | | 2011-07-01 | 2,722 | 0.516 |
| 2010-12-01 | 3,465 | 0.380 | | 2011-08-01 | 2,766 | 0.557 |
| 2011-01-01 | 3,403 | 0.377 | | 2011-09-01 | 2,768 | 0.607 |

Hệ quả cho code và modeling:

- 16 snapshot hợp lệ, khớp SPEC §5. Split đề xuất: train khoảng 24.0k dòng (8 snapshot), validation khoảng 6.3k, test khoảng 5.5k.
- Prevalence 0.38–0.62, tức **không mất cân bằng nặng**; PR-AUC vẫn phải được so với prevalence baseline.
- **Seasonality rõ rệt:** snapshot có outcome rơi vào Q4 (T0 từ tháng 8–10) có prevalence cao; T0 tháng 12–1 có prevalence thấp. Test (2011-08, 2011-09) có prevalence cao hơn trung bình train (~0.50) → calibration sẽ lệch. Model nên có feature `t0_month` hoặc `outcome_includes_q4`, và model card phải ghi rõ điểm này.
