import copy
import datetime as dt

import pandas as pd
import pytest

from helpers import todo
from retail_targeting.config import Config, REPO_ROOT
from retail_targeting.models.split import assign_split, check_split_config


def test_proposed_split_is_valid(cfg):
    check_split_config(cfg)


def test_purge_violation_detected(raw_config_dict):
    raw = copy.deepcopy(raw_config_dict)
    raw["temporal"]["validation_snapshots"] = [dt.date(2011, 2, 1)]  # bypass validate_config on purpose
    with pytest.raises(ValueError, match="purge"):
        check_split_config(Config(raw=raw, root=REPO_ROOT))


def test_assign_split(cfg):
    dates = pd.to_datetime(["2010-06-01", "2011-02-01", "2011-04-01", "2011-06-01", "2011-09-01", "2011-11-01"])
    out = assign_split(pd.DataFrame({"decision_date": dates}), cfg)
    assert out.tolist() == ["train", "purged", "validation", "purged", "test", "unused"]
