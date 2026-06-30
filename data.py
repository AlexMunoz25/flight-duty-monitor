import tempfile
import uuid
from functools import lru_cache
from pathlib import Path

import polars as pl

from analytics import (
    LOW_ALERTNESS_THRESHOLD,
    ROLLING_WINDOW,
    WEEKLY_BLOCK_LIMIT_HOURS,
    crew_operating_summary,
    fatigue_warnings,
    rolling_block_hour_events,
)
from roster import load_roster

REPO_ROOT = Path(__file__).resolve().parent
ROSTER_CACHE = REPO_ROOT / "data" / "rosters"

WARNING_TYPE_LABELS = {
    "low_alertness": "Low alertness",
    "block_hours_7d": "Block hours (7-day)",
}


def artifact_path(token, name):
    return ROSTER_CACHE / f"{token}-{name}.parquet"


def ingest_roster(contents):
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as upload:
        upload.write(contents)
        upload.flush()
        roster = load_roster(upload.name)
        warnings = fatigue_warnings(roster)
        crew_summary = crew_operating_summary(roster)
        workload_events = rolling_block_hour_events(roster, WEEKLY_BLOCK_LIMIT_HOURS, ROLLING_WINDOW)
    token = uuid.uuid4().hex
    ROSTER_CACHE.mkdir(parents=True, exist_ok=True)
    warnings.write_parquet(ROSTER_CACHE / f"{token}.parquet")
    crew_summary.write_parquet(artifact_path(token, "crew-summary"))
    workload_events.write_parquet(artifact_path(token, "workload-events"))
    return token


@lru_cache(maxsize=8)
def warnings_frame(token):
    return pl.read_parquet(ROSTER_CACHE / f"{token}.parquet")


@lru_cache(maxsize=8)
def crew_summary_frame(token):
    return pl.read_parquet(artifact_path(token, "crew-summary"))


@lru_cache(maxsize=8)
def workload_events_frame(token):
    return pl.read_parquet(artifact_path(token, "workload-events"))


def distinct_values(token, column):
    return warnings_frame(token)[column].unique().drop_nulls().sort().to_list()


def apply_crew_filters(frame, ranks=None, homebases=None, crew_query=None):
    if ranks:
        frame = frame.filter(pl.col("rank").is_in(ranks))
    if homebases:
        frame = frame.filter(pl.col("homebase").is_in(homebases))
    if crew_query:
        needle = crew_query.strip().upper()
        name_match = pl.col("fullname").str.to_uppercase().str.contains(needle, literal=True)
        id_match = pl.col("crew_id").cast(pl.String).str.contains(needle, literal=True)
        frame = frame.filter(name_match | id_match)
    return frame


def apply_filters(token, warning_type=None, severity=None, ranks=None, homebases=None, crew_query=None):
    frame = warnings_frame(token)
    if warning_type:
        frame = frame.filter(pl.col("warning_type") == warning_type)
    if severity:
        frame = frame.filter(pl.col("severity") == severity)
    return apply_crew_filters(frame, ranks, homebases, crew_query)


def apply_workload_filters(token, warning_type=None, severity=None, ranks=None, homebases=None, crew_query=None):
    frame = workload_events_frame(token)
    if warning_type and warning_type != "block_hours_7d":
        frame = frame.filter(pl.lit(False))
    if severity:
        frame = frame.filter(pl.col("severity") == severity)
    return apply_crew_filters(frame, ranks, homebases, crew_query)


def operating_kpis(token, warnings, ranks=None, homebases=None, crew_query=None):
    crew_summary = apply_crew_filters(crew_summary_frame(token), ranks, homebases, crew_query)
    low_alertness = warnings.filter(pl.col("warning_type") == "low_alertness")
    block_warnings = warnings.filter(pl.col("warning_type") == "block_hours_7d")
    period_start = crew_summary["period_start"].min()
    period_end = crew_summary["period_end"].max()
    period = "No operated flights" if period_start is None else f"{period_start} to {period_end}"
    return [
        {
            "label": "Roster period",
            "value": period,
            "help": "Date range covered by operated flight legs in the current crew/base/rank view.",
        },
        {
            "label": "Flights operated",
            "value": int(crew_summary["flight_count"].sum() or 0),
            "help": "Operated flight legs in the current crew/base/rank view.",
        },
        {
            "label": "Block hours",
            "value": round(float(crew_summary["block_hours"].sum() or 0), 1),
            "help": "Total operated block hours in the current crew/base/rank view.",
        },
        {
            "label": "Low alertness",
            "value": low_alertness.height,
            "help": f"Operated legs below the configured alertness threshold of {LOW_ALERTNESS_THRESHOLD}.",
        },
        {
            "label": "7-day workload warnings",
            "value": block_warnings.height,
            "help": f"Crew members over the configured rolling {ROLLING_WINDOW} block-hour limit of {WEEKLY_BLOCK_LIMIT_HOURS} h.",
        },
        {
            "label": "Crew over workload limit",
            "value": block_warnings["crew_id"].n_unique(),
            "help": "Distinct crew members with a rolling workload warning in the current warning view.",
        },
    ]


def threshold_label():
    return (
        f"Active thresholds: low alertness below {LOW_ALERTNESS_THRESHOLD}; "
        f"rolling {ROLLING_WINDOW} block-hour warning above {WEEKLY_BLOCK_LIMIT_HOURS} h."
    )
