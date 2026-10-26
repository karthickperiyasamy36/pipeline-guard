
import pytest

from app.storage.database import create_database_engine, create_tables
from app.storage.repository import PipelineRunRepository


@pytest.fixture
def repository(tmp_path):
    database_path = tmp_path / "repository_test.db"
    engine = create_database_engine(f"sqlite:///{database_path}")
    create_tables(engine)

    yield PipelineRunRepository(engine)

    engine.dispose()


def test_create_run(repository):
    run_id = repository.create_run()

    run = repository.get_run(run_id)

    assert run is not None
    assert run.id == run_id
    assert run.status == "running"
    assert run.completed_at is None


def test_complete_run_saves_metrics(repository):
    run_id = repository.create_run()

    repository.complete_run(
        run_id,
        status="success",
        input_rows=100,
        accepted_rows=90,
        quarantined_rows=10,
        output_rows=90,
        missing_values={"product": 2},
        negative_values={"quantity": 5},
        processed_file="processed.csv",
        quarantine_file="quarantine.csv",
    )

    run = repository.get_run(run_id)

    assert run is not None
    assert run.status == "success"
    assert run.completed_at is not None
    assert run.input_rows == 100
    assert run.accepted_rows == 90
    assert run.quarantined_rows == 10
    assert run.output_rows == 90
    assert run.missing_values == {"product": 2}
    assert run.negative_values == {"quantity": 5}


def test_list_runs_returns_newest_first(repository):
    first_id = repository.create_run()
    second_id = repository.create_run()

    runs = repository.list_runs(limit=10)

    assert [run.id for run in runs] == [second_id, first_id]


def test_list_runs_rejects_invalid_limit(repository):
    with pytest.raises(ValueError, match="Limit must be greater than zero"):
        repository.list_runs(limit=0)


def test_complete_run_rejects_invalid_status(repository):
    run_id = repository.create_run()

    with pytest.raises(ValueError, match="Status must be one of"):
        repository.complete_run(run_id, status="pending")


def test_complete_run_rejects_negative_counts(repository):
    run_id = repository.create_run()

    with pytest.raises(ValueError, match="Row counts must not be negative"):
        repository.complete_run(
            run_id,
            status="success",
            input_rows=-1,
        )


def test_complete_run_rejects_unknown_id(repository):
    with pytest.raises(ValueError, match="does not exist"):
        repository.complete_run(999, status="success")
