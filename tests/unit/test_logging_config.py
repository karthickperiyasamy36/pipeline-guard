 
import json
import logging

from app.logging_config import JsonFormatter


def test_json_formatter_includes_standard_fields():
    record = logging.LogRecord(
        name="app.pipeline",
        level=logging.INFO,
        pathname="pipeline.py",
        lineno=25,
        msg="Pipeline started",
        args=(),
        exc_info=None,
    )

    result = json.loads(JsonFormatter().format(record))

    assert result["level"] == "INFO"
    assert result["logger"] == "app.pipeline"
    assert result["message"] == "Pipeline started"
    assert result["line"] == 25
    assert "timestamp" in result


def test_json_formatter_includes_custom_fields():
    record = logging.LogRecord(
        name="app.pipeline",
        level=logging.INFO,
        pathname="pipeline.py",
        lineno=30,
        msg="Input CSV loaded",
        args=(),
        exc_info=None,
    )

    record.run_id = 12
    record.input_rows = 500
    record.input_columns = 8

    result = json.loads(JsonFormatter().format(record))

    assert result["run_id"] == 12
    assert result["input_rows"] == 500
    assert result["input_columns"] == 8


def test_json_formatter_handles_non_json_custom_values():
    record = logging.LogRecord(
        name="app.pipeline",
        level=logging.INFO,
        pathname="pipeline.py",
        lineno=35,
        msg="Output saved",
        args=(),
        exc_info=None,
    )

    record.output_path = __import__("pathlib").Path("output.csv")

    result = json.loads(JsonFormatter().format(record))

    assert result["output_path"] == "output.csv"
