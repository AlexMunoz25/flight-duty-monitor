import dash_bootstrap_components as dbc
from dash import dcc, html

from filters.utils import ALL


def _field(field_id, label, control, help_text):
    help_id = f"{field_id}-help"
    label_row = html.Label(
        [label, html.Span("ⓘ", id=help_id, className="fdm-info")],
        className="fdm-filter-label",
    )
    return html.Div(
        [label_row, control, dbc.Tooltip(help_text, target=help_id, placement="top")],
        className="fdm-filter",
    )


def select_field(control_id, label, values, help_text, labels=None):
    options = [{"label": "All", "value": ALL}]
    options += [{"label": (labels or {}).get(value, value), "value": value} for value in values]
    return _field(control_id, label, dbc.Select(id=control_id, options=options, value=ALL, size="sm"), help_text)


def choice_field(control_id, label, values, default, help_text):
    options = [{"label": str(value), "value": value} for value in values]
    return _field(control_id, label, dbc.Select(id=control_id, options=options, value=default, size="sm"), help_text)


def multi_field(control_id, label, values, help_text):
    options = [{"label": value, "value": value} for value in values]
    control = dcc.Dropdown(id=control_id, options=options, multi=True, placeholder="All", className="fdm-dropdown")
    return _field(control_id, label, control, help_text)


def search_field(control_id, label, help_text):
    control = dbc.Input(id=control_id, type="search", placeholder="Name or crew id", size="sm", value="")
    return _field(control_id, label, control, help_text)
