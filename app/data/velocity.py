# this file will take a list of results from the get_rrg_data function and calculate velocity and volatility
# i.e. is the magnitude of the velocity beyond a certain level of noise in either direction?

from typing import List

import numpy as np
import pandas as pd
from components.quadrant_colors import (
    QUADRANT_COLORS,
)
from components.rrg_table import assign_quadrant
from palettable.colorbrewer.diverging import RdBu_11


# This function takes two RRG DataFrames (from get_rrg_data) and computes the difference for each symbol
# The DataFrames should have columns: ['Symbol', 'Date', 'Price', 'Benchmark', 'RS_Ratio', 'RS_Momentum', 'Momentum_Flip_Count']
def compare_rrg_timeframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    columns: List[str] = ["RS_Ratio", "RS_Momentum"],
) -> pd.DataFrame:
    """
    For each symbol, compute the difference in selected columns between df2 (later) and df1 (earlier).
    Returns a DataFrame with columns: Symbol, <col>_Diff for each selected column and their perpendicular components.
    """

    # Get latest valid point per symbol for each df
    def get_latest(df):
        valid = df.dropna(subset=["RS_Ratio", "RS_Momentum"])
        idx = valid.groupby("Symbol")["Date"].idxmax()
        return valid.loc[idx].set_index("Symbol")

    latest1 = get_latest(df1)
    latest2 = get_latest(df2)

    # Only compare symbols present in both
    common_symbols = latest1.index.intersection(latest2.index)
    latest1 = latest1.loc[common_symbols]
    latest2 = latest2.loc[common_symbols]

    # Compute differences for each symbol
    diff_data = []
    for symbol in common_symbols:
        row = {"Symbol": symbol}
        for col in columns:
            row[f"{col}_Diff"] = latest2.loc[symbol, col] - latest1.loc[symbol, col]
            row[f"{col}_HTF"] = latest2.loc[symbol, col]
            row[f"{col}_LTF"] = latest1.loc[symbol, col]

        # Calculate the perpendicular vector components
        rs_ratio_diff = row["RS_Ratio_Diff"]
        rs_momentum_diff = row["RS_Momentum_Diff"]

        # Calculate the magnitude of the velocity vector
        velocity_magnitude = np.sqrt(rs_ratio_diff**2 + rs_momentum_diff**2)

        # Calculate the perpendicular vector components
        row["Perp_RS_Ratio"] = -rs_momentum_diff / velocity_magnitude
        row["Perp_RS_Momentum"] = rs_ratio_diff / velocity_magnitude

        diff_data.append(row)

    return pd.DataFrame(diff_data)


def rrg_velocity_table(diff_df: pd.DataFrame):
    """
    Sorts and styles the velocity table.
    - Adds Distance_HTF and Distance_LTF columns (distance from (100, 100)).
    - Styles the distance columns based on their quadrant.
    - Styles RS_Ratio_Diff as green/red if sign flips.
    - Renders the two _Diff columns next to one another.
    """
    df = diff_df.copy()
    for col in [
        "RS_Ratio_Diff",
        "RS_Momentum_Diff",
        "RS_Ratio_HTF",
        "RS_Momentum_HTF",
        "RS_Ratio_LTF",
        "RS_Momentum_LTF",
    ]:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[col].fillna(0)
            df[col] = df[col].round(2)

    df = df.sort_values(
        by=["RS_Momentum_Diff", "RS_Ratio_HTF"], ascending=[True, False]
    ).reset_index(drop=True)

    # Assign quadrants for HTF and LTF
    df["Quadrant_HTF"] = df.apply(
        lambda row: assign_quadrant(row["RS_Ratio_HTF"], row["RS_Momentum_HTF"]), axis=1
    )
    df["Quadrant_LTF"] = df.apply(
        lambda row: assign_quadrant(row["RS_Ratio_LTF"], row["RS_Momentum_LTF"]), axis=1
    )

    # Calculate distances
    df["Distance_HTF"] = (
        (df["RS_Ratio_HTF"] - 100) ** 2 + (df["RS_Momentum_HTF"] - 100) ** 2
    ) ** 0.5
    df["Distance_LTF"] = (
        (df["RS_Ratio_LTF"] - 100) ** 2 + (df["RS_Momentum_LTF"] - 100) ** 2
    ) ** 0.5
    df["Distance_LogPct_Diff"] = np.log(df["Distance_HTF"] / df["Distance_LTF"])
    df["Distance_HTF"] = df["Distance_HTF"].round(2)
    df["Distance_LTF"] = df["Distance_LTF"].round(2)

    # Save the quadrant columns for styling, then drop them for display
    quadrant_htf = df["Quadrant_HTF"]
    quadrant_ltf = df["Quadrant_LTF"]

    # Reorder columns: Symbol, RS_Ratio_Diff, RS_Momentum_Diff, Distance_HTF, Distance_LTF, ...
    base_cols = [
        "Symbol",
        "Distance_HTF",
        "Distance_LTF",
        "Distance_LogPct_Diff",
    ]
    display_cols = [col for col in base_cols if col in df.columns]
    display_cols += [
        col
        for col in df.columns
        if col not in display_cols
        and col
        not in (
            "Quadrant_HTF",
            "Quadrant_LTF",
            "RS_Ratio_HTF",
            "RS_Momentum_HTF",
            "RS_Ratio_LTF",
            "RS_Momentum_LTF",
            "RS_Ratio_Diff",
            "RS_Momentum_Diff",
        )
    ]
    df_display = df[display_cols].copy()

    # Now, for styling, we need to know the quadrant for each row
    def style_func_htf(row):
        idx = row.name
        styles = []
        for col in df_display.columns:
            if col == "Distance_HTF":
                styles.append(color_quadrant(row[col], quadrant_htf.iloc[idx]))
            elif col == "Distance_LTF":
                styles.append(color_quadrant(row[col], quadrant_ltf.iloc[idx]))
            elif col == "Distance_LogPct_Diff":
                styles.append(color_log_diff(row[col]))
            elif col == "Perp_RS_Ratio":
                styles.append(color_log_diff(row[col]))
            elif col == "Perp_RS_Momentum":
                styles.append(color_log_diff(row[col]))
            else:
                styles.append("")
        return styles

    def color_log_diff(val):
        # Clamp val to [-1, 1]
        val = max(-1, min(1, val))
        # Normalize to [0, 1]
        norm_val = (val + 1) / 2
        # Get color from colormap
        idx = int(norm_val * (len(RdBu_11.mpl_colors) - 1))
        rgb = RdBu_11.mpl_colors[idx]
        # Convert to hex
        hex_color = "#%02x%02x%02x" % tuple(int(255 * c) for c in rgb)
        # Calculate brightness for contrast
        brightness = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        text_color = "black" if brightness > 0.6 else "white"
        return f"background-color: {hex_color}; color: {text_color};"

    def color_quadrant(val, quadrant):
        color = QUADRANT_COLORS.get(quadrant, "rgba(255,255,255,0.3)")
        return f"background-color: {color}; color: black;"

    styled = df_display.style.apply(style_func_htf, axis=1)
    styled = styled.format(
        {col: "{:.2f}" for col in df_display.select_dtypes(include="number").columns}
    )
    return styled
