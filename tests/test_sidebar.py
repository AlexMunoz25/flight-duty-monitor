from dash import html

from sidebar.components import roster_items, sidebar_toggle
from stores import STORES


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk(child)
    elif children is not None:
        yield from _walk(children)


def test_sidebar_toggle_is_a_hamburger_button():
    button = sidebar_toggle()
    assert button.id == "sidebar-toggle"
    assert button.className == "fdm-hamburger"


def test_root_layout_wires_collapsible_shell():
    from layout import root_layout

    nodes = list(_walk(root_layout()))
    root = nodes[0]
    toggles = [n for n in nodes if isinstance(n, html.Button) and getattr(n, "id", None) == "sidebar-toggle"]

    assert root.id == "fdm-app"
    assert len(toggles) == 1
    assert "sidebar-collapsed-store" in {store.id for store in STORES.values()}


def test_roster_items_highlight_only_the_active_file():
    rosters = [
        {"token": "aaa", "filename": "01.- January.csv"},
        {"token": "bbb", "filename": "02.- February.csv"},
    ]

    items = roster_items(rosters, "bbb")

    assert [item.id["index"] for item in items] == ["aaa", "bbb"]
    assert [item.children[1].children for item in items] == ["01.- January.csv", "02.- February.csv"]
    assert ["active" in item.className for item in items] == [False, True]


def test_roster_items_empty_when_no_files():
    assert roster_items([], None) == []
