import plotly.graph_objects as go
import polars as pl

from theme import ACCENT, CHART_LAYOUT, SEVERITY_COLORS


def daily_low_alertness_chart(warnings):
    low_alertness = warnings.filter(pl.col("warning_type") == "low_alertness")
    return severity_day_chart(low_alertness, "Low-alertness events")


def daily_workload_chart(workload_events):
    return severity_day_chart(workload_events, "Crew over limit")


def severity_day_chart(frame, y_title):
    days = sorted(frame["window_end"].unique().drop_nulls().to_list())
    grouped = frame.group_by("window_end", "severity").len()
    figure = go.Figure()
    for severity in ("HIGH", "MEDIUM"):
        counts = {row["window_end"]: row["len"] for row in grouped.filter(pl.col("severity") == severity).to_dicts()}
        figure.add_bar(
            x=days,
            y=[counts.get(day, 0) for day in days],
            name=severity,
            marker_color=SEVERITY_COLORS[severity],
        )
    figure.update_layout(**CHART_LAYOUT, barmode="stack", xaxis_title=None, yaxis_title=y_title)
    return figure


def route_risk_frame(warnings):
    low_alertness = warnings.filter(pl.col("warning_type") == "low_alertness", pl.col("route").is_not_null())
    return (
        low_alertness.group_by("route")
        .agg(
            pl.len().alias("low_alertness_events"),
            pl.col("crew_id").n_unique().alias("crew_affected"),
            pl.col("alertness").mean().round(1).alias("avg_alertness"),
            pl.col("alertness").min().alias("min_alertness"),
            pl.col("block_hours").sum().round(1).alias("flagged_block_hours"),
            pl.col("window_end").min().alias("first_event"),
            pl.col("window_end").max().alias("last_event"),
        )
        .sort(["low_alertness_events", "min_alertness"], descending=[True, False])
    )


def route_risk_chart(route_risk):
    chart_frame = route_risk.head(12).sort("low_alertness_events")
    figure = go.Figure()
    figure.add_bar(
        x=chart_frame["low_alertness_events"].to_list(),
        y=chart_frame["route"].to_list(),
        orientation="h",
        marker_color=ACCENT,
        customdata=chart_frame.select("avg_alertness", "min_alertness", "crew_affected").to_numpy(),
        hovertemplate="Events: %{x}<br>Avg alertness: %{customdata[0]}<br>Min alertness: %{customdata[1]}<br>Crew: %{customdata[2]}<extra></extra>",
    )
    figure.update_layout(**CHART_LAYOUT, xaxis_title="Low-alertness events", yaxis_title=None)
    return figure


def route_rows(route_risk):
    display = route_risk.with_columns(
        pl.col("first_event").cast(pl.String),
        pl.col("last_event").cast(pl.String),
    )
    return display.to_dicts()


def low_alertness_rows(warnings):
    display = warnings.filter(pl.col("warning_type") == "low_alertness").with_columns(
        pl.col("window_end").cast(pl.String),
        pl.col("alertness").round(0),
        pl.col("block_hours").round(1),
    )
    return display.to_dicts()


def workload_rows(workload_events):
    display = workload_events.with_columns(
        pl.col("window_start").cast(pl.String),
        pl.col("window_end").cast(pl.String),
        pl.col("block_hours").round(1),
    )
    return display.to_dicts()
