
import pandas as pd


def find_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return the number of missing values in each column."""

    return dataframe.isnull().sum().to_frame(name="missing_count")


def find_negative_values(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> dict[str, int]:
    """Count negative values in the specified numeric columns."""

    results = {}

    for column in columns:
        if column not in dataframe.columns:
            raise ValueError(f"Column not found: {column}")

        if not pd.api.types.is_numeric_dtype(dataframe[column]):
            raise ValueError(f"Column must be numeric: {column}")

        results[column] = int((dataframe[column] < 0).sum())

    return results
