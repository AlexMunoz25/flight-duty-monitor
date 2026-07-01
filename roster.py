import re
from pathlib import Path

import polars as pl

ROSTER_SHEET_ID = 1


def excel_time_to_hours(column):
    clock = pl.col(column)
    return clock.dt.hour() + clock.dt.minute() / 60 + clock.dt.second() / 3600


def csv_read_options(path):
    with open(path, "rb") as handle:
        first_line = handle.readline()
    directive = re.fullmatch(rb'"?sep=(.)"?\s*', first_line)
    if directive:
        return directive.group(1).decode(), 1
    counts = {separator: first_line.count(separator.encode()) for separator in (",", ";", "\t")}
    return max(counts, key=counts.get), 0


def csv_datetime(column):
    text = pl.col(column)
    return pl.coalesce(
        text.str.to_datetime("%d/%m/%y %H:%M", strict=False),
        text.str.to_datetime("%d/%m/%Y %H:%M", strict=False),
    )


def csv_block_time(column):
    text = (
        pl.col(column)
        .str.replace_all(r"(?i)a\.?\s*m\.?\s*$", "AM")
        .str.replace_all(r"(?i)p\.?\s*m\.?\s*$", "PM")
        .str.strip_chars()
        .str.strip_prefix("-")
    )
    return pl.coalesce(
        text.str.to_time("%I:%M:%S %p", strict=False),
        text.str.to_time("%H:%M:%S", strict=False),
        text.str.to_time("%H:%M", strict=False),
    )


def read_roster_csv(path):
    separator, skip_rows = csv_read_options(path)
    raw = pl.read_csv(path, separator=separator, skip_rows=skip_rows)
    roster = raw.with_columns(
        csv_datetime("ldep_timeHB").alias("ldep_timeHB"),
        csv_block_time("lblock").alias("lblock"),
    )
    for column in ("ldep_timeHB", "lblock"):
        unparsed = raw[column].is_not_null() & roster[column].is_null()
        if unparsed.any():
            sample = raw[column].filter(unparsed).first()
            raise ValueError(f"Unrecognized {column} format: {sample!r}")
    return roster


def read_roster(path, sheet_id):
    if Path(path).suffix == ".csv":
        return read_roster_csv(path)
    return pl.read_excel(path, sheet_id=sheet_id, engine="calamine")


def load_roster(path, sheet_id=ROSTER_SHEET_ID):
    roster = read_roster(path, sheet_id)
    return roster.with_columns(excel_time_to_hours("lblock").alias("lblock_hours"))
