
import argparse
import json
import logging
from pathlib import Path

from app.logging_config import configure_logging
from app.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Pipeline Guard CSV quality pipeline."
    )
    parser.add_argument(
        "file",
        help="Path to the input CSV file",
    )
    args = parser.parse_args()

    configure_logging()
    logger = logging.getLogger(__name__)

    try:
        result = run_pipeline(Path(args.file))

        summary = {
            "status": result["status"],
            "input_rows": result["input_rows"],
            "output_rows": result["output_rows"],
            "missing_values": result["missing_values"],
            "negative_values": result["negative_values"],
            "output_preview": result["data"].head(5).to_dict(
                orient="records"
            ),
        }

        print(json.dumps(summary, indent=2, default=str))
        return 0

    except Exception as exc:
        logger.exception("Pipeline execution failed")
        print(
            json.dumps(
                {"status": "failed", "error": str(exc)},
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
