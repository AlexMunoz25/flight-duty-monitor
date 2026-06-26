import polars as pl

ROSTER_SHEET_ID = 1


def excel_time_to_hours(column):
    clock = pl.col(column)
    return clock.dt.hour() + clock.dt.minute() / 60 + clock.dt.second() / 3600


def load_roster(path, sheet_id=ROSTER_SHEET_ID):
    roster = pl.read_excel(path, sheet_id=sheet_id, engine="calamine")
    return roster.with_columns(excel_time_to_hours("lblock").alias("lblock_hours"))
