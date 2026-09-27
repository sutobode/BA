# Topic 1 — Customer Value & Promotion Targeting for an Online Retailer

Business question: *Which customers should the retailer prioritize for retention or promotion to increase expected future margin without over-discounting?*

Promotion results in this project are **scenario-based simulations under stated assumptions**. Online Retail II has no promotion treatment/control, so no causal uplift, ROI or revenue-lift claims are made.

## Tài liệu

**Người mới: đọc `docs/onboarding_topic1.md` trước.**

| File | Nội dung |
|---|---|
| `docs/onboarding_topic1.md` | **Bắt đầu tại đây**: bức tranh tổng thể, glossary, quy trình, git workflow |
| `docs/project_specification_topic1.md` | Business/analytics spec (SPEC) — nghiệp vụ & phương pháp |
| `docs/code_specification_topic1.md` | **Code spec**: module, hàm, schema, config, test, con số tham chiếu |
| `docs/implementation_plan_topic1.md` | Kế hoạch 6 tuần, 38 task, trạng thái |
| `docs/decision_log_topic1.md` | Quyết định D01–D28 |
| `docs/review_v1_topic1.md` | Review spec & giải pháp (lý do Policy E, lift structure, value cap) |
| `docs/data_profile_topic1.md` | Profiling dữ liệu thật |
| `docs/source_log.md`, `docs/data_dictionary.md` | Nguồn dữ liệu; định nghĩa từng cột |
| `docs/traceability_matrix_topic1.md` | Yêu cầu capstone → task → evidence |
| `docs/archive/` | Tài liệu cũ đã bị thay thế (không dùng) |

## Chạy bằng Docker (khuyến nghị)

Yêu cầu: Docker Desktop đang chạy. Tải data vào `data/raw/` trước (mục *Dữ liệu*).

```bash
docker compose build
docker compose run --rm test                                   # pytest
docker compose run --rm pipeline validate-config --require-scenarios
docker compose run --rm pipeline run all                       # khi các stage đã được implement
docker compose up dashboard                                    # http://localhost:8501
docker compose --profile dev up notebook                       # JupyterLab http://localhost:8888
```

`src/`, `tests/`, `dashboard/`, config, `data/` và `outputs/` được mount vào container, nên sửa code trên máy thì container thấy ngay. Dashboard và notebook chỉ bind `127.0.0.1` vì không có authentication.

## Setup local (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
```

## Dữ liệu

Nguồn: UCI Online Retail II — <https://archive.ics.uci.edu/dataset/502/online+retail+ii> (CC BY 4.0, DOI 10.24432/C5CG6D). Raw data không được commit.

```powershell
New-Item -ItemType Directory -Force data\raw
Invoke-WebRequest https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip -OutFile data\raw\online_retail_ii.zip
Expand-Archive data\raw\online_retail_ii.zip data\raw
Get-FileHash data\raw\online_retail_II.xlsx   # phải bằng source.sha256_xlsx trong project_config.yaml
```

Khi `data.ingest.download_raw` được implement, lệnh trên sẽ được thay bằng `python -m retail_targeting run ingest`.

## Chạy

```powershell
.\.venv\Scripts\python.exe -m pytest                     # test suite
.\.venv\Scripts\python.exe -m retail_targeting validate-config
.\.venv\Scripts\python.exe -m retail_targeting run all   # sau khi các stage được implement
```

## Bắt đầu code

1. Chọn module theo thứ tự ở `docs/code_specification_topic1.md` §10.
2. Đọc mục §6.x của module đó: signature, hành vi, invariant.
3. Implement hàm đang raise `NotImplementedError`.
4. Chạy test tương ứng. Khi pass, pytest báo `XPASS(strict)` → xoá `@todo` ở test đó.
5. Nếu cần một quyết định mà spec chưa có, ghi vào `docs/decision_log_topic1.md` trước khi code.
