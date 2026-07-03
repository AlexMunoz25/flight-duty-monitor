import datetime as dt

import polars as pl

from analytics import (
    WARNING_COLUMNS,
    block_hour_warnings,
    crew_operating_summary,
    daily_flight_counts,
    fatigue_warnings,
    low_alertness_warnings,
    rolling_block_hour_events,
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


def test_crew_operating_summary_counts_operated_legs_and_block_hours():
    summary = crew_operating_summary(_roster([_leg(1, 5, block=2.5), _leg(1, 6, block=3.0)]))
    assert summary["flight_count"][0] == 2
    assert summary["block_hours"][0] == 5.5
    assert summary["period_start"][0] == dt.date(2026, 1, 5)
    assert summary["period_end"][0] == dt.date(2026, 1, 6)


def test_daily_flight_counts_aggregate_operated_legs_per_crew_day():
    rows = [
        _leg(1, 5, lnum=1, block=2.0),
        _leg(1, 5, lnum=2, block=1.5),
        _leg(1, 6, lnum=1, block=2.0),
        _leg(2, 5, onduty=False, flightduty=False, lnum=None, block=9.0),
    ]
    counts = daily_flight_counts(_roster(rows))
    day5 = counts.filter((pl.col("crew_id") == 1) & (pl.col("day") == dt.date(2026, 1, 5)))
    assert day5["flight_count"][0] == 2
    assert day5["block_hours"][0] == 3.5
    assert counts.filter(pl.col("crew_id") == 2).height == 0


def test_rolling_block_hour_events_keep_daily_exceedances():
    rows = [_leg(1, day, block=10.0, lnum=index) for index, day in enumerate((5, 6, 7, 8, 9), start=1)]
    events = rolling_block_hour_events(_roster(rows), limit=30, window="7d")
    assert events["window_end"].to_list() == [dt.date(2026, 1, 9), dt.date(2026, 1, 8)]
    assert events["block_hours"].to_list() == [50.0, 40.0]


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
