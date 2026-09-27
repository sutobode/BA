"""Probability calibration on validation (CODE SPEC §6.11). Owner: M2."""

from __future__ import annotations

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.pipeline import Pipeline

from retail_targeting.config import Config
from retail_targeting.models.train import feature_matrix


def calibrate(model: Pipeline, val: pd.DataFrame, cfg: Config) -> object:
    """model.calibration == "none" → return model unchanged; otherwise
    CalibratedClassifierCV(FrozenEstimator(model), method=...) fitted on validation rows only."""
    method = cfg.raw["model"]["calibration"]
    if method == "none":
        return model
    if (val["split"] != "validation").any():
        raise ValueError("calibrate: only validation rows allowed")
    target = cfg.raw["temporal"]["target_name"]
    cal = CalibratedClassifierCV(FrozenEstimator(model), method=method)
    return cal.fit(feature_matrix(val, cfg), val[target].to_numpy())
