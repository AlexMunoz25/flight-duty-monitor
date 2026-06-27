import plotly.graph_objects as go
import polars as pl

from data import WARNING_TYPE_LABELS
from theme import CHART_LAYOUT, SEVERITY_COLORS


def severity_chart(frame):
    bases = sorted(frame["homebase"].unique().drop_nulls().to_list())
    grouped = frame.group_by("homebase", "severity").len()
    figure = go.Figure()
    for severity in ("HIGH", "MEDIUM"):
        counts = {row["homebase"]: row["len"] for row in grouped.filter(pl.col("severity") == severity).to_dicts()}
        figure.add_bar(
            x=bases,
            y=[counts.get(base, 0) for base in bases],
            name=severity,
            marker_color=SEVERITY_COLORS[severity],
        )
    figure.update_layout(**CHART_LAYOUT, barmode="group", xaxis_title=None, yaxis_title="Warnings")
    return figure


def grid_rows(frame):
    display = frame.with_columns(
        pl.col("window_start").cast(pl.String),
        pl.col("window_end").cast(pl.String),
        pl.col("block_hours").round(1),
        pl.col("warning_type").replace_strict(WARNING_TYPE_LABELS, default=pl.col("warning_type")).alias("type_label"),
    )
    return display.to_dicts()
