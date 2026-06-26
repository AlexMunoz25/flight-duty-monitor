from dash import html

from fdm.dashboard.filters.layout import filters_layout
from fdm.dashboard.guide import guide_panel
from fdm.dashboard.stores import STORES
from fdm.dashboard.warnings.layout import warnings_layout


def header():
    return html.Div(
        [
            html.Div("Flight Duty Monitor", className="fdm-title"),
            html.Div(
                "Crew fatigue warnings — low alertness on flight legs and accumulated 7-day block hours",
                className="fdm-subtitle",
            ),
        ],
        className="fdm-header",
    )


def root_layout():
    return html.Div(
        [*STORES.values(), header(), guide_panel(), filters_layout(), warnings_layout()],
        className="fdm-page",
    )
