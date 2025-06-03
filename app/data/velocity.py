# this file will take a list of results from the get_rrg_data function and calculate velocity and volatility
# i.e. is the magnitude of the velocity beyond a certain level of noise in either direction?

from typing import List

import numpy as np
import pandas as pd
from components.quadrant_colors import (
    QUADRANT_COLORS,
)
from components.rrg_table import assign_quadrant


# This function takes two RRG DataFrames (from get_rrg_data) and computes the difference for each symbol
# The DataFrames should have columns: ['Symbol', 'Date', 'Price', 'Benchmark', 'RS_Ratio', 'RS_Momentum', 'Momentum_Flip_Count']
def compare_rrg_timeframes(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    columns: List[str] = ["RS_Ratio", "RS_Momentum"],
) -> pd.DataFrame:
    """
    For each symbol, compute the difference in selected columns between df2 (later) and df1 (earlier).
    Returns a DataFrame with columns: Symbol, <col>_Diff for each selected column.
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
        "Distance_Diff",
        "RS_Ratio_Diff",
        "RS_Momentum_Diff",
        "Distance_HTF",
        "Distance_LTF",
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
        )
    ]
    df_display = df[display_cols].copy()

    # Now, for styling, we need to know the quadrant for each row
    def style_func_htf(row):
        idx = row.name
        styles = []
        quadrant_changed = (
            str(quadrant_htf.iloc[idx]).strip() != str(quadrant_ltf.iloc[idx]).strip()
        )
        for col in df_display.columns:
            if col == "Distance_HTF" or col == "Distance_LTF":
                styles.append(color_htf(row[col], quadrant_htf.iloc[idx]))
            elif col == "RS_Momentum_Diff":
                # Style as green/red if sign flips
                ratio_sign = np.sign(row.get("RS_Ratio_Diff", 0))
                momentum_sign = np.sign(row.get("RS_Momentum_Diff", 0))
                # if ratio sign is positive, momentum is negative
                if ratio_sign > 0 and momentum_sign < 0:
                    base = f"background-color: {QUADRANT_COLORS['Weakening']};"
                # if ratio sign is negative, momentum is positive
                elif ratio_sign < 0 and momentum_sign > 0:
                    base = f"background-color: {QUADRANT_COLORS['Improving']};"
                # if ratio sign is negative, momentum is negative
                elif ratio_sign < 0 and momentum_sign < 0:
                    base = f"background-color: {QUADRANT_COLORS['Lagging']};"
                # if ratio sign is positive, momentum is positive
                elif ratio_sign > 0 and momentum_sign > 0:
                    base = f"background-color: {QUADRANT_COLORS['Leading']};"
                else:
                    base = ""
                # Highlight if quadrant changed
                if quadrant_changed:
                    base += " border: 2px solid orange; font-weight: bold;"
                styles.append(base)
            elif col == "RS_Momentum_Diff":
                # Highlight if quadrant changed
                if quadrant_changed:
                    styles.append("border: 2px solid orange; font-weight: bold;")
                else:
                    styles.append("")
            elif col == "Distance_LogPct_Diff":
                if np.abs(row[col]) > 0.618:
                    styles.append(f"background-color: {QUADRANT_COLORS['Improving']};")
                elif np.abs(row[col]) < 0.786:
                    styles.append(f"background-color: {QUADRANT_COLORS['Weakening']};")
                elif np.abs(row[col]) < 1.0:
                    styles.append(f"background-color: {QUADRANT_COLORS['Lagging']};")
                else:
                    styles.append("")
            else:
                styles.append("")
        return styles

    def color_htf(val, quadrant):
        color = QUADRANT_COLORS.get(quadrant, "rgba(255,255,255,0.3)")
        return f"background-color: {color}; color: black;"

    styled = df_display.style.apply(style_func_htf, axis=1)
    styled = styled.format(
        {col: "{:.2f}" for col in df_display.select_dtypes(include="number").columns}
    )
    return styled
