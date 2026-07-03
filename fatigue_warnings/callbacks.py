from dash import Input, MATCH, Output
from dash.exceptions import PreventUpdate

from analytics import DAILY_FLIGHT_LIMIT_DEFAULT
from data import apply_filters, apply_flight_count_filters, apply_workload_filters, operating_kpis
from fatigue_warnings.components import kpi_cards
from fatigue_warnings.utils import (
    daily_flight_count_chart,
    daily_low_alertness_chart,
    daily_workload_chart,
    flight_count_rows,
    low_alertness_rows,
    route_risk_chart,
    route_risk_frame,
    route_rows,
    workload_rows,
)


def warnings_callbacks(app):
    @app.callback(
        Output("kpi-row", "children"),
        Output("daily-low-alertness-chart", "figure"),
        Output("daily-workload-chart", "figure"),
        Output("route-risk-chart", "figure"),
        Output("daily-flight-count-chart", "figure"),
        Output({"type": "warnings-grid", "index": "low-alertness-grid"}, "rowData"),
        Output({"type": "warnings-grid", "index": "workload-grid"}, "rowData"),
        Output({"type": "warnings-grid", "index": "route-risk-grid"}, "rowData"),
        Output({"type": "warnings-grid", "index": "flight-count-grid"}, "rowData"),
        Input("filters-store", "data"),
        Input("active-roster-store", "data"),
    )
    def render_warnings(filters, token):
        if not token:
            raise PreventUpdate
        filters = filters or {}
        frame = apply_filters(
            token,
            warning_type=filters.get("warning_type"),
            severity=filters.get("severity"),
            ranks=filters.get("ranks"),
            homebases=filters.get("homebases"),
            crew_query=filters.get("crew"),
        )
        workload_events = apply_workload_filters(
            token,
            warning_type=filters.get("warning_type"),
            severity=filters.get("severity"),
            ranks=filters.get("ranks"),
            homebases=filters.get("homebases"),
            crew_query=filters.get("crew"),
        )
        flight_limit = filters.get("flight_limit") or DAILY_FLIGHT_LIMIT_DEFAULT
        flight_counts = apply_flight_count_filters(
            token,
            flight_limit,
            ranks=filters.get("ranks"),
            homebases=filters.get("homebases"),
            crew_query=filters.get("crew"),
        )
        route_risk = route_risk_frame(frame)
        return (
            kpi_cards(
                operating_kpis(
                    token,
                    frame,
                    ranks=filters.get("ranks"),
                    homebases=filters.get("homebases"),
                    crew_query=filters.get("crew"),
                )
            ),
            daily_low_alertness_chart(frame),
            daily_workload_chart(workload_events),
            route_risk_chart(route_risk),
            daily_flight_count_chart(flight_counts),
            low_alertness_rows(frame),
            workload_rows(workload_events),
            route_rows(route_risk),
            flight_count_rows(flight_counts),
        )

    @app.callback(
        Output({"type": "warnings-grid", "index": MATCH}, "exportDataAsCsv"),
        Input({"type": "warnings-grid-export", "index": MATCH}, "n_clicks"),
        prevent_initial_call=True,
    )
    def export_grid_csv(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return True
