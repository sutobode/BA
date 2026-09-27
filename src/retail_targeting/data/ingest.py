"""Raw data acquisition and sheet combination (CODE SPEC §6.3). Owner: M1."""

from __future__ import annotations

import hashlib
import logging
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

from retail_targeting.config import Config, resolve_path

log = logging.getLogger(__name__)


class ChecksumError(RuntimeError):
    """Raised when a raw file does not match the checksum in the config (INV-01)."""


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    """Upper-case hex SHA-256 of a file (same format as PowerShell Get-FileHash)."""
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest().upper()


def verify_checksum(path: Path, expected: str) -> None:
    """Raise ChecksumError if ``sha256_file(path)`` != ``expected`` (case-insensitive)."""
    actual = sha256_file(path)
    if actual != expected.upper():
        raise ChecksumError(f"{path}: sha256 {actual} != expected {expected.upper()}")


def download_raw(cfg: Config, *, force: bool = False) -> Path:
    """Download ``source.download_url`` into ``paths.raw_dir``, verify zip checksum, extract xlsx.

    Skip download when the zip exists and its checksum matches, unless ``force``.
    Returns the path of the extracted xlsx.
    """
    src = cfg.raw["source"]
    raw_dir = resolve_path(cfg, "raw_dir")
    raw_dir.mkdir(parents=True, exist_ok=True)
    xlsx = raw_dir / src["raw_filename"]
    zpath = raw_dir / src["zip_filename"]
    if xlsx.exists() and not force:
        try:
            verify_checksum(xlsx, src["sha256_xlsx"])
            return xlsx
        except ChecksumError:
            log.warning("xlsx checksum mismatch, re-downloading")
    if force or not zpath.exists() or sha256_file(zpath) != src["sha256_zip"].upper():
        log.info("downloading %s", src["download_url"])
        urllib.request.urlretrieve(src["download_url"], zpath)  # noqa: S310 - fixed https URL from config
    verify_checksum(zpath, src["sha256_zip"])
    with zipfile.ZipFile(zpath) as zf:
        zf.extract(src["raw_filename"], raw_dir)
    verify_checksum(xlsx, src["sha256_xlsx"])
    return xlsx


def read_raw_excel(xlsx: Path, sheets: list[str]) -> dict[str, pd.DataFrame]:
    """Read the given sheets with dtype={"Invoice": str, "StockCode": str}. No transformation."""
    return pd.read_excel(xlsx, sheet_name=sheets, dtype={"Invoice": str, "StockCode": str}, engine="openpyxl")


def combine_sheets(sheets: dict[str, pd.DataFrame], boundary: pd.Timestamp,
                   sheet_order: list[str]) -> pd.DataFrame:
    """CR-00 (D21): rows of sheet_order[0] with InvoiceDate < boundary + rows of
    sheet_order[1] with InvoiceDate >= boundary; add column ``source_sheet``.

    Rows of each sheet outside its period are dropped (on real data: 22,523 overlap rows).
    INV-02: no row of the overlap period may come from both sheets.
    Preserves original row order within each sheet.
    """
    boundary = pd.Timestamp(boundary)
    a, b = sheets[sheet_order[0]], sheets[sheet_order[1]]
    a_keep = a[a["InvoiceDate"] < boundary].assign(source_sheet=sheet_order[0])
    b_keep = b[b["InvoiceDate"] >= boundary].assign(source_sheet=sheet_order[1])
    dropped = (len(a) - len(a_keep)) + (len(b) - len(b_keep))
    log.info("CR-00 combine_sheets: kept %d + %d rows, dropped %d overlap rows", len(a_keep), len(b_keep), dropped)
    out = pd.concat([a_keep, b_keep], ignore_index=True)
    for col in ("Invoice", "StockCode", "Description", "Country", "source_sheet"):
        out[col] = out[col].astype("string")
    out["Quantity"] = out["Quantity"].astype("int64")
    out["Price"] = out["Price"].astype("float64")
    out["Customer ID"] = out["Customer ID"].astype("float64")
    out["InvoiceDate"] = pd.to_datetime(out["InvoiceDate"]).astype("datetime64[ns]")
    return out


def load_raw(cfg: Config, *, use_cache: bool = True) -> pd.DataFrame:
    """Verify xlsx checksum (INV-01), read sheets (or parquet cache keyed by sha256[:12]),
    apply :func:`combine_sheets`. Expected on real data: 1,044,848 rows.
    Output must satisfy contract ``transactions_raw``.
    """
    from retail_targeting.contracts import validate_frame

    src = cfg.raw["source"]
    xlsx = resolve_path(cfg, "raw_dir") / src["raw_filename"]
    if not xlsx.exists():
        xlsx = download_raw(cfg)
    verify_checksum(xlsx, src["sha256_xlsx"])
    cache = resolve_path(cfg, "interim_dir") / f"transactions_raw_{src['sha256_xlsx'][:12].lower()}.parquet"
    if use_cache and cache.exists():
        log.info("loading cache %s", cache.name)
        out = pd.read_parquet(cache)
    else:
        sheets = read_raw_excel(xlsx, list(src["sheets"]))
        out = combine_sheets(sheets, pd.Timestamp(src["sheet_boundary"]), list(src["sheets"]))
        cache.parent.mkdir(parents=True, exist_ok=True)
        out.to_parquet(cache, index=False)
    for col in ("Invoice", "StockCode", "Description", "Country", "source_sheet"):
        out[col] = out[col].astype("string")
    return validate_frame(out, "transactions_raw")
