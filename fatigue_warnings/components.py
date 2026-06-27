import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html

from fatigue_warnings.models import COLUMN_DEFS, DEFAULT_COL_DEF, KPI_DEFS
from theme import GRID_THEME


def section_title(text, help_id, help_text):
    return html.Div(
        [
            html.Span(text, className="fdm-section-title"),
            html.Span("ⓘ", id=help_id, className="fdm-info"),
            dbc.Tooltip(help_text, target=help_id, placement="top"),
        ],
        className="fdm-section-header",
    )


def kpi_card(index, label, value, help_text):
    card_id = f"kpi-card-{index}"
    body = dbc.CardBody(
        [
            html.Div(f"{value:,}", className="fdm-kpi-value"),
            html.Div([label, html.Span("ⓘ", className="fdm-info")], className="fdm-kpi-label"),
        ]
    )
    return dbc.Col(
        [dbc.Card(body, className="fdm-kpi", id=card_id), dbc.Tooltip(help_text, target=card_id, placement="bottom")],
        width="auto",
    )


def kpi_cards(frame):
    return [kpi_card(index, label, value(frame), help_text) for index, (label, value, help_text) in enumerate(KPI_DEFS)]


def warnings_grid():
    return dag.AgGrid(
        id="warnings-grid",
        columnDefs=COLUMN_DEFS,
        defaultColDef=DEFAULT_COL_DEF,
        className=GRID_THEME,
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 25,
            "animateRows": False,
            "tooltipShowDelay": 300,
        },
        style={"height": "calc(100vh - 430px)", "minHeight": "320px"},
    )
