
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.database import Base


class PipelineRun(Base):
    """Database record describing one execution of Pipeline Guard."""

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="running",
    )

    input_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    accepted_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    quarantined_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    output_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    missing_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    negative_values: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    processed_file: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    quarantine_file: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
