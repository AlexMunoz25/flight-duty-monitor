from dash import dcc, html


def upload_control():
    return dcc.Upload(
        id="roster-upload",
        accept=".xlsx,.csv",
        multiple=False,
        className="fdm-upload",
        children=html.Span("⬆  Upload roster (.xlsx, .csv)"),
    )


def empty_state():
    return html.Div(
        [
            html.Div("No roster loaded", className="fdm-empty-title"),
            html.Div(
                "Use Upload roster (top right) to select an .xlsx or .csv roster export. "
                "Fatigue warnings appear here once it is read.",
                className="fdm-empty-hint",
            ),
        ],
        className="fdm-empty",
    )
