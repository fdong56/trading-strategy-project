import os
import pandas as pd


def all_y_same(data_y):
    """
    This function is useful for checking if a dataset is homogeneous,
    which is often used in decision tree algorithms to determine if
    a node should be a leaf node.

    Parameters
    ----------
    data_y : numpy.ndarray
        Target values to check for homogeneity

    Returns
    -------
    bool
        True if all values are the same, False otherwise

    """
    if_equal = data_y == data_y[0]
    if False in if_equal:
        return False
    else:
        return True


def symbol_to_path(symbol, base_dir=None):
    """
    This function converts a stock symbol to its corresponding CSV file path.

    Parameters
    ----------
    symbol : str
        Stock symbol to convert to the file path
    base_dir : str, optional
        Base directory for data files. If None, uses MARKET_DATA_DIR
        environment variable or defaults to "./data/"

    Returns
    -------
    str
        Full path to the CSV file for the given symbol
    """
    if base_dir is None:
        # Always resolve data directory relative to the project root
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../backend/data/")
        )
    return os.path.join(base_dir, f"{symbol}.csv")


def get_data(symbols, dates, add_spy=True, col_name="Adj Close"):
    """
    This function loads historical stock data for the given symbols and dates,
    optionally adding SPY data for reference. It handles missing data and
    ensures all data is properly aligned by date.

    Parameters
    ----------
    symbols : list of str
        List of stock symbols to load data for
    dates : pandas.DatetimeIndex
        Date range for the data
    add_spy : bool, optional
        Whether to add SPY data for reference, defaults to True
    col_name : str, optional
        Column name to use from the CSV files, defaults to "Adj Close"

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the stock data, indexed by date
    """
    df = pd.DataFrame(index=dates)
    df.index = df.index.tz_localize(None)
    # print("DEBUG: df index tz before join:", df.index.tz)
    if add_spy and "SPY" not in symbols:
        symbols = ["SPY"] + list(symbols)
    for symbol in symbols:
        df_temp = pd.read_csv(
            symbol_to_path(symbol),
            index_col="Date",
            parse_dates=True,
            usecols=["Date", col_name],
            na_values=["nan"],
        )
        df_temp = df_temp.rename(columns={col_name: symbol})
        # print(f"DEBUG: df_temp index tz for {symbol}:", df_temp.index.tz)
        df = df.join(df_temp)
        if symbol == "SPY":
            df = df.dropna(subset=["SPY"])
    return df


def process_data(symbol, dates):
    """
    This function loads and processes stock data, handling missing values
    and ensuring data consistency. It optionally removes SPY data if
    the symbol is not SPY.

    Parameters
    ----------
    symbol : str
        Stock symbol to process data for
    dates : pandas.DatetimeIndex
        Date range for the data

    Returns
    -------
    pandas.DataFrame
        Processed stock price data
    """
    prices_train = get_data([symbol], dates)

    if symbol != "SPY":
        prices_train = prices_train.drop("SPY", axis=1)

    prices_train.ffill(inplace=True)
    prices_train.bfill(inplace=True)

    return prices_train


def normalize_indicator(indicator):
    """
    This function performs min-max normalization on technical indicators,
    scaling all values to be between 0 and 1.

    Parameters
    ----------
    indicator : pandas.DataFrame
        Technical indicator values to normalize

    Returns
    -------
    pandas.DataFrame
        Normalized indicator values
    """
    indicator_min = indicator.min()
    indicator_max = indicator.max()
    indicator_norm = (indicator - indicator_min) / (indicator_max - indicator_min)
    return indicator_norm


def compute_portvals(
    trades, start_val=100000, commission=9.95, impact=0.005, symbol="JPM"
):
    """
    This function computes the portfolio value over time based on a series
    of trades, taking into account commission and market impact.

    Parameters
    ----------
    trades : pandas.DataFrame
        DataFrame containing trade information
    start_val : float, optional
        Starting portfolio value, defaults to 100000
    commission : float, optional
        Commission per trade, defaults to 9.95
    impact : float, optional
        Market impact factor, defaults to 0.005
    symbol : str, optional
        Stock symbol being traded, defaults to 'JPM'

    Returns
    -------
    pandas.DataFrame
        DataFrame containing portfolio values over time
    """
    start_date = trades.index[0]
    end_date = trades.index[-1]
    prices = process_data(symbol, pd.date_range(start_date, end_date))
    prices["CASH"] = 1.0

    # create Trades dataframe
    trades["CASH"] = 0.0
    trades.loc[(trades[symbol] != 0.0), ["CASH"]] = (
        prices[symbol] * trades[symbol] * (-1.0)
        - commission
        - prices[symbol] * impact * abs(trades[symbol])
    )

    # create Holdings dataframe
    holdings_ = prices.copy()
    holdings_.iloc[:, :] = 0.0
    # holdings_['CASH'].iloc[0] = start_val
    holdings_.loc[holdings_.index[0], "CASH"] = start_val
    holdings_ += trades
    holdings = holdings_.expanding(1).sum()

    # create Values dataframe
    values = prices.copy()
    values.iloc[:, :] = 0.0
    values = prices * holdings
    port_vals = values.sum(axis=1)
    port_vals_df = pd.DataFrame(
        data=port_vals.values, index=port_vals.index, columns=["p_VALUE"]
    )

    return port_vals_df
