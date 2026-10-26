
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.engine import Engine

from app.storage.database import get_session_factory
from app.storage.models import PipelineRun


class PipelineRunRepository:
    """Manage pipeline run records in the database."""

    def __init__(self, engine: Engine) -> None:
        self._session_factory = get_session_factory(engine)

    def create_run(self) -> int:
        """Create a run with running status and return its ID."""
        with self._session_factory() as session:
            run = PipelineRun(status="running")
            session.add(run)
            session.commit()
            session.refresh(run)
            return run.id

    def complete_run(
        self,
        run_id: int,
        *,
        status: str,
        input_rows: int = 0,
        accepted_rows: int = 0,
        quarantined_rows: int = 0,
        output_rows: int = 0,
        missing_values: dict | None = None,
        negative_values: dict | None = None,
        processed_file: str | None = None,
        quarantine_file: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Update a run with its final status and metrics."""
        allowed_statuses = {"success", "failed"}

        if status not in allowed_statuses:
            raise ValueError(
                f"Status must be one of {sorted(allowed_statuses)}."
            )

        counts = {
            "input_rows": input_rows,
            "accepted_rows": accepted_rows,
            "quarantined_rows": quarantined_rows,
            "output_rows": output_rows,
        }
        if any(value < 0 for value in counts.values()):
            raise ValueError("Row counts must not be negative.")

        with self._session_factory() as session:
            run = session.get(PipelineRun, run_id)

            if run is None:
                raise ValueError(f"Pipeline run {run_id} does not exist.")

            run.status = status
            run.completed_at = datetime.now(timezone.utc)
            run.input_rows = input_rows
            run.accepted_rows = accepted_rows
            run.quarantined_rows = quarantined_rows
            run.output_rows = output_rows
            run.missing_values = missing_values
            run.negative_values = negative_values
            run.processed_file = processed_file
            run.quarantine_file = quarantine_file
            run.error_message = error_message

            session.commit()

    def get_run(self, run_id: int) -> PipelineRun | None:
        """Retrieve one run by its ID."""
        with self._session_factory() as session:
            return session.get(PipelineRun, run_id)

    def list_runs(self, limit: int = 100) -> list[PipelineRun]:
        """Return the most recent runs first."""
        if limit < 1:
            raise ValueError("Limit must be greater than zero.")

        statement = (
            select(PipelineRun)
            .order_by(PipelineRun.id.desc())
            .limit(limit)
        )

        with self._session_factory() as session:
            return list(session.scalars(statement).all())
