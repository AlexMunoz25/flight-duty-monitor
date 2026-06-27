from dash import dcc

FILTER_STORES = {
    "filters_store": dcc.Store(id="filters-store", storage_type="memory", data={}),
}

STORES = {**FILTER_STORES}
