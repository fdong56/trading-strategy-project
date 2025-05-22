import datetime
import utility
import matplotlib.pyplot as plt
import DecisionTreeTrader as dtt
import QLearningTrader as qlt


def get_plot(trades_benchmark, trades_learner, symbol_="JPM", impact_=0.005, commission_=9.95,
             start_cash=100000, title="In Sample", fig_name="experiment1_in_sample.png"):

    portvals_benchmark = utility.compute_portvals(trades_benchmark, start_val=start_cash, commission=commission_, impact=impact_, symbol=symbol_)
    portvals_benchmark = portvals_benchmark / portvals_benchmark.iloc[0]

    portvals_learner = utility.compute_portvals(trades_learner, start_val=start_cash, commission=commission_, impact=impact_, symbol=symbol_)
    portvals_learner = portvals_learner / portvals_learner.iloc[0]

    ax = portvals_benchmark[portvals_benchmark.columns[0]].plot(label="Benchmark", color="purple")
    portvals_learner[portvals_learner.columns[0]].plot(label="Strategy Learner", color="green", ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Portfolio Value")
    ax.legend(loc="best")
    plt.title("Strategy Model and Benchmark Trading JPM - " + title, pad=13)
    plt.savefig("./images/" + fig_name, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":


    # ---------------------------- #
    #       DecisionTreeTrader     #
    # ---------------------------- #
    # The in-sample period is from January 1, 2008, to December 31, 2009.
    # The out-of-sample/testing period is from January 1, 2010, to December 31, 2011.
    # The starting cash is $100,000
    start_date_in = datetime.datetime(2008, 1, 1)
    end_date_in = datetime.datetime(2009, 12, 31)
    start_date_out = datetime.datetime(2010, 1, 1)
    end_date_out = datetime.datetime(2011, 12, 31)
    cash = 100000
    symbol_select = "JPM"
    impact_select = 0.005
    commission_select = 9.95

    dt_model = dtt.DecisionTreeTrader(impact=impact_select,
                                      commission=commission_select,
                                      n_day_return=5,
                                      y_buy=0.008,
                                      y_sell=-0.008,
                                      leaf_size=6,
                                      num_bags=10)
    dt_model.train_model(symbol=symbol_select, sd=start_date_in, ed=end_date_in)
    trades_model_in = dt_model.test_model(symbol=symbol_select, sd=start_date_in, ed=end_date_in)
    trades_model_out = dt_model.test_model(symbol=symbol_select, sd=start_date_out, ed=end_date_out)

    trades_benchmark_in = trades_model_in.copy()
    trades_benchmark_in.iloc[:, :] = 0.0
    trades_benchmark_in.iloc[0, 0] = 1000
    trades_benchmark_out = trades_model_out.copy()
    trades_benchmark_out.iloc[:, :] = 0.0
    trades_benchmark_out.iloc[0, 0] = 1000

    # in-sample
    get_plot(trades_benchmark_in, trades_model_in, symbol_=symbol_select, impact_=impact_select,
             commission_=commission_select, start_cash=cash, title="In Sample", fig_name="experiment1_in_sample.png")
    # out-sample
    get_plot(trades_benchmark_out, trades_model_out, symbol_=symbol_select, impact_=impact_select,
             commission_=commission_select, start_cash=cash, title="Out of Sample",
             fig_name="experiment1_out_sample.png")



    # ---------------------------- #
    #         QLearningTrader      #
    # ---------------------------- #

    ql_model = qlt.QLearningTrader(impact=impact_select,
                                 commission=commission_select,
                                 bins=10,
                                 alpha=0.2,
                                 gamma=0.9,
                                 rar=0.98,
                                 radr=0.999,
                                 dyna=0)
    ql_model.train_model(symbol=symbol_select, sd=start_date_in, ed=end_date_in)
    trades_model_in = ql_model.test_model(symbol=symbol_select, sd=start_date_in, ed=end_date_in)
    trades_model_out = ql_model.test_model(symbol=symbol_select, sd=start_date_out, ed=end_date_out)

    trades_benchmark_in = trades_model_in.copy()
    trades_benchmark_in.iloc[:, :] = 0.0
    trades_benchmark_in.iloc[0, 0] = 1000
    trades_benchmark_out = trades_model_out.copy()
    trades_benchmark_out.iloc[:, :] = 0.0
    trades_benchmark_out.iloc[0, 0] = 1000

    # in-sample
    get_plot(trades_benchmark_in, trades_model_in, symbol_=symbol_select, impact_=impact_select,
             commission_=commission_select, start_cash=cash, title="In Sample", fig_name="experiment2_in_sample.png")
    # out-sample
    get_plot(trades_benchmark_out, trades_model_out, symbol_=symbol_select, impact_=impact_select,
             commission_=commission_select, start_cash=cash, title="Out of Sample",
             fig_name="experiment2_out_sample.png")

