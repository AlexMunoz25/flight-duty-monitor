from sidebar.components import roster_items


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
