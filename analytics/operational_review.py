import polars as pl


def operational_legs(roster):
    return roster.filter(
        pl.col("onduty")
        & pl.col("flightduty")
        & pl.col("lnum").is_not_null()
        & pl.col("ldep_timeHB").is_not_null()
    )


def crew_operating_summary(roster):
    legs = operational_legs(roster).with_columns(pl.col("ldep_timeHB").dt.date().alias("day"))
    return (
        legs.group_by("crew_id", "fullname", "rank", "homebase")
        .agg(
            pl.len().alias("flight_count"),
            pl.col("lblock_hours").sum().round(2).alias("block_hours"),
            pl.col("day").min().alias("period_start"),
            pl.col("day").max().alias("period_end"),
        )
        .sort("block_hours", descending=True)
    )


def rolling_block_hour_events(roster, limit, window):
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
        .alias("block_hours")
    )
    severity = (
        pl.when(pl.col("block_hours") > limit * 1.2)
        .then(pl.lit("HIGH"))
        .otherwise(pl.lit("MEDIUM"))
    )
    message = pl.format(
        "{} block hours in 7 days ending {} (limit {})",
        pl.col("block_hours").round(1),
        pl.col("day"),
        pl.lit(limit),
    )
    return (
        rolling.filter(pl.col("block_hours") > limit)
        .select(
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
            pl.col("block_hours").round(2).alias("block_hours"),
            severity.alias("severity"),
            message.alias("message"),
        )
        .sort(["window_end", "block_hours"], descending=[True, True])
    )
