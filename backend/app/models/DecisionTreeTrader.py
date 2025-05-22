import numpy as np
import pandas as pd
import datetime
from .BagEnsembleModel import BagEnsembleModel as bag
from .TreeModel import TreeModel as tm
from ..utils import indicators, utility


def get_indicators(prices_data):
    """
    Calculate technical indicators used for trading decisions.

    Parameters
    ----------
    prices_data : pandas.DataFrame
        Historical price data

    Returns
    -------
    pandas.DataFrame containing normalized technical indicators:
        - Bollinger Bands (%B)
        - Relative Strength Index (RSI)
        - Golden/Death Cross (SMA crossovers)
    """
    bbp_df = indicators.bollinger_band_indicator(prices_data, lookback=10)
    bbp_df = utility.normalize_indicator(bbp_df)
    rsi_df = indicators.rsi_indicator(prices_data, 10)
    rsi_df = utility.normalize_indicator(rsi_df)
    gold_cross_df = indicators.golden_death_cross(prices_data, 10, 15)
    gold_cross_df = utility.normalize_indicator(gold_cross_df)
    indi_df = (bbp_df.join(rsi_df)).join(gold_cross_df)
    indi_df.ffill(inplace=True)
    indi_df.bfill(inplace=True)
    return indi_df


class DecisionTreeTrader(object):
    """
    A trading system that uses an ensemble of decision trees to make trading decisions.
    The system uses technical indicators (Bollinger Bands, RSI, and Golden/Death Cross)
    to predict future price movements and generate trading signals.

    Parameters
    ----------
    impact : float, optional
        The market impact of each transaction, defaults to 0.0
    commission : float, optional
        The commission amount charged, defaults to 0.0
    n_day_return : int, optional
        Number of days to look ahead for return calculation, defaults to 5
    y_buy : float, optional
        Threshold for buy signal, defaults to 0.008
    y_sell : float, optional
        Threshold for sell signal, defaults to -0.008
    leaf_size : int, optional
        Maximum number of samples at leaf nodes in the decision tree, defaults to 6
    num_bags : int, optional
        Number of trees in the ensemble, defaults to 10
    """

    # Constructor
    def __init__(self,
                 impact=0.0,
                 commission=0.0,
                 n_day_return=5,
                 y_buy=0.008,
                 y_sell=-0.008,
                 leaf_size=6,
                 num_bags=10):
        """
        Initialize the trading system with specified parameters.
        """
        self.impact = impact
        self.commission = commission
        self.N = n_day_return
        self.YBUY = y_buy + impact
        self.YSELL = y_sell - impact
        self.learner = bag.BagEnsembleModel(tm.TreeModel, kwargs={"leaf_size": leaf_size}, bags=num_bags)

    
    def train_model(
            self,
            symbol="IBM",
            sd=datetime.datetime(2008, 1, 1),
            ed=datetime.datetime(2009, 1, 1)
    ):
        """
        Train the trading model using historical data.

        Parameters
        ----------
        symbol : str, optional
            The stock symbol to train on, defaults to "IBM"
        sd : datetime, optional
            Start date for training data, defaults to 1/1/2008
        ed : datetime, optional
            End date for training data, defaults to 1/1/2009

        Notes
        -----
        The model uses technical indicators to predict future returns and classifies them into:
        - Long (+1): When N-day return > YBUY
        - Short (-1): When N-day return < YSELL
        - Cash (0): Otherwise
        """

        prices_train = utility.process_data(symbol, pd.date_range(sd, ed))
        indicators_df = get_indicators(prices_train)
        ret_df = prices_train.copy()
        ret_df = ret_df.shift(-1 * (self.N + 1)) / ret_df.shift(-1) - 1  # Future N day return
        data_train_df = indicators_df.join(ret_df).dropna()
        data_train_arr = data_train_df.to_numpy()

        # Classify Y column (last column) into three categories:
        # +1 (Long): N-day return > YBUY
        # -1 (Short): N-day return < YSELL
        # 0 (Cash): Other
        data_train_arr[:, -1] = np.where(data_train_arr[:, -1] > self.YBUY, 1, data_train_arr[:, -1])
        data_train_arr[:, -1] = np.where(data_train_arr[:, -1] < self.YSELL, -1, data_train_arr[:, -1])
        data_train_arr[:, -1] = np.where((data_train_arr[:, -1] != 1) & (data_train_arr[:, -1] != -1), 0, data_train_arr[:, -1])

        data_x = data_train_arr[:, :-1]
        data_y = data_train_arr[:, -1]

        self.learner.add_evidence(data_x, data_y)

    
    def test_model(
            self,
            symbol="IBM",
            sd=datetime.datetime(2009, 1, 1),
            ed=datetime.datetime(2010, 1, 1)
    ):
        """
        Test the trading model on out-of-sample data.

        Parameters
        ----------
        symbol : str, optional
            The stock symbol to test on, defaults to "IBM"
        sd : datetime, optional
            Start date for test data, defaults to 1/1/2009
        ed : datetime, optional
            End date for test data, defaults to 1/1/2010

        Returns
        -------
        pandas.DataFrame
            A DataFrame with trading signals for each day:
            - +1000.0: BUY 1000 shares
            - -1000.0: SELL 1000 shares
            - 0.0: NO TRADE
            - +2000.0/-2000.0: Switch positions (long to short or vice versa)
        """

        prices_test = utility.process_data(symbol, pd.date_range(sd, ed))
        indicators_test_df = get_indicators(prices_test)
        data_test_x_arr = indicators_test_df.to_numpy()
        predict_res = self.learner.query(data_test_x_arr)
        trades = pd.DataFrame(0.0, index=prices_test.index, columns=prices_test.columns)

        holding_shares = 0
        for i, pred in enumerate(predict_res[:-1]):
            if pred == 1:  # Long
                trades.iloc[i + 1] = 1000 - holding_shares
                holding_shares = 1000
            elif pred == -1:  # Short
                trades.iloc[i + 1] = -1000 - holding_shares
                holding_shares = -1000
            else:  # pred == 0, Cash
                trades.iloc[i + 1] = holding_shares * (-1)
                holding_shares = 0

        return trades
