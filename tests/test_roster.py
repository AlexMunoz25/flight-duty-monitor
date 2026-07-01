from datetime import datetime

import polars as pl
import pytest

from roster import load_roster


def write_csv(tmp_path, body):
    csv_path = tmp_path / "roster.csv"
    csv_path.write_text(body)
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
        ("-0:22", 0.37),
    ],
)
def test_load_roster_parses_csv_block_time_renderings(tmp_path, lblock, expected_hours):
    roster = load_roster(write_csv(tmp_path, f"ldep_timeHB,lblock\n26/01/26 0:00,{lblock}\n"))

    assert roster.schema["ldep_timeHB"] == pl.Datetime
    assert roster["ldep_timeHB"].to_list() == [datetime(2026, 1, 26)]
    assert round(roster["lblock_hours"].item(), 2) == expected_hours


def test_load_roster_reads_excel_sep_directive_and_four_digit_year(tmp_path):
    body = '"sep=,"\nldep_timeHB,lblock\n31/01/2026 10:40,14:23\n'

    roster = load_roster(write_csv(tmp_path, body))

    assert roster["ldep_timeHB"].to_list() == [datetime(2026, 1, 31, 10, 40)]
    assert round(roster["lblock_hours"].item(), 2) == 14.38


def test_load_roster_reads_semicolon_delimited_csv(tmp_path):
    body = "ldep_timeHB;lblock;fullname\n26/01/26 0:00;3:39:00;PEREZ, JR\n"

    roster = load_roster(write_csv(tmp_path, body))

    assert round(roster["lblock_hours"].item(), 2) == 3.65
    assert roster["fullname"].item() == "PEREZ, JR"


def test_load_roster_raises_on_unrecognized_block_time(tmp_path):
    with pytest.raises(ValueError, match="Unrecognized lblock format"):
        load_roster(write_csv(tmp_path, "ldep_timeHB,lblock\n26/01/26 0:00,3h39\n"))
