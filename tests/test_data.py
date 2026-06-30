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
