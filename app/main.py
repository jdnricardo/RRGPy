import streamlit as st

st.set_page_config(page_title="Relative Rotation Graph (RRG)", layout="wide")
st.title("Relative Rotation Graph (RRG) Interactive App")

st.markdown("""
This app visualizes the JdK RS Ratio vs JdK RS Momentum for a set of tickers relative to a benchmark, using Plotly for interactive charts.
""")

# Placeholder for controls and plot
st.sidebar.header("Controls")
st.sidebar.write("(Ticker selection, period, benchmark, etc. will go here)")

st.write("## RRG Plot")
st.info("The interactive RRG plot will appear here.")
