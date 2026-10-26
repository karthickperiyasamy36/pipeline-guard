import pytest

from app.ingestion.csv_reader import CSVIngestionError, read_csv_file


def test_read_valid_csv(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity\nPen,10\nBook,5\n",
        encoding="utf-8",
    )

    dataframe = read_csv_file(csv_file)

    assert list(dataframe.columns) == ["product", "quantity"]
    assert len(dataframe) == 2
    assert dataframe.iloc[0]["product"] == "Pen"
    assert dataframe.iloc[0]["quantity"] == 10


def test_missing_file_is_rejected(tmp_path):
    csv_file = tmp_path / "missing.csv"

    with pytest.raises(CSVIngestionError, match="does not exist"):
        read_csv_file(csv_file)


def test_empty_file_is_rejected(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(CSVIngestionError, match="is empty"):
        read_csv_file(csv_file)


def test_headers_without_data_are_rejected(tmp_path):
    csv_file = tmp_path / "headers_only.csv"
    csv_file.write_text("product,quantity\n", encoding="utf-8")

    with pytest.raises(CSVIngestionError, match="no data rows"):
        read_csv_file(csv_file)


def test_directory_is_rejected(tmp_path):
    with pytest.raises(CSVIngestionError, match="not a file"):
        read_csv_file(tmp_path)
