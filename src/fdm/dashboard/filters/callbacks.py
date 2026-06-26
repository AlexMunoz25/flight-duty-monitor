from dash import Input, Output

from fdm.dashboard.filters.components import ALL


def _clear(value):
    return None if value in (None, "", ALL) else value


def filters_callbacks(app):
    @app.callback(
        Output("filters-store", "data"),
        Input("filter-type", "value"),
        Input("filter-severity", "value"),
        Input("filter-rank", "value"),
        Input("filter-homebase", "value"),
        Input("filter-crew", "value"),
    )
    def collect_filters(warning_type, severity, ranks, homebases, crew):
        return {
            "warning_type": _clear(warning_type),
            "severity": _clear(severity),
            "ranks": ranks,
            "homebases": homebases,
            "crew": crew,
        }

    @app.callback(
        Output("filter-type", "value"),
        Output("filter-severity", "value"),
        Output("filter-rank", "value"),
        Output("filter-homebase", "value"),
        Output("filter-crew", "value"),
        Input("filter-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_clicks):
        return ALL, ALL, [], [], ""
