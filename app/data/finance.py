from typing import List

import numpy as np
import pandas as pd
import yfinance as yf

period_options = ["1mo", "1y", "5y", "10y", "max"]
interval_map = {"1mo": "1d", "1y": "5d", "5y": "1mo", "10y": "3mo", "max": "3mo"}
window_map = {"1mo": 7, "1y": 20, "5y": 50, "10y": 100, "max": 200}

# Define the schema for RRG data in one place
RRG_DATA_COLUMNS = ["Symbol", "Date", "Price", "Benchmark", "RS_Ratio", "RS_Momentum"]


def fetch_prices(
    symbols: List[str], period: str = "1y", interval: str = "1d"
) -> pd.DataFrame:
    """
    Fetch historical adjusted close prices for a list of symbols using yfinance.
    Returns a DataFrame with columns as symbols and index as dates.
    """
    data = yf.download(
        symbols, period=period, interval=interval, auto_adjust=True, progress=False
    )
    if data.empty:
        return pd.DataFrame()

    # Always get 'Close' (already adjusted if auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        # Select only the 'Close' price for all tickers
        data = data["Close"]
        # If only one ticker, data is a Series; convert to DataFrame
        if isinstance(data, pd.Series):
            data = data.to_frame(name=symbols[0])
        else:
            # Ensure columns are just ticker symbols
            data.columns = [str(col) for col in data.columns]
    else:
        # Single ticker, single-level columns
        data = data[["Close"]]
        data.columns = [symbols[0]]
    return data


def calculate_rs_ratio_and_momentum(
    prices: pd.DataFrame, benchmark: pd.Series, window: int = 10
):
    """
    Calculate RS-Ratio (RSR) and RS-Momentum (RSM) for each ticker relative to the benchmark.
    Returns a DataFrame with columns: Symbol, Date, RS_Ratio, RS_Momentum
    """
    results = []
    for symbol in prices.columns:
        if symbol == benchmark.name:
            continue
        # 1. Relative Strength (RS): ratio of ticker to benchmark
        rs = 100 * (prices[symbol] / benchmark)
        # 2. RS-Ratio (RSR): z-score of RS over rolling window, shifted/scaled to StockCharts convention
        rs_mean = rs.rolling(window=window).mean()
        rs_std = rs.rolling(window=window).std(ddof=0)
        rsr = 100 + (rs - rs_mean) / rs_std
        # 3. RS-Ratio ROC: percent change of RS-Ratio
        rsr_roc = 100 * (rsr / rsr.shift(1) - 1)
        # 4. RS-Momentum (RSM): z-score of RS-Ratio ROC over rolling window, shifted/scaled
        rsm_mean = rsr_roc.rolling(window=window).mean()
        rsm_std = rsr_roc.rolling(window=window).std(ddof=0)
        rsm = 101 + (rsr_roc - rsm_mean) / rsm_std
        # Align indices
        valid_idx = rsr.index.intersection(rsm.index)
        for date in valid_idx:
            results.append(
                {
                    "Symbol": symbol,
                    "Date": date,
                    "RS_Ratio": rsr.loc[date],
                    "RS_Momentum": rsm.loc[date],
                }
            )
    return pd.DataFrame(results)


def calculate_momentum_flip_count(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each ticker, track the number of times RS-Momentum crosses 100 (up or down),
    resetting the count whenever RS-Ratio crosses 100 (changes half).
    Adds a new column 'Momentum_Flip_Count' to the DataFrame.
    """
    df = df.sort_values(["Symbol", "Date"]).copy()
    df["Momentum_Flip_Count"] = 0
    for symbol in df["Symbol"].unique():
        mask = df["Symbol"] == symbol
        sub = df.loc[mask]
        last_half = None
        last_momentum = None
        flip_count = 0
        counts = []
        for _, row in sub.iterrows():
            rsr = row["RS_Ratio"]
            rsm = row["RS_Momentum"]
            # Determine current half
            current_half = "right" if rsr >= 100 else "left"
            # Reset if half changes
            if last_half is not None and current_half != last_half:
                flip_count = 0
                last_momentum = None
            # Count momentum flips
            if last_momentum is not None:
                if (last_momentum < 100 and rsm >= 100) or (
                    last_momentum >= 100 and rsm < 100
                ):
                    flip_count += 1
            counts.append(flip_count)
            last_half = current_half
            last_momentum = rsm
        df.loc[mask, "Momentum_Flip_Count"] = counts
    return df


def get_rrg_data(tickers, benchmark, period):
    """
    Fetch price data for tickers and benchmark. Return a DataFrame with columns:
    ['Symbol', 'Date', 'Price', 'Benchmark', 'RS_Ratio', 'RS_Momentum', 'Momentum_Flip_Count']
    Also returns a list of tickers that were dropped due to insufficient data.
    """
    if not tickers:
        return pd.DataFrame(columns=RRG_DATA_COLUMNS + ["Momentum_Flip_Count"]), []

    interval = interval_map.get(period, "1wk")
    window = window_map.get(period, 50)

    prices = fetch_prices(tickers + [benchmark], period=period, interval=interval)
    if prices.empty:
        return pd.DataFrame(columns=RRG_DATA_COLUMNS + ["Momentum_Flip_Count"]), tickers

    prices = prices.dropna()
    if prices.empty:
        return pd.DataFrame(columns=RRG_DATA_COLUMNS + ["Momentum_Flip_Count"]), tickers

    # Only keep tickers that are present in the prices DataFrame
    available_tickers = [t for t in tickers if t in prices.columns]
    dropped_tickers = [t for t in tickers if t not in prices.columns]

    if not available_tickers:
        return pd.DataFrame(columns=RRG_DATA_COLUMNS + ["Momentum_Flip_Count"]), tickers

    df = (
        prices[available_tickers]
        .reset_index()
        .melt(id_vars=["Date"], var_name="Symbol", value_name="Price")
    )
    # Add benchmark price for each date
    benchmark_prices = prices[benchmark].reset_index()
    df = df.merge(benchmark_prices, on="Date", how="left", suffixes=("", "_Benchmark"))
    df = df.rename(columns={benchmark: "Benchmark"})

    # Calculate RS-Ratio and RS-Momentum
    rs_df = calculate_rs_ratio_and_momentum(
        prices[available_tickers], prices[benchmark], window
    )
    if rs_df.empty:
        df["RS_Ratio"] = np.nan
        df["RS_Momentum"] = np.nan
        df["Momentum_Flip_Count"] = 0
        return df[RRG_DATA_COLUMNS + ["Momentum_Flip_Count"]], dropped_tickers

    df = df.merge(rs_df, on=["Symbol", "Date"], how="left")
    df = calculate_momentum_flip_count(df)
    # TODO: add volatility metric to normalize flip count and distance
    return df, dropped_tickers


def get_latest_valid_points(df):
    # Only keep rows with valid RS_Ratio and RS_Momentum
    valid = df.dropna(subset=["RS_Ratio", "RS_Momentum"])
    # For each symbol, get the row with the latest date
    idx = valid.groupby("Symbol")["Date"].idxmax()
    return valid.loc[idx]
