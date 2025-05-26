import pandas as pd
import plotly.express as px


def plot_rrg(df: pd.DataFrame):
    """
    Plot a Relative Rotation Graph (RRG) using Plotly.
    Args:
        df (pd.DataFrame): DataFrame with columns ['RS_Ratio', 'RS_Momentum', 'Symbol', ...]
    Returns:
        fig: Plotly Figure
    """
    # Stub: Replace with actual logic
    fig = px.scatter(
        df,
        x="RS_Ratio",
        y="RS_Momentum",
        color="Symbol",
        title="Relative Rotation Graph (RRG)",
    )
    return fig
