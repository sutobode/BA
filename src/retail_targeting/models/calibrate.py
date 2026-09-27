"""Probability calibration on validation (CODE SPEC §6.11). Owner: M2."""

from __future__ import annotations

import pandas as pd
from sklearn.pipeline import Pipeline

from retail_targeting.config import Config


def calibrate(model: Pipeline, val: pd.DataFrame, cfg: Config) -> object:
    """model.calibration == "none" → return model unchanged; otherwise
    CalibratedClassifierCV(FrozenEstimator(model), method=...) fitted on validation rows only."""
    raise NotImplementedError("M2 — CODE SPEC §6.11")
