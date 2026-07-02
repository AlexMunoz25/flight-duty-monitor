import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html

from fatigue_warnings.models import DEFAULT_COL_DEF
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


def export_button(grid_id):
    return html.Button(
        "⬇ CSV",
        id={"type": "warnings-grid-export", "index": grid_id},
        className="fdm-export-btn",
        title="Export table as CSV",
        n_clicks=0,
    )


def kpi_card(index, label, value, help_text):
    card_id = f"kpi-card-{index}"
    body = dbc.CardBody(
        [
            html.Div(f"{value:,}" if isinstance(value, int | float) else value, className="fdm-kpi-value"),
            html.Div([label, html.Span("ⓘ", className="fdm-info")], className="fdm-kpi-label"),
        ]
    )
    return dbc.Col(
        [dbc.Card(body, className="fdm-kpi", id=card_id), dbc.Tooltip(help_text, target=card_id, placement="bottom")],
        width="auto",
    )


def kpi_cards(cards):
    return [kpi_card(index, card["label"], card["value"], card["help"]) for index, card in enumerate(cards)]


def detail_grid(grid_id, column_defs, height="320px"):
    return dag.AgGrid(
        id={"type": "warnings-grid", "index": grid_id},
        columnDefs=column_defs,
        defaultColDef=DEFAULT_COL_DEF,
        className=GRID_THEME,
        csvExportParams={"fileName": f"{grid_id}.csv"},
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 25,
            "animateRows": False,
            "tooltipShowDelay": 300,
        },
        style={"height": height, "minHeight": "260px"},
    )
