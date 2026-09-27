"""Customer snapshots at decision date T0 (SPEC §5, CODE SPEC §5.3, §6.6). Owner: M1."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from retail_targeting.config import Config

log = logging.getLogger(__name__)
_DAY = pd.Timedelta(days=1)


class LeakageError(AssertionError):
    """Raised when post-T0 information reaches a feature (INV-05/INV-06)."""


def generate_t0_dates(data_start: pd.Timestamp, data_end: pd.Timestamp, cfg: Config) -> list[pd.Timestamp]:
    """First-of-month dates with T0 >= data_start + observation_days and
    T0 + outcome_days <= data_end. Real data (2009-12-01 → 2011-12-09, 180/90) → 16 dates
    2010-06-01 … 2011-09-01."""
    t = cfg.raw["temporal"]
    lo = pd.Timestamp(data_start) + pd.Timedelta(days=t["observation_days"])
    hi = pd.Timestamp(data_end) - pd.Timedelta(days=t["outcome_days"])
    first = lo if (lo == lo.normalize() and lo.day == 1) else lo.normalize() + pd.offsets.MonthBegin(1)
    return [pd.Timestamp(d) for d in pd.date_range(first, hi, freq="MS")]


def _features(hist: pd.DataFrame, obs_lines: pd.DataFrame, t0: pd.Timestamp) -> pd.DataFrame:
    purchases_all = hist[hist["order_type"] == "purchase"]
    p = purchases_all[purchases_all["order_ts"] >= hist.attrs["obs_start"]]
    a = hist[(hist["order_type"] == "adjustment") & (hist["order_ts"] >= hist.attrs["obs_start"])]
    g = p.groupby("customer_id", observed=True)
    elig = g.size().index
    df = pd.DataFrame(index=elig)
    df["recency_days"] = (t0 - g["order_ts"].max()) / _DAY
    df["frequency_orders"] = g.size().astype("int64")
    df["purchase_value"] = g["order_value"].sum()
    df["adjustment_value"] = a.groupby("customer_id", observed=True)["order_value"].sum().abs().reindex(elig).fillna(0.0)
    df["monetary_net"] = df["purchase_value"] - df["adjustment_value"]
    df["aov"] = df["monetary_net"] / df["frequency_orders"]
    df["return_rate"] = (df["adjustment_value"] / df["purchase_value"]).clip(upper=1.0)
    first_ts = purchases_all.groupby("customer_id", observed=True)["order_ts"].min().reindex(elig)
    df["tenure_days"] = (t0 - first_ts) / _DAY
    df["active_months"] = (p.assign(m=p["order_ts"].dt.to_period("M"))
                           .groupby("customer_id", observed=True)["m"].nunique().astype("int64"))
    ps = p.sort_values(["customer_id", "order_ts"])
    gaps = ps.groupby("customer_id", observed=True)["order_ts"].diff() / _DAY
    df["avg_interpurchase_days"] = gaps.groupby(ps["customer_id"], observed=True).mean().reindex(elig)
    pl = obs_lines[obs_lines["invoice"].isin(p["order_id"])]
    gl = pl.groupby("customer_id", observed=True)
    df["unique_products"] = gl["stock_code"].nunique().reindex(elig).fillna(0).astype("int64")
    df["total_units"] = gl["quantity"].sum().reindex(elig).fillna(0).astype("int64")
    recent = p[p["order_ts"] >= t0 - pd.Timedelta(days=30)]
    df["orders_last_30d"] = recent.groupby("customer_id", observed=True).size().reindex(elig).fillna(0).astype("int64")
    df["t0_month_sin"] = float(np.sin(2 * np.pi * t0.month / 12))
    df["t0_month_cos"] = float(np.cos(2 * np.pi * t0.month / 12))
    df["cohort_month"] = first_ts.dt.strftime("%Y-%m").astype("string")
    last = ps.drop_duplicates("customer_id", keep="last").set_index("customer_id")["country"]
    df["country"] = last.reindex(elig).astype("string")
    return df


def build_snapshot(orders: pd.DataFrame, lines: pd.DataFrame, t0: pd.Timestamp, cfg: Config) -> pd.DataFrame:
    """One row per eligible customer (>= 1 purchase order in [T0-obs, T0)).

    Features use only orders/lines with ts < T0 (assert, raise LeakageError);
    target ``repeat_purchase_{outcome}d`` and ``label_future_value_{outcome}d`` use only
    purchase orders in [T0, T0+outcome). Column formulas: CODE SPEC §5.3.
    Does not add RFM scores, segment or split (added by rfm/split).
    """
    t = cfg.raw["temporal"]
    t0 = pd.Timestamp(t0)
    obs_start = t0 - pd.Timedelta(days=t["observation_days"])
    out_end = t0 + pd.Timedelta(days=t["outcome_days"])
    hist = orders[orders["order_ts"] < t0].copy()
    hist.attrs["obs_start"] = obs_start
    obs_lines = lines[(lines["invoice_ts"] < t0) & (lines["invoice_ts"] >= obs_start)
                      & (lines["line_type"] == "purchase")]
    if len(hist) and hist["order_ts"].max() >= t0:
        raise LeakageError("post-T0 order in feature history")
    if len(obs_lines) and obs_lines["invoice_ts"].max() >= t0:
        raise LeakageError("post-T0 line in feature history")
    df = _features(hist, obs_lines, t0)

    fut = orders[(orders["order_ts"] >= t0) & (orders["order_ts"] < out_end) & (orders["order_type"] == "purchase")]
    if len(fut) and (fut["order_ts"].min() < t0 or fut["order_ts"].max() >= out_end):
        raise LeakageError("outcome outside [T0, T0+outcome)")
    fv = fut.groupby("customer_id", observed=True)["order_value"].sum()
    target = t["target_name"]
    df[target] = df.index.isin(fv.index).astype("int8")
    df[f"label_future_value_{t['outcome_days']}d"] = fv.reindex(df.index).fillna(0.0).astype("float64")

    df.index.name = "customer_id"
    df = df.reset_index()
    df["customer_id"] = df["customer_id"].astype("string")
    df.insert(1, "decision_date", pd.Series(t0, index=df.index).astype("datetime64[ns]"))
    return df.sort_values("customer_id", kind="mergesort").reset_index(drop=True)


def build_all_snapshots(orders: pd.DataFrame, lines: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Concatenate build_snapshot for every T0 from generate_t0_dates; add feature_version.
    Sorted by (decision_date, customer_id). Satisfies contract ``customer_snapshots``."""
    from retail_targeting.contracts import validate_frame

    dates = generate_t0_dates(lines["invoice_ts"].min(), lines["invoice_ts"].max(), cfg)
    purchase_lines = lines[lines["line_type"] == "purchase"]
    frames = []
    for t0 in dates:
        frames.append(build_snapshot(orders, purchase_lines, t0, cfg))
        log.info("snapshot %s: %d customers", t0.date(), len(frames[-1]))
    snaps = pd.concat(frames, ignore_index=True)
    snaps["feature_version"] = pd.Series(cfg.raw["versions"]["feature_version"], index=snaps.index, dtype="string")
    return validate_frame(snaps, "customer_snapshots")
