from dash import dcc

ROSTER_STORES = {
    "rosters_store": dcc.Store(id="rosters-store", storage_type="memory", data=[]),
    "active_roster_store": dcc.Store(id="active-roster-store", storage_type="memory"),
}

FILTER_STORES = {
    "filters_store": dcc.Store(id="filters-store", storage_type="memory", data={}),
}

UI_STORES = {
    "sidebar_collapsed_store": dcc.Store(id="sidebar-collapsed-store", storage_type="local", data=False),
}

STORES = {**ROSTER_STORES, **FILTER_STORES, **UI_STORES}
