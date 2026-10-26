
import pandas as pd
import pytest

from app.transformation.cleaner import (
    DataTransformationError,
    clean_sales_data,
)


def test_sales_data_is_transformed():
    dataframe = pd.DataFrame(
        {
            "product": [" Pen ", "Book"],
            "quantity": [10, 5],
            "price": [5.0, 25.0],
        }
    )

    result = clean_sales_data(dataframe)

    assert result["product"].tolist() == ["Pen", "Book"]
    assert result["total_amount"].tolist() == [50.0, 125.0]


def test_original_dataframe_is_not_modified():
    dataframe = pd.DataFrame(
        {
            "product": [" Pen "],
            "quantity": [10],
            "price": [5.0],
        }
    )
    original = dataframe.copy(deep=True)

    clean_sales_data(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)


def test_missing_required_column_is_rejected():
    dataframe = pd.DataFrame(
        {"product": ["Pen"], "quantity": [10]}
    )

    with pytest.raises(
        DataTransformationError,
        match="Missing required columns",
    ):
        clean_sales_data(dataframe)


def test_missing_product_is_rejected():
    dataframe = pd.DataFrame(
        {
            "product": [None],
            "quantity": [10],
            "price": [5.0],
        }
    )

    with pytest.raises(
        DataTransformationError,
        match="missing values",
    ):
        clean_sales_data(dataframe)


def test_non_numeric_quantity_is_rejected():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen"],
            "quantity": ["abc"],
            "price": [5.0],
        }
    )

    with pytest.raises(
        DataTransformationError,
        match="must contain numeric values",
    ):
        clean_sales_data(dataframe)


def test_missing_quantity_is_preserved_for_quality_reporting():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen"],
            "quantity": [None],
            "price": [5.0],
        }
    )

    result = clean_sales_data(dataframe)

    assert pd.isna(result.loc[0, "quantity"])
    assert pd.isna(result.loc[0, "total_amount"])


def test_missing_price_is_preserved_for_quality_reporting():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen"],
            "quantity": [10],
            "price": [None],
        }
    )

    result = clean_sales_data(dataframe)

    assert pd.isna(result.loc[0, "price"])
    assert pd.isna(result.loc[0, "total_amount"])


def test_negative_price_is_preserved_for_quality_reporting():
    dataframe = pd.DataFrame(
        {
            "product": ["Pen"],
            "quantity": [10],
            "price": [-5.0],
        }
    )

    result = clean_sales_data(dataframe)

    assert result.loc[0, "price"] == -5.0
    assert result.loc[0, "total_amount"] == -50.0


def test_negative_quantity_is_allowed():
    dataframe = pd.DataFrame(
        {
            "product": ["Returned Book"],
            "quantity": [-2],
            "price": [25.0],
        }
    )

    result = clean_sales_data(dataframe)

    assert result["quantity"].tolist() == [-2]
    assert result["total_amount"].tolist() == [-50.0]
