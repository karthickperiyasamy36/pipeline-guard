
import pandas as pd
import pytest

from app.pipeline import run_pipeline
from app.config import get_settings
from app.validation.schema_validator import SchemaValidationError
from app.storage.database import create_database_engine
from app.storage.repository import PipelineRunRepository


def test_pipeline_runs_successfully(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity,price\n"
        "Pen,10,5.0\n"
        "Book,2,25.0\n",
        encoding="utf-8",
    )

    result = run_pipeline(csv_file)

    assert result["status"] == "success"
    assert result["input_rows"] == 2
    assert result["output_rows"] == 2
    assert result["accepted_rows"] == 2
    assert result["quarantined_rows"] == 0
    assert result["quarantine_file"] is None
    assert isinstance(result["data"], pd.DataFrame)

    # Verify that the processed CSV was saved.
    processed_file = result["processed_file"]
    assert processed_file is not None

    processed_path = tmp_path / processed_file
    assert processed_path.exists()

    saved_data = pd.read_csv(processed_path)
    assert len(saved_data) == 2
    assert "total_amount" in saved_data.columns


def test_pipeline_reports_missing_values(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity,price\n"
        "Pen,,5.0\n"
        "Book,2,25.0\n",
        encoding="utf-8",
    )

    result = run_pipeline(csv_file)

    assert result["missing_values"]["quantity"] == 1
    assert result["quarantined_rows"] == 1
    assert result["accepted_rows"] == 1


def test_pipeline_counts_negative_values(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity,price\n"
        "Pen,-2,5.0\n"
        "Book,2,25.0\n",
        encoding="utf-8",
    )

    result = run_pipeline(csv_file)

    assert result["negative_values"]["quantity"] == 1
    assert result["accepted_rows"] == 2
    assert result["quarantined_rows"] == 0


def test_pipeline_quarantines_missing_product(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity,price\n"
        "Pen,10,5.0\n"
        ",3,2.0\n",
        encoding="utf-8",
    )

    result = run_pipeline(csv_file)

    assert result["status"] == "success"
    assert result["input_rows"] == 2
    assert result["accepted_rows"] == 1
    assert result["quarantined_rows"] == 1
    assert result["output_rows"] == 1

    quarantined = result["quarantined_data"]
    assert "Product is missing or blank" in (
        quarantined.iloc[0]["rejection_reason"]
    )


def test_pipeline_rejects_missing_required_columns(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity\n"
        "Pen,10\n",
        encoding="utf-8",
    )

    with pytest.raises(
        SchemaValidationError,
        match="Missing required columns",
    ):
        run_pipeline(csv_file)


def test_pipeline_uses_configured_required_columns(tmp_path):
    settings = get_settings()
    original_columns = settings.required_columns

    try:
        settings.required_columns = ["product", "quantity"]

        csv_file = tmp_path / "sales.csv"
        csv_file.write_text(
            "product,quantity,price\n"
            "Pen,10,5.0\n",
            encoding="utf-8",
        )

        result = run_pipeline(csv_file)

        assert result["status"] == "success"
        assert result["accepted_rows"] == 1
    finally:
        settings.required_columns = original_columns

def test_pipeline_persists_successful_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    settings = get_settings()
    database_path = tmp_path / "pipeline_history.db"
    settings.database_url = f"sqlite:///{database_path.as_posix()}"

    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,quantity,price\n"
        "Pen,10,5.0\n"
        "Book,2,25.0\n",
        encoding="utf-8",
    )

    result = run_pipeline(csv_file)

    assert result["status"] == "success"
    assert result["run_id"] is not None

    engine = create_database_engine(settings.database_url)
    try:
        repository = PipelineRunRepository(engine)
        saved_run = repository.get_run(result["run_id"])

        assert saved_run is not None
        assert saved_run.status == "success"
        assert saved_run.input_rows == 2
        assert saved_run.accepted_rows == 2
        assert saved_run.quarantined_rows == 0
        assert saved_run.output_rows == 2
        assert saved_run.completed_at is not None
        assert saved_run.processed_file == result["processed_file"]
    finally:
        engine.dispose()


def test_pipeline_persists_failed_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    settings = get_settings()
    database_path = tmp_path / "pipeline_history.db"
    settings.database_url = f"sqlite:///{database_path.as_posix()}"

    csv_file = tmp_path / "invalid_sales.csv"
    csv_file.write_text(
        "product,quantity\n"
        "Pen,10\n",
        encoding="utf-8",
    )

    with pytest.raises(
        SchemaValidationError,
        match="Missing required columns",
    ):
        run_pipeline(csv_file)

    engine = create_database_engine(settings.database_url)
    try:
        repository = PipelineRunRepository(engine)
        saved_runs = repository.list_runs(limit=10)

        assert len(saved_runs) == 1

        failed_run = saved_runs[0]
        assert failed_run.status == "failed"
        assert failed_run.completed_at is not None
        assert failed_run.error_message is not None
        assert "Missing required columns" in failed_run.error_message
    finally:
        engine.dispose()
