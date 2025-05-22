import numpy as np
import pandas as pd


def golden_death_cross(prices, lookback_1=20, lookback_2=50):
    """
    Calculate the Golden/Death Cross indicator using two Simple Moving Averages (SMA).

    The Golden Cross occurs when a shorter-term SMA crosses above a longer-term SMA,
    while the Death Cross occurs when it crosses below. This is often used as a
    bullish/bearish signal.

    Parameters
    ----------
    prices : pandas.DataFrame
        Price data to calculate the indicator for
    lookback_1 : int, optional
        Period for the shorter-term SMA, defaults to 20
    lookback_2 : int, optional
        Period for the longer-term SMA, defaults to 50

    Returns
    -------
    pandas.DataFrame
        DataFrame containing both SMAs
    """
    ret_df = pd.DataFrame(0.0, index=prices.index, columns=['%d-day SMA' % lookback_1, '%d-day SMA' % lookback_2])
    sma_1 = prices.rolling(window=lookback_1, min_periods=lookback_1).mean()
    sma_2 = prices.rolling(window=lookback_2, min_periods=lookback_2).mean()
    ret_df['%d-day SMA' % lookback_1] = sma_1
    ret_df['%d-day SMA' % lookback_2] = sma_2
    return ret_df


def bollinger_band_indicator(prices, lookback=20):
    """
    Calculate the Bollinger Bands %B indicator.

    Bollinger Bands consist of a middle band (SMA) and two outer bands that are
    standard deviations away from the middle band. The %B indicator shows where
    the price is relative to the bands, normalized between 0 and 1.

    Parameters
    ----------
    prices : pandas.DataFrame
        Price data to calculate the indicator for
    lookback : int, optional
        Period for the moving average and standard deviation, defaults to 20

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the %B values
    """
    ret_df = pd.DataFrame(0.0, index=prices.index, columns=['%B'])
    rolling_std = prices.rolling(window=lookback, min_periods=lookback).std()
    sma = prices.rolling(window=lookback, min_periods=lookback).mean()
    upper_band = sma + (2 * rolling_std)
    lower_band = sma - (2 * rolling_std)
    bbp_df = (prices - lower_band) / (upper_band - lower_band)
    ret_df['%B'] = bbp_df
    return ret_df


def roc_indicator(prices, lookback):
    """
    Calculate the Rate of Change (ROC) indicator.

    ROC measures the percentage change in price over a specified period,
    helping to identify momentum and potential trend reversals.

    Parameters
    ----------
    prices : pandas.DataFrame
        Price data to calculate the indicator for
    lookback : int
        Period for the ROC calculation

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the ROC values
    """
    ret_df = pd.DataFrame(0.0, index=prices.index, columns=['ROC'])
    roc = (prices / prices.shift(lookback - 1) - 1) * 100
    ret_df['ROC'] = roc
    ret_df = ret_df.dropna()
    return ret_df


def macd_indicator(prices, short_period=12, long_period=26, signal_period=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD) indicator.

    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of a security's price.

    Parameters
    ----------
    prices : pandas.DataFrame
        Price data to calculate the indicator for
    short_period : int, optional
        Period for the short-term EMA, defaults to 12
    long_period : int, optional
        Period for the long-term EMA, defaults to 26
    signal_period : int, optional
        Period for the signal line EMA, defaults to 9

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the MACD values
    """
    ret_df = pd.DataFrame(0.0, index=prices.index, columns=['MACD', 'Signal'])
    ema_short = prices.ewm(span=short_period).mean()
    ema_long = prices.ewm(span=long_period).mean()
    macd = ema_short - ema_long
    ret_df['MACD'] = macd
    ret_df['Signal'] = ret_df['MACD'].ewm(span=signal_period).mean()
    ret_df = ret_df.drop('Signal', axis=1)
    return ret_df


def rsi_indicator(prices, lookback):
    """
    Calculate the Relative Strength Index (RSI) indicator.

    RSI is a momentum oscillator that measures the speed and change of price
    movements, typically used to identify overbought or oversold conditions.

    Parameters
    ----------
    prices : pandas.DataFrame
        Price data to calculate the indicator for
    lookback : int
        Period for the RSI calculation

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the RSI values
    """
    ret_df = pd.DataFrame(0.0, index=prices.index, columns=['RSI'])
    dif = prices.diff()
    # dif = dif.dropna()
    gain = dif.clip(lower=0)
    loss = dif.clip(upper=0).abs()
    roll_gain_ave = gain.rolling(window=lookback, min_periods=lookback).mean()
    roll_loss_ave = loss.rolling(window=lookback, min_periods=lookback).mean()
    rs = roll_gain_ave / roll_loss_ave
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi[rsi == np.inf] = 100
    ret_df['RSI'] = rsi
    return ret_df