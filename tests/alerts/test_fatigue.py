import datetime as dt

import polars as pl

from alerts.fatigue import (
    WARNING_COLUMNS,
    block_hour_warnings,
    fatigue_warnings,
    low_alertness_warnings,
)


def _leg(crew_id, day, *, onduty=True, flightduty=True, lnum=1, alertness=6000,
         block=2.0, dep="MEX", arr="GDL", trip=1, duty=100):
    return {
        "crew_id": crew_id,
        "fullname": f"CREW {crew_id}",
        "rank": "CAP",
        "homebase": "MEX",
        "onduty": onduty,
        "flightduty": flightduty,
        "lnum": lnum,
        "ldep_timeHB": dt.datetime(2026, 1, day, 8, 0),
        "alertness": alertness,
        "ldeparture": dep,
        "larrival": arr,
        "trip number": trip,
        "duty": duty,
        "lblock_hours": block,
    }


def _roster(rows):
    return pl.DataFrame(rows, schema_overrides={"lnum": pl.Int64, "alertness": pl.Int64})


def test_offduty_zero_alertness_is_not_flagged():
    rows = [
        _leg(1, 5, onduty=False, flightduty=False, lnum=None, alertness=0),
        _leg(2, 5, alertness=1000),
    ]
    warnings = low_alertness_warnings(_roster(rows))
    assert warnings["crew_id"].to_list() == [2]
    assert warnings["severity"][0] == "HIGH"


def test_low_alertness_threshold_and_context():
    rows = [
        _leg(1, 5, alertness=2000, dep="MEX", arr="JFK"),
        _leg(2, 5, alertness=6000),
    ]
    warnings = low_alertness_warnings(_roster(rows))
    assert warnings["crew_id"].to_list() == [1]
    assert warnings["severity"][0] == "MEDIUM"
    assert warnings["route"][0] == "MEX-JFK"


def test_block_hours_use_leg_block_over_rolling_window():
    rows = [_leg(1, day, block=10.0, lnum=index) for index, day in enumerate((5, 6, 7, 8), start=1)]
    rows.append(_leg(2, 5, block=10.0))
    warnings = block_hour_warnings(_roster(rows))
    assert warnings["crew_id"].to_list() == [1]
    assert warnings["block_hours"][0] == 40.0
    assert warnings["severity"][0] == "HIGH"
    assert warnings["window_start"][0] == dt.date(2026, 1, 2)
    assert warnings["window_end"][0] == dt.date(2026, 1, 8)


def test_block_hours_ignore_non_operational_rows():
    rows = [
        _leg(3, 5, block=10.0),
        _leg(3, 6, onduty=False, flightduty=False, lnum=None, block=99.0),
    ]
    assert block_hour_warnings(_roster(rows)).height == 0


def test_fatigue_warnings_share_one_schema():
    rows = [_leg(1, day, block=10.0, lnum=index) for index, day in enumerate((5, 6, 7, 8), start=1)]
    rows.append(_leg(2, 5, alertness=1000))
    warnings = fatigue_warnings(_roster(rows))
    assert warnings.columns == WARNING_COLUMNS
    assert set(warnings["warning_type"].unique()) == {"block_hours_7d", "low_alertness"}
