
import pandas as pd
import pytest

from app.validation.record_validator import validate_sales_records


def test_valid_records_are_accepted():
    dataframe = pd.DataFrame({
        "product": ["Pen", "Book"],
        "quantity": [10, 5],
        "price": [5.0, 25.0],
    })

    accepted, quarantined = validate_sales_records(dataframe)

    assert len(accepted) == 2
    assert quarantined.empty


def test_missing_quantity_is_quarantined():
    dataframe = pd.DataFrame({
        "product": ["Pen"],
        "quantity": [None],
        "price": [5.0],
    })

    accepted, quarantined = validate_sales_records(dataframe)

    assert accepted.empty
    assert len(quarantined) == 1
    assert "Quantity is missing or non-numeric" in (
        quarantined.iloc[0]["rejection_reason"]
    )


def test_negative_price_is_quarantined():
    dataframe = pd.DataFrame({
        "product": ["Pen"],
        "quantity": [10],
        "price": [-5.0],
    })

    accepted, quarantined = validate_sales_records(dataframe)

    assert accepted.empty
    assert "Price is negative" in quarantined.iloc[0]["rejection_reason"]


def test_negative_quantity_is_allowed():
    dataframe = pd.DataFrame({
        "product": ["Returned Book"],
        "quantity": [-2],
        "price": [25.0],
    })

    accepted, quarantined = validate_sales_records(dataframe)

    assert len(accepted) == 1
    assert quarantined.empty


def test_blank_product_is_quarantined():
    dataframe = pd.DataFrame({
        "product": ["   "],
        "quantity": [10],
        "price": [5.0],
    })

    accepted, quarantined = validate_sales_records(dataframe)

    assert accepted.empty
    assert "Product is missing or blank" in (
        quarantined.iloc[0]["rejection_reason"]
    )


def test_missing_required_column_raises_error():
    dataframe = pd.DataFrame({
        "product": ["Pen"],
        "quantity": [10],
    })

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_sales_records(dataframe)


def test_input_dataframe_is_not_modified():
    dataframe = pd.DataFrame({
        "product": [" Pen "],
        "quantity": [10],
        "price": [5.0],
    })
    original = dataframe.copy(deep=True)

    validate_sales_records(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)
