import dash_bootstrap_components as dbc
from dash import html

from data import WARNING_TYPE_LABELS, distinct_values
from filters.components import multi_field, search_field, select_field


def filters_layout(token):
    controls = [
        select_field(
            "filter-type",
            "Warning type",
            distinct_values(token, "warning_type"),
            "Low alertness (a fatigued flight leg) or Block hours (7-day flight-time limit exceeded).",
            WARNING_TYPE_LABELS,
        ),
        select_field(
            "filter-severity",
            "Severity",
            ["HIGH", "MEDIUM"],
            "HIGH = the more extreme cases (deep alertness debt or well over the block-hour limit). MEDIUM = past the limit but less extreme.",
        ),
        multi_field("filter-rank", "Rank", distinct_values(token, "rank"), "Filter by crew rank (CAP, OFI, EJE, SOB)."),
        multi_field("filter-homebase", "Home base", distinct_values(token, "homebase"), "Filter by the crew member's home base."),
        search_field("filter-crew", "Crew", "Type a name or crew id to review every warning for one crew member."),
        html.Div(
            dbc.Button("Reset", id="filter-reset", color="secondary", outline=True, size="sm"),
            className="fdm-filter fdm-filter-reset",
        ),
    ]
    return html.Div(controls, className="fdm-filter-bar")
