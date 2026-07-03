from dash import dcc, html

from fatigue_warnings.layout import warnings_layout
from filters.layout import filters_layout
from guide import guide_panel
from sidebar.components import empty_state, sidebar_toggle
from sidebar.layout import sidebar_layout
from stores import STORES


def dashboard_view(token):
    return html.Div([guide_panel(), filters_layout(token), warnings_layout()])


def topbar():
    return html.Div(
        [sidebar_toggle(), html.Span("Flight Duty Monitor", className="fdm-topbar-title")],
        className="fdm-topbar",
    )


def root_layout():
    return html.Div(
        [
            *STORES.values(),
            topbar(),
            html.Div(
                [
                    sidebar_layout(),
                    html.Div(
                        dcc.Loading(html.Div(empty_state(), id="dashboard-body"), type="default"),
                        className="fdm-canvas",
                    ),
                ],
                className="fdm-body",
            ),
        ],
        id="fdm-app",
        className="fdm-app",
    )
