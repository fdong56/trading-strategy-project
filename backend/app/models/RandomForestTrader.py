import numpy as np
import pandas as pd
import datetime
from ..utils import indicators, utility
from .BagEnsembleModel import BagEnsembleModel as bag
from .TreeModel import TreeModel as tm


"""
RandomForestTrader: Implements a bagged decision tree (Random Forest) trading strategy with technical indicators.

This class supports training and testing a trading model using historical price data and user-specified technical indicators.
It normalizes indicators, classifies returns, and generates trading signals.
"""


class RandomForestTrader(object):
    """
    A trading strategy model using a bagged decision tree (Random Forest) approach.

    Attributes:
        impact (float): Market impact parameter.
        commission (float): Commission per trade.
        N (int): Lookback period for N-day return.
        YBUY (float): Threshold for buy signal.
        YSELL (float): Threshold for sell signal.
        learner: Bagged decision tree learner.
        scaler_map (dict): Stores min/max scalers for each indicator.
    """

    # Constructor
    def __init__(
        self,
        impact=0.0,
        commission=0.0,
        n_day_return=5,
        y_buy=0.008,
        y_sell=-0.008,
        leaf_size=6,
        num_bags=10,
    ):
        """
        Initialize the RandomForestTrader with trading parameters and model configuration.

        Args:
            impact (float): Market impact parameter.
            commission (float): Commission per trade.
            n_day_return (int): Lookback period for N-day return.
            y_buy (float): Buy threshold for N-day return.
            y_sell (float): Sell threshold for N-day return.
            leaf_size (int): Leaf size for decision tree.
            num_bags (int): Number of bags for bagging.
        """
        self.scaler_map = {}
        self.impact = impact
        self.commission = commission
        self.N = n_day_return
        self.YBUY = y_buy + impact
        self.YSELL = y_sell - impact
        self.learner = bag(tm, kwargs={"leaf_size": leaf_size}, bags=num_bags)

    def train_model(
        self,
        symbol="IBM",
        sd=datetime.datetime(2008, 1, 1),
        ed=datetime.datetime(2009, 1, 1),
        sv=100000,
        indicators_with_params=None,
    ):
        """
        Train the trading model using historical data and user-specified indicators.

        Args:
            symbol (str): The stock symbol to train on.
            sd (datetime): Start date for training data.
            ed (datetime): End date for training data.
            sv (float): Starting portfolio value (unused).
            indicators_with_params (dict): Mapping of indicator names to their parameter dicts.
        """

        if indicators_with_params is None:
            indicators_with_params = {
                "bbp": {"lookback": 10},
                "rsi": {"lookback": 10},
                "macd": {"short_period": 12, "long_period": 26},
            }
        self.indicators_with_params = indicators_with_params

        prices_train = utility.process_data(symbol, pd.date_range(sd, ed))
        indicators_df = self.get_indicators(prices_train, indicators_with_params)
        ret_df = prices_train.copy()
        ret_df = (
            ret_df.shift(-1 * (self.N + 1)) / ret_df.shift(-1) - 1
        )  # Future N day return
        data_train_df = indicators_df.join(ret_df).dropna()
        data_train_arr = data_train_df.to_numpy()

        # Classify Y column (last column) into three categories:
        # +1 (Long): N-day return > YBUY
        # -1 (Short): N-day return < YSELL
        # 0 (Cash): Otherwise
        data_train_arr[:, -1] = np.where(
            data_train_arr[:, -1] > self.YBUY, 1, data_train_arr[:, -1]
        )
        data_train_arr[:, -1] = np.where(
            data_train_arr[:, -1] < self.YSELL, -1, data_train_arr[:, -1]
        )
        data_train_arr[:, -1] = np.where(
            (data_train_arr[:, -1] != 1) & (data_train_arr[:, -1] != -1),
            0,
            data_train_arr[:, -1],
        )

        data_x = data_train_arr[:, :-1]
        data_y = data_train_arr[:, -1]

        self.learner.add_evidence(data_x, data_y)

    def test_model(
        self,
        symbol="IBM",
        sd=datetime.datetime(2009, 1, 1),
        ed=datetime.datetime(2010, 1, 1),
    ):
        """
        Test the trading model on out-of-sample data using the same indicators and parameters as training.

        Args:
            symbol (str): The stock symbol to test on.
            sd (datetime): Start date for test data.
            ed (datetime): End date for test data.

        Returns:
            pandas.DataFrame: Trading signals for each day.
        """

        if (
            not hasattr(self, "indicators_with_params")
            or self.indicators_with_params is None
        ):
            raise ValueError(
                "No indicators_with_params stored from training. Please train the model first."
            )

        prices_test = utility.process_data(symbol, pd.date_range(sd, ed))
        indicators_test_df = self.get_indicators(
            prices_test,
            self.indicators_with_params,
        )
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

    def predict(self, indicators_arr, symbol="IBM"):
        """
        Predict trading signals for given indicator values (not implemented).

        Args:
            indicators_arr (np.ndarray): Array of indicator values.
            symbol (str): The stock symbol.
        """
        if (
            not hasattr(self, "indicators_with_params")
            or self.indicators_with_params is None
        ):
            raise ValueError(
                "No indicators_with_params stored from training. Please train the model first."
            )

        pass

    def get_indicators(self, prices_data, indicators_with_params, scaler_map=None):
        """
        Calculate and normalize selected technical indicators with user-defined parameters.

        Args:
            prices_data (pandas.DataFrame): Historical price data.
            indicators_with_params (dict): Mapping of indicator names to their parameter dicts.
            scaler_map (dict, optional): Existing scaler map for normalization.

        Returns:
            pandas.DataFrame: Normalized technical indicators.
        """

        indicator_funcs = {
            "gold cross": indicators.golden_death_cross,
            "bbp": indicators.bollinger_band_indicator,
            "roc": indicators.roc_indicator,
            "macd": indicators.macd_indicator,
            "rsi": indicators.rsi_indicator,
        }

        indicator_mapping = {}

        for name, params in indicators_with_params.items():
            if name not in indicator_funcs:
                raise ValueError(f"Indicator '{name}' is not supported.")
            # Convert all params to int if possible
            for k, v in params.items():
                try:
                    params[k] = int(v)
                except (ValueError, TypeError):
                    pass
            indi_df = indicator_funcs[name](prices_data, **params)
            indi_df, scaler_min_, scaler_max_ = utility.normalize_indicator(
                indi_df, indicator_name=name, scaler_map=self.scaler_map
            )
            self.scaler_map[name] = [scaler_min_, scaler_max_]
            indicator_mapping[name] = indi_df

        # Join all selected indicators
        indi_df = None
        for df in indicator_mapping.values():
            if indi_df is None:
                indi_df = df
            else:
                indi_df = indi_df.join(df)

        indi_df.ffill(inplace=True)
        indi_df.bfill(inplace=True)
        return indi_df
