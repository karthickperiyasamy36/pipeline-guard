
import pandas as pd
import pytest

from app.validation.schema_validator import (
    SchemaValidationError,
    validate_required_columns,
)


def test_valid_schema_passes():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen"],
            "quantity": [10],
            "price": [5.0],
        }
    )

    validate_required_columns(
        dataframe,
        ["product", "quantity", "price"],
    )


def test_missing_column_is_rejected():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen"],
            "quantity": [10],
        }
    )

    with pytest.raises(
        SchemaValidationError,
        match="Missing required columns: price",
    ):
        validate_required_columns(
            dataframe,
            ["product", "quantity", "price"],
        )


def test_multiple_missing_columns_are_reported():
    dataframe = pd.DataFrame({"product": ["Pen"]})

    with pytest.raises(
        SchemaValidationError,
        match="quantity, price",
    ):
        validate_required_columns(
            dataframe,
            ["product", "quantity", "price"],
        )


def test_empty_required_columns_are_rejected():
    dataframe = pd.DataFrame({"product": ["Pen"]})

    with pytest.raises(
        ValueError,
        match="required_columns must not be empty",
    ):
        validate_required_columns(dataframe, [])
