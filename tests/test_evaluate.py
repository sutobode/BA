import numpy as np
import pytest

from helpers import todo
from retail_targeting.models.evaluate import classification_metrics, top_k_count


def test_top_k_count():
    assert top_k_count(100, 0.05) == 5 and top_k_count(10, 0.01) == 1


def test_classification_metrics_hand_example():
    y = np.array([1, 0, 1, 0])
    s = np.array([0.9, 0.8, 0.7, 0.1])
    m = classification_metrics(y, s, [0.5])
    assert m["prevalence"] == 0.5
    assert m["precision_at_0.5"] == 0.5 and m["recall_at_0.5"] == 0.5 and m["lift_at_0.5"] == 1.0
    assert m["roc_auc"] == pytest.approx(0.75)
    assert "brier" in m


def test_no_brier_for_unbounded_score():
    m = classification_metrics(np.array([1, 0]), np.array([12.0, 3.0]), [0.5])
    assert "brier" not in m and m["roc_auc"] == 1.0
