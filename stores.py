from dash import dcc

ROSTER_STORES = {
    "rosters_store": dcc.Store(id="rosters-store", storage_type="memory", data=[]),
    "active_roster_store": dcc.Store(id="active-roster-store", storage_type="memory"),
}

FILTER_STORES = {
    "filters_store": dcc.Store(id="filters-store", storage_type="memory", data={}),
}

STORES = {**ROSTER_STORES, **FILTER_STORES}
