from dash import dcc, html


def sidebar_toggle():
    return html.Button(
        "☰",
        id="sidebar-toggle",
        className="fdm-hamburger",
        title="Collapse or expand the sidebar",
        n_clicks=0,
    )


def upload_control():
    return dcc.Upload(
        id="roster-upload",
        accept=".xlsx,.csv",
        multiple=True,
        className="fdm-upload",
        children=html.Span("⬆  Upload rosters (.xlsx, .csv)"),
    )


def roster_item(token, filename, active):
    class_name = "fdm-roster-item active" if active else "fdm-roster-item"
    return html.Button(
        [
            html.Span("🗎", className="fdm-roster-icon"),
            html.Span(filename, className="fdm-roster-name"),
        ],
        id={"type": "roster-item", "index": token},
        className=class_name,
        n_clicks=0,
    )


def roster_items(rosters, active):
    return [roster_item(roster["token"], roster["filename"], roster["token"] == active) for roster in rosters]


def empty_state():
    return html.Div(
        [
            html.Div("No roster selected", className="fdm-empty-title"),
            html.Div(
                "Upload one or more .xlsx or .csv roster exports from the sidebar, then select a roster to see its "
                "fatigue warnings.",
                className="fdm-empty-hint",
            ),
        ],
        className="fdm-empty",
    )
