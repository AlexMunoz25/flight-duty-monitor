from pathlib import Path

import polars as pl

ROSTER_SHEET_ID = 1


def excel_time_to_hours(column):
    clock = pl.col(column)
    return clock.dt.hour() + clock.dt.minute() / 60 + clock.dt.second() / 3600


def csv_block_time(column):
    text = (
        pl.col(column)
        .str.replace_all(r"(?i)a\.?\s*m\.?\s*$", "AM")
        .str.replace_all(r"(?i)p\.?\s*m\.?\s*$", "PM")
        .str.strip_chars()
    )
    return pl.coalesce(
        text.str.to_time("%I:%M:%S %p", strict=False),
        text.str.to_time("%H:%M:%S", strict=False),
        text.str.to_time("%H:%M", strict=False),
    )


def read_roster_csv(path):
    roster = pl.read_csv(path).with_columns(
        pl.col("ldep_timeHB").str.to_datetime("%d/%m/%y %H:%M"),
        csv_block_time("lblock").alias("lblock_time"),
    )
    unparsed = roster.filter(pl.col("lblock").is_not_null() & pl.col("lblock_time").is_null())
    if not unparsed.is_empty():
        raise ValueError(f"Unrecognized lblock time format: {unparsed['lblock'][0]!r}")
    return roster.drop("lblock").rename({"lblock_time": "lblock"})


def read_roster(path, sheet_id):
    if Path(path).suffix == ".csv":
        return read_roster_csv(path)
    return pl.read_excel(path, sheet_id=sheet_id, engine="calamine")


def load_roster(path, sheet_id=ROSTER_SHEET_ID):
    roster = read_roster(path, sheet_id)
    return roster.with_columns(excel_time_to_hours("lblock").alias("lblock_hours"))
