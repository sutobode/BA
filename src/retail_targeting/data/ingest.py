"""Raw data acquisition and sheet combination (CODE SPEC §6.3). Owner: M1."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from retail_targeting.config import Config


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
    raise NotImplementedError("M1 — CODE SPEC §6.3")


def download_raw(cfg: Config, *, force: bool = False) -> Path:
    """Download ``source.download_url`` into ``paths.raw_dir``, verify zip checksum, extract xlsx.

    Skip download when the zip exists and its checksum matches, unless ``force``.
    Returns the path of the extracted xlsx.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.3")


def read_raw_excel(xlsx: Path, sheets: list[str]) -> dict[str, pd.DataFrame]:
    """Read the given sheets with dtype={"Invoice": str, "StockCode": str}. No transformation."""
    raise NotImplementedError("M1 — CODE SPEC §6.3")


def combine_sheets(sheets: dict[str, pd.DataFrame], boundary: pd.Timestamp,
                   sheet_order: list[str]) -> pd.DataFrame:
    """CR-00 (D21): rows of sheet_order[0] with InvoiceDate < boundary + rows of
    sheet_order[1] with InvoiceDate >= boundary; add column ``source_sheet``.

    Rows of each sheet outside its period are dropped (on real data: 22,523 overlap rows).
    INV-02: no row of the overlap period may come from both sheets.
    Preserves original row order within each sheet.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.3")


def load_raw(cfg: Config, *, use_cache: bool = True) -> pd.DataFrame:
    """Verify xlsx checksum (INV-01), read sheets (or parquet cache keyed by sha256[:12]),
    apply :func:`combine_sheets`. Expected on real data: 1,044,848 rows.
    Output must satisfy contract ``transactions_raw``.
    """
    raise NotImplementedError("M1 — CODE SPEC §6.3")
