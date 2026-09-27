"""Temporal split and purge (SPEC §6, CODE SPEC §6.9). Owner: M2."""

from __future__ import annotations

import pandas as pd

from retail_targeting.config import Config

SPLIT_VALUES = ("train", "validation", "test", "purged", "unused")


def check_split_config(cfg: Config) -> None:
    """INV-08: splits increasing, disjoint; max(train)+purge <= min(val); max(val)+purge <= min(test).
    Raise ValueError with the violated rule."""
    raise NotImplementedError("M2 — CODE SPEC §6.9")


def assign_split(snapshots: pd.DataFrame, cfg: Config) -> pd.Series:
    """Map decision_date → split. Dates not listed: "purged" if strictly between
    min(train) and max(test), otherwise "unused". Returns string Series aligned with index."""
    raise NotImplementedError("M2 — CODE SPEC §6.9")
