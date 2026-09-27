# Topic 1 — Customer Value & Promotion Targeting for an Online Retailer

Business question: *Which customers should the retailer prioritize for retention or promotion to increase expected future margin without over-discounting?*

Promotion results in this project are **scenario-based simulations under stated assumptions**. Online Retail II has no promotion treatment/control, so no causal uplift, ROI or revenue-lift claims are made.

## Tài liệu

| File | Nội dung |
|---|---|
| `docs/project_specification_topic1.md` | Business/analytics spec (SPEC) |
| `docs/implementation_plan_topic1.md` | Kế hoạch 6 tuần, 38 task |
| `docs/code_specification_topic1.md` | **Code spec**: module, hàm, schema, config, test |
| `docs/data_profile_topic1.md` | Profiling dữ liệu thật |
| `docs/decision_log_topic1.md` | Quyết định D01–D24 |
| `docs/traceability_matrix_topic1.md` | Yêu cầu capstone → task → evidence |

## Setup (Windows PowerShell)

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
