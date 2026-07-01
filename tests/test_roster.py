from datetime import datetime

import polars as pl
import pytest

from roster import load_roster


def write_csv(tmp_path, lblock):
    csv_path = tmp_path / "roster.csv"
    csv_path.write_text(f"ldep_timeHB,lblock\n26/01/26 0:00,{lblock}\n")
    return csv_path


@pytest.mark.parametrize(
    "lblock,expected_hours",
    [
        ("3:39:00", 3.65),
        ("03:39:00", 3.65),
        ("3:39", 3.65),
        ("3:39:00 AM", 3.65),
        ("3:39:00 a. m.", 3.65),
        ("2:00:00 p. m.", 14.0),
        ("12:00:00 a. m.", 0.0),
    ],
)
def test_load_roster_parses_csv_block_time_renderings(tmp_path, lblock, expected_hours):
    roster = load_roster(write_csv(tmp_path, lblock))

    assert roster.schema["ldep_timeHB"] == pl.Datetime
    assert roster["ldep_timeHB"].to_list() == [datetime(2026, 1, 26)]
    assert round(roster["lblock_hours"].item(), 2) == expected_hours


def test_load_roster_raises_on_unrecognized_block_time(tmp_path):
    with pytest.raises(ValueError, match="Unrecognized lblock time format"):
        load_roster(write_csv(tmp_path, "3h39"))


def test_load_roster_reads_semicolon_delimited_csv(tmp_path):
    csv_path = tmp_path / "roster.csv"
    csv_path.write_text("ldep_timeHB;lblock;fullname\n26/01/26 0:00;3:39:00;PEREZ, JR\n")

    roster = load_roster(csv_path)

    assert round(roster["lblock_hours"].item(), 2) == 3.65
    assert roster["fullname"].item() == "PEREZ, JR"
