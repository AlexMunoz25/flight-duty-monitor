import polars as pl

from alerts.fatigue import LOW_ALERTNESS_THRESHOLD, WEEKLY_BLOCK_LIMIT_HOURS
from theme import SEVERITY_COLORS

COLUMN_DEFS = [
    {
        "headerName": "Type",
        "field": "type_label",
        "width": 150,
        "headerTooltip": "Warning category: 'Low alertness' (a fatigued flight leg) or "
        "'Block hours (7-day)' (rolling flight-time limit exceeded).",
    },
    {
        "headerName": "Crew ID",
        "field": "crew_id",
        "width": 100,
        "pinned": "left",
        "headerTooltip": "Crew member identifier. Each row is one warning for this crew member.",
    },
    {
        "headerName": "Name",
        "field": "fullname",
        "width": 230,
        "pinned": "left",
        "sort": "asc",
        "sortIndex": 0,
        "headerTooltip": "Crew member name. Rows are grouped by crew member by default; sort any column to reorder.",
    },
    {
        "headerName": "Severity",
        "field": "severity",
        "width": 120,
        "sort": "asc",
        "sortIndex": 1,
        "headerTooltip": "HIGH = the most extreme cases (deep alertness debt or well over the block-hour limit). "
        "MEDIUM = past the limit but less extreme.",
        "cellStyle": {
            "styleConditions": [
                {"condition": "params.value == 'HIGH'", "style": {"color": SEVERITY_COLORS["HIGH"], "fontWeight": "bold"}},
                {"condition": "params.value == 'MEDIUM'", "style": {"color": SEVERITY_COLORS["MEDIUM"]}},
            ]
        },
    },
    {"headerName": "Rank", "field": "rank", "width": 90, "headerTooltip": "Crew rank (CAP, OFI, EJE, SOB)."},
    {"headerName": "Base", "field": "homebase", "width": 80, "headerTooltip": "Crew member's home base."},
    {
        "headerName": "Window start",
        "field": "window_start",
        "width": 130,
        "headerTooltip": "Low alertness: the flight-leg date. Block hours: first day of the 7-day window.",
    },
    {
        "headerName": "Window end",
        "field": "window_end",
        "width": 130,
        "headerTooltip": "Low alertness: the flight-leg date. Block hours: last day of the 7-day window "
        "(the day the limit was exceeded).",
    },
    {"headerName": "Trip", "field": "trip", "width": 80, "headerTooltip": "Trip number of the flagged leg (low-alertness rows)."},
    {"headerName": "Duty", "field": "duty", "width": 80, "headerTooltip": "Duty sequence within the trip (low-alertness rows)."},
    {"headerName": "Route", "field": "route", "width": 110, "headerTooltip": "Departure–arrival of the flagged leg (low-alertness rows)."},
    {
        "headerName": "Alertness",
        "field": "alertness",
        "width": 110,
        "headerTooltip": f"Modelled alertness on the operated leg; higher = more rested. Flagged below "
        f"{LOW_ALERTNESS_THRESHOLD}; negative means severe alertness debt. Off-duty rows are excluded.",
    },
    {
        "headerName": "Block h",
        "field": "block_hours",
        "width": 100,
        "headerTooltip": f"Low alertness: the leg's block hours. Block hours: total operated block hours in the "
        f"7-day window (limit {WEEKLY_BLOCK_LIMIT_HOURS} h).",
    },
    {
        "headerName": "Message",
        "field": "message",
        "width": 340,
        "tooltipField": "message",
        "headerTooltip": "Plain-language summary of the warning.",
    },
]

DEFAULT_COL_DEF = {"sortable": True, "filter": True, "resizable": True}

KPI_DEFS = [
    (
        "Total warnings",
        lambda frame: frame.height,
        "Warnings in the current view (after filters). Each row is one warning for one crew member.",
    ),
    (
        "High severity",
        lambda frame: frame.filter(pl.col("severity") == "HIGH").height,
        "Warnings in the HIGH band — the most extreme alertness debt or block-hour overruns.",
    ),
    (
        "Crew affected",
        lambda frame: frame["crew_id"].n_unique(),
        "Distinct crew members with at least one warning in the current view.",
    ),
    (
        "Block hours (7d)",
        lambda frame: frame.filter(pl.col("warning_type") == "block_hours_7d").height,
        f"Crew members over the {WEEKLY_BLOCK_LIMIT_HOURS} h rolling 7-day limit (one per crew, their worst window).",
    ),
    (
        "Low alertness",
        lambda frame: frame.filter(pl.col("warning_type") == "low_alertness").height,
        f"Flight legs flagged for modelled alertness below {LOW_ALERTNESS_THRESHOLD}.",
    ),
]
