"""Load and validate ``project_config.yaml`` (CODE SPEC §4, §6.1)."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SECTIONS = (
    "project", "paths", "source", "cleaning", "temporal",
    "segmentation", "model", "simulation", "versions",
)
SCENARIO_KEYS = ("discount_rate", "incremental_lift", "gross_margin", "contact_cost")
REQUIRED_PATHS = (
    "raw_dir", "interim_dir", "processed_dir", "tables_dir",
    "figures_dir", "models_dir", "reports_dir",
)
_HEX64 = re.compile(r"^[0-9A-Fa-f]{64}$")


class ConfigError(ValueError):
    """Raised when the configuration violates the schema in CODE SPEC §4."""


class _Section:
    """Read-only attribute access over a config mapping."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __getattr__(self, item: str) -> Any:
        try:
            value = self._data[item]
        except KeyError as exc:
            raise AttributeError(item) from exc
        return _Section(value) if isinstance(value, dict) else value

    def __getitem__(self, item: str) -> Any:
        return self._data[item]

    def get(self, item: str, default: Any = None) -> Any:
        return self._data.get(item, default)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


@dataclass(frozen=True)
class Config:
    """Validated configuration. Sections are accessible as attributes."""

    raw: dict[str, Any]
    root: Path

    def __getattr__(self, item: str) -> Any:
        raw = object.__getattribute__(self, "raw")
        if item in raw:
            value = raw[item]
            return _Section(value) if isinstance(value, dict) else value
        raise AttributeError(item)


def _to_date(value: Any, field: str) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError as exc:
            raise ConfigError(f"{field}: invalid date {value!r}") from exc
    raise ConfigError(f"{field}: expected date, got {type(value).__name__}")


def _require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def _validate_temporal(t: dict[str, Any], errors: list[str]) -> None:
    _require(t.get("snapshot_cadence") == "monthly", "temporal.snapshot_cadence: only 'monthly' is supported", errors)
    for key in ("observation_days", "outcome_days", "purge_days"):
        _require(isinstance(t.get(key), int) and t.get(key, 0) > 0, f"temporal.{key}: must be a positive int", errors)
    if errors:
        return
    _require(t["purge_days"] >= t["outcome_days"], "temporal.purge_days: must be >= outcome_days", errors)
    expected_target = f"repeat_purchase_{t['outcome_days']}d"
    _require(t.get("target_name") == expected_target, f"temporal.target_name: must be {expected_target!r}", errors)

    splits: dict[str, list[dt.date]] = {}
    for name in ("train_snapshots", "validation_snapshots", "test_snapshots"):
        values = t.get(name) or []
        if not values:
            errors.append(f"temporal.{name}: must be a non-empty list")
            continue
        try:
            dates = [_to_date(v, f"temporal.{name}") for v in values]
        except ConfigError as exc:
            errors.append(str(exc))
            continue
        _require(all(d.day == 1 for d in dates), f"temporal.{name}: dates must be the 1st of a month", errors)
        _require(dates == sorted(set(dates)), f"temporal.{name}: dates must be strictly increasing", errors)
        splits[name] = dates
    if len(splits) != 3:
        return
    tr, va, te = splits["train_snapshots"], splits["validation_snapshots"], splits["test_snapshots"]
    purge = dt.timedelta(days=t["purge_days"])
    _require(max(tr) < min(va) and max(va) < min(te), "temporal: splits must be chronological and disjoint", errors)
    _require(max(tr) + purge <= min(va), "temporal: purge violated between train and validation", errors)
    _require(max(va) + purge <= min(te), "temporal: purge violated between validation and test", errors)


def _validate_model(m: dict[str, Any], target: str | None, errors: list[str]) -> None:
    num = list(m.get("numeric_features") or [])
    cat = list(m.get("categorical_features") or [])
    _require(bool(num or cat), "model: at least one feature is required", errors)
    feats = num + cat
    _require(len(feats) == len(set(feats)), "model: duplicated feature names", errors)
    forbidden = [f for f in feats if f.startswith("label_") or f == target or f in ("split", "customer_id", "decision_date")]
    _require(not forbidden, f"model: forbidden (target/label/key) features {forbidden}", errors)
    extra_log = set(m.get("log1p_features") or []) - set(num)
    _require(not extra_log, f"model.log1p_features: not in numeric_features {sorted(extra_log)}", errors)
    _require(m.get("calibration") in ("none", "sigmoid", "isotonic"), "model.calibration: none|sigmoid|isotonic", errors)
    fracs = m.get("top_k_fractions") or []
    _require(bool(fracs) and all(0 < f <= 1 for f in fracs), "model.top_k_fractions: values in (0, 1]", errors)
    _require(bool(m.get("C_grid")), "model.C_grid: must be non-empty", errors)


def _validate_scenario(name: str, s: dict[str, Any], require_values: bool, errors: list[str]) -> None:
    missing = [k for k in SCENARIO_KEYS if k not in s]
    if missing:
        errors.append(f"simulation.scenarios.{name}: missing keys {missing}")
        return
    if any(s[k] is None for k in SCENARIO_KEYS):
        _require(not require_values, f"simulation.scenarios.{name}: values are still null (freeze D10/D11)", errors)
        return
    d, lift, m, c = (float(s[k]) for k in SCENARIO_KEYS)
    _require(0 <= d < m <= 1, f"simulation.scenarios.{name}: require 0 <= discount_rate < gross_margin <= 1", errors)
    _require(0 <= lift <= 1, f"simulation.scenarios.{name}: incremental_lift in [0, 1]", errors)
    _require(c >= 0, f"simulation.scenarios.{name}: contact_cost >= 0", errors)


def _validate_simulation(s: dict[str, Any], require_scenarios: bool, errors: list[str]) -> None:
    scenarios = s.get("scenarios") or {}
    _require(len(scenarios) >= 3, "simulation.scenarios: at least 3 scenarios required (CAP R20)", errors)
    for name, params in scenarios.items():
        _validate_scenario(name, params or {}, require_scenarios, errors)
    fracs = s.get("capacity_fractions") or []
    _require(bool(fracs) and all(0 < f <= 1 for f in fracs), "simulation.capacity_fractions: values in (0, 1]", errors)
    budget = s.get("budget")
    _require(budget is None or float(budget) > 0, "simulation.budget: null or > 0", errors)
    seeds = s.get("random_baseline_seeds")
    _require(isinstance(seeds, int) and seeds >= 1, "simulation.random_baseline_seeds: int >= 1", errors)
    bases = set(s.get("value_bases") or [])
    _require(bases <= {"model_p", "actual_outcome"} and bool(bases), "simulation.value_bases: subset of {model_p, actual_outcome}", errors)


def validate_config(raw: dict[str, Any], *, require_scenarios: bool = False) -> None:
    """Validate a raw config mapping; raise :class:`ConfigError` listing every violation."""
    if not isinstance(raw, dict):
        raise ConfigError("config root must be a mapping")
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        _require(isinstance(raw.get(section), dict), f"missing section: {section}", errors)
    if errors:
        raise ConfigError("; ".join(errors))

    seed = raw["project"].get("random_seed")
    _require(isinstance(seed, int) and seed >= 0, "project.random_seed: int >= 0", errors)
    for key in REQUIRED_PATHS:
        _require(isinstance(raw["paths"].get(key), str), f"paths.{key}: required string", errors)

    src = raw["source"]
    for key in ("sha256_zip", "sha256_xlsx"):
        _require(bool(_HEX64.match(str(src.get(key, "")))), f"source.{key}: must be 64 hex chars", errors)
    _require(len(src.get("sheets") or []) == 2, "source.sheets: exactly 2 sheet names", errors)
    try:
        _to_date(src.get("sheet_boundary"), "source.sheet_boundary")
    except ConfigError as exc:
        errors.append(str(exc))

    cl = raw["cleaning"]
    for key in ("cancellation_prefix", "bad_debt_prefix"):
        _require(isinstance(cl.get(key), str) and len(cl[key]) >= 1, f"cleaning.{key}: required string", errors)
    for key in ("non_product_codes", "non_product_prefixes"):
        _require(isinstance(cl.get(key), list), f"cleaning.{key}: must be a list", errors)

    _validate_temporal(raw["temporal"], errors)

    seg = raw["segmentation"]
    rules = seg.get("rules") or []
    _require(isinstance(seg.get("n_bins"), int) and seg.get("n_bins", 0) >= 2, "segmentation.n_bins: int >= 2", errors)
    _require(bool(rules) and rules[-1].get("when") == "default", "segmentation.rules: last rule must be 'default'", errors)

    _validate_model(raw["model"], raw["temporal"].get("target_name"), errors)
    _validate_simulation(raw["simulation"], require_scenarios, errors)

    if errors:
        raise ConfigError("; ".join(errors))


def load_config(path: str | Path = "project_config.yaml", *, require_scenarios: bool = False) -> Config:
    """Load YAML config (relative paths resolve against the repo root) and validate it."""
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    if not p.exists():
        raise ConfigError(f"config file not found: {p}")
    with p.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    validate_config(raw, require_scenarios=require_scenarios)
    return Config(raw=raw, root=REPO_ROOT)


def config_hash(cfg: Config) -> str:
    """SHA-256 of the canonical JSON form of the config (used in run manifests)."""
    canonical = json.dumps(cfg.raw, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def resolve_path(cfg: Config, key: str) -> Path:
    """Return the absolute path for ``paths.<key>``."""
    try:
        rel = cfg.raw["paths"][key]
    except KeyError as exc:
        raise ConfigError(f"paths.{key} is not defined") from exc
    return (cfg.root / rel).resolve()


def split_dates(cfg: Config) -> dict[str, list[dt.date]]:
    """Return {'train': [...], 'validation': [...], 'test': [...]} as ``datetime.date`` lists."""
    t = cfg.raw["temporal"]
    return {
        "train": [_to_date(v, "train") for v in t["train_snapshots"]],
        "validation": [_to_date(v, "validation") for v in t["validation_snapshots"]],
        "test": [_to_date(v, "test") for v in t["test_snapshots"]],
    }
