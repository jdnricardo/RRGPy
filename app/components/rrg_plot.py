import pandas as pd
import plotly.graph_objects as go

from .quadrant_colors import (
    QUADRANT_COLORS,
    QUADRANT_COLORS_SOLID,
    QUADRANT_COLORS_SOLID_TEXT,
)


def assign_quadrant(rs_ratio, rs_momentum):
    if rs_ratio >= 100 and rs_momentum >= 100:
        return "Leading"
    elif rs_ratio < 100 and rs_momentum >= 100:
        return "Improving"
    elif rs_ratio >= 100 and rs_momentum < 100:
        return "Weakening"
    else:
        return "Lagging"


def plot_rrg(df: pd.DataFrame, max_points_per_ticker: int = None):
    """
    Plot a Relative Rotation Graph (RRG) using Plotly.
    Args:
        df (pd.DataFrame): DataFrame with columns ['RS_Ratio', 'RS_Momentum', 'Symbol', ...]
        max_points_per_ticker (int, optional): If set, only plot the last N points for each ticker.
    Returns:
        fig: Plotly Figure
    """
    fig = go.Figure()
    symbols = df["Symbol"].unique()

    # Calculate axis ranges with 12.18% buffer
    x_min, x_max = df["RS_Ratio"].min(), df["RS_Ratio"].max()
    y_min, y_max = df["RS_Momentum"].min(), df["RS_Momentum"].max()
    x_buffer = 0.1218 * (x_max - x_min) if x_max > x_min else 1
    y_buffer = 0.1218 * (y_max - y_min) if y_max > y_min else 1
    x_range = [x_min - x_buffer, x_max + x_buffer]
    y_range = [y_min - y_buffer, y_max + y_buffer]

    for symbol in symbols:
        sub = df[df["Symbol"] == symbol].sort_values("Date")
        if max_points_per_ticker is not None:
            sub = sub.tail(max_points_per_ticker)
        n = len(sub)
        # Determine quadrant and color for the latest point
        latest_row = sub.iloc[-1]
        quadrant = assign_quadrant(latest_row["RS_Ratio"], latest_row["RS_Momentum"])
        # color except for "weakening" which should use solid color
        color = (
            QUADRANT_COLORS.get(quadrant, "#888888")
            if quadrant != "Weakening"
            else QUADRANT_COLORS_SOLID.get(quadrant, "#000000")
        )
        solid_color = QUADRANT_COLORS_SOLID.get(quadrant, "#000000")
        text_color = QUADRANT_COLORS_SOLID_TEXT.get(quadrant, "#000000")
        # Spline line for the trail
        fig.add_trace(
            go.Scatter(
                x=sub["RS_Ratio"],
                y=sub["RS_Momentum"],
                mode="lines",
                line=dict(color=color, width=4, shape="spline"),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # Markers for all points, faded except the last two
        marker_opacities = [0.2] * (n - 2) + [0.6, 1.0] if n >= 2 else [1.0]
        fig.add_trace(
            go.Scatter(
                x=sub["RS_Ratio"],
                y=sub["RS_Momentum"],
                mode="markers",
                marker=dict(size=6, color="#000000", opacity=marker_opacities),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # Label the latest point with the ticker symbol, offset and colored
        fig.add_trace(
            go.Scatter(
                x=[latest_row["RS_Ratio"]],
                y=[latest_row["RS_Momentum"]],
                mode="text",
                text=[symbol],
                textposition="top right",
                textfont=dict(size=14, color=text_color, weight="bold"),
                showlegend=False,
                hoverinfo="skip",
            )
        )
    # Add quadrant coloring using shapes
    fig.update_layout(
        height=600,
        shapes=[
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                x1=100,
                y0=y_range[0],
                y1=100,
                fillcolor="red",
                opacity=0.2,
                line_width=0,
            ),
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=100,
                x1=x_range[1],
                y0=y_range[0],
                y1=100,
                fillcolor="yellow",
                opacity=0.2,
                line_width=0,
            ),
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=100,
                x1=x_range[1],
                y0=100,
                y1=y_range[1],
                fillcolor="green",
                opacity=0.2,
                line_width=0,
            ),
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=x_range[0],
                x1=100,
                y0=100,
                y1=y_range[1],
                fillcolor="blue",
                opacity=0.2,
                line_width=0,
            ),
        ],
        annotations=[
            dict(
                x=x_range[0] + 0.075 * (x_range[1] - x_range[0]),
                y=y_range[1] - 0.075 * (y_range[1] - y_range[0]),
                text="Improving",
                showarrow=False,
                font=dict(size=14),
            ),
            dict(
                x=x_range[1] - 0.075 * (x_range[1] - x_range[0]),
                y=y_range[1] - 0.075 * (y_range[1] - y_range[0]),
                text="Leading",
                showarrow=False,
                font=dict(size=14),
            ),
            dict(
                x=x_range[1] - 0.075 * (x_range[1] - x_range[0]),
                y=y_range[0] + 0.075 * (y_range[1] - y_range[0]),
                text="Weakening",
                showarrow=False,
                font=dict(size=14),
            ),
            dict(
                x=x_range[0] + 0.075 * (x_range[1] - x_range[0]),
                y=y_range[0] + 0.075 * (y_range[1] - y_range[0]),
                text="Lagging",
                showarrow=False,
                font=dict(size=14),
            ),
        ],
        title="Relative Rotation Graph (RRG)",
        xaxis_title="RS-Ratio",
        yaxis_title="RS-Momentum",
        template="plotly_white",
        hovermode="closest",
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
    )
    return fig
