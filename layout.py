from dash import dcc, html

from fatigue_warnings.layout import warnings_layout
from filters.layout import filters_layout
from guide import guide_panel
from sidebar.components import empty_state
from sidebar.layout import sidebar_layout
from stores import STORES


def dashboard_view(token):
    return html.Div([guide_panel(), filters_layout(token), warnings_layout()])


def root_layout():
    return html.Div(
        [
            *STORES.values(),
            sidebar_layout(),
            html.Div(
                dcc.Loading(html.Div(empty_state(), id="dashboard-body"), type="default"),
                className="fdm-canvas",
            ),
        ],
        className="fdm-app",
    )
