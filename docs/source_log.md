# Source Log — Topic 1

Yêu cầu capstone (CAP tr.2, tr.11): source URL, download date, license/terms, filters, joins và các quyết định cleaning chính.

## 1. Dataset

| Field | Giá trị |
|---|---|
| Tên | Online Retail II — UCI Machine Learning Repository |
| Trang dataset | <https://archive.ics.uci.edu/dataset/502/online+retail+ii> (hyperlink trong capstone tr.3, tr.11) |
| Download URL | <https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip> |
| Truy cập thay thế | `ucimlrepo.fetch_ucirepo(id=502)` (không dùng trong pipeline) |
| Citation | Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D |
| License | CC BY 4.0 — được chia sẻ và chỉnh sửa cho mọi mục đích, **phải ghi nguồn** (citation ở trên) |
| Mô tả nguồn | Giao dịch 01/12/2009–09/12/2011 của một online retailer (UK, non-store); chủ yếu bán quà tặng; nhiều khách là wholesaler |
| File | `online_retail_ii.zip` → `online_retail_II.xlsx` (2 sheet) |

## 2. Lịch sử tải

| # | Ngày giờ (+07:00) | Người | SHA-256 zip | SHA-256 xlsx | Ghi chú |
|---|---|---|---|---|---|
| 1 | 2026-09-27 | Team (verify) | `572E36277C2390FBFDE10664750731E0A86F55E33470D91919085F0408E67BFB` | `BCBE73B35F5B7BABF197FB0CB983A11F5D9FF929078D4AA53D171B1F2DF2E980` | 45,622,418 / 45,622,278 bytes; khớp config |

Mỗi lần tải lại, **thêm một dòng mới**, không sửa dòng cũ. Nếu checksum khác thì dừng lại, báo M1 và ghi decision log.

## 3. Filters

| Bước | Filter | Rows trước → sau | Nguồn |
|---|---|---|---|
| CR-00 | Bỏ phần trùng giữa 2 sheet (01–09/12/2010 lấy từ sheet 2010-2011) | 1,067,371 → 1,044,848 | D21 |
| CR-07 | Bỏ exact duplicate | 1,044,848 → 1,033,036 | SPEC §4 |
| Line types | purchase 776,596 · adjustment 17,915 · non_product 5,795 · excluded 232,730 | — | Code Spec §3.1 |
| Orders | Chỉ khách có Customer ID; purchase 36,594 · adjustment 7,283 | — | Code Spec §3.1 |
| Snapshots | Khách có ≥ 1 purchase trong 180 ngày trước T0; 16 T0 | 47,933 rows | SPEC §5 |

Các số trên đã được pipeline chính thức tái tạo chính xác (2026-09-27, Docker): `outputs/reports/cleaning_log.csv`, `reconciliation.csv` (3/3 PASS), `run_manifest.json`. Giá trị (£) bị ảnh hưởng theo rule: CR-07 £54,228 · CR-05 −£147,614 · CR-05b £75,749 · adjustment −£716,463 · CR-06 (không ID) £2,575,279 · purchase lines £17,068,583. Snapshot targeting (D29): loại thêm 16 customer-snapshot có monetary_net ≤ 0 ở test.

## 4. Joins

Không có. MVP không join dataset ngoài (capstone R23: không ghép dataset không liên quan).

## 5. Quyết định cleaning chính

SPEC §4 (bảng CR-00…CR-12), decision log D04, D19, D21, D23, D27.
