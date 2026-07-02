from fatigue_warnings.components import detail_grid, export_button
from fatigue_warnings.models import ROUTE_RISK_COLUMN_DEFS
from theme import CHART_CONFIG


def test_chart_config_exposes_native_modebar():
    assert CHART_CONFIG["displayModeBar"] is True


def test_export_button_and_grid_share_match_index():
    grid = detail_grid("route-risk-grid", ROUTE_RISK_COLUMN_DEFS)
    button = export_button("route-risk-grid")

    assert grid.id == {"type": "warnings-grid", "index": "route-risk-grid"}
    assert button.id == {"type": "warnings-grid-export", "index": "route-risk-grid"}
    assert grid.csvExportParams == {"fileName": "route-risk-grid.csv"}
