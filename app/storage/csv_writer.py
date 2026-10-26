
from pathlib import Path

import pandas as pd


class CSVStorageError(Exception):
    """Raised when a DataFrame cannot be saved to a CSV file."""


def write_csv_file(
    dataframe: pd.DataFrame,
    file_path: str | Path,
) -> Path:
    """Save a DataFrame to a CSV file and return its path."""

    path = Path(file_path)

    if dataframe.empty:
        raise CSVStorageError(
            "Cannot save an empty DataFrame."
        )

    try:
        # Create the output directory if it does not exist.
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save without writing the DataFrame index as a column.
        dataframe.to_csv(path, index=False)

    except (OSError, ValueError) as exc:
        raise CSVStorageError(
            f"Unable to save CSV file '{path}': {exc}"
        ) from exc

    return path
