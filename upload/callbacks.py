import base64

from dash import Input, Output, State
from dash.exceptions import PreventUpdate

from data import ingest_roster
from layout import dashboard_view


def upload_callbacks(app):
    @app.callback(
        Output("roster-store", "data"),
        Output("dashboard-body", "children"),
        Output("roster-filename", "children"),
        Input("roster-upload", "contents"),
        State("roster-upload", "filename"),
        prevent_initial_call=True,
    )
    def load_uploaded_roster(contents, filename):
        if not contents:
            raise PreventUpdate
        encoded = contents.split(",", 1)[1]
        token = ingest_roster(base64.b64decode(encoded))
        return {"token": token, "filename": filename}, dashboard_view(token), filename
