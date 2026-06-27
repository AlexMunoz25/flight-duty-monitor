import polars as pl

LOW_ALERTNESS_THRESHOLD = 2500
WEEKLY_BLOCK_LIMIT_HOURS = 30
ROLLING_WINDOW = "7d"

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


def operational_legs(roster):
    return roster.filter(
        pl.col("onduty")
        & pl.col("flightduty")
        & pl.col("lnum").is_not_null()
        & pl.col("ldep_timeHB").is_not_null()
    )


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
    legs = operational_legs(roster)
    daily = (
        legs.with_columns(pl.col("ldep_timeHB").dt.date().alias("day"))
        .group_by("crew_id", "fullname", "rank", "homebase", "day")
        .agg(pl.col("lblock_hours").sum().alias("day_block"))
        .sort("crew_id", "day")
        .rechunk()
    )
    rolling = daily.with_columns(
        pl.col("day_block")
        .rolling_sum_by("day", window, closed="right")
        .over("crew_id")
        .alias("rolling_block")
    )
    peak = (
        rolling.filter(pl.col("rolling_block") > limit)
        .group_by("crew_id")
        .agg(pl.all().sort_by("rolling_block", descending=True).first())
    )
    severity = (
        pl.when(pl.col("rolling_block") > limit * 1.2)
        .then(pl.lit("HIGH"))
        .otherwise(pl.lit("MEDIUM"))
    )
    message = pl.format(
        "{} block hours in 7 days ending {} (limit {})",
        pl.col("rolling_block").round(1),
        pl.col("day"),
        pl.lit(limit),
    )
    return peak.select(
        pl.lit("block_hours_7d").alias("warning_type"),
        "crew_id",
        "fullname",
        "rank",
        "homebase",
        (pl.col("day") - pl.duration(days=6)).alias("window_start"),
        pl.col("day").alias("window_end"),
        pl.lit(None, dtype=pl.Int64).alias("trip"),
        pl.lit(None, dtype=pl.Int64).alias("duty"),
        pl.lit(None, dtype=pl.String).alias("route"),
        pl.lit(None, dtype=pl.Int64).alias("alertness"),
        pl.col("rolling_block").round(2).alias("block_hours"),
        severity.alias("severity"),
        message.alias("message"),
    )


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
