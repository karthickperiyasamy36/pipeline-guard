 
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.config import get_settings
from app.ingestion.csv_reader import read_csv_file
from app.validation.schema_validator import validate_required_columns
from app.validation.data_quality import (
    find_missing_values,
    find_negative_values,
)
from app.validation.record_validator import validate_sales_records
from app.transformation.cleaner import clean_sales_data
from app.storage.csv_writer import write_csv_file
from app.storage.database import create_database_engine, create_tables
from app.storage.repository import PipelineRunRepository


logger = logging.getLogger(__name__)


def run_pipeline(file_path: str | Path) -> dict:
    """Process a CSV file, log execution events, and persist run history."""

    settings = get_settings()
    input_path = Path(file_path)

    logger.info(
        "Pipeline execution requested",
        extra={"input_file": str(input_path)},
    )

    engine = create_database_engine(settings.database_url)

    try:
        create_tables(engine)
        repository = PipelineRunRepository(engine)
        run_id = repository.create_run()

        logger.info(
            "Pipeline execution started",
            extra={
                "run_id": run_id,
                "input_file": str(input_path),
            },
        )

        dataframe = None
        accepted_records = None
        quarantined_records = None
        transformed_data = None
        missing_values = {}
        negative_values = {}
        processed_file = None
        quarantine_file = None

        try:
            # 1. Read the input CSV.
            dataframe = read_csv_file(input_path)

            logger.info(
                "Input CSV loaded",
                extra={
                    "run_id": run_id,
                    "input_rows": len(dataframe),
                    "input_columns": list(dataframe.columns),
                },
            )

            # 2. Validate the required schema.
            validate_required_columns(
                dataframe,
                settings.required_columns,
            )

            logger.info(
                "Input schema validated",
                extra={
                    "run_id": run_id,
                    "required_columns": settings.required_columns,
                },
            )

            # 3. Calculate quality metrics.
            missing_values = (
                find_missing_values(dataframe)["missing_count"].to_dict()
            )

            for column in settings.negative_value_columns:
                if column in dataframe.columns:
                    if dataframe[column].dtype.kind in "iuf":
                        negative_values.update(
                            find_negative_values(dataframe, [column])
                        )

            logger.info(
                "Data-quality metrics calculated",
                extra={
                    "run_id": run_id,
                    "missing_values": missing_values,
                    "negative_values": negative_values,
                },
            )

            # 4. Separate accepted and quarantined records.
            accepted_records, quarantined_records = (
                validate_sales_records(dataframe)
            )

            logger.info(
                "Record validation completed",
                extra={
                    "run_id": run_id,
                    "accepted_rows": len(accepted_records),
                    "quarantined_rows": len(quarantined_records),
                },
            )

            # 5. Save quarantined records.
            if not quarantined_records.empty:
                quarantine_directory = Path("data") / "quarantine"
                quarantine_directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                timestamp = datetime.now(timezone.utc).strftime(
                    "%Y%m%dT%H%M%S%fZ"
                )
                quarantine_path = (
                    quarantine_directory
                    / f"quarantine_{timestamp}.csv"
                )

                quarantined_records.to_csv(
                    quarantine_path,
                    index=False,
                )
                quarantine_file = str(quarantine_path)

                logger.warning(
                    "Rejected records saved to quarantine",
                    extra={
                        "run_id": run_id,
                        "quarantined_rows": len(quarantined_records),
                        "quarantine_file": quarantine_file,
                    },
                )

            # 6. Transform accepted records.
            transformed_data = clean_sales_data(accepted_records)

            logger.info(
                "Accepted records transformed",
                extra={
                    "run_id": run_id,
                    "output_rows": len(transformed_data),
                },
            )

            # 7. Save processed output.
            if not transformed_data.empty:
                processed_directory = Path("data") / "processed"

                timestamp = datetime.now(timezone.utc).strftime(
                    "%Y%m%dT%H%M%S%fZ"
                )
                processed_path = (
                    processed_directory
                    / f"processed_{timestamp}.csv"
                )

                processed_file = str(
                    write_csv_file(transformed_data, processed_path)
                )

                logger.info(
                    "Processed output saved",
                    extra={
                        "run_id": run_id,
                        "processed_file": processed_file,
                    },
                )

            # 8. Persist successful execution.
            repository.complete_run(
                run_id,
                status="success",
                input_rows=len(dataframe),
                accepted_rows=len(accepted_records),
                quarantined_rows=len(quarantined_records),
                output_rows=len(transformed_data),
                missing_values=missing_values,
                negative_values=negative_values,
                processed_file=processed_file,
                quarantine_file=quarantine_file,
            )

            logger.info(
                "Pipeline execution completed successfully",
                extra={
                    "run_id": run_id,
                    "input_rows": len(dataframe),
                    "accepted_rows": len(accepted_records),
                    "quarantined_rows": len(quarantined_records),
                    "output_rows": len(transformed_data),
                },
            )

            # 9. Preserve the existing return structure.
            return {
                "run_id": run_id,
                "status": "success",
                "input_rows": len(dataframe),
                "accepted_rows": len(accepted_records),
                "quarantined_rows": len(quarantined_records),
                "output_rows": len(transformed_data),
                "missing_values": missing_values,
                "negative_values": negative_values,
                "processed_file": processed_file,
                "quarantine_file": quarantine_file,
                "quarantined_data": quarantined_records,
                "data": transformed_data,
            }

        except Exception as exc:
            logger.exception(
                "Pipeline execution failed",
                extra={
                    "run_id": run_id,
                    "input_file": str(input_path),
                },
            )

            # Preserve the existing failed-run database recording.
            try:
                repository.complete_run(
                    run_id,
                    status="failed",
                    input_rows=(
                        len(dataframe) if dataframe is not None else 0
                    ),
                    accepted_rows=(
                        len(accepted_records)
                        if accepted_records is not None
                        else 0
                    ),
                    quarantined_rows=(
                        len(quarantined_records)
                        if quarantined_records is not None
                        else 0
                    ),
                    output_rows=(
                        len(transformed_data)
                        if transformed_data is not None
                        else 0
                    ),
                    missing_values=missing_values,
                    negative_values=negative_values,
                    processed_file=processed_file,
                    quarantine_file=quarantine_file,
                    error_message=str(exc),
                )
            except Exception:
                logger.exception(
                    "Could not persist pipeline failure",
                    extra={"run_id": run_id},
                )

            raise

    finally:
        engine.dispose()
