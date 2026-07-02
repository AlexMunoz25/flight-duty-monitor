import dash_bootstrap_components as dbc
from dash import dcc, html

from data import threshold_label
from fatigue_warnings.components import detail_grid, export_button, section_title
from fatigue_warnings.models import LOW_ALERTNESS_COLUMN_DEFS, ROUTE_RISK_COLUMN_DEFS, WORKLOAD_COLUMN_DEFS
from theme import CHART_CONFIG


def chart_card(title, help_id, help_text, graph_id):
    return dbc.Card(
        dbc.CardBody(
            [
                section_title(title, help_id, help_text),
                dcc.Graph(id=graph_id, config=CHART_CONFIG),
            ]
        ),
        className="fdm-chart-card",
    )


def grid_card(title, help_id, help_text, grid_id, column_defs, height="320px"):
    return dbc.Card(
        dbc.CardBody(
            [
                export_button(grid_id),
                section_title(title, help_id, help_text),
                detail_grid(grid_id, column_defs, height),
            ]
        ),
        className="fdm-grid-card",
    )


def warnings_layout():
    daily_low_alertness = chart_card(
        "Daily low-alertness events",
        "daily-alertness-help",
        "Operated flight legs below the configured low-alertness threshold, grouped by day and severity.",
        "daily-low-alertness-chart",
    )
    daily_workload = chart_card(
        "Daily rolling 7-day block-hour warnings",
        "daily-workload-help",
        "Crew-day rolling workload exceedances against the configured block-hour limit.",
        "daily-workload-chart",
    )
    route_risk = chart_card(
        "Route alertness risk",
        "route-risk-chart-help",
        "Routes with low-alertness events, sorted by event count and minimum alertness.",
        "route-risk-chart",
    )
    route_detail = grid_card(
        "Route risk detail",
        "route-risk-grid-help",
        "Route-level low-alertness counts, affected crew, alertness values, and flagged block hours.",
        "route-risk-grid",
        ROUTE_RISK_COLUMN_DEFS,
        "300px",
    )
    low_alertness_detail = grid_card(
        "Low-alertness event drilldown",
        "low-alertness-grid-help",
        "One row per operated leg below the configured alertness threshold.",
        "low-alertness-grid",
        LOW_ALERTNESS_COLUMN_DEFS,
        "360px",
    )
    workload_detail = grid_card(
        "Rolling 7-day workload drilldown",
        "workload-grid-help",
        "One row per crew-day where rolling block hours exceeded the configured workload threshold.",
        "workload-grid",
        WORKLOAD_COLUMN_DEFS,
        "360px",
    )
    return html.Div(
        [
            dbc.Row(id="kpi-row", className="fdm-kpi-row g-3"),
            html.Div(threshold_label(), className="fdm-threshold-label"),
            dbc.Row([dbc.Col(daily_low_alertness, lg=6), dbc.Col(daily_workload, lg=6)], className="g-3"),
            dbc.Row([dbc.Col(route_risk, lg=6), dbc.Col(route_detail, lg=6)], className="g-3"),
            low_alertness_detail,
            workload_detail,
        ],
        className="fdm-content",
    )
