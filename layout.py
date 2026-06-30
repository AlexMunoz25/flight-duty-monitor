from dash import dcc, html

from fatigue_warnings.layout import warnings_layout
from filters.layout import filters_layout
from guide import guide_panel
from stores import STORES
from upload.layout import empty_state, upload_control


def header():
    titles = html.Div(
        [
            html.Div("Flight Duty Monitor", className="fdm-title"),
            html.Div(
                "Crew fatigue warnings — low alertness on flight legs and accumulated 7-day block hours",
                className="fdm-subtitle",
            ),
        ]
    )
    upload_bar = html.Div(
        [upload_control(), html.Span(id="roster-filename", className="fdm-filename")],
        className="fdm-upload-bar",
    )
    return html.Div([titles, upload_bar], className="fdm-header")


def dashboard_view(token):
    return html.Div([guide_panel(), filters_layout(token), warnings_layout()])


def root_layout():
    return html.Div(
        [
            *STORES.values(),
            header(),
            dcc.Loading(html.Div(empty_state(), id="dashboard-body"), type="default"),
        ],
        className="fdm-page",
    )
