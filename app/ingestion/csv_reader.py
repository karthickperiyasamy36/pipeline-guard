from pathlib import Path

import pandas as pd


class CSVIngestionError(Exception):
    """Raised when a CSV file cannot be ingested."""


def read_csv_file(file_path: str | Path) -> pd.DataFrame:
    """Read a CSV file and return its contents as a DataFrame."""

    path = Path(file_path)

    if not path.exists():
        raise CSVIngestionError(f"CSV file does not exist: {path}")

    if not path.is_file():
        raise CSVIngestionError(f"Path is not a file: {path}")

    if path.stat().st_size == 0:
        raise CSVIngestionError(f"CSV file is empty: {path}")

    try:
        dataframe = pd.read_csv(path)
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as exc:
        raise CSVIngestionError(
            f"Unable to read CSV file '{path}': {exc}"
        ) from exc
    except OSError as exc:
        raise CSVIngestionError(
            f"Unable to access CSV file '{path}': {exc}"
        ) from exc

    if dataframe.empty:
        raise CSVIngestionError(
            f"CSV file contains headers but no data rows: {path}"
        )

    return dataframe
