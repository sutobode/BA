import pandas as pd
import pytest

from retail_targeting.contracts import SCHEMAS, ContractError, validate_frame


def _orders(**over):
    df = pd.DataFrame({
        "order_id": pd.Series(["1", "C2"], dtype="string"),
        "customer_id": pd.Series(["10001", "10001"], dtype="string"),
        "order_ts": pd.to_datetime(["2010-01-01", "2010-01-02"]),
        "order_type": pd.Series(["purchase", "adjustment"], dtype="string"),
        "order_value": [10.0, -3.0],
        "n_lines": [1, 1], "n_units": [2, 1], "n_products": [1, 1],
        "country": pd.Series(["UK", "UK"], dtype="string"),
    })
    for k, v in over.items():
        df[k] = v
    return df


def test_valid_orders_pass():
    assert validate_frame(_orders(), "orders") is not None


def test_missing_column():
    with pytest.raises(ContractError, match="missing columns"):
        validate_frame(_orders().drop(columns="order_value"), "orders")


def test_wrong_dtype():
    with pytest.raises(ContractError, match="dtype"):
        validate_frame(_orders(n_lines=[1.5, 1.0]), "orders")


def test_null_in_non_nullable():
    with pytest.raises(ContractError, match="null"):
        validate_frame(_orders(customer_id=pd.Series(["10001", None], dtype="string")), "orders")


def test_duplicate_key():
    with pytest.raises(ContractError, match="duplicated"):
        validate_frame(_orders(order_id=pd.Series(["1", "1"], dtype="string")), "orders")


def test_custom_check_sign():
    with pytest.raises(ContractError, match="sign"):
        validate_frame(_orders(order_value=[-1.0, -3.0]), "orders")


def test_all_spec_artifacts_have_schema():
    for name in ["transactions_raw", "lines", "orders", "customer_snapshots", "customer_predictions",
                 "scenario_results", "customer_targeting_table"]:
        assert name in SCHEMAS
