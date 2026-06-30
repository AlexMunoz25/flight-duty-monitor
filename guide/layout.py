import dash_bootstrap_components as dbc
from dash import html

from alerts.fatigue import LOW_ALERTNESS_THRESHOLD, WEEKLY_BLOCK_LIMIT_HOURS

_ALERTNESS_HIGH = LOW_ALERTNESS_THRESHOLD // 2
_BLOCK_HIGH = round(WEEKLY_BLOCK_LIMIT_HOURS * 1.2)


def _category(color_class, title, lines):
    return dbc.Col(
        html.Div(
            [
                html.Div([html.Span(className=f"fdm-dot {color_class}"), html.Span(title, className="fdm-guide-title")]),
                html.Ul([html.Li(line) for line in lines], className="fdm-guide-list"),
            ],
            className="fdm-guide-category",
        ),
        md=6,
    )


def guide_panel():
    low_alertness = _category(
        "fdm-dot-high",
        "Low alertness",
        [
            "Raised when a crew member's modelled alertness on an operated flight leg (on duty and flying, not "
            "deadhead or off duty) drops below {threshold}.".format(threshold=LOW_ALERTNESS_THRESHOLD),
            "Higher alertness = more rested; negative values mean severe alertness debt. Off-duty rows (alertness 0) "
            "are never flagged.",
            "Window start/end show the leg date; Trip, Duty and Route identify the exact flight.",
            "Severity is HIGH below {high}, otherwise MEDIUM. A crew member can have many of these.".format(high=_ALERTNESS_HIGH),
        ],
    )
    block_hours = _category(
        "fdm-dot-medium",
        "Block hours (7-day)",
        [
            "Raised when operated block (flight) hours add up to more than {limit} h in any rolling 7-day "
            "window.".format(limit=WEEKLY_BLOCK_LIMIT_HOURS),
            "The workload warning count preserves the existing one-worst-window-per-crew logic; the drilldown lists every crew-day exceedance.",
            "Severity is HIGH above {high} h (more than 20% over the limit), otherwise MEDIUM.".format(high=_BLOCK_HIGH),
        ],
    )
    body = dbc.CardBody(
        [
            html.P(
                "The dashboard summarizes the uploaded roster period, then shows daily trends, route risk, and "
                "crew-level drilldowns. Use Crew search to review one crew member.",
                className="fdm-guide-intro",
            ),
            dbc.Row([low_alertness, block_hours], className="g-4"),
        ]
    )
    return dbc.Accordion(
        [dbc.AccordionItem(body, title="How to read these warnings", item_id="guide")],
        active_item="guide",
        flush=True,
        className="fdm-guide",
    )
