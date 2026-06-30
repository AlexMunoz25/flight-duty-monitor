import datetime as dt

import polars as pl

from analytics.operational_review import crew_operating_summary, rolling_block_hour_events


def _leg(crew_id, day, *, block=2.0, lnum=1):
    return {
        "crew_id": crew_id,
        "fullname": f"CREW {crew_id}",
        "rank": "CAP",
        "homebase": "MEX",
        "onduty": True,
        "flightduty": True,
        "lnum": lnum,
        "ldep_timeHB": dt.datetime(2026, 1, day, 8, 0),
        "lblock_hours": block,
    }


def _roster(rows):
    return pl.DataFrame(rows, schema_overrides={"lnum": pl.Int64})


def test_crew_operating_summary_counts_operated_legs_and_block_hours():
    summary = crew_operating_summary(_roster([_leg(1, 5, block=2.5), _leg(1, 6, block=3.0)]))
    assert summary["flight_count"][0] == 2
    assert summary["block_hours"][0] == 5.5
    assert summary["period_start"][0] == dt.date(2026, 1, 5)
    assert summary["period_end"][0] == dt.date(2026, 1, 6)


def test_rolling_block_hour_events_keep_daily_exceedances():
    rows = [_leg(1, day, block=10.0, lnum=index) for index, day in enumerate((5, 6, 7, 8, 9), start=1)]
    events = rolling_block_hour_events(_roster(rows), limit=30, window="7d")
    assert events["window_end"].to_list() == [dt.date(2026, 1, 9), dt.date(2026, 1, 8)]
    assert events["block_hours"].to_list() == [50.0, 40.0]
