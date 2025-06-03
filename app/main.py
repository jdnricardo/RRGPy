import streamlit as st
from components.rrg_plot import plot_rrg, plot_rrg_diff
from data.finance import (
    get_latest_valid_points,
    get_rrg_data,
)
from data.velocity import compare_rrg_timeframes, rrg_velocity_table

st.set_page_config(page_title="Relative Rotation Graph (RRG)", layout="wide")
st.title("RRG")

st.markdown("""
This app visualizes the JdK RS Ratio vs JdK RS Momentum for a set of tickers relative to a benchmark using [plotly](https://plotly.com/python/).
""")

# Shared controls
priority_tickers = [
    "NVDA",
    "SGOL",
    "IONQ",
    "PM",
    "BJ",
    "COST",
    "MOS",
]
prod_staple_tickers = [
    "MOS",
    "PM",
    "BJ",
    "COST",
    "HARD",
    "GUNR",
]
# Tickers you hear about
beta_tickers = ["CRWD", "RKT", "UBER", "RIVN", "APP", "PLTR", "MSTR", "GME", "TSLA"]
# Is international diversification worth it?
geography_tickers = [
    "EWG",
    "EWZ",
    "FXI",
    "EWS",
    "EWC",
    "EWI",
]
# What alts are you considering relative to gold (e.g. trend-following?)
alt_tickers = [
    "DBMF",
    "KMLM",
    "TFPN",
    "TRTY",
    "UUP",
]
# Keeping a closer eye on pharma names
pharma_tickers = [
    "IVVD",
    "SDGR",
    "MDGL",
    "DVAX",
    "PTCT",
    "KROS",
    "RCKT",
    "ALKS",
    "BHVN",
    "TARS",
    "RZLT",
    "THTX",
]
# Like geo, seeing if there's any worthwhile sector tilts
sector_tickers = [
    "XLK",
    "XLE",
    "XLF",
    "XLU",
    "XLB",
    "XLI",
    "XLC",
    "XLY",
    "XLP",
]

def_benchmark = "SPY"
def_period = "1mo"
def_interval = "1d"
def_window = 20

# Sidebar inputs
benchmark_options = ["SPY", "QQQ", "GLD", "Other (type below)"]
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

# Group options for dropdown
GROUPS = {
    "Priority": priority_tickers,
    "Geographies": geography_tickers,
    "Alternatives": alt_tickers,
    "Beta": beta_tickers,
    "Pharma": pharma_tickers,
    "Sectors": sector_tickers,
}

group_name = st.selectbox(
    "Select ticker group",
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
    comparison_options = [
        ("1mo", "6mo"),
        ("6mo", "1y"),
    ]
    comparison_labels = [f"{a} vs {b}" for a, b in comparison_options]
    selected_comparison = st.selectbox(
        "Select timeframe comparison",
        options=range(len(comparison_options)),
        format_func=lambda i: comparison_labels[i],
        help="Compare RRG metrics between two periods.",
    )
    period_a, period_b = comparison_options[selected_comparison]

    # Fetch data for both periods
    rrg_a, dropped_a = get_rrg_data(selected_tickers, benchmark, period_a)
    rrg_b, dropped_b = get_rrg_data(selected_tickers, benchmark, period_b)

    # Last updated for higher-timeframe group
    if not rrg_b.empty and "Date" in rrg_b.columns:
        st.text(f"Last data point: {rrg_b['Date'].max().strftime('%Y-%m-%d')}")

    if not rrg_a.empty and not rrg_b.empty:
        diff_df = compare_rrg_timeframes(rrg_a, rrg_b)
        styled_velocity_table = rrg_velocity_table(diff_df)
        st.dataframe(styled_velocity_table)

        fig_diff = plot_rrg_diff(
            diff_df,
            period=f"{period_a} vs {period_b}",
            fix_axes=True,
        )
        st.plotly_chart(fig_diff, use_container_width=True)

        if dropped_a or dropped_b:
            st.info(
                f"Dropped tickers due to insufficient data: {', '.join(set(dropped_a + dropped_b))}"
            )
    else:
        st.warning("Not enough data to compare these periods for the selected tickers.")

    # Use rrg_b (HTF) for single-period analysis
    show_single_rrg = st.checkbox("Show single-period RRG charts", value=False)
    try:
        if (
            show_single_rrg
            and not rrg_b.empty
            and {"RS_Ratio", "RS_Momentum", "Symbol"}.issubset(rrg_b.columns)
        ):
            latest_points_htf = get_latest_valid_points(rrg_b)
            latest_points_ltf = get_latest_valid_points(rrg_a)
            fig_htf = plot_rrg(
                rrg_b,
                latest_points=latest_points_htf,
                max_points_per_ticker=4,
                period=period_b,
                fix_axes=True,
            )
            st.plotly_chart(fig_htf, use_container_width=True)
            fig_ltf = plot_rrg(
                rrg_a,
                latest_points=latest_points_ltf,
                max_points_per_ticker=4,
                period=period_a,
                fix_axes=True,
            )
            st.plotly_chart(fig_ltf, use_container_width=True)
    except Exception as e:
        st.error(f"Error fetching RRG data for {group_name}: {e}")

    if dropped_a or dropped_b:
        st.warning(
            f"The following tickers were dropped due to insufficient data: {', '.join(set(dropped_a + dropped_b))}"
        )

else:
    st.warning("Please enter a benchmark ticker to view the chart and table.")
