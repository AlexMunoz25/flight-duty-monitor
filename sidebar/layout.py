from dash import html

from sidebar.components import roster_items, upload_control


def sidebar_layout():
    header = html.Div(
        [
            html.Div("Flight Duty Monitor", className="fdm-title"),
            html.Div(
                "Crew fatigue warnings — low alertness on flight legs and accumulated 7-day block hours",
                className="fdm-subtitle",
            ),
        ],
        className="fdm-sidebar-header",
    )
    return html.Div(
        [
            header,
            upload_control(),
            html.Div("Rosters", className="fdm-sidebar-section"),
            html.Div(roster_items([], None), id="roster-list", className="fdm-roster-list"),
        ],
        className="fdm-sidebar",
    )
