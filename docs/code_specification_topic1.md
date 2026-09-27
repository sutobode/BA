# Code Specification v1.0 — Topic 1

**Customer Value & Promotion Targeting for an Online Retailer**

| Metadata | Giá trị |
|---|---|
| Căn cứ | `project_specification_topic1.md` (SPEC), `implementation_plan_topic1.md` (PLAN), `data_profile_topic1.md` (PROFILE — số liệu thật), `decision_log_topic1.md` |
| Package | `retail_targeting` (thư mục `src/retail_targeting/`) |
| Python | 3.13; dependencies pinned trong `requirements.txt` |
| Trạng thái scaffold | Foundation đã implement (`config`, `contracts`, `decision.simulation.compute_eim`). Các module còn lại là stub có signature + docstring, và đã có test viết trước (test-first) |

Mục tiêu của tài liệu: một thành viên đọc xong có thể code module mình phụ trách mà **không phải tự quyết định** tên cột, kiểu dữ liệu, quy tắc hay đường dẫn. Khi code gặp tình huống spec chưa nói tới, phải ghi vào decision log trước rồi mới code.

---

## 1. Nguyên tắc kỹ thuật

1. **Logic nằm trong `src/`, notebook chỉ gọi hàm và vẽ biểu đồ.** Không copy logic cleaning/feature vào notebook.
2. **Single source of truth:** mỗi artifact chỉ có một hàm sinh ra (§5). Consumer không tính lại cột của producer.
3. **Config-driven:** mọi hằng số nghiệp vụ (window, split, danh sách mã, tham số scenario, seed) đọc từ `project_config.yaml`. Không hard-code trong code.
4. **Leakage-safe by construction:** hàm tạo feature chỉ nhận dữ liệu đã lọc `< T0`. Có assertion trong code và test phủ định (negative test).
5. **Deterministic:** cùng config và cùng raw file ⇒ cùng output byte-for-byte với CSV. Mọi random dùng `numpy.random.default_rng(seed)`; sort ổn định với khoá phụ cuối cùng là `customer_id`.
6. **Pure functions ưu tiên:** hàm nhận DataFrame và config, trả DataFrame, không đọc/ghi file. I/O chỉ nằm trong `io.py` và `pipeline.py`.
7. **Fail loudly:** vi phạm contract phải raise `ContractError`, vi phạm config phải raise `ConfigError`. Không nuốt exception.
8. Type hints đầy đủ; docstring nêu input, output và invariant; dùng `logging` (không dùng `print`) trong `src/`.

---

## 2. Cấu trúc repository

```text
BA/
├── pyproject.toml              # package metadata + pytest config (pythonpath=src,tests)
├── requirements.txt            # pinned
├── project_config.example.yaml # template (commit)
├── project_config.yaml         # config chạy thật (commit; không chứa secret)
├── README.md
├── data/
│   ├── raw/                    # gitignored: online_retail_ii.zip, online_retail_II.xlsx
│   ├── interim/                # gitignored: transactions_raw.parquet, lines.parquet, orders.parquet
│   └── processed/              # gitignored: customer_snapshots.parquet, rfm_segments.parquet
├── outputs/
│   ├── tables/                 # CSV deliverables (commit bản final)
│   ├── figures/
│   ├── models/                 # model_v{n}.joblib + metadata json
│   └── reports/                # data_quality_report.md, run_manifest.json, test_access_log.jsonl
├── scripts/profiling/          # script profiling ban đầu (tham khảo)
├── src/retail_targeting/
│   ├── __init__.py
│   ├── config.py               # [IMPLEMENTED] load + validate config
│   ├── contracts.py            # [IMPLEMENTED] schema artifact + validate_frame
│   ├── io.py                   # đọc/ghi parquet/csv, manifest
│   ├── pipeline.py             # orchestration các stage
│   ├── cli.py                  # entrypoint `python -m retail_targeting`
│   ├── __main__.py
│   ├── data/
│   │   ├── ingest.py           # download, checksum, đọc 2 sheet, CR-00, cache
│   │   ├── clean.py            # CR-01..CR-12, lines, orders
│   │   └── quality.py          # profiling, reconciliation, DQ report
│   ├── features/
│   │   ├── snapshots.py        # T0 dates, observation/outcome, features, target
│   │   ├── rfm.py              # cutoffs (fit train), scores, segments
│   │   └── cohort.py           # cohort retention
│   ├── models/
│   │   ├── split.py            # gán split, purge, kiểm tra
│   │   ├── train.py            # benchmark, LR pipeline, tuning
│   │   ├── calibrate.py        # calibration trên validation
│   │   └── evaluate.py         # metrics, top-K, reliability, theo nhóm
│   └── decision/
│       ├── simulation.py       # [IMPLEMENTED compute_eim] ScenarioParams, EIM
│       ├── policy.py           # policy A/B/C/D, capacity/budget
│       └── sensitivity.py      # grid
├── dashboard/app.py            # Streamlit (W5), chỉ đọc outputs/tables
├── notebooks/01..09_*.ipynb
└── tests/
    ├── conftest.py             # fixtures dữ liệu tổng hợp có đáp án
    ├── helpers.py              # marker `todo`
    ├── test_config.py  test_contracts.py  test_simulation.py
    ├── test_ingest.py  test_cleaning.py  test_snapshots.py  test_leakage.py
    ├── test_rfm.py  test_split.py  test_evaluate.py  test_policy.py
```

---

## 3. Dữ liệu thật mà code phải xử lý (từ PROFILE)

| Hạng mục | Thực tế | Hệ quả trong code |
|---|---|---|
| File | `online_retail_II.xlsx`, 2 sheet `Year 2009-2010`, `Year 2010-2011` | `ingest.read_raw_excel` đọc cả hai sheet |
| Cột gốc | `Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country` | `clean.standardize_columns` đổi sang snake_case (§4.2) |
| Thời gian đọc xlsx | ~161 s | Cache parquet ở `data/interim/transactions_raw.parquet`; chỉ đọc lại khi checksum đổi |
| Overlap sheet | 2010-12-01 → 2010-12-09 có ở cả 2 sheet, 22,523 dòng giống hệt | CR-00 cắt theo `sheet_boundary` |
| Duplicate exact | 11,812 sau CR-00 | CR-07 `drop_duplicates()` |
| `Customer ID` | float, thiếu 22.76% dòng | Đổi sang string `"12346"`; thiếu → `<NA>` |
| Invoice `C` | 19,104 dòng (cancellation/return, gộp chung) | `line_type="adjustment"` |
| Invoice `A` | 6 dòng "Adjust bad debt", price âm | `excluded`, reason `bad_debt_adjustment` |
| Quantity âm không có `C` | 3,393 dòng, đều không ID, price 0 | `excluded`, reason `stock_adjustment` |
| Price = 0 | 6,014 dòng | `excluded`, reason `zero_price` (nếu không phải adjustment) |
| Mã non-product | POST, DOT, C2, M, D, S, BANK CHARGES, AMAZONFEE, … | `line_type="non_product"`, không tính vào value |
| Invoice nhiều timestamp | 83 | `order_ts = min(invoice_ts)` |
| Invoice nhiều customer | 0 | Assert trong `build_orders` |
| Prevalence target | 0.38–0.62 theo T0, có seasonality | Feature mùa vụ `t0_month_sin/cos` (D22) |

### 3.1 Con số tham chiếu trên data thật (acceptance cho implementation)

Các giá trị dưới đây thu được bằng cách chạy một reference implementation đúng theo §6 trên file thật (2026-09-27). Reference này chỉ để kiểm chứng spec, không commit. Code của nhóm phải ra **đúng các số này**; nếu khác, hoặc code sai, hoặc spec cần đổi (ghi decision log).

| Bước | Giá trị |
|---|---|
| `load_raw` (sau CR-00) | 1,044,848 dòng |
| `lines` (sau CR-07) | 1,033,036 dòng: purchase 776,596 · excluded 232,730 · adjustment 17,915 · non_product 5,795 |
| `exclude_reason` | missing_customer 226,761 · stock_adjustment 3,391 · zero_price 2,572 · bad_debt_adjustment 6 |
| INV-03 | Σ line_value raw (sau CR-07) − Σ theo line_type = 0.0 |
| `orders` | purchase 36,594 · adjustment 7,283 · purchase bị loại vì value ≤ 0: 0 |
| `generate_t0_dates` | 16 ngày, 2010-06-01 … 2011-09-01 |
| `customer_snapshots` | 47,933 dòng: train 23,987 · validation 6,346 · test 5,534 · purged 12,066 |
| Prevalence theo T0 | khớp bảng `data_profile_topic1.md` §5 (0.500 … 0.607) |
| `aov ≤ 0` | 149 dòng → dùng fallback (D23) |
| `monetary_net < 0` | 34 dòng |
| `avg_interpurchase_days` NaN | 21,884 dòng (khách chỉ có 1 order) → imputer median |
| Thời gian ingest→snapshots (từ cache) | ~2 phút với cách groupby/apply đơn giản; tối ưu nếu cần |

Ghi chú: `stock_adjustment` là 3,391 chứ không phải 3,393 như trong profile, vì 2 dòng quantity âm có mã non-product đã được CR-05b xếp loại trước.

---

## 4. Configuration (`project_config.yaml`)

### 4.1 Schema

Được `config.load_config()` validate; sai một trường sẽ raise `ConfigError` và báo tên trường.

| Key | Type | Ràng buộc | Dùng ở |
|---|---|---|---|
| `project.random_seed` | int | ≥ 0 | mọi random |
| `paths.*` | str | tương đối so với root repo | `io` |
| `source.url`, `download_url`, `sha256_zip`, `sha256_xlsx` | str | sha256 là 64 hex | `ingest` |
| `source.sheets` | list[str] | 2 tên sheet | `ingest` |
| `source.sheet_boundary` | date | `2010-12-01` | CR-00 |
| `cleaning.non_product_codes` | list[str] | so khớp chính xác (case-sensitive) | CR-05b |
| `cleaning.non_product_prefixes` | list[str] | so khớp `startswith` | CR-05b |
| `cleaning.cancellation_prefix` | str | `"C"` | CR-01 |
| `cleaning.bad_debt_prefix` | str | `"A"` | CR-05 |
| `temporal.snapshot_cadence` | str | chỉ hỗ trợ `monthly` | snapshots |
| `temporal.observation_days` / `outcome_days` / `purge_days` | int | > 0; `purge_days ≥ outcome_days` | snapshots, split |
| `temporal.target_name` | str | phải bằng `repeat_purchase_{outcome_days}d` | snapshots |
| `temporal.train/validation/test_snapshots` | list[date] | ngày 1 của tháng, tăng dần, rời nhau, purge hợp lệ | split |
| `segmentation.n_bins` | int | 5 | rfm |
| `segmentation.rules` | list[dict] | có ít nhất một rule `default` | rfm |
| `model.numeric_features`, `model.categorical_features` | list[str] | ⊆ cột feature của `customer_snapshots`, không chứa cột `label_*` | train |
| `model.log1p_features` | list[str] | ⊆ numeric | train |
| `model.C_grid`, `class_weight_options` | list | | train |
| `model.calibration` | str | `none` \| `sigmoid` \| `isotonic` | calibrate |
| `model.top_k_fractions` | list[float] | (0, 1] | evaluate |
| `simulation.scenarios.<name>` | dict | `0 ≤ d < m ≤ 1`, `0 ≤ δ ≤ 1`, `c ≥ 0`; ≥ 3 scenario | simulation |
| `simulation.capacity_fractions` | list[float] | (0, 1] | policy |
| `simulation.budget` | float \| null | > 0 nếu có | policy |
| `simulation.random_baseline_seeds` | int | ≥ 1 (spec: 100) | policy B |
| `simulation.value_fallback` | str | `median_aov_by_segment_train` | simulation |
| `versions.*` | str | | mọi artifact |

Tham số scenario còn `null` là hợp lệ khi load; chỉ `decision.*` mới yêu cầu giá trị cụ thể (`require_scenarios=True`). Nhờ vậy M1/M2 chạy được pipeline trước khi D10/D11 được freeze.

### 4.2 Chuẩn hoá tên cột (raw → canonical)

| Raw | Canonical | dtype sau chuẩn hoá |
|---|---|---|
| `Invoice` | `invoice` | `string` |
| `StockCode` | `stock_code` | `string` (strip) |
| `Description` | `description` | `string` |
| `Quantity` | `quantity` | `int64` |
| `InvoiceDate` | `invoice_ts` | `datetime64[ns]` |
| `Price` | `price` | `float64` |
| `Customer ID` | `customer_id` | `string` — `str(int(x))`, `<NA>` nếu thiếu |
| `Country` | `country` | `string` |
| *(thêm)* | `source_sheet` | `string` |

---

## 5. Data contracts (artifact)

Được định nghĩa trong `contracts.py` (`SCHEMAS`). `validate_frame(df, name)` kiểm tra: đủ cột, đúng dtype family, cột non-null không có null, key unique, và các `checks` riêng. Cột thừa được phép, trừ khi schema đặt `strict=True`.

| Artifact | Producer (hàm) | File | Key | Owner |
|---|---|---|---|---|
| `transactions_raw` | `ingest.load_raw` | `data/interim/transactions_raw.parquet` | — | M1 |
| `lines` | `clean.clean_transactions` | `data/interim/lines.parquet` | — | M1 |
| `orders` | `clean.build_orders` | `data/interim/orders.parquet` | `order_id` | M1 |
| `customer_snapshots` | `snapshots.build_all_snapshots` + `rfm.apply_*` + `split.assign_split` | `data/processed/customer_snapshots.parquet` | `customer_id, decision_date` | M1 (M2 thêm cột `split`) |
| `customer_predictions` | `train/calibrate` + `pipeline.predict_stage` | `outputs/tables/customer_predictions.csv` | `customer_id, decision_date` | M2 |
| `scenario_results` | `policy.run_policies` | `outputs/tables/scenario_results.csv` | `scenario, policy, decision_date, capacity_k, seed, value_basis` | M3 |
| `policy_comparison` | `policy.summarize` | `outputs/tables/policy_comparison.csv` | `scenario, policy, capacity_fraction, value_basis` | M3 |
| `sensitivity_results` | `sensitivity.run_grid` | `outputs/tables/sensitivity_results.csv` | grid keys | M3 |
| `customer_targeting_table` | `policy.build_targeting_table` | `outputs/tables/customer_targeting_table.csv` | `customer_id, decision_date, scenario, policy` | M3 |

### 5.1 `lines` (line-level, sau cleaning)

| Cột | dtype | Null | Mô tả |
|---|---|---|---|
| invoice, stock_code, description, country, source_sheet | string | description có thể null | từ raw |
| quantity | int64 | không | |
| invoice_ts | datetime64[ns] | không | |
| price | float64 | không | |
| customer_id | string | **có** | |
| line_value | float64 | không | `quantity × price` |
| line_type | string | không | `purchase` \| `adjustment` \| `non_product` \| `excluded` |
| exclude_reason | string | null khi không excluded | `missing_customer` \| `zero_price` \| `stock_adjustment` \| `bad_debt_adjustment` \| `invalid_quantity` |

Checks: `line_type=="purchase"` ⇒ `quantity>0 & price>0 & customer_id notna`; `line_type=="adjustment"` ⇒ invoice bắt đầu bằng `cancellation_prefix`.

Ghi chú: dòng thiếu `customer_id` vẫn giữ trong `lines` (với `excluded/missing_customer`) để tính coverage và revenue share. Chúng không đi vào `orders`.

### 5.2 `orders` (order-level, chỉ khách có ID, chỉ dòng sản phẩm)

| Cột | dtype | Mô tả |
|---|---|---|
| order_id | string | = invoice |
| customer_id | string | non-null |
| order_ts | datetime64[ns] | `min(invoice_ts)` |
| order_type | string | `purchase` \| `adjustment` |
| order_value | float64 | tổng `line_value`: > 0 với purchase, < 0 với adjustment |
| n_lines, n_units, n_products | int64 | n_units = Σ\|quantity\| |
| country | string | mode của các dòng |

Checks: key unique; mỗi order chỉ có 1 customer; purchase ⇒ `order_value > 0`; adjustment ⇒ `order_value < 0`. Order purchase có value ≤ 0 sau khi gộp sẽ bị loại và được ghi log.

**Valid purchase event** = một dòng `orders` có `order_type=="purchase"`.

### 5.3 `customer_snapshots`

Key `(customer_id, decision_date)`. Observation window `W_obs = [T0 − observation_days, T0)`; outcome `W_out = [T0, T0 + outcome_days)`.

| Cột | dtype | Công thức (chỉ dùng orders trong cửa sổ nêu) | Vai trò |
|---|---|---|---|
| customer_id | string | | key |
| decision_date | datetime64[ns] | T0 | key |
| recency_days | float64 | `(T0 − max order_ts purchase ∈ W_obs) / 1 day` | feature |
| frequency_orders | int64 | số purchase orders ∈ W_obs (≥ 1 do eligibility) | feature |
| purchase_value | float64 | Σ order_value purchase ∈ W_obs | feature |
| adjustment_value | float64 | Σ \|order_value\| adjustment ∈ W_obs (≥ 0) | feature |
| monetary_net | float64 | `purchase_value − adjustment_value` (có thể âm) | feature |
| aov | float64 | `monetary_net / frequency_orders` | feature, value proxy |
| return_rate | float64 | `min(adjustment_value / purchase_value, 1.0)` | feature |
| tenure_days | float64 | `(T0 − first purchase order_ts < T0) / 1 day` — dùng toàn bộ lịch sử trước T0 | feature |
| active_months | int64 | số tháng khác nhau có purchase ∈ W_obs | feature |
| avg_interpurchase_days | float64 | trung bình diff các order_ts purchase ∈ W_obs; NaN nếu 1 order | feature |
| unique_products | int64 | distinct stock_code (purchase lines ∈ W_obs) | feature |
| total_units | int64 | Σ quantity purchase lines ∈ W_obs | feature |
| orders_last_30d | int64 | purchase ∈ `[T0−30d, T0)` | feature |
| t0_month_sin, t0_month_cos | float64 | `sin/cos(2π·month(T0)/12)` — lịch, không leakage | feature (D22) |
| cohort_month | string | `YYYY-MM` của first purchase < T0 | descriptive |
| country | string | country của order gần nhất < T0 | descriptive (không dùng làm feature MVP, xem ethics) |
| repeat_purchase_90d | int8 | 1 nếu có ≥ 1 purchase order ∈ W_out | **target** |
| label_future_value_90d | float64 | Σ order_value purchase ∈ W_out | label, chỉ để đánh giá/stretch S2 |
| r_score, f_score, m_score | int8 | 1–5, cutoffs fit trên train (§6.6) | segmentation, benchmark |
| rfm_score | int8 | r+f+m (3–15) | benchmark |
| customer_segment | string | rule §6.6 | segmentation |
| split | string | `train` \| `validation` \| `test` \| `purged` \| `unused` | M2 |
| feature_version | string | từ config | trace |

Eligibility: khách có ≥ 1 purchase order ∈ W_obs. Cột có tiền tố `label_` và cột target **không bao giờ** được nằm trong `model.*_features` (`config` kiểm tra điều này).

### 5.4 `customer_predictions`

`customer_id, decision_date, split, actual_repeat_purchase:int8, rfm_benchmark_score:float64, predicted_repeat_probability_raw:float64, predicted_repeat_probability:float64 (calibrated), model_version, feature_version`. Check: xác suất ∈ [0, 1].

### 5.5 `customer_targeting_table` (deliverable "customer-level score table")

`customer_id, decision_date, scenario, scenario_version, policy, customer_segment, recency_days, frequency_orders, monetary_net, rfm_score, repeat_purchase_probability, customer_value_proxy, value_is_fallback:bool, discount_rate, incremental_lift_assumption, gross_margin, contact_cost, expected_promotion_cost, simulated_expected_incremental_margin, target_rank:Int64 (null nếu không target), recommended_action ∈ {TARGET, DO_NOT_TARGET}, model_version`.

Check: số `TARGET` ≤ `capacity_k` cho mỗi `(decision_date, scenario, policy)`; policy D ⇒ mọi TARGET có EIM > 0.

### 5.6 `scenario_results`

`scenario, scenario_version, policy{A,B,C,D}, decision_date, value_basis{model_p, actual_outcome}, capacity_fraction, capacity_k, budget, seed (Int64, chỉ B), target_count, expected_future_value, expected_promotion_cost, simulated_eim, eim_per_target, discount_leakage_share, actual_repeat_rate_targeted`.

---

## 6. Đặc tả module

Ký hiệu: `cfg` là đối tượng `Config` (dataclass bất biến, truy cập `cfg.temporal.observation_days` …).

### 6.1 `config.py` — IMPLEMENTED (owner M2)

```python
class ConfigError(ValueError): ...
@dataclass(frozen=True) class Config: raw: dict; root: Path  # + các section truy cập qua thuộc tính
def load_config(path: str | Path = "project_config.yaml", *, require_scenarios: bool = False) -> Config
def validate_config(raw: dict, *, require_scenarios: bool = False) -> None
def config_hash(cfg: Config) -> str          # sha256 của YAML đã canonical hoá (cho manifest)
def resolve_path(cfg: Config, key: str) -> Path   # paths.<key> → tuyệt đối
```

### 6.2 `contracts.py` — IMPLEMENTED (owner M2)

```python
class ContractError(ValueError): ...
@dataclass(frozen=True) class ColumnSpec: name: str; dtype: str; nullable: bool = False
@dataclass(frozen=True) class Schema: name: str; columns: tuple[ColumnSpec, ...]; key: tuple[str, ...] = (); strict: bool = False
SCHEMAS: dict[str, Schema]
def validate_frame(df: pd.DataFrame, name: str) -> pd.DataFrame   # trả lại df để chain; raise ContractError liệt kê mọi lỗi
```

dtype family: `string`, `int`, `float`, `datetime`, `bool`, `category_or_string`.

### 6.3 `data/ingest.py` (owner M1, task T1.2/T2.1)

```python
def download_raw(cfg: Config, *, force: bool = False) -> Path
    # tải download_url về paths.raw_dir; bỏ qua nếu file đã có và checksum khớp; giải nén xlsx
def sha256_file(path: Path, chunk: int = 1 << 20) -> str
def verify_checksum(path: Path, expected: str) -> None          # raise ChecksumError
def read_raw_excel(xlsx: Path, sheets: list[str]) -> dict[str, pd.DataFrame]
    # dtype={"Invoice": str, "StockCode": str}; không sửa dữ liệu
def combine_sheets(sheets: dict[str, pd.DataFrame], boundary: pd.Timestamp, sheet_order: list[str]) -> pd.DataFrame
    # CR-00: sheet[0] lấy InvoiceDate < boundary; sheet[1] lấy >= boundary; thêm source_sheet
    # log số dòng bị bỏ do overlap (kỳ vọng 22,523)
def load_raw(cfg: Config, *, use_cache: bool = True) -> pd.DataFrame
    # verify checksum → cache parquet (tên cache chứa 12 ký tự đầu sha256_xlsx) → combine_sheets
```

Kỳ vọng trên data thật: `len(load_raw(cfg)) == 1_044_848`.

### 6.4 `data/clean.py` (owner M1, task T2.1)

```python
def standardize_columns(raw: pd.DataFrame) -> pd.DataFrame           # §4.2
def classify_lines(df: pd.DataFrame, cfg: Config) -> pd.DataFrame      # thêm line_value, line_type, exclude_reason
def clean_transactions(raw: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]
    # trả (lines, cleaning_log); cleaning_log: rule_id, description, rows_before, rows_after,
    #   rows_affected, value_affected, customers_affected
def build_orders(lines: pd.DataFrame) -> pd.DataFrame                  # §5.2
def is_non_product(stock_code: pd.Series, codes: list[str], prefixes: list[str]) -> pd.Series
```

**Thứ tự quy tắc** trong `classify_lines` (áp theo thứ tự, dòng nào đã có loại thì không xét lại):

| Thứ tự | Rule | Điều kiện | Kết quả |
|---|---|---|---|
| 1 | CR-07 | exact duplicate (trên cột raw) | bỏ khỏi frame (ghi log) |
| 2 | CR-08 | `invoice_ts` null | `excluded/invalid_date` |
| 3 | CR-05 bad debt | invoice bắt đầu `A` | `excluded/bad_debt_adjustment` |
| 4 | CR-05b non-product | `is_non_product(stock_code)` | `non_product` |
| 5 | CR-01/02 | invoice bắt đầu `C` | `adjustment` (nếu `quantity>0` → `excluded/invalid_quantity`) |
| 6 | CR-04 | `quantity < 0` (không phải C) | `excluded/stock_adjustment` |
| 7 | CR-05 | `price <= 0` | `excluded/zero_price` |
| 8 | CR-06 | `customer_id` null | `excluded/missing_customer` |
| 9 | — | còn lại | `purchase` |

Lưu ý: CR-06 đứng sau các quy tắc về loại dòng, nên cleaning log vẫn tách được cancellation không có ID. `build_orders` chỉ nhận dòng `purchase` và `adjustment` có `customer_id`. Adjustment không có ID sẽ bị ghi log là `excluded/missing_customer` trong bước này.

CR-11 (extreme values): **không** xử lý ở cleaning. Giao dịch 80,995/74,215 đơn vị đã được invoice `C` bù trừ, nên `monetary_net` tự triệt tiêu. Winsorize (nếu có) chỉ làm trong pipeline model.

### 6.5 `data/quality.py` (owner M1, task T1.3/T2.3)

```python
def profile_raw(raw: pd.DataFrame) -> dict            # các chỉ số của PROFILE §1–§5
def customer_coverage(lines: pd.DataFrame) -> pd.DataFrame   # theo tháng & country: rows, % missing id, % revenue missing id
def reconcile(raw: pd.DataFrame, lines: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame
    # tổng value raw = Σ theo line_type; Σ orders = Σ lines(purchase+adjustment có id); sai số < 0.01
def write_quality_report(profile: dict, coverage: pd.DataFrame, cleaning_log: pd.DataFrame, path: Path) -> None
```

### 6.6 `features/snapshots.py` (owner M1, task T2.4/T3.1)

```python
def generate_t0_dates(data_start: pd.Timestamp, data_end: pd.Timestamp, cfg: Config) -> list[pd.Timestamp]
    # ngày 1 của tháng; T0 >= data_start + observation_days; T0 + outcome_days <= data_end
    # data thật → 16 ngày 2010-06-01..2011-09-01
def build_snapshot(orders: pd.DataFrame, lines: pd.DataFrame, t0: pd.Timestamp, cfg: Config) -> pd.DataFrame
    # 1) hist = orders[order_ts < t0]; obs = hist[order_ts >= t0 - obs_days]
    # 2) assert obs.order_ts.max() < t0 (LeakageError)
    # 3) features chỉ từ hist/obs (§5.3); product features từ lines purchase trong obs
    # 4) target, label từ orders[t0 <= order_ts < t0 + out_days], không join ngược vào feature
def build_all_snapshots(orders, lines, cfg) -> pd.DataFrame     # concat các T0 trong train+validation+test (+ unused)
class LeakageError(AssertionError): ...
```

Hàm tính feature nhận `hist` đã lọc (tức chữ ký `_compute_features(hist_orders, obs_lines, t0, cfg)`), nên không thể "vô tình" nhìn thấy dữ liệu tương lai.

### 6.7 `features/rfm.py` (owner M1, task T3.2)

```python
def fit_rfm_cutoffs(train: pd.DataFrame, n_bins: int = 5) -> dict[str, list[float]]
    # quantile edges trên toàn bộ dòng split=="train"; loại edge trùng (np.unique)
def apply_rfm_scores(df: pd.DataFrame, cutoffs: dict) -> pd.DataFrame
    # score = 1 + searchsorted(edges, x, side="right"), clip 1..n_bins
    # recency: đảo chiều (recency nhỏ → r_score cao); f dùng frequency_orders; m dùng monetary_net
def assign_segments(df: pd.DataFrame, rules: list[dict]) -> pd.Series   # đánh giá theo thứ tự, rule đầu khớp thắng
```

Rule mặc định (config `segmentation.rules`, đầy đủ và loại trừ nhau):

1. `m>=4 & r>=4` → `High-value active`
2. `m>=4 & r<=2` → `High-value at risk`
3. `r>=3 & (m>=3 | f>=3)` → `Developing`
4. `r>=3` → `Low-value active`
5. `default` → `Dormant`

Cutoffs được lưu vào `outputs/models/rfm_cutoffs.json` và áp nguyên cho validation/test.

### 6.8 `features/cohort.py` (owner M1, task T3.3)

```python
def cohort_retention(orders: pd.DataFrame, max_age_months: int = 12) -> pd.DataFrame
    # cohort_month × age_month → n_customers_active, retention_rate; cờ left_censored cho cohort 2009-12
```

### 6.9 `models/split.py` (owner M2, task T2.5)

```python
def assign_split(snapshots: pd.DataFrame, cfg: Config) -> pd.Series
    # train/validation/test theo config; T0 hợp lệ nhưng không nằm trong list → "purged" nếu nằm giữa các split, ngược lại "unused"
def check_split_config(cfg: Config) -> None
    # tăng dần, rời nhau, max(train)+purge_days <= min(val), max(val)+purge_days <= min(test)
```

### 6.10 `models/train.py` (owner M2, task T2.7/T3.4)

```python
def feature_matrix(df: pd.DataFrame, cfg: Config) -> pd.DataFrame   # chỉ cột whitelist; raise nếu thiếu
def rfm_benchmark_score(df: pd.DataFrame) -> pd.Series                # rfm_score + 1e-3·r_score (tie-break), dùng làm score
def build_pipeline(cfg: Config, *, C: float, class_weight) -> sklearn.pipeline.Pipeline
    # ColumnTransformer: log1p (signed cho monetary_net/aov) → SimpleImputer(median) → StandardScaler
    # LogisticRegression(C, class_weight, max_iter=2000, random_state=seed)
def tune_logreg(train: pd.DataFrame, val: pd.DataFrame, cfg: Config) -> tuple[Pipeline, pd.DataFrame]
    # grid C × class_weight; fit trên train; chọn theo PR-AUC validation (tie → Brier thấp hơn);
    # trả model (fit trên train) + bảng kết quả grid
def save_model(model, meta: dict, cfg: Config) -> Path               # joblib + json (features, C, dates, metrics, versions)
```

Signed log: `sign(x)·log1p(|x|)`.

### 6.11 `models/calibrate.py` (owner M2, task T4.1)

```python
def calibrate(model: Pipeline, val: pd.DataFrame, cfg: Config) -> object
    # method = cfg.model.calibration; "none" → trả model
    # else CalibratedClassifierCV(FrozenEstimator(model), method=...).fit(X_val, y_val)
```

Calibration fit trên validation, do đó metric validation sau calibration là in-sample. Chỉ số của test mới là số dùng để báo cáo.

### 6.12 `models/evaluate.py` (owner M2, task T3.4/T4.2)

```python
def classification_metrics(y: np.ndarray, score: np.ndarray, top_k_fractions: list[float]) -> dict
    # prevalence, pr_auc (average_precision), roc_auc, brier*, log_loss*, và với mỗi k:
    # precision_at_k, recall_at_k, lift_at_k  (*chỉ khi score ∈ [0,1])
def reliability_table(y, p, n_bins: int = 10, strategy: str = "quantile") -> pd.DataFrame
def metrics_by_group(df: pd.DataFrame, score_col: str, group_col: str, cfg) -> pd.DataFrame  # segment/cohort/decision_date
def log_test_access(cfg: Config, what: str) -> None   # append JSONL outputs/reports/test_access_log.jsonl
```

top-K: sắp xếp score giảm dần, tie-break theo `customer_id`, `k = max(1, floor(frac·n))`.

### 6.13 `decision/simulation.py` (owner M3; `compute_eim` IMPLEMENTED)

```python
@dataclass(frozen=True) class ScenarioParams:
    name: str; discount_rate: float; incremental_lift: float; gross_margin: float; contact_cost: float; version: str = "v0"
    def validate(self) -> None                 # 0 ≤ d < m ≤ 1; 0 ≤ δ ≤ 1; c ≥ 0
def scenarios_from_config(cfg: Config) -> list[ScenarioParams]      # raise ConfigError nếu còn null
def compute_eim(p: ArrayLike, value: ArrayLike, params: ScenarioParams) -> pd.DataFrame
    # delta_i = min(δ, 1 - p); m0 = p·V·m; m1 = (p+δ_i)·V·(m-d) - c
    # eim = m1 - m0; expected_cost = (p+δ_i)·V·d + c; expected_value = (p+δ_i)·V; leakage_discount = p·V·d
def fit_value_fallback(train: pd.DataFrame) -> dict[str, float]    # median aov>0 theo segment trên train (+ "__all__")
def value_proxy(df: pd.DataFrame, fallback: dict) -> tuple[pd.Series, pd.Series]
    # V = aov nếu aov > 0, ngược lại fallback[segment]; trả (V, value_is_fallback)
```

### 6.14 `decision/policy.py` (owner M3, task T2.8/T4.4/T4.5)

```python
def capacity_from_fraction(n_eligible: int, frac: float) -> int                 # floor, tối thiểu 1
def select_policy_a(frame) -> np.ndarray[bool]
def select_policy_b(frame, k: int, seed: int) -> np.ndarray[bool]               # rng.choice không lặp
def select_policy_c(frame, k: int) -> np.ndarray[bool]                          # top-k rfm_score, tie: monetary_net desc, customer_id asc
def select_policy_d(frame, k: int, budget: float | None) -> np.ndarray[bool]     # eim>0, eim desc, customer_id asc; dừng khi đủ k hoặc Σcost vượt budget
def summarize_selection(frame, selected, value_basis: str) -> dict               # các cột §5.6
def run_policies(scored: pd.DataFrame, scenarios, cfg, *, value_basis: str) -> pd.DataFrame
def build_targeting_table(scored, selections, scenario, cfg) -> pd.DataFrame     # §5.5
```

**Tránh vòng lặp tự đánh giá (bắt buộc).** Policy D chọn khách bằng EIM tính từ `p` của model. Nếu cũng đánh giá bằng chính EIM đó, D thắng theo định nghĩa. Vì vậy `run_policies` phải chạy với hai `value_basis`:

- `model_p`: EIM tính với `p = predicted_repeat_probability` — expected value **theo niềm tin của model**, dùng cho planning.
- `actual_outcome` (chỉ trên validation/test): **lựa chọn** vẫn dựa trên `p` của model, nhưng **đánh giá** thay `p` bằng `y = actual_repeat_purchase` trong công thức. Khi đó `δ_i = min(δ, 1 − y)`: khách vốn tự mua (y = 1) không có incremental và discount của họ tính là leakage. Đây là số liệu chính để so sánh policy A/B/C/D.

Cả hai vẫn là **simulation dưới assumption δ**, không phải causal estimate.

### 6.15 `decision/sensitivity.py` (owner M3, task T5.1)

```python
def run_grid(scored: pd.DataFrame, base: ScenarioParams, grid: dict[str, list[float]], cfg) -> pd.DataFrame
    # tích Descartes discount_rate × incremental_lift × capacity_fractions (+ gross_margin, contact_cost nếu có)
    # policy B: mean + p5 + p95 trên n seeds; value_basis="actual_outcome" cho test
def break_even(grid_df: pd.DataFrame) -> pd.DataFrame    # vùng tham số mà D ≤ B
```

### 6.16 `io.py`, `pipeline.py`, `cli.py`

```python
# io.py
def read_parquet(path) / write_parquet(df, path, *, schema: str | None)   # validate_frame trước khi ghi
def write_csv(df, path, *, schema: str | None)                            # float_format="%.6f", sort theo key
def write_manifest(cfg, stage: str, outputs: list[Path]) -> None          # config_hash, git commit, package versions, timestamp, sha256 outputs
# pipeline.py — mỗi stage đọc input từ đĩa, ghi output, gọi write_manifest
def stage_ingest(cfg); stage_clean(cfg); stage_snapshots(cfg); stage_train(cfg)
def stage_evaluate(cfg, *, include_test: bool = False); stage_simulate(cfg); stage_sensitivity(cfg)
STAGES: dict[str, Callable]
```

CLI:

```text
python -m retail_targeting run <stage|all> [--config project_config.yaml] [--force]
python -m retail_targeting validate-config [--config ...] [--require-scenarios]
python -m retail_targeting check <artifact_name>        # validate_frame trên file đã ghi
```

`all` = `ingest → clean → snapshots → train → evaluate → simulate → sensitivity`. Test set chỉ được đánh giá khi truyền `--include-test` và mọi lượt đọc đều ghi vào `test_access_log.jsonl`.

---

## 7. Runtime invariants (phải có trong code)

| ID | Invariant | Nơi kiểm tra |
|---|---|---|
| INV-01 | `sha256(xlsx) == cfg.source.sha256_xlsx` | `ingest.load_raw` |
| INV-02 | Sau CR-00 không còn dòng trùng giữa 2 sheet | `combine_sheets` |
| INV-03 | Σ line_value raw = Σ theo line_type (±0.01) | `quality.reconcile` |
| INV-04 | Mỗi order có đúng 1 customer | `build_orders` |
| INV-05 | Feature chỉ từ `order_ts < T0` | `build_snapshot` (LeakageError) |
| INV-06 | Target chỉ từ `[T0, T0+out)` | `build_snapshot` |
| INV-07 | Model features ∩ (target ∪ `label_*`) = ∅ | `config.validate_config`, `train.feature_matrix` |
| INV-08 | Split tăng dần + purge | `split.check_split_config` |
| INV-09 | Preprocessing/RFM cutoffs/value fallback chỉ fit trên `split=="train"` | `train`, `rfm`, `simulation` (assert tập T0 dùng để fit) |
| INV-10 | `eim == m1 − m0` (tolerance 1e-9) | `compute_eim` |
| INV-11 | Target count ≤ k; Σcost ≤ budget; D không chọn EIM ≤ 0 | `policy` |
| INV-12 | Mọi policy trong cùng một so sánh dùng cùng tập customer và cùng k | `run_policies` |

---

## 8. Test specification

Chạy bằng `pytest` (`pyproject.toml` đặt `pythonpath = ["src", "tests"]`). Fixture tổng hợp nằm trong `tests/conftest.py`, đáp án được tính tay.

**Fixture `tiny_raw`** (dạng raw, 2 sheet, boundary 2010-12-01): 3 khách `"10001"`, `"10002"`, `"10003"` cùng các trường hợp biên.

- Một invoice nằm ở cả 2 sheet trong giai đoạn overlap.
- Một duplicate exact.
- Một invoice `C` của khách 10001.
- Một dòng `POST`.
- Một dòng quantity âm không có `C`, price 0, không ID.
- Một invoice `A` có price âm.
- Một dòng thiếu Customer ID.
- Một invoice có 2 timestamp.

| Test file | Nội dung chính | Trạng thái |
|---|---|---|
| `test_config.py` | load example config; lỗi khi purge < outcome, split chồng nhau, feature chứa target/label, scenario null khi `require_scenarios=True` | **pass** |
| `test_contracts.py` | thiếu cột, sai dtype, null ở cột non-null, key trùng → `ContractError` | **pass** |
| `test_simulation.py` | EIM = M1−M0 (1,000 ca ngẫu nhiên); δ_i ≤ 1−p; δ=0,d=0 → EIM=−c; validate params | **pass** |
| `test_ingest.py` | `combine_sheets` bỏ đúng dòng overlap; `sha256_file` | todo |
| `test_cleaning.py` | line_type/exclude_reason từng ca; cleaning_log; orders value/timestamp; invoice 2 timestamp → min | todo |
| `test_snapshots.py` | `generate_t0_dates` cho data thật → 16 ngày; recency/frequency/monetary/target của fixture | todo |
| `test_leakage.py` | thêm order sau T0 không làm đổi feature (chỉ đổi target); order đúng tại T0 thuộc outcome | todo |
| `test_rfm.py` | cutoffs chỉ từ train; recency đảo chiều; rule exhaustive | todo |
| `test_split.py` | `check_split_config` và `assign_split` với config đề xuất | todo |
| `test_evaluate.py` | precision/recall@k trên ví dụ tay; prevalence | todo |
| `test_policy.py` | k, budget, D bỏ EIM ≤ 0, B tái lập theo seed, tie-break | todo |

Test `todo` dùng marker `helpers.todo`, là `xfail(raises=NotImplementedError, strict=True)`. Chúng hiện ở trạng thái `xfail` khi hàm còn là stub. Khi hàm được implement đúng, test sẽ báo `XPASS(strict)` = fail, nhắc người code **xoá marker**. Nếu implement sai, test fail thật.

---

## 9. Hiệu năng

| Bước | Ước lượng | Cách xử lý |
|---|---|---|
| Đọc xlsx | ~161 s (đã đo) | Cache parquet; các lần sau < 2 s |
| Cleaning ~1.04M dòng | vài giây | Vectorized, không dùng `apply` theo dòng |
| 16 snapshots | < 30 s | Groupby theo customer trên orders (~37k purchase orders) |
| Policy B 100 seeds × 3 scenarios × 3 k × 2 value_basis | < 10 s | numpy |

---

## 10. Thứ tự code và ownership

| Bước | Module | Task PLAN | Owner | Done khi |
|---|---|---|---|---|
| 1 | `config`, `contracts` | T1.1 | M2 | ✅ đã xong, test pass |
| 2 | `data.ingest` | T1.2 | M1 | test_ingest pass; `len(load_raw)==1_044_848` |
| 3 | `data.clean`, `data.quality` | T2.1–T2.3 | M1 | test_cleaning pass; reconcile ±0.01; DQ report |
| 4 | `features.snapshots` | T2.4, T3.1 | M1 | test_snapshots + test_leakage pass; 16 T0 |
| 5 | `models.split` | T2.5 | M2 | test_split pass |
| 6 | `features.rfm`, `features.cohort` | T3.2–T3.3 | M1 | test_rfm pass |
| 7 | `models.train`, `models.evaluate` | T2.7, T3.4 | M2 | test_evaluate pass; metrics validation |
| 8 | `decision.simulation` (còn lại), `decision.policy` | T2.8, T4.4–T4.5 | M3 | test_policy pass |
| 9 | `models.calibrate` | T4.1 | M2 | reliability before/after |
| 10 | `decision.sensitivity`, `pipeline`, `cli` | T5.1, T6.1 | M3, M2 | `run all` từ môi trường sạch |
| 11 | `dashboard/app.py` | T5.3 | M3 | KPI khớp `scenario_results` |

Bước 2–4 (M1) và bước 5, 7 (M2) chạy song song: M2 phát triển trên fixture `tiny_raw` và schema §5.3 trước khi có snapshot thật.

---

## 11. Quyết định kỹ thuật mới (đã ghi vào decision log)

- **D21** — CR-00 cắt overlap theo `sheet_boundary` (Decided).
- **D22** — Feature mùa vụ `t0_month_sin/cos`, **không** dùng one-hot. Lý do: tháng T0 của validation (4, 5) không có trong tháng của train theo split đề xuất, nên one-hot sẽ thành vector 0. Status: Proposed, M2 kiểm chứng trên validation.
- **D23** — Value proxy `V = aov` nếu `aov > 0`, ngược lại dùng fallback median theo segment fit trên train. `monetary_net` có thể âm do adjustment (Decided).
- **D24** — Policy comparison báo cáo cả `model_p` và `actual_outcome`; `actual_outcome` là số liệu chính để so sánh (Decided).
