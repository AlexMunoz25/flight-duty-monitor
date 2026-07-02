import dash_bootstrap_components as dbc
from dash import Dash

from fatigue_warnings.callbacks import warnings_callbacks
from filters.callbacks import filters_callbacks
from layout import root_layout
from sidebar.callbacks import sidebar_callbacks

FEATURE_CALLBACKS = [sidebar_callbacks, filters_callbacks, warnings_callbacks]


def build_dashboard():
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY],
        title="Flight Duty Monitor",
        suppress_callback_exceptions=True,
    )
    app.layout = root_layout()
    for register_callbacks in FEATURE_CALLBACKS:
        register_callbacks(app)
    return app


if __name__ == "__main__":
    build_dashboard().run(debug=False, host="127.0.0.1", port=8050)
