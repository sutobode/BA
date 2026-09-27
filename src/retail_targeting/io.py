"""File I/O with contract validation and run manifests (CODE SPEC §6.16). Owner: M2."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from retail_targeting.config import Config


def read_parquet(path: Path) -> pd.DataFrame:
    raise NotImplementedError("M2 — CODE SPEC §6.16")


def write_parquet(df: pd.DataFrame, path: Path, *, schema: str | None = None) -> Path:
    """validate_frame(df, schema) if schema is given, create parent dirs, write."""
    raise NotImplementedError("M2 — CODE SPEC §6.16")


def write_csv(df: pd.DataFrame, path: Path, *, schema: str | None = None) -> Path:
    """validate, sort by schema key, float_format='%.6f', index=False (deterministic output)."""
    raise NotImplementedError("M2 — CODE SPEC §6.16")


def write_manifest(cfg: Config, stage: str, outputs: list[Path]) -> Path:
    """reports_dir/run_manifest.json: stage, timestamp, config_hash, git commit, package versions,
    sha256 of each output."""
    raise NotImplementedError("M2 — CODE SPEC §6.16")
