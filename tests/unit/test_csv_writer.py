
import pandas as pd
import pytest

from app.storage.csv_writer import (
    CSVStorageError,
    write_csv_file,
)


def test_write_csv_file_creates_file(tmp_path):
    dataframe = pd.DataFrame({
        "product": ["Pen", "Book"],
        "quantity": [10, 2],
        "price": [5.0, 25.0],
    })

    output_path = tmp_path / "processed" / "sales.csv"

    saved_path = write_csv_file(dataframe, output_path)

    assert saved_path == output_path
    assert output_path.exists()


def test_write_csv_file_preserves_data(tmp_path):
    dataframe = pd.DataFrame({
        "product": ["Pen", "Book"],
        "quantity": [10, 2],
        "price": [5.0, 25.0],
    })

    output_path = tmp_path / "sales.csv"
    write_csv_file(dataframe, output_path)

    saved_dataframe = pd.read_csv(output_path)

    pd.testing.assert_frame_equal(
        saved_dataframe,
        dataframe,
    )


def test_write_csv_file_does_not_save_index(tmp_path):
    dataframe = pd.DataFrame({
        "product": ["Pen"],
        "quantity": [10],
        "price": [5.0],
    })

    output_path = tmp_path / "sales.csv"
    write_csv_file(dataframe, output_path)

    saved_dataframe = pd.read_csv(output_path)

    assert "Unnamed: 0" not in saved_dataframe.columns


def test_write_csv_file_rejects_empty_dataframe(tmp_path):
    dataframe = pd.DataFrame(
        columns=["product", "quantity", "price"]
    )

    output_path = tmp_path / "sales.csv"

    with pytest.raises(
        CSVStorageError,
        match="empty DataFrame",
    ):
        write_csv_file(dataframe, output_path)

    assert not output_path.exists()
