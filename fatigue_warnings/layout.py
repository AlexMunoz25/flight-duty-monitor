import dash_bootstrap_components as dbc
from dash import dcc, html

from fatigue_warnings.components import section_title, warnings_grid


def warnings_layout():
    chart_card = dbc.Card(
        dbc.CardBody(
            [
                section_title(
                    "Warnings by home base",
                    "chart-help",
                    "Counts of the warnings in the current view, grouped by home base and split by severity. "
                    "Updates with the filters above.",
                ),
                dcc.Graph(id="warnings-chart", config={"displayModeBar": False}),
            ]
        ),
        className="fdm-chart-card",
    )
    grid_card = dbc.Card(
        dbc.CardBody(
            [
                section_title(
                    "Warning detail",
                    "grid-help",
                    "One row per warning. Crew ID and Name are pinned so each crew member stays visible while you "
                    "scroll. Hover a column header for what it means.",
                ),
                warnings_grid(),
            ]
        ),
        className="fdm-grid-card",
    )
    return html.Div(
        [dbc.Row(id="kpi-row", className="fdm-kpi-row g-3"), chart_card, grid_card],
        className="fdm-content",
    )
