import tomllib
from dataclasses import dataclass
from pathlib import Path

import polars as pl

CONFIG_PATH = Path(__file__).with_name("fatigue.toml")


@dataclass(frozen=True)
class FatigueConfig:
    low_alertness_threshold: int
    weekly_block_limit_hours: int
    rolling_window: str
    daily_flight_limits: tuple[int, ...]
    daily_flight_limit_default: int


def load_fatigue_config(path=CONFIG_PATH):
    fatigue = tomllib.loads(path.read_text())["fatigue"]
    return FatigueConfig(
        low_alertness_threshold=fatigue["low_alertness_threshold"],
        weekly_block_limit_hours=fatigue["weekly_block_limit_hours"],
        rolling_window=fatigue["rolling_window"],
        daily_flight_limits=tuple(fatigue["daily_flight_limits"]),
        daily_flight_limit_default=fatigue["daily_flight_limit_default"],
    )


FATIGUE_CONFIG = load_fatigue_config()
LOW_ALERTNESS_THRESHOLD = FATIGUE_CONFIG.low_alertness_threshold
WEEKLY_BLOCK_LIMIT_HOURS = FATIGUE_CONFIG.weekly_block_limit_hours
ROLLING_WINDOW = FATIGUE_CONFIG.rolling_window
DAILY_FLIGHT_LIMITS = FATIGUE_CONFIG.daily_flight_limits
DAILY_FLIGHT_LIMIT_DEFAULT = FATIGUE_CONFIG.daily_flight_limit_default

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


def daily_flight_counts(roster):
    legs = operational_legs(roster).with_columns(pl.col("ldep_timeHB").dt.date().alias("day"))
    return (
        legs.group_by("crew_id", "fullname", "rank", "homebase", "day")
        .agg(
            pl.len().alias("flight_count"),
            pl.col("lblock_hours").sum().round(2).alias("block_hours"),
        )
        .sort(["day", "flight_count"], descending=[True, True])
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
