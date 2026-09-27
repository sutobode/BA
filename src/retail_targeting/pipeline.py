"""Stage orchestration (CODE SPEC §6.16). Each stage reads inputs from disk, writes outputs,
validates contracts and records a manifest. Owner: M2 (integration), stage bodies by module owners."""

from __future__ import annotations

from typing import Callable

from retail_targeting.config import Config


def stage_ingest(cfg: Config) -> None:
    """download_raw → load_raw → data/interim/transactions_raw.parquet."""
    raise NotImplementedError("M1")


def stage_clean(cfg: Config) -> None:
    """clean_transactions → lines.parquet, cleaning_log.csv; build_orders → orders.parquet;
    quality report + reconcile (INV-03)."""
    raise NotImplementedError("M1")


def stage_snapshots(cfg: Config) -> None:
    """build_all_snapshots → assign_split → fit_rfm_cutoffs(train) → apply scores/segments
    → data/processed/customer_snapshots.parquet; cohort_summary.csv."""
    raise NotImplementedError("M1 + M2 (split)")


def stage_train(cfg: Config) -> None:
    """tune_logreg on train/validation → calibrate → save_model; model_metrics (validation)."""
    raise NotImplementedError("M2")


def stage_evaluate(cfg: Config, *, include_test: bool = False) -> None:
    """customer_predictions.csv; metrics by group; test only if include_test (log_test_access)."""
    raise NotImplementedError("M2")


def stage_simulate(cfg: Config) -> None:
    """scenarios_from_config (require values) → run_policies for both value bases →
    scenario_results.csv, policy_comparison.csv, customer_targeting_table.csv."""
    raise NotImplementedError("M3")


def stage_sensitivity(cfg: Config) -> None:
    """run_grid → sensitivity_results.csv; break_even."""
    raise NotImplementedError("M3")


STAGES: dict[str, Callable[..., None]] = {
    "ingest": stage_ingest,
    "clean": stage_clean,
    "snapshots": stage_snapshots,
    "train": stage_train,
    "evaluate": stage_evaluate,
    "simulate": stage_simulate,
    "sensitivity": stage_sensitivity,
}
