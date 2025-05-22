import numpy as np
import pandas as pd
import QLearner as ql
import datetime
import utility
import indicators


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
        self.learner = ql.QLearner(
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
        sv=100000
    ):  		  	   		 	   			  		 			     			  	 
        """  		  	   		 	   			  		 			     			  	 
        Train the strategy model over a given time frame.  		  	   		 	   			  		 			     			  	 
  		  	   		 	   			  		 			     			  	 
        :param symbol: The stock symbol to train on  		  	   		 	   			  		 			     			  	 
        :type symbol: str  		  	   		 	   			  		 			     			  	 
        :param sd: A datetime object that represents the start date, defaults to 1/1/2008  		  	   		 	   			  		 			     			  	 
        :type sd: datetime  		  	   		 	   			  		 			     			  	 
        :param ed: A datetime object that represents the end date, defaults to 1/1/2009  		  	   		 	   			  		 			     			  	 
        :type ed: datetime  		  	   		 	   			  		 			     			  	 
        :param sv: The starting value of the portfolio  		  	   		 	   			  		 			     			  	 
        :type sv: int  		  	   		 	   			  		 			     			  	 
        """  		  	   		 	   			  		 			     			  	 

        prices_train = utility.process_data(symbol, pd.date_range(sd, ed))
        indi_states_df = self.get_indi_states(prices_train)

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
        ed=datetime.datetime(2010, 1, 1),
        sv=100000
    ):  		  	   		 	   			  		 			     			  	 
        """  		  	   		 	   			  		 			     			  	 
        Tests your learner using data outside of the training data  		  	   		 	   			  		 			     			  	 
  		  	   		 	   			  		 			     			  	 
        :param symbol: The stock symbol that you trained on on  		  	   		 	   			  		 			     			  	 
        :type symbol: str  		  	   		 	   			  		 			     			  	 
        :param sd: A datetime object that represents the start date, defaults to 1/1/2008  		  	   		 	   			  		 			     			  	 
        :type sd: datetime  		  	   		 	   			  		 			     			  	 
        :param ed: A datetime object that represents the end date, defaults to 1/1/2009  		  	   		 	   			  		 			     			  	 
        :type ed: datetime  		  	   		 	   			  		 			     			  	 
        :param sv: The starting value of the portfolio  		  	   		 	   			  		 			     			  	 
        :type sv: int  		  	   		 	   			  		 			     			  	 
        :return: A DataFrame with values representing trades for each day. Legal values are +1000.0 indicating  		  	   		 	   			  		 			     			  	 
            a BUY of 1000 shares, -1000.0 indicating a SELL of 1000 shares, and 0.0 indicating NOTHING.  		  	   		 	   			  		 			     			  	 
            Values of +2000 and -2000 for trades are also legal when switching from long to short or short to  		  	   		 	   			  		 			     			  	 
            long so long as net holdings are constrained to -1000, 0, and 1000.  		  	   		 	   			  		 			     			  	 
        :rtype: pandas.DataFrame  		  	   		 	   			  		 			     			  	 
        """

        prices_test = utility.process_data(symbol, pd.date_range(sd, ed))
        indi_states_test = self.get_indi_states(prices_test)
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

    def get_indi_states(self, prices_data):
        bbp_df = indicators.bollinger_band_indicator(prices_data, lookback=10)
        rsi_df = indicators.rsi_indicator(prices_data, 10)
        macd_df = indicators.macd_indicator(prices_data, short_period=12, long_period=26)
        indi_states = self.discretize(bbp_df, rsi_df, macd_df)
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

