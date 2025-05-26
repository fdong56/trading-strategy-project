import numpy as np
import pandas as pd
import datetime
from backend.app.models.QLearner import QLearner as ql
from backend.app.utils import indicators, utility


class QLearningTrader(object):

    # constructor  		  	   		 	   			  		 			     			  	 
    def __init__(self, 
                 impact=0.0, 
                 commission=0.0, 
                 bins=10,
                 alpha=0.2,
                 gamma=0.9,
                 rar=0.98,
                 radr=0.999,
                 dyna=0):
        """
        Constructor method

        :param impact: The market impact of each transaction, defaults to 0.0
        :type impact: float
        :param commission: The commission amount charged, defaults to 0.0
        :type commission: float
        """

        self.impact = impact  		  	   		 	   			  		 			     			  	 
        self.commission = commission
        self.learner = None
        self.bins = bins
        states_amount = (bins - 1) * 111 + 1
        self.learner = ql(
            num_states=states_amount,
            num_actions=3,
            alpha=alpha,
            gamma=gamma,
            rar=rar,
            radr=radr,
            dyna=dyna
        )
  		  	   		 	   			  		 			     			  	 
    # Train the model for trading
    def train_model(
        self,
        symbol="IBM",
        sd=datetime.datetime(2008, 1, 1),
        ed=datetime.datetime(2009, 1, 1),
        sv=100000,
        indicators_with_params=None
    ):
        """
        Train the strategy model over a given time frame using user-specified indicators and parameters.

        Parameters
        ----------
        symbol : str
            The stock symbol to train on
        sd : datetime
            Start date for training data
        ed : datetime
            End date for training data
        sv : int
            The starting value of the portfolio
        indicators_with_params : dict, optional
            Dictionary mapping indicator names to their parameter dicts. Must specify exactly three indicators. Example:
            {
                "bbp": {"lookback": 10},
                "rsi": {"lookback": 10},
                "macd": {"short_period": 12, "long_period": 26}
            }
        """

        if indicators_with_params is None:
            indicators_with_params = {
                "bbp": {"lookback": 10},
                "rsi": {"lookback": 10},
                "macd": {"short_period": 12, "long_period": 26}
            }
        self.indicators_with_params = indicators_with_params  # Store for later use
        prices_train = utility.process_data(symbol, pd.date_range(sd, ed))
        indi_states_df = self.get_indi_states(prices_train, indicators_with_params)

        last_cum_ret = -100
        current_cum_ret = 0
        trades = pd.DataFrame(0, index=prices_train.index, columns=prices_train.columns)
        while np.abs(current_cum_ret - last_cum_ret) > 0.001:
            last_cum_ret = current_cum_ret
            day = 0
            state = indi_states_df.iloc[day]
            # action: 0 (Buy), 1 (Sell), 2 (Do nothing)
            action = self.learner.querysetstate(state)
            holding_shares = 0
            while day < prices_train.shape[0] - 1:
                step_reward, shares_to_buy, holding_shares = self.calculate_reward(day, action, holding_shares, prices_train)
                state = indi_states_df.iloc[day + 1]
                action = self.learner.query(state, step_reward)
                trades.iloc[day] = shares_to_buy
                day += 1
            port_vals_df = utility.compute_portvals(trades, start_val=sv, commission=self.commission, impact=self.impact, symbol=symbol)
            portvals = port_vals_df[port_vals_df.columns[0]]
            current_cum_ret = portvals.iloc[-1] / portvals.iloc[0] - 1

    # Test the model against new data
    def test_model(
        self,
        symbol="IBM",
        sd=datetime.datetime(2009, 1, 1),
        ed=datetime.datetime(2010, 1, 1)
    ):
        """
        Test the trained model using the same indicators and parameters as in training.

        Parameters
        ----------
        symbol : str
            The stock symbol to test on
        sd : datetime
            Start date for test data
        ed : datetime
            End date for test data
        sv : int
            The starting value of the portfolio

        Returns
        -------
        pandas.DataFrame
            DataFrame with values representing trades for each day.
        """
        if not hasattr(self, "indicators_with_params") or self.indicators_with_params is None:
            raise ValueError("No indicators_with_params stored from training. Please train the model first.")
        prices_test = utility.process_data(symbol, pd.date_range(sd, ed))
        indi_states_test = self.get_indi_states(prices_test, self.indicators_with_params)
        day = 0
        holding_shares = 0
        trades_test = pd.DataFrame(0, index=prices_test.index, columns=prices_test.columns)
        while day < prices_test.shape[0] - 1:
            state = indi_states_test.iloc[day]
            action = self.learner.querysetstate(state)
            step_reward, shares_to_buy, holding_shares = self.calculate_reward(day, action, holding_shares, prices_test)
            trades_test.iloc[day] = shares_to_buy
            day += 1
        return trades_test

    def get_indi_states(self, prices_data, indicators_with_params=None):
        """
        Compute indicator states for Q-Learning using user-specified indicators and parameters.

        Parameters
        ----------
        prices_data : pandas.DataFrame
            Historical price data
        indicators_with_params : dict, optional
            Dictionary mapping indicator names to their parameter dicts. Must specify exactly three indicators.

        Returns
        -------
        pandas.DataFrame
            DataFrame of discretized indicator states.
        """
        # Default indicators if none provided
        indicator_funcs = {
            "gold cross": indicators.golden_death_cross,
            "bbp": indicators.bollinger_band_indicator,
            "roc": indicators.roc_indicator,
            "macd": indicators.macd_indicator,
            "rsi": indicators.rsi_indicator,
        }
        # Compute the three indicators
        indicator_dfs = []
        for name, params in indicators_with_params.items():
            if name not in indicator_funcs:
                raise ValueError(f"Indicator '{name}' is not supported.")
            # Convert all parameters to integers
            params = {k: int(v) for k, v in params.items()}
            df = indicator_funcs[name](prices_data, **params)
            indicator_dfs.append(df)
        indi_states = self.discretize(*indicator_dfs)
        return indi_states

    def calculate_reward(self, i_day, a, holding, prices_data):
        price_today = prices_data.iloc[i_day]
        price_next = prices_data.iloc[i_day + 1]

        # return followings
        r = (price_next / price_today) - 1
        to_buy = 0
        updated_holding = holding

        if a == 0: # Long
            updated_holding = 1000
            if holding == 1000:
                to_buy = 0
            elif holding == -1000:
                to_buy = 2000
            elif holding == 0:
                to_buy = 1000
        elif a == 1: # Short
            r = r * (-1)
            updated_holding = -1000
            if holding == -1000:
                to_buy = 0
            elif holding == 1000:
                to_buy = -2000
            elif holding == 0:
                to_buy = -1000
        elif a == 2: # CASH
            r = 0
            updated_holding = 0
            if holding == 1000:
                to_buy = -1000
            elif holding == -1000:
                to_buy = 1000
            elif holding == 0:
                to_buy = 0
        if to_buy != 0:
            r -= self.impact
        return r, to_buy, updated_holding

    def discretize(self, indicator_1, indicator_2, indicator_3):
        indicator_1_norm = utility.normalize_indicator(indicator_1)
        indicator_2_norm = utility.normalize_indicator(indicator_2)
        indicator_3_norm = utility.normalize_indicator(indicator_3)
        indicator_1_norm[indicator_1.columns[0]] = pd.cut(indicator_1_norm[indicator_1_norm.columns[0]], self.bins, labels=False)
        indicator_2_norm[indicator_2.columns[0]] = pd.cut(indicator_2_norm[indicator_2_norm.columns[0]], self.bins, labels=False)
        indicator_3_norm[indicator_3.columns[0]] = pd.cut(indicator_3_norm[indicator_3_norm.columns[0]], self.bins, labels=False)
        indicator_state = indicator_1_norm.copy()
        indicator_state[indicator_state.columns[0]] = (indicator_1_norm[indicator_1_norm.columns[0]] * 100
                                                       + indicator_2_norm[indicator_2_norm.columns[0]] * 10
                                                       + indicator_3_norm[indicator_3_norm.columns[0]])
        indicator_state.ffill(inplace=True)
        indicator_state.bfill(inplace=True)
        indicator_state = indicator_state.astype('int32')
        return indicator_state

