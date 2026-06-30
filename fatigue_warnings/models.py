from analytics import LOW_ALERTNESS_THRESHOLD, ROLLING_WINDOW, WEEKLY_BLOCK_LIMIT_HOURS
from theme import SEVERITY_COLORS

SEVERITY_STYLE = {
    "styleConditions": [
        {"condition": "params.value == 'HIGH'", "style": {"color": SEVERITY_COLORS["HIGH"], "fontWeight": "bold"}},
        {"condition": "params.value == 'MEDIUM'", "style": {"color": SEVERITY_COLORS["MEDIUM"]}},
    ]
}

DEFAULT_COL_DEF = {"sortable": True, "filter": True, "resizable": True}

LOW_ALERTNESS_COLUMN_DEFS = [
    {"headerName": "Crew ID", "field": "crew_id", "width": 100, "pinned": "left"},
    {"headerName": "Name", "field": "fullname", "width": 230, "pinned": "left", "sort": "asc"},
    {"headerName": "Severity", "field": "severity", "width": 120, "cellStyle": SEVERITY_STYLE},
    {"headerName": "Rank", "field": "rank", "width": 90},
    {"headerName": "Base", "field": "homebase", "width": 80},
    {"headerName": "Date", "field": "window_end", "width": 120},
    {"headerName": "Trip", "field": "trip", "width": 80},
    {"headerName": "Duty", "field": "duty", "width": 80},
    {"headerName": "Route", "field": "route", "width": 110},
    {
        "headerName": "Alertness",
        "field": "alertness",
        "width": 110,
        "headerTooltip": f"Configured low-alertness cutoff: {LOW_ALERTNESS_THRESHOLD}.",
    },
    {"headerName": "Block h", "field": "block_hours", "width": 100},
    {"headerName": "Message", "field": "message", "width": 340, "tooltipField": "message"},
]

WORKLOAD_COLUMN_DEFS = [
    {"headerName": "Crew ID", "field": "crew_id", "width": 100, "pinned": "left"},
    {"headerName": "Name", "field": "fullname", "width": 230, "pinned": "left", "sort": "asc"},
    {"headerName": "Severity", "field": "severity", "width": 120, "cellStyle": SEVERITY_STYLE},
    {"headerName": "Rank", "field": "rank", "width": 90},
    {"headerName": "Base", "field": "homebase", "width": 80},
    {"headerName": "Window start", "field": "window_start", "width": 130},
    {"headerName": "Window end", "field": "window_end", "width": 130},
    {
        "headerName": "Rolling block h",
        "field": "block_hours",
        "width": 145,
        "headerTooltip": f"Configured rolling {ROLLING_WINDOW} limit: {WEEKLY_BLOCK_LIMIT_HOURS} h.",
    },
    {"headerName": "Message", "field": "message", "width": 360, "tooltipField": "message"},
]

ROUTE_RISK_COLUMN_DEFS = [
    {"headerName": "Route", "field": "route", "width": 120, "pinned": "left", "sort": "asc"},
    {"headerName": "Low-alert events", "field": "low_alertness_events", "width": 150},
    {"headerName": "Crew affected", "field": "crew_affected", "width": 135},
    {"headerName": "Avg alertness", "field": "avg_alertness", "width": 135},
    {"headerName": "Min alertness", "field": "min_alertness", "width": 135},
    {"headerName": "Flagged block h", "field": "flagged_block_hours", "width": 145},
    {"headerName": "First event", "field": "first_event", "width": 125},
    {"headerName": "Last event", "field": "last_event", "width": 125},
]
