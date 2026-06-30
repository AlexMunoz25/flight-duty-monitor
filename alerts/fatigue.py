import polars as pl

from analytics.operational_review import operational_legs, rolling_block_hour_events
from config.fatigue import FATIGUE_CONFIG

LOW_ALERTNESS_THRESHOLD = FATIGUE_CONFIG.low_alertness_threshold
WEEKLY_BLOCK_LIMIT_HOURS = FATIGUE_CONFIG.weekly_block_limit_hours
ROLLING_WINDOW = FATIGUE_CONFIG.rolling_window

WARNING_COLUMNS = [
    "warning_type",
    "crew_id",
    "fullname",
    "rank",
    "homebase",
    "window_start",
    "window_end",
    "trip",
    "duty",
    "route",
    "alertness",
    "block_hours",
    "severity",
    "message",
]


def low_alertness_warnings(roster, threshold=LOW_ALERTNESS_THRESHOLD):
    legs = operational_legs(roster).filter(pl.col("alertness") < threshold)
    leg_date = pl.col("ldep_timeHB").dt.date()
    route = pl.format("{}-{}", "ldeparture", "larrival")
    severity = (
        pl.when(pl.col("alertness") < threshold / 2)
        .then(pl.lit("HIGH"))
        .otherwise(pl.lit("MEDIUM"))
    )
    message = pl.format(
        "Alertness {} on operated leg {} (below {})",
        "alertness",
        route,
        pl.lit(threshold),
    )
    return legs.select(
        pl.lit("low_alertness").alias("warning_type"),
        "crew_id",
        "fullname",
        "rank",
        "homebase",
        leg_date.alias("window_start"),
        leg_date.alias("window_end"),
        pl.col("trip number").alias("trip"),
        "duty",
        route.alias("route"),
        "alertness",
        pl.col("lblock_hours").round(2).alias("block_hours"),
        severity.alias("severity"),
        message.alias("message"),
    )


def block_hour_warnings(roster, limit=WEEKLY_BLOCK_LIMIT_HOURS, window=ROLLING_WINDOW):
    rolling = rolling_block_hour_events(roster, limit, window)
    peak = (
        rolling.group_by("crew_id")
        .agg(pl.all().sort_by("block_hours", descending=True).first())
        .select(WARNING_COLUMNS)
    )
    return peak


def fatigue_warnings(
    roster,
    low_alertness_threshold=LOW_ALERTNESS_THRESHOLD,
    block_limit_hours=WEEKLY_BLOCK_LIMIT_HOURS,
):
    alertness = low_alertness_warnings(roster, low_alertness_threshold)
    block = block_hour_warnings(roster, block_limit_hours)
    warnings = pl.concat([alertness, block])
    high_first = pl.when(pl.col("severity") == "HIGH").then(0).otherwise(1)
    return warnings.sort([high_first, pl.col("window_end")], descending=[False, True])
