 
import numpy as np
import pandas as pd


class DataTransformationError(Exception):
    """Raised when data cannot be transformed."""


def clean_sales_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Standardize sales data and calculate total amounts."""

    required_columns = ["product", "quantity", "price"]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise DataTransformationError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Work on a copy so the input DataFrame remains unchanged.
    result = dataframe.copy()

    # Validate and standardize product names.
    if result["product"].isnull().any():
        raise DataTransformationError(
            "Column 'product' contains missing values"
        )

    result["product"] = result["product"].astype(str).str.strip()

    if result["product"].eq("").any():
        raise DataTransformationError(
            "Column 'product' contains blank values"
        )

    # Convert numeric columns, rejecting invalid text.
    try:
        result["quantity"] = pd.to_numeric(
            result["quantity"],
            errors="raise",
        )
        result["price"] = pd.to_numeric(
            result["price"],
            errors="raise",
        )
    except (ValueError, TypeError) as exc:
        raise DataTransformationError(
            "Quantity and price must contain numeric values"
        ) from exc

    # Reject infinite values but preserve missing values for quality reporting.
    for column in ["quantity", "price"]:
        values = result[column].dropna()

        if not np.isfinite(values).all():
            raise DataTransformationError(
                f"Column '{column}' contains infinite values"
            )

    # Negative quantities and prices are reported by the quality layer.
    # Negative quantities can represent returns or cancellations.
    # Missing numeric values are preserved for pipeline quality reporting.

    # Calculate totals; missing numeric values produce missing totals.
    result["total_amount"] = result["quantity"] * result["price"]

    return result
