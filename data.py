import os
from functools import lru_cache
from pathlib import Path

import polars as pl

from alerts.fatigue import fatigue_warnings
from ingestion.roster import load_roster

REPO_ROOT = Path(__file__).resolve().parent
ROSTER_PATH = Path(os.environ.get("FDM_ROSTER_PATH", REPO_ROOT / "template.xlsx"))

WARNING_TYPE_LABELS = {
    "low_alertness": "Low alertness",
    "block_hours_7d": "Block hours (7-day)",
}


@lru_cache(maxsize=1)
def warnings_frame():
    return fatigue_warnings(load_roster(ROSTER_PATH))


def distinct_values(column):
    return warnings_frame()[column].unique().drop_nulls().sort().to_list()


def apply_filters(warning_type=None, severity=None, ranks=None, homebases=None, crew_query=None):
    frame = warnings_frame()
    if warning_type:
        frame = frame.filter(pl.col("warning_type") == warning_type)
    if severity:
        frame = frame.filter(pl.col("severity") == severity)
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
