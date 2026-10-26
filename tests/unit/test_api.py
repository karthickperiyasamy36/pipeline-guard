
from fastapi.testclient import TestClient

from app import api
from app.storage.database import create_database_engine, create_tables
from app.storage.repository import PipelineRunRepository


def setup_test_database(tmp_path, monkeypatch):
    """Configure an isolated SQLite database for API tests."""
    database_path = tmp_path / "api_test.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    settings = api.get_settings()
    monkeypatch.setattr(settings, "database_url", database_url)

    engine = create_database_engine(database_url)
    create_tables(engine)

    repository = PipelineRunRepository(engine)

    return engine, repository


def test_health_endpoint():
    client = TestClient(api.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_runs_returns_saved_runs(tmp_path, monkeypatch):
    engine, repository = setup_test_database(tmp_path, monkeypatch)

    try:
        run_id = repository.create_run()
        repository.complete_run(
            run_id,
            status="success",
            input_rows=10,
            accepted_rows=9,
            quarantined_rows=1,
            output_rows=9,
        )

        client = TestClient(api.app)
        response = client.get("/runs")

        assert response.status_code == 200

        runs = response.json()
        assert len(runs) == 1
        assert runs[0]["id"] == run_id
        assert runs[0]["status"] == "success"
        assert runs[0]["input_rows"] == 10
        assert runs[0]["accepted_rows"] == 9
        assert runs[0]["quarantined_rows"] == 1
        assert runs[0]["output_rows"] == 9
    finally:
        engine.dispose()


def test_list_runs_respects_limit(tmp_path, monkeypatch):
    engine, repository = setup_test_database(tmp_path, monkeypatch)

    try:
        for _ in range(3):
            repository.create_run()

        client = TestClient(api.app)
        response = client.get("/runs?limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2
    finally:
        engine.dispose()


def test_list_runs_rejects_invalid_limit():
    client = TestClient(api.app)

    response = client.get("/runs?limit=0")

    assert response.status_code == 422


def test_get_existing_run(tmp_path, monkeypatch):
    engine, repository = setup_test_database(tmp_path, monkeypatch)

    try:
        run_id = repository.create_run()
        repository.complete_run(
            run_id,
            status="failed",
            input_rows=5,
            error_message="Missing required columns: price",
        )

        client = TestClient(api.app)
        response = client.get(f"/runs/{run_id}")

        assert response.status_code == 200
        assert response.json()["id"] == run_id
        assert response.json()["status"] == "failed"
        assert (
            response.json()["error_message"]
            == "Missing required columns: price"
        )
    finally:
        engine.dispose()


def test_get_nonexistent_run_returns_404():
    client = TestClient(api.app)

    response = client.get("/runs/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Pipeline run 999999 was not found."
    )
