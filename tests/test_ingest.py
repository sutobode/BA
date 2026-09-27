import pandas as pd
import pytest

from conftest import BOUNDARY, EXPECTED, SHEETS
from helpers import todo
from retail_targeting.contracts import validate_frame
from retail_targeting.data.ingest import ChecksumError, combine_sheets, sha256_file, verify_checksum


def test_sha256_file(tmp_path_file):
    assert sha256_file(tmp_path_file) == "BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD"


@todo
def test_verify_checksum(tmp_path_file):
    verify_checksum(tmp_path_file, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    with pytest.raises(ChecksumError):
        verify_checksum(tmp_path_file, "0" * 64)


@todo
def test_combine_sheets_drops_overlap(tiny_sheets):
    out = combine_sheets(tiny_sheets, BOUNDARY, SHEETS)
    assert len(out) == EXPECTED["rows_after_combine"]
    a = out[out["source_sheet"] == SHEETS[0]]
    b = out[out["source_sheet"] == SHEETS[1]]
    assert (a["InvoiceDate"] < BOUNDARY).all() and (b["InvoiceDate"] >= BOUNDARY).all()
    assert (out["Invoice"] == "100008").sum() == 1
    validate_frame(out, "transactions_raw")
