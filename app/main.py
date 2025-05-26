import streamlit as st
from components.rrg_plot import plot_rrg
from components.rrg_table import build_rrg_table
from data.finance import get_rrg_data, interval_map, period_options, window_map

st.set_page_config(page_title="Relative Rotation Graph (RRG)", layout="wide")
st.title("RRG")

st.markdown("""
This app visualizes the JdK RS Ratio vs JdK RS Momentum for a set of tickers relative to a benchmark using [plotly](https://plotly.com/python/).
""")

# Sidebar controls
st.sidebar.header("Controls")

# Shared controls
custom_tickers = ["AIVL", "GRNY", "GUNR", "TRTY", "FTCE"]
sector_tickers = ["XLK", "XLE", "XLF", "XLU", "XLB", "XLI", "XLC", "XLY", "XLP"]
geography_tickers = ["EWG", "EWZ", "FXI", "EWS", "EWC"]
alt_tickers = ["GLD", "DBMF", "KMLM", "TFPN"]

def_benchmark = "SPY"
def_period = "1mo"
def_interval = "1d"
def_window = 20

# Sidebar inputs
benchmark_options = ["SPY", "QQQ", "Other (type below)"]
selected_benchmark_option = st.selectbox(
    "Benchmark",
    options=benchmark_options,
    index=benchmark_options.index(def_benchmark)
    if def_benchmark in benchmark_options
    else 0,
    help="Select the benchmark ticker or choose 'Other' to enter a custom one.",
)
if selected_benchmark_option == "Other (type below)":
    benchmark = (
        st.text_input(
            "Custom Benchmark",
            value=def_benchmark if def_benchmark not in benchmark_options else "",
            help="Enter the custom benchmark ticker.",
        )
        .strip()
        .upper()
    )
else:
    benchmark = selected_benchmark_option
period = st.sidebar.selectbox(
    "Period",
    options=period_options,
    index=period_options.index(def_period),
    help="Select the lookback period.",
)
interval = interval_map.get(period, def_interval)
window = window_map.get(period, def_window)
st.sidebar.write(f"**Interval b/w points:** {interval}")
st.sidebar.write(f"**Window for rolling RS:** {window}")

# Group options for dropdown
GROUPS = {
    "Sectors": sector_tickers,
    "Geographies": geography_tickers,
    "Alternatives": alt_tickers,
    "Custom": custom_tickers,
}

group_name = st.selectbox(
    "Select Ticker Group",
    options=list(GROUPS.keys()),
    index=0,
    help="Choose which group of tickers to display.",
)
selected_tickers = GROUPS[group_name]
# map through all groups and create set of tickers
all_tickers = set()
for group in GROUPS.values():
    all_tickers.update(group)
all_tickers = list(all_tickers)

# Only proceed if benchmark is not empty
if benchmark:
    # Fetch data for selected group
    selected_rrg_df = get_rrg_data(selected_tickers, benchmark, period)

    # Last updated for selected group
    if not selected_rrg_df.empty and "Date" in selected_rrg_df.columns:
        st.text(
            f"Last data point: {selected_rrg_df['Date'].max().strftime('%Y-%m-%d')}"
        )

    try:
        if not selected_rrg_df.empty and {"RS_Ratio", "RS_Momentum", "Symbol"}.issubset(
            selected_rrg_df.columns
        ):
            fig = plot_rrg(
                selected_rrg_df.dropna(subset=["RS_Ratio", "RS_Momentum"]),
                max_points_per_ticker=4,
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching RRG data for {group_name}: {e}")

    # Table always shows all tickers
    all_rrg_df = get_rrg_data(all_tickers, benchmark, period)
    # Build a mapping from symbol to group
    symbol_to_group = {}
    for group, tickers in GROUPS.items():
        for ticker in tickers:
            symbol_to_group[ticker] = group
    # Table always shows all tickers, grouped by their category
    grouped_tables = []
    for group, tickers in GROUPS.items():
        group_df = all_rrg_df[all_rrg_df["Symbol"].isin(tickers)]
        grouped_tables.append((group_df, group))
    all_table, all_quadrant_colors = build_rrg_table(grouped_tables)
    st.write("## Full RRG Ranking")
    st.dataframe(all_table)
    st.write("MFC: Momentum Flip Count")
else:
    st.warning("Please enter a benchmark ticker to view the chart and table.")
