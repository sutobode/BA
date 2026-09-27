import copy
import datetime as dt

import pytest

from retail_targeting.config import ConfigError, config_hash, load_config, split_dates, validate_config


def test_example_config_loads():
    cfg = load_config("project_config.example.yaml")
    assert cfg.temporal.observation_days == 180
    assert cfg.temporal.target_name == "repeat_purchase_90d"
    assert len(cfg.raw["simulation"]["scenarios"]) >= 3


def test_project_config_matches_example():
    assert load_config("project_config.yaml").raw == load_config("project_config.example.yaml").raw


def test_split_dates_proposed():
    s = split_dates(load_config("project_config.example.yaml"))
    assert (len(s["train"]), len(s["validation"]), len(s["test"])) == (8, 2, 2)
    assert s["test"][-1] == dt.date(2011, 9, 1)


def test_config_hash_is_stable(cfg):
    assert config_hash(cfg) == config_hash(cfg) and len(config_hash(cfg)) == 64


def _mutate(raw, fn):
    r = copy.deepcopy(raw)
    fn(r)
    return r


@pytest.mark.parametrize("mutation, message", [
    (lambda r: r["temporal"].update(purge_days=30), "purge_days"),
    (lambda r: r["temporal"].update(validation_snapshots=[dt.date(2011, 2, 1)]), "purge violated"),
    (lambda r: r["temporal"].update(test_snapshots=[dt.date(2011, 1, 1)]), "chronological"),
    (lambda r: r["temporal"].update(target_name="repeat_purchase_60d"), "target_name"),
    (lambda r: r["model"]["numeric_features"].append("repeat_purchase_90d"), "forbidden"),
    (lambda r: r["model"]["numeric_features"].append("label_future_value_90d"), "forbidden"),
    (lambda r: r["model"].update(log1p_features=["not_a_feature"]), "log1p_features"),
    (lambda r: r["simulation"]["scenarios"].pop("base"), "at least 3"),
    (lambda r: r["source"].update(sha256_xlsx="abc"), "sha256_xlsx"),
    (lambda r: r.pop("model"), "missing section"),
])
def test_invalid_configs_rejected(raw_config_dict, mutation, message):
    with pytest.raises(ConfigError, match=message):
        validate_config(_mutate(raw_config_dict, mutation))


def test_null_scenarios_rejected_when_required(raw_config_dict):
    validate_config(raw_config_dict)  # allowed for data/model stages
    with pytest.raises(ConfigError, match="still null"):
        validate_config(raw_config_dict, require_scenarios=True)


def test_invalid_scenario_values(raw_config_dict):
    r = copy.deepcopy(raw_config_dict)
    r["simulation"]["scenarios"]["base"] = {"discount_rate": 0.5, "incremental_lift": 0.1,
                                           "gross_margin": 0.4, "contact_cost": 0}
    with pytest.raises(ConfigError, match="discount_rate < gross_margin"):
        validate_config(r, require_scenarios=False)
