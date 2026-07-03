window.dash_clientside = Object.assign({}, window.dash_clientside, {
    sidebar: {
        toggle: function (nClicks, collapsed) {
            return !collapsed;
        },
        applyCollapsed: function (collapsed) {
            return collapsed ? "fdm-app collapsed" : "fdm-app";
        }
    }
});
