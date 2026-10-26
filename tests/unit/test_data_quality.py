
import pandas as pd
import pytest

from app.validation.data_quality import (
    find_missing_values,
    find_negative_values,
)


def test_missing_values_are_counted():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen", None, "Book"],
            "quantity": [10, 5, None],
        }
    )

    result = find_missing_values(dataframe)

    assert result.loc["product", "missing_count"] == 1
    assert result.loc["quantity", "missing_count"] == 1


def test_no_missing_values():
    dataframe = pd.DataFrame({"product": ["Pen", "Book"]})

    result = find_missing_values(dataframe)

    assert result["missing_count"].sum() == 0


def test_negative_values_are_counted():
    dataframe = pd.DataFrame(
        {
            "quantity": [10, -2, 5, -1],
            "price": [5.0, 25.0, -3.0, 2.0],
        }
    )

    result = find_negative_values(dataframe, ["quantity", "price"])

    assert result == {"quantity": 2, "price": 1}


def test_missing_column_is_rejected():
    dataframe = pd.DataFrame({"quantity": [10, 5]})

    with pytest.raises(ValueError, match="Column not found"):
        find_negative_values(dataframe, ["price"])


def test_non_numeric_column_is_rejected():
    dataframe = pd.DataFrame({"product": ["Pen", "Book"]})

    with pytest.raises(ValueError, match="must be numeric"):
        find_negative_values(dataframe, ["product"])
