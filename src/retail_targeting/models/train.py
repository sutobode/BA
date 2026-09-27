"""RFM benchmark and Logistic Regression baseline (SPEC §8, CODE SPEC §6.10). Owner: M2."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from retail_targeting.config import Config, resolve_path
from retail_targeting.models.evaluate import classification_metrics


def _signed_log1p(x):
    x = np.asarray(x, dtype=float)
    return np.sign(x) * np.log1p(np.abs(x))


def feature_names(cfg: Config) -> list[str]:
    m = cfg.raw["model"]
    return list(m["numeric_features"]) + list(m.get("categorical_features") or [])


def feature_matrix(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Return only model.numeric_features + model.categorical_features (in that order).
    Raise KeyError if a column is missing; raise ValueError if a target/label column is requested (INV-07)."""
    feats = feature_names(cfg)
    target = cfg.raw["temporal"]["target_name"]
    bad = [f for f in feats if f == target or f.startswith("label_") or f in ("split", "customer_id", "decision_date")]
    if bad:
        raise ValueError(f"INV-07: forbidden features {bad}")
    missing = [f for f in feats if f not in df.columns]
    if missing:
        raise KeyError(f"missing feature columns {missing}")
    return df[feats]


def rfm_benchmark_score(df: pd.DataFrame) -> pd.Series:
    """Benchmark ranking score: rfm_score + 1e-3 * r_score (float)."""
    return (df["rfm_score"].astype(float) + 1e-3 * df["r_score"].astype(float)).rename("rfm_benchmark_score")


def build_pipeline(cfg: Config, *, C: float, class_weight: str | None) -> Pipeline:
    """ColumnTransformer(signed log1p on model.log1p_features → SimpleImputer(median) → StandardScaler)
    → LogisticRegression(C=C, class_weight=class_weight, max_iter=2000, random_state=seed)."""
    m = cfg.raw["model"]
    num = list(m["numeric_features"])
    logf = [f for f in num if f in set(m.get("log1p_features") or [])]
    plain = [f for f in num if f not in logf]
    log_pipe = Pipeline([("log", FunctionTransformer(_signed_log1p, feature_names_out="one-to-one")),
                         ("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    plain_pipe = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    pre = ColumnTransformer([("log", log_pipe, logf), ("plain", plain_pipe, plain)], remainder="drop")
    lr = LogisticRegression(C=C, class_weight=class_weight, max_iter=2000,
                            random_state=cfg.raw["project"]["random_seed"])
    return Pipeline([("pre", pre), ("lr", lr)])


def tune_logreg(train: pd.DataFrame, val: pd.DataFrame, cfg: Config) -> tuple[Pipeline, pd.DataFrame]:
    """Grid C_grid × class_weight_options; fit on train only; select by validation PR-AUC
    (tie → lower Brier). Returns (fitted best pipeline, grid results table)."""
    if (train["split"] != "train").any() or (val["split"] != "validation").any():
        raise ValueError("tune_logreg: train/val frames must contain only their split (INV-09)")
    target = cfg.raw["temporal"]["target_name"]
    m = cfg.raw["model"]
    Xtr, ytr = feature_matrix(train, cfg), train[target].to_numpy()
    Xva, yva = feature_matrix(val, cfg), val[target].to_numpy()
    rows, best, best_key = [], None, None
    for C in m["C_grid"]:
        for cw in m["class_weight_options"]:
            pipe = build_pipeline(cfg, C=float(C), class_weight=cw).fit(Xtr, ytr)
            p = pipe.predict_proba(Xva)[:, 1]
            met = classification_metrics(yva, p, m["top_k_fractions"], val["customer_id"].to_numpy())
            rows.append({"C": C, "class_weight": str(cw), **met})
            key = (round(met["pr_auc"], 6), -round(met["brier"], 6))
            if best_key is None or key > best_key:
                best, best_key = pipe, key
    return best, pd.DataFrame(rows)


def coefficients(model: Pipeline) -> pd.DataFrame:
    """Standardized LR coefficients and odds ratios (explainability, SPEC §8)."""
    names = [n.split("__", 1)[-1] for n in model.named_steps["pre"].get_feature_names_out()]
    coef = model.named_steps["lr"].coef_[0]
    return (pd.DataFrame({"feature": names, "coefficient": coef, "odds_ratio_per_sd": np.exp(coef)})
            .sort_values("coefficient", key=np.abs, ascending=False).reset_index(drop=True))


def save_model(model: object, meta: dict, cfg: Config) -> Path:
    """joblib dump to models_dir/model_{model_version}.joblib + metadata json next to it."""
    d = resolve_path(cfg, "models_dir")
    d.mkdir(parents=True, exist_ok=True)
    version = cfg.raw["versions"]["model_version"]
    path = d / f"model_{version}.joblib"
    joblib.dump(model, path)
    (d / f"model_{version}_metadata.json").write_text(json.dumps(meta, indent=1, default=str), encoding="utf-8")
    return path
