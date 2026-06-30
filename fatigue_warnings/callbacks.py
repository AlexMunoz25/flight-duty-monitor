from dash import Input, Output
from dash.exceptions import PreventUpdate

from data import apply_filters, apply_workload_filters, operating_kpis
from fatigue_warnings.components import kpi_cards
from fatigue_warnings.utils import (
    daily_low_alertness_chart,
    daily_workload_chart,
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
        Output("route-risk-grid", "rowData"),
        Output("low-alertness-grid", "rowData"),
        Output("workload-grid", "rowData"),
        Input("filters-store", "data"),
        Input("roster-store", "data"),
    )
    def render_warnings(filters, roster):
        token = (roster or {}).get("token")
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
            route_rows(route_risk),
            low_alertness_rows(frame),
            workload_rows(workload_events),
        )
