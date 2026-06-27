import dash_bootstrap_components as dbc
from dash import Dash

from data import warnings_frame
from fatigue_warnings.callbacks import warnings_callbacks
from filters.callbacks import filters_callbacks
from layout import root_layout

FEATURE_CALLBACKS = [filters_callbacks, warnings_callbacks]


def build_dashboard():
    warnings_frame()  # warm the cache at startup, never inside a callback
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="Flight Duty Monitor")
    app.layout = root_layout()
    for register_callbacks in FEATURE_CALLBACKS:
        register_callbacks(app)
    return app
