import base64

from dash import ALL, ClientsideFunction, Input, Output, State, ctx
from dash.exceptions import PreventUpdate

from data import ingest_roster
from layout import dashboard_view
from sidebar.components import roster_items


def _ingest_upload(content, filename):
    encoded = content.split(",", 1)[1]
    token = ingest_roster(base64.b64decode(encoded), filename)
    return {"token": token, "filename": filename}


def _ingest_uploads(contents, filenames):
    uploads = list(zip(contents, filenames))
    return [_ingest_upload(content, filename) for content, filename in uploads]


def sidebar_callbacks(app):
    @app.callback(
        Output("rosters-store", "data"),
        Output("active-roster-store", "data"),
        Output("dashboard-body", "children"),
        Input("roster-upload", "contents"),
        State("roster-upload", "filename"),
        State("rosters-store", "data"),
        prevent_initial_call=True,
    )
    def add_rosters(contents, filenames, rosters):
        if not contents:
            raise PreventUpdate
        new_rosters = _ingest_uploads(contents, filenames)
        active_token = new_rosters[-1]["token"]
        return (rosters or []) + new_rosters, active_token, dashboard_view(active_token)

    @app.callback(
        Output("active-roster-store", "data", allow_duplicate=True),
        Output("dashboard-body", "children", allow_duplicate=True),
        Input({"type": "roster-item", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def select_roster(clicks):
        if not any(clicks):
            raise PreventUpdate
        active_token = ctx.triggered_id["index"]
        return active_token, dashboard_view(active_token)

    @app.callback(
        Output("roster-list", "children"),
        Input("rosters-store", "data"),
        Input("active-roster-store", "data"),
    )
    def render_roster_list(rosters, active):
        return roster_items(rosters or [], active)

    app.clientside_callback(
        ClientsideFunction(namespace="sidebar", function_name="toggle"),
        Output("sidebar-collapsed-store", "data"),
        Input("sidebar-toggle", "n_clicks"),
        State("sidebar-collapsed-store", "data"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        ClientsideFunction(namespace="sidebar", function_name="applyCollapsed"),
        Output("fdm-app", "className"),
        Input("sidebar-collapsed-store", "data"),
    )
