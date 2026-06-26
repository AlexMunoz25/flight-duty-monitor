from dash import Input, Output

from fdm.dashboard.data import apply_filters
from fdm.dashboard.warnings.components import grid_rows, kpi_cards, severity_chart


def warnings_callbacks(app):
    @app.callback(
        Output("kpi-row", "children"),
        Output("warnings-chart", "figure"),
        Output("warnings-grid", "rowData"),
        Input("filters-store", "data"),
    )
    def render_warnings(filters):
        filters = filters or {}
        frame = apply_filters(
            warning_type=filters.get("warning_type"),
            severity=filters.get("severity"),
            ranks=filters.get("ranks"),
            homebases=filters.get("homebases"),
            crew_query=filters.get("crew"),
        )
        return kpi_cards(frame), severity_chart(frame), grid_rows(frame)
