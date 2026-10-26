
from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, select

from app.storage.database import (
    create_database_engine,
    create_tables,
    get_session_factory,
)
from app.storage.models import PipelineRun


def test_create_database_tables(tmp_path):
    database_path = tmp_path / "test_pipeline_guard.db"
    engine = create_database_engine(f"sqlite:///{database_path}")

    try:
        create_tables(engine)

        table_names = inspect(engine).get_table_names()

        assert "pipeline_runs" in table_names
    finally:
        engine.dispose()


def test_save_and_read_pipeline_run(tmp_path):
    database_path = tmp_path / "test_pipeline_guard.db"
    engine = create_database_engine(f"sqlite:///{database_path}")

    try:
        create_tables(engine)
        session_factory = get_session_factory(engine)

        with session_factory() as session:
            run = PipelineRun(
                status="success",
                input_rows=100,
                accepted_rows=90,
                quarantined_rows=10,
                output_rows=90,
                missing_values={"product": 2},
                negative_values={"quantity": 5},
                processed_file="data/processed/example.csv",
                quarantine_file="data/quarantine/example.csv",
                completed_at=datetime.now(timezone.utc),
            )

            session.add(run)
            session.commit()
            saved_id = run.id

        with session_factory() as session:
            saved_run = session.get(PipelineRun, saved_id)

            assert saved_run is not None
            assert saved_run.status == "success"
            assert saved_run.input_rows == 100
            assert saved_run.accepted_rows == 90
            assert saved_run.quarantined_rows == 10
            assert saved_run.output_rows == 90
            assert saved_run.missing_values == {"product": 2}
            assert saved_run.negative_values == {"quantity": 5}

    finally:
        engine.dispose()


def test_pipeline_run_defaults(tmp_path):
    database_path = tmp_path / "test_pipeline_guard.db"
    engine = create_database_engine(f"sqlite:///{database_path}")

    try:
        create_tables(engine)
        session_factory = get_session_factory(engine)

        with session_factory() as session:
            run = PipelineRun()
            session.add(run)
            session.commit()

            assert run.id is not None
            assert run.status == "running"
            assert run.input_rows == 0
            assert run.accepted_rows == 0
            assert run.quarantined_rows == 0
            assert run.output_rows == 0
            assert run.started_at is not None

    finally:
        engine.dispose()


def test_empty_database_url_is_rejected():
    with pytest.raises(ValueError, match="Database URL must not be empty"):
        create_database_engine("   ")
