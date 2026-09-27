"""RFM benchmark and Logistic Regression baseline (SPEC §8, CODE SPEC §6.10). Owner: M2."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline

from retail_targeting.config import Config


def feature_matrix(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Return only model.numeric_features + model.categorical_features (in that order).
    Raise KeyError if a column is missing; raise ValueError if a target/label column is requested (INV-07)."""
    raise NotImplementedError("M2 — CODE SPEC §6.10")


def rfm_benchmark_score(df: pd.DataFrame) -> pd.Series:
    """Benchmark ranking score: rfm_score + 1e-3 * r_score (float)."""
    raise NotImplementedError("M2 — CODE SPEC §6.10")


def build_pipeline(cfg: Config, *, C: float, class_weight: str | None) -> Pipeline:
    """ColumnTransformer(signed log1p on model.log1p_features → SimpleImputer(median) → StandardScaler)
    → LogisticRegression(C=C, class_weight=class_weight, max_iter=2000, random_state=seed)."""
    raise NotImplementedError("M2 — CODE SPEC §6.10")


def tune_logreg(train: pd.DataFrame, val: pd.DataFrame, cfg: Config) -> tuple[Pipeline, pd.DataFrame]:
    """Grid C_grid × class_weight_options; fit on train only; select by validation PR-AUC
    (tie → lower Brier). Returns (fitted best pipeline, grid results table)."""
    raise NotImplementedError("M2 — CODE SPEC §6.10")


def save_model(model: object, meta: dict, cfg: Config) -> Path:
    """joblib dump to models_dir/model_{model_version}.joblib + metadata json next to it."""
    raise NotImplementedError("M2 — CODE SPEC §6.10")
