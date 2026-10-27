# Pipeline Guard

Pipeline Guard is a Python-based data ingestion and quality-checking project. It reads CSV files, validates their structure and records, calculates data-quality metrics, transforms accepted data, and saves the processed output. It also records pipeline execution history and provides API endpoints and a dashboard for monitoring runs.

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
├── docs/
├── logs/
├── scripts/
├── tests/
│   └── unit/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Run these commands from the project root in Git Bash on Windows.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

```bash
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run the Pipeline

Execute the pipeline against the sample CSV file:

```bash
python -m app.cli data/raw/sample_sales.csv
```

The command prints a JSON summary containing the execution status, input and output row counts, data-quality metrics, and a preview of the processed records.

## Run Unit Tests

Run the unit tests with:

```bash
python -m pytest tests/unit -q -W default
```

The previously verified baseline is **72 passing unit tests**. Run the command again after making changes to verify the current result.

## Start the API

Start the FastAPI server:

```bash
python -m uvicorn app.api:app --reload
```

Open the following URL in your browser to explore the interactive API documentation:

http://127.0.0.1:8000/docs

Available endpoints:

- `GET /health` — checks API health.
- `GET /runs` — retrieves recent pipeline runs.
- `GET /runs/{run_id}` — retrieves details for an individual pipeline run.

The health endpoint and the pipeline run history endpoints have been tested successfully in the local development environment.

## Start the Dashboard

Open a separate terminal in the project root, activate the virtual environment, and run:

```bash
python -m streamlit run app/dashboard.py
```

The dashboard provides a visual overview of pipeline runs and allows users to inspect individual run details.

## Configuration

Use `.env.example` as a reference for environment configuration. Create a local `.env` file if required by the application's settings.

Do not commit secrets or credentials.

## Current Scope and Limitations

This project currently uses a sample sales CSV and SQLite for local development. Production deployment, broader dataset testing, and additional operational features should be verified separately before being described as production-ready.

## License

No license has been specified yet.
