import numpy as np
import pandas as pd

from .quadrant_colors import QUADRANT_COLORS


def assign_quadrant(rs_ratio, rs_momentum):
    if rs_ratio >= 100 and rs_momentum >= 100:
        return "Leading"
    elif rs_ratio < 100 and rs_momentum >= 100:
        return "Improving"
    elif rs_ratio >= 100 and rs_momentum < 100:
        return "Weakening"
    else:
        return "Lagging"


def build_rrg_table(category_dfs):
    """
    category_dfs: list of (df, category_name) tuples, where df has columns ['Symbol', 'Date', 'RS_Ratio', 'RS_Momentum']
    Returns: ranked DataFrame with columns: Symbol, Category, Quadrant, Prev_Quadrant, Distance
    """
    rows = []
    for df, category in category_dfs:
        if df is None or df.empty:
            continue
        for _, row in df.iterrows():
            # row is already the latest for this symbol
            rows.append(
                {
                    "Symbol": row["Symbol"],
                    "Quadrant": assign_quadrant(row["RS_Ratio"], row["RS_Momentum"]),
                    "Distance": round(
                        np.sqrt(
                            (row["RS_Ratio"] - 100) ** 2
                            + (row["RS_Momentum"] - 100) ** 2
                        ),
                        2,
                    ),
                    "MFC": row.get("Momentum_Flip_Count", None),
                }
            )
    table = pd.DataFrame(rows)
    if table.empty:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(
            columns=["Symbol", "Quadrant", "Distance", "MFC"]
        ), QUADRANT_COLORS
    # Rank by quadrant (Leading > Improving > Weakening > Lagging), then by distance (descending)
    quadrant_order = ["Leading", "Improving", "Weakening", "Lagging"]
    table["QuadrantRank"] = table["Quadrant"].apply(lambda q: quadrant_order.index(q))
    table = table.sort_values(["QuadrantRank", "Distance"], ascending=[True, False])
    table = table.drop(columns=["QuadrantRank"])
    table = style_quadrant_column(table, QUADRANT_COLORS)
    return table, QUADRANT_COLORS


def style_quadrant_column(table, quadrant_colors):
    """
    Returns a pandas Styler that colors the Quadrant column based on the quadrant_colors mapping.
    Usage:
        table, quadrant_colors = build_rrg_table(...)
        styled_table = style_quadrant_column(table, quadrant_colors)
        st.dataframe(styled_table)
    """

    def color_quadrant(val):
        color = quadrant_colors.get(val, "rgba(255,255,255,0.3)")
        return f"background-color: {color}; color: black;"

    # Use Styler.map for the 'Quadrant' column only
    return table.style.map(lambda v: color_quadrant(v), subset=["Quadrant"])
