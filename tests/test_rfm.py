import pandas as pd
import pytest

from helpers import todo
from retail_targeting.features.rfm import apply_rfm_scores, assign_segments, fit_rfm_cutoffs


def _train(n=100):
    return pd.DataFrame({"split": ["train"] * n, "recency_days": range(n),
                         "frequency_orders": [1 + i % 10 for i in range(n)],
                         "monetary_net": [float(i * 10) for i in range(n)]})


@todo
def test_cutoffs_train_only():
    df = _train()
    df.loc[0, "split"] = "validation"
    with pytest.raises(ValueError):
        fit_rfm_cutoffs(df)


@todo
def test_scores_range_and_recency_reversed():
    tr = _train()
    scored = apply_rfm_scores(tr, fit_rfm_cutoffs(tr))
    for c in ("r_score", "f_score", "m_score"):
        assert scored[c].between(1, 5).all()
    assert scored.loc[0, "r_score"] == 5 and scored.loc[99, "r_score"] == 1  # small recency → high score
    assert scored.loc[99, "m_score"] == 5
    assert (scored["rfm_score"] == scored[["r_score", "f_score", "m_score"]].sum(axis=1)).all()


@todo
def test_segments_first_match_and_default(cfg):
    df = pd.DataFrame({"r_score": [5, 1, 3, 3, 1], "f_score": [5, 1, 3, 1, 1], "m_score": [5, 5, 2, 1, 1]})
    seg = assign_segments(df, cfg.raw["segmentation"]["rules"])
    assert seg.tolist() == ["High-value active", "High-value at risk", "Developing", "Low-value active", "Dormant"]
