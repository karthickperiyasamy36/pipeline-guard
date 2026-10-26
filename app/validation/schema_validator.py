    
import pandas as pd


class SchemaValidationError(Exception):
    """Raised when a DataFrame does not match the required schema."""


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """Check whether a DataFrame contains all required columns."""

    if not required_columns:
        raise ValueError("required_columns must not be empty")

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        missing = ", ".join(missing_columns)
        raise SchemaValidationError(
            f"Missing required columns: {missing}"
        )
