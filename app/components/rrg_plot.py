import pandas as pd
import plotly.graph_objects as go

from .quadrant_colors import (
    QUADRANT_COLORS_MID,
    QUADRANT_COLORS_TEXT,
)
from .rrg_table import assign_quadrant


def plot_rrg(
    df: pd.DataFrame,
    latest_points: pd.DataFrame,
    max_points_per_ticker: int = None,
    period: str = "1y",
    fix_axes: bool = False,
):
    """
    Plot a Relative Rotation Graph (RRG) using Plotly.
    Args:
        df (pd.DataFrame): DataFrame with columns ['RS_Ratio', 'RS_Momentum', 'Symbol', ...]
        latest_points (pd.DataFrame): DataFrame with columns ['RS_Ratio', 'RS_Momentum', 'Symbol', ...]
        max_points_per_ticker (int, optional): If set, only plot the last N points for each ticker.
        period (str, optional): Not used here, for compatibility.
        fix_axes (bool, optional): If True, fix axes to [96, 104].
    Returns:
        fig: Plotly Figure
    """
    fig = go.Figure()
    symbols = df["Symbol"].unique()

    # Calculate axis ranges with 12.18% buffer, unless fix_axes is True
    if fix_axes:
        x_range = [95, 105]
        y_range = [95, 105]
    else:
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
        # Use latest_points for label/quadrant
        latest_row = latest_points[latest_points["Symbol"] == symbol].iloc[0]
        quadrant = assign_quadrant(latest_row["RS_Ratio"], latest_row["RS_Momentum"])
        color = QUADRANT_COLORS_MID.get(quadrant, "#888888")
        text_color = QUADRANT_COLORS_TEXT.get(quadrant, "#000000")
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
                marker=dict(size=6, color=color, opacity=marker_opacities),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # Latest point: filled marker with label
        fig.add_trace(
            go.Scatter(
                x=[latest_row["RS_Ratio"]],
                y=[latest_row["RS_Momentum"]],
                mode="markers+text",
                marker=dict(
                    size=14,
                    color=color,
                    symbol="circle",
                    line=dict(width=2, color=text_color),
                ),
                text=[symbol],
                textposition="top right",
                name=symbol,
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # Optionally, previous point: open marker (directionality)
        if n > 1:
            prev_row = sub.iloc[-2]
            fig.add_trace(
                go.Scatter(
                    x=[prev_row["RS_Ratio"]],
                    y=[prev_row["RS_Momentum"]],
                    mode="markers",
                    marker=dict(
                        size=12,
                        color=color,
                        symbol="circle-open",
                        line=dict(width=2, color=color),
                    ),
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
                fillcolor=QUADRANT_COLORS_MID["Lagging"],
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
                fillcolor=QUADRANT_COLORS_MID["Weakening"],
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
                fillcolor=QUADRANT_COLORS_MID["Leading"],
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
                fillcolor=QUADRANT_COLORS_MID["Improving"],
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
        title=f"Relative Rotation over the last {period}",
        xaxis_title="RS-Ratio",
        yaxis_title="RS-Momentum",
        template="plotly_white",
        hovermode="closest",
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    return fig


def plot_rrg_diff(
    diff_df,
    max_points_per_ticker=1,
    period="diff",
    fix_axes=True,
):
    """
    Plots a dumbbell (line+marker) for each symbol, connecting LTF to HTF in RRG space.
    Each endpoint is colored by its quadrant. Arrow and marker style indicate direction.
    """
    fig = go.Figure()
    x_range = [95, 105] if fix_axes else None
    y_range = [95, 105] if fix_axes else None

    for _, row in diff_df.iterrows():
        symbol = row["Symbol"]
        x0, y0 = row["RS_Ratio_LTF"], row["RS_Momentum_LTF"]
        x1, y1 = row["RS_Ratio_HTF"], row["RS_Momentum_HTF"]
        q0 = assign_quadrant(x0, y0)
        q1 = assign_quadrant(x1, y1)
        color0 = QUADRANT_COLORS_MID.get(q0, "#888888")
        color1 = QUADRANT_COLORS_MID.get(q1, "#888888")
        text_color = QUADRANT_COLORS_TEXT.get(q1, "#000000")

        # Line connecting LTF to HTF
        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color="#888", width=2, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # LTF marker (open circle)
        fig.add_trace(
            go.Scatter(
                x=[x0],
                y=[y0],
                mode="markers",
                marker=dict(
                    size=12,
                    color=color0,
                    symbol="circle-open",
                    line=dict(width=2, color=color0),
                ),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # HTF marker (filled circle, with label)
        fig.add_trace(
            go.Scatter(
                x=[x1],
                y=[y1],
                mode="markers+text",
                marker=dict(
                    size=14,
                    color=color1,
                    symbol="circle",
                    line=dict(width=2, color=text_color),
                ),
                text=[symbol],
                textposition="top right",
                name=symbol,
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Add quadrant coloring using shapes (optional, as in your RRG plot)
    if fix_axes:
        fig.update_layout(
            shapes=[
                dict(
                    type="rect",
                    xref="x",
                    yref="y",
                    x0=x_range[0],
                    x1=100,
                    y0=y_range[0],
                    y1=100,
                    fillcolor=QUADRANT_COLORS_MID["Lagging"],
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
                    fillcolor=QUADRANT_COLORS_MID["Weakening"],
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
                    fillcolor=QUADRANT_COLORS_MID["Leading"],
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
                    fillcolor=QUADRANT_COLORS_MID["Improving"],
                    opacity=0.2,
                    line_width=0,
                ),
            ]
        )
    fig.update_layout(
        title=f"RRG Dumbbell Plot: {period}",
        xaxis_title="RS-Ratio",
        yaxis_title="RS-Momentum",
        template="plotly_white",
        hovermode="closest",
        xaxis=dict(range=x_range),
        yaxis=dict(range=y_range),
        height=600,
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    )
    return fig
