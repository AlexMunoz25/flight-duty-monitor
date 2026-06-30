from dash import dcc

ROSTER_STORES = {
    "roster_store": dcc.Store(id="roster-store", storage_type="memory"),
}

FILTER_STORES = {
    "filters_store": dcc.Store(id="filters-store", storage_type="memory", data={}),
}

STORES = {**ROSTER_STORES, **FILTER_STORES}
