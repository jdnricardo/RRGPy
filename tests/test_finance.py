import numpy as np
import pandas as pd

from app.data.finance import (
    fetch_prices,
    get_rrg_data,
    interval_map,
    period_options,
    window_map,
)


def test_fetch_prices_valid():
    tickers = ["AAPL", "MSFT"]
    df = fetch_prices(tickers, period="1mo", interval="1d")
    print(df.columns)
    assert isinstance(df, pd.DataFrame)
    assert all(ticker in df.columns for ticker in tickers)
    assert not df.empty


def test_fetch_prices_invalid():
    tickers = ["FAKE_TICKER_123"]
    df = fetch_prices(tickers, period="1mo", interval="1d")
    assert isinstance(df, pd.DataFrame)
    # Should be empty or all NaN
    assert df.empty or df.isna().all().all()


def test_get_rrg_data_empty():
    tickers = []
    benchmark = "SPY"
    df = get_rrg_data(tickers, benchmark, period="1mo")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
    # Should still have the expected columns
    for col in ["Symbol", "Date", "Price", "Benchmark", "RS_Ratio", "RS_Momentum"]:
        assert col in df.columns


def test_get_rrg_data_single_ticker():
    tickers = ["AAPL"]
    benchmark = "SPY"
    df = get_rrg_data(tickers, benchmark, period="1mo")
    assert isinstance(df, pd.DataFrame)
    assert set(df["Symbol"]).issubset(set(tickers))
    assert not df.empty


def test_get_rrg_data_periods():
    tickers = ["AAPL", "MSFT"]
    benchmark = "SPY"
    for period in period_options:
        df = get_rrg_data(tickers, benchmark, period=period)
        assert isinstance(df, pd.DataFrame)
        assert set(df["Symbol"]).issubset(set(tickers))
        # Should not error, may be empty for some periods


def test_get_rrg_data_rs_columns():
    tickers = ["AAPL", "MSFT"]
    benchmark = "SPY"
    df = get_rrg_data(tickers, benchmark, period="1mo")
    assert "RS_Ratio" in df.columns
    assert "RS_Momentum" in df.columns
    # Should be numeric
    assert np.issubdtype(df["RS_Ratio"].dtype, np.number)
    assert np.issubdtype(df["RS_Momentum"].dtype, np.number)


def test_window_and_interval_logic():
    # Check that window and interval are set as expected for each period
    for period in period_options:
        interval = interval_map.get(period)
        window = window_map.get(period)
        assert interval is not None
        assert window is not None
