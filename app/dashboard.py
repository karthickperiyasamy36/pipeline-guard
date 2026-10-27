
import pandas as pd
import streamlit as st

from app.config import get_settings
from app.storage.database import create_database_engine, create_tables
from app.storage.repository import PipelineRunRepository


st.set_page_config(
    page_title="Pipeline Guard",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data(ttl=10)
def load_runs() -> list[dict]:
    """Load recent pipeline executions from the configured database."""
    settings = get_settings()
    engine = create_database_engine(settings.database_url)

    try:
        create_tables(engine)
        repository = PipelineRunRepository(engine)
        runs = repository.list_runs(limit=100)

        return [
            {
                "Run ID": run.id,
                "Status": run.status,
                "Input Rows": run.input_rows,
                "Accepted Rows": run.accepted_rows,
                "Quarantined Rows": run.quarantined_rows,
                "Output Rows": run.output_rows,
                "Processed File": run.processed_file,
                "Quarantine File": run.quarantine_file,
                "Error": run.error_message,
            }
            for run in runs
        ]
    finally:
        engine.dispose()


def display_file_path(file_path) -> str:
    """Display a placeholder when a file path is missing."""
    if pd.isna(file_path) or not str(file_path).strip():
        return "—"

    return str(file_path)


st.title("🛡️ Pipeline Guard")
st.caption(
    "Data ingestion, validation, quality monitoring, and execution history."
)

if st.button("Refresh data"):
    load_runs.clear()

try:
    runs = load_runs()
except Exception as exc:
    st.error(f"Could not load pipeline history: {exc}")
    st.stop()

if not runs:
    st.info(
        "No pipeline runs found. Execute the pipeline first, "
        "then refresh this dashboard."
    )
    st.stop()


df = pd.DataFrame(runs)

# Convert missing file paths to None so the dashboard displays them cleanly.
for column in ["Processed File", "Quarantine File"]:
    df[column] = df[column].where(df[column].notna(), None)


# KPI metrics
total_runs = len(df)
successful_runs = int((df["Status"] == "success").sum())
failed_runs = int((df["Status"] == "failed").sum())

success_rate = (
    successful_runs / total_runs * 100
    if total_runs > 0
    else 0.0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Runs", total_runs)
col2.metric("Successful Runs", successful_runs)
col3.metric("Failed Runs", failed_runs)
col4.metric("Success Rate", f"{success_rate:.1f}%")


st.divider()


# Record processing summary
st.subheader("Record Processing Summary")

metric_columns = [
    "Input Rows",
    "Accepted Rows",
    "Quarantined Rows",
    "Output Rows",
]

totals = df[metric_columns].sum()

chart_data = pd.DataFrame(
    {
        "Record Type": metric_columns,
        "Total Records": totals.values,
    }
)

st.bar_chart(
    chart_data,
    x="Record Type",
    y="Total Records",
)


# Recent pipeline runs
st.subheader("Recent Pipeline Runs")

status_filter = st.selectbox(
    "Filter by status",
    ["All", "success", "failed"],
)

filtered_df = df.copy()

if status_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Status"] == status_filter
    ]

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True,
)


# Inspect an individual pipeline run
st.subheader("Inspect a Pipeline Run")

run_ids = df["Run ID"].tolist()

selected_run_id = st.selectbox(
    "Select run ID",
    run_ids,
)

selected_run = df[
    df["Run ID"] == selected_run_id
].iloc[0]

left, right = st.columns(2)

with left:
    st.write("**Status:**", selected_run["Status"])
    st.write("**Input rows:**", selected_run["Input Rows"])
    st.write("**Accepted rows:**", selected_run["Accepted Rows"])
    st.write("**Quarantined rows:**", selected_run["Quarantined Rows"])
    st.write("**Output rows:**", selected_run["Output Rows"])

with right:
    processed_file = display_file_path(
        selected_run["Processed File"]
    )
    quarantine_file = display_file_path(
        selected_run["Quarantine File"]
    )

    st.write("**Processed file:**", processed_file)
    st.write("**Quarantine file:**", quarantine_file)

    error_message = selected_run["Error"]

    if pd.notna(error_message) and str(error_message).strip():
        st.error(f"Pipeline error: {error_message}")
    else:
        st.success("No pipeline error recorded for this run.")
