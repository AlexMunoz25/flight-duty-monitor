import datetime as dt

import polars as pl

import data


def _warnings_frame():
    return pl.DataFrame(
        {
            "warning_type": ["low_alertness", "block_hours_7d"],
            "crew_id": [11, 22],
            "fullname": ["ALICE STONE", "BOB REYES"],
            "rank": ["CAP", "OFI"],
            "homebase": ["MEX", "GDL"],
            "severity": ["HIGH", "MEDIUM"],
        }
    )


def test_query_layer_reads_warnings_by_token(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "ROSTER_CACHE", tmp_path)
    token = "roster-token"
    _warnings_frame().write_parquet(tmp_path / f"{token}.parquet")
    data.warnings_frame.cache_clear()

    assert data.distinct_values(token, "rank") == ["CAP", "OFI"]
    assert data.apply_filters(token, severity="HIGH")["crew_id"].to_list() == [11]
    assert data.apply_filters(token, homebases=["GDL"])["crew_id"].to_list() == [22]
    assert data.apply_filters(token, crew_query="reyes")["crew_id"].to_list() == [22]


def _flight_counts_frame():
    return pl.DataFrame(
        {
            "crew_id": [11, 22, 33],
            "fullname": ["ALICE STONE", "BOB REYES", "CY DIAZ"],
            "rank": ["CAP", "OFI", "CAP"],
            "homebase": ["MEX", "GDL", "MEX"],
            "day": [dt.date(2026, 1, 5), dt.date(2026, 1, 5), dt.date(2026, 1, 6)],
            "flight_count": [6, 4, 5],
            "block_hours": [10.0, 8.0, 9.0],
        }
    )


def test_flight_count_filters_apply_limit_and_crew(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "ROSTER_CACHE", tmp_path)
    token = "roster-token"
    _flight_counts_frame().write_parquet(data.artifact_path(token, "flight-counts"))
    data.flight_counts_frame.cache_clear()

    assert data.apply_flight_count_filters(token, 4)["crew_id"].to_list() == [11, 33]
    assert data.apply_flight_count_filters(token, 5)["crew_id"].to_list() == [11]
    assert data.apply_flight_count_filters(token, 4, ranks=["OFI"]).height == 0
