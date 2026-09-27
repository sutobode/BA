"""Temporal split and purge (SPEC §6, CODE SPEC §6.9). Owner: M2."""

from __future__ import annotations

import datetime as dt

import pandas as pd

from retail_targeting.config import Config, split_dates

SPLIT_VALUES = ("train", "validation", "test", "purged", "unused")


def check_split_config(cfg: Config) -> None:
    """INV-08: splits increasing, disjoint; max(train)+purge <= min(val); max(val)+purge <= min(test).
    Raise ValueError with the violated rule."""
    s = split_dates(cfg)
    purge = dt.timedelta(days=cfg.raw["temporal"]["purge_days"])
    for name, dates in s.items():
        if dates != sorted(set(dates)):
            raise ValueError(f"{name} snapshots must be strictly increasing")
    if not (max(s["train"]) < min(s["validation"]) and max(s["validation"]) < min(s["test"])):
        raise ValueError("splits must be chronological and disjoint")
    if max(s["train"]) + purge > min(s["validation"]):
        raise ValueError("purge violated between train and validation")
    if max(s["validation"]) + purge > min(s["test"]):
        raise ValueError("purge violated between validation and test")


def assign_split(snapshots: pd.DataFrame, cfg: Config) -> pd.Series:
    """Map decision_date → split. Dates not listed: "purged" if strictly between
    min(train) and max(test), otherwise "unused". Returns string Series aligned with index."""
    s = split_dates(cfg)
    mapping = {pd.Timestamp(d): name for name, dates in s.items() for d in dates}
    lo, hi = pd.Timestamp(min(s["train"])), pd.Timestamp(max(s["test"]))
    dates = pd.to_datetime(snapshots["decision_date"])
    out = dates.map(mapping)
    between = (dates > lo) & (dates < hi)
    out = out.where(out.notna(), pd.Series("purged", index=dates.index).where(between, "unused"))
    return out.astype("string")
