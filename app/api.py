 
from collections.abc import Generator
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.engine import Engine

from app.config import get_settings
from app.storage.database import create_database_engine, create_tables
from app.storage.repository import PipelineRunRepository


app = FastAPI(
    title="Pipeline Guard API",
    description="Inspect data pipeline health and execution history.",
    version="1.0.0",
)


class PipelineRunResponse(BaseModel):
    """Public API representation of a pipeline run."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    input_rows: int
    accepted_rows: int
    quarantined_rows: int
    output_rows: int
    processed_file: str | None
    quarantine_file: str | None
    error_message: str | None


@contextmanager
def get_repository() -> Generator[PipelineRunRepository, None, None]:
    """Yield a repository while its database engine remains available."""
    settings = get_settings()
    engine: Engine = create_database_engine(settings.database_url)

    try:
        create_tables(engine)
        yield PipelineRunRepository(engine)
    finally:
        engine.dispose()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report whether the API is responding."""
    return {"status": "healthy"}


@app.get("/runs", response_model=list[PipelineRunResponse])
def list_pipeline_runs(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PipelineRunResponse]:
    """Return the most recent pipeline runs."""
    try:
        with get_repository() as repository:
            runs = repository.list_runs(limit=limit)
            return [
                PipelineRunResponse.model_validate(run)
                for run in runs
            ]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve pipeline run history.",
        ) from exc


@app.get("/runs/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_run(run_id: int) -> PipelineRunResponse:
    """Return one pipeline run by its ID."""
    try:
        with get_repository() as repository:
            run = repository.get_run(run_id)

            if run is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Pipeline run {run_id} was not found.",
                )

            return PipelineRunResponse.model_validate(run)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve pipeline run.",
        ) from exc
