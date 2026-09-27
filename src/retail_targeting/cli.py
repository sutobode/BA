"""Command-line entrypoint: ``python -m retail_targeting ...`` (CODE SPEC §6.16)."""

from __future__ import annotations

import argparse
import logging
import sys

from retail_targeting.config import ConfigError, load_config


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config, require_scenarios=args.require_scenarios)
    except ConfigError as exc:
        print(f"CONFIG INVALID: {exc}", file=sys.stderr)
        return 1
    t = cfg.raw["temporal"]
    print(f"CONFIG OK: {args.config} | train={len(t['train_snapshots'])} "
          f"validation={len(t['validation_snapshots'])} test={len(t['test_snapshots'])} "
          f"| scenarios={list(cfg.raw['simulation']['scenarios'])}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    from retail_targeting.pipeline import STAGES

    cfg = load_config(args.config, require_scenarios=args.stage in ("simulate", "sensitivity", "all"))
    names = list(STAGES) if args.stage == "all" else [args.stage]
    for name in names:
        logging.info("stage %s", name)
        if name == "evaluate":
            STAGES[name](cfg, include_test=args.include_test)
        else:
            STAGES[name](cfg)
    return 0


_ARTIFACT_FILES = {
    "transactions_raw": ("interim_dir", "transactions_raw.parquet"),
    "lines": ("interim_dir", "lines.parquet"),
    "orders": ("interim_dir", "orders.parquet"),
    "customer_snapshots": ("processed_dir", "customer_snapshots.parquet"),
    "customer_predictions": ("tables_dir", "customer_predictions.csv"),
    "scenario_results": ("tables_dir", "scenario_results.csv"),
    "customer_targeting_table": ("tables_dir", "customer_targeting_table.csv"),
}


def _cmd_check(args: argparse.Namespace) -> int:
    from retail_targeting.config import resolve_path
    from retail_targeting.contracts import ContractError, validate_frame
    from retail_targeting.io import read_csv_artifact, read_parquet

    if args.artifact not in _ARTIFACT_FILES:
        print(f"unknown artifact; choose from {sorted(_ARTIFACT_FILES)}", file=sys.stderr)
        return 2
    cfg = load_config(args.config)
    key, name = _ARTIFACT_FILES[args.artifact]
    path = resolve_path(cfg, key) / name
    df = read_parquet(path) if name.endswith(".parquet") else read_csv_artifact(path)
    if args.artifact == "customer_targeting_table":
        df["value_is_fallback"] = df["value_is_fallback"].astype(str).str.lower().eq("true")
        df["target_rank"] = df["target_rank"].astype("Int64")
    if args.artifact == "scenario_results":
        df["seed"] = df["seed"].astype("Int64")
    try:
        validate_frame(df, args.artifact)
    except ContractError as exc:
        print(f"CONTRACT FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"CONTRACT OK: {args.artifact} ({len(df):,} rows) {path.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    from retail_targeting.pipeline import STAGES

    parser = argparse.ArgumentParser(prog="retail_targeting")
    parser.add_argument("--config", default="project_config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate-config")
    v.add_argument("--require-scenarios", action="store_true")
    v.set_defaults(func=_cmd_validate)

    r = sub.add_parser("run")
    r.add_argument("stage", choices=[*STAGES, "all"])
    r.add_argument("--include-test", action="store_true")
    r.add_argument("--force", action="store_true")
    r.set_defaults(func=_cmd_run)

    c = sub.add_parser("check")
    c.add_argument("artifact")
    c.set_defaults(func=_cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)
    return args.func(args)
