# Pipeline Guard

Pipeline Guard is a Python-based data ingestion and quality-checking project. It reads CSV files, validates their structure and records, calculates data-quality metrics, transforms accepted data, and saves the processed output.

## Features

- CSV data ingestion using pandas
- Required-column schema validation
- Missing-value and negative-value metrics
- Record validation and quarantine handling
- Data transformation and calculated columns
- SQLite persistence for pipeline run history
- JSON-formatted application logs
- Command-line pipeline execution
- FastAPI endpoints for health checks and run history
- Streamlit dashboard for monitoring pipeline runs
- Automated unit tests using pytest

## Technology Stack

- Python
- pandas
- SQLAlchemy
- SQLite
- FastAPI
- Streamlit
- pytest

See `requirements.txt` for the project's Python dependencies.

## Project Structure

```text
pipeline-guard/
├── app/
│   ├── ingestion/
│   ├── storage/
│   ├── transformation/
│   ├── validation/
│   ├── api.py
│   ├── cli.py
│   ├── config.py
│   ├── dashboard.py
│   ├── logging_config.py
│   └── pipeline.py
├── data/
│   └── raw/
│       └── sample_sales.csv
├── tests/
│   └── unit/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Run the following commands from the project root in Git Bash on Windows:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

## Run the Pipeline

Execute the pipeline against the sample CSV:

```bash
python -m app.cli data/raw/sample_sales.csv
```

The command prints a JSON summary containing the execution status, input and output row counts, data-quality metrics, and a preview of the processed records.

## Run Unit Tests

```bash
python -m pytest tests/unit -q -W default
```

The current verified baseline is 72 passing unit tests. Run the command again after making changes to confirm the latest result.

## Start the API

```bash
uvicorn app.api:app --reload
```

When the server starts, open `http://127.0.0.1:8000/docs` to explore the interactive API documentation.

## Start the Dashboard

Open a separate terminal in the project root, activate the virtual environment, and run:

```bash
streamlit run app/dashboard.py
```

## Configuration

Use `.env.example` as a reference for environment configuration. Create a local `.env` file if required by the application's settings. Do not commit secrets or credentials.

## Current Scope

This project currently uses a sample sales CSV and SQLite for local development. Production deployment, broader dataset testing, and additional operational features should be verified separately before being described as production-ready.

## License

No license has been specified yet.