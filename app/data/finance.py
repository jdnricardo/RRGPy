import pandas as pd


def get_rrg_data(tickers, benchmark, period, window):
    """
    Fetch price data and calculate RRG metrics for the given tickers and benchmark.
    Args:
        tickers (list): List of ticker symbols
        benchmark (str): Benchmark symbol
        period (str): Period for historical prices (e.g., '1y')
        window (int): Rolling window size
    Returns:
        pd.DataFrame: DataFrame with columns ['RS_Ratio', 'RS_Momentum', 'Symbol', ...]
    """
    # Stub: Replace with actual logic
    data = {
        "RS_Ratio": [100, 102, 98],
        "RS_Momentum": [99, 101, 97],
        "Symbol": tickers[:3],
    }
    return pd.DataFrame(data)
