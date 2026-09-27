"""File I/O with contract validation and run manifests (CODE SPEC §6.16). Owner: M2."""

from __future__ import annotations

import datetime as dt
import importlib.metadata as md
import json
import subprocess
from pathlib import Path

import pandas as pd

from retail_targeting.config import Config, config_hash, resolve_path
from retail_targeting.contracts import SCHEMAS, validate_frame

_PACKAGES = ("pandas", "numpy", "scikit-learn", "scipy", "pyarrow", "PyYAML", "matplotlib", "streamlit")


def read_parquet(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype("string")
    return df


def write_parquet(df: pd.DataFrame, path: Path, *, schema: str | None = None) -> Path:
    """validate_frame(df, schema) if schema is given, create parent dirs, write."""
    if schema:
        validate_frame(df, schema)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def write_csv(df: pd.DataFrame, path: Path, *, schema: str | None = None) -> Path:
    """validate, sort by schema key, float_format='%.6f', index=False (deterministic output)."""
    out = df
    if schema:
        validate_frame(df, schema)
        key = [k for k in SCHEMAS[schema].key if k in df.columns]
        if key:
            out = df.sort_values(key, kind="mergesort", na_position="first")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, float_format="%.6f")
    return path


def read_csv_artifact(path: Path, parse_dates: tuple[str, ...] = ("decision_date",)) -> pd.DataFrame:
    """Read a CSV written by write_csv, restoring string/datetime dtypes."""
    df = pd.read_csv(path, dtype={"customer_id": "string"})
    for col in parse_dates:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).astype("datetime64[ns]")
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype("string")
    return df


def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True,
                              check=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001 - git may be missing inside the container
        return None


def write_manifest(cfg: Config, stage: str, outputs: list[Path]) -> Path:
    """reports_dir/run_manifest.json: stage, timestamp, config_hash, git commit, package versions,
    sha256 of each output."""
    from retail_targeting.data.ingest import sha256_file

    path = resolve_path(cfg, "reports_dir") / "run_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"stages": {}}
    versions = {}
    for pkg in _PACKAGES:
        try:
            versions[pkg] = md.version(pkg)
        except md.PackageNotFoundError:
            versions[pkg] = None
    manifest["stages"][stage] = {
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "config_hash": config_hash(cfg),
        "git_commit": _git_commit(cfg.root),
        "packages": versions,
        "outputs": {str(Path(p).resolve().relative_to(cfg.root)).replace("\\", "/"): sha256_file(Path(p))
                    for p in outputs},
    }
    path.write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    return path
