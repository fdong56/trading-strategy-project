import argparse
import datetime
from backend.app.utils import utility
import matplotlib.pyplot as plt
from backend.app.models.QLearningTrader import QLearningTrader
from backend.app.models.DecisionTreeTrader import DecisionTreeTrader


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Trading Strategy Runner')
    
    # Model selection argument
    parser.add_argument('--model', 
                       type=str,
                       choices=['qlearning', 'tree'],
                       default='qlearning',
                       help='Select which model to use (qlearning, tree)')
    
    # Common parameters
    parser.add_argument('--symbol',
                       type=str,
                       default='JPM',
                       help='Stock symbol to trade')
    
    parser.add_argument('--start-date',
                       type=str,
                       default='2008-01-01',
                       help='Start date for training (YYYY-MM-DD)')
    
    parser.add_argument('--end-date',
                       type=str,
                       default='2009-01-01',
                       help='End date for training (YYYY-MM-DD)')
    
    parser.add_argument('--test-start',
                       type=str,
                       default='2009-01-01',
                       help='Start date for testing (YYYY-MM-DD)')
    
    parser.add_argument('--test-end',
                       type=str,
                       default='2010-01-01',
                       help='End date for testing (YYYY-MM-DD)')
    
    parser.add_argument('--start-val',
                       type=float,
                       default=100000,
                       help='Starting portfolio value')
    
    # Model-specific parameters
    parser.add_argument('--impact',
                       type=float,
                       default=0.0,
                       help='Market impact of each transaction')
    
    parser.add_argument('--commission',
                       type=float,
                       default=0.0,
                       help='Commission amount charged per transaction')
    
    # QLearning specific parameters
    parser.add_argument('--bins',
                       type=int,
                       default=10,
                       help='Number of bins for QLearning discretization')
    
    parser.add_argument('--alpha',
                       type=float,
                       default=0.2,
                       help='Learning rate for QLearning')
    
    parser.add_argument('--gamma',
                       type=float,
                       default=0.9,
                       help='Discount factor for QLearning')
    
    return parser.parse_args()

def create_model(args):
    """
    Create the appropriate model based on command line arguments.
    
    Args:
        args (argparse.Namespace): Parsed command line arguments
        
    Returns:
        object: Instance of the selected model
    """
    if args.model == 'qlearning':
        return QLearningTrader(
            impact=args.impact,
            commission=args.commission,
            bins=args.bins,
            alpha=args.alpha,
            gamma=args.gamma
        )
    elif args.model == 'tree':
        return DecisionTreeTrader(
            impact=args.impact,
            commission=args.commission,
            n_day_return=5,
            y_buy=0.008,
            y_sell=-0.008,
            leaf_size=6,
            num_bags=10)
    return None

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

def main():
    args = parse_args()
    
    # Convert date strings to datetime objects
    start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
    test_start = datetime.datetime.strptime(args.test_start, '%Y-%m-%d')
    test_end = datetime.datetime.strptime(args.test_end, '%Y-%m-%d')
    
    # Create and train the model
    model = create_model(args)
    
    # Train the model
    model.train_model(
        symbol=args.symbol,
        sd=start_date,
        ed=end_date,
        sv=args.start_val
    )
    
    # Test the model
    trades_model_in = model.test_model(
        symbol=args.symbol,
        sd=start_date,
        ed=end_date,
        sv=args.start_val
    )

    trades_model_out = model.test_model(
        symbol=args.symbol,
        sd=test_start,
        ed=test_end,
        sv=args.start_val
    )

    impact_select = 0.005
    commission_select = 9.95

    trades_benchmark_in = trades_model_in.copy()
    trades_benchmark_in.iloc[:, :] = 0.0
    trades_benchmark_in.iloc[0, 0] = 1000
    trades_benchmark_out = trades_model_out.copy()
    trades_benchmark_out.iloc[:, :] = 0.0
    trades_benchmark_out.iloc[0, 0] = 1000

    # in-sample
    get_plot(trades_benchmark_in, trades_model_in, symbol_=args.symbol, impact_=impact_select,
             commission_=commission_select, start_cash=args.start_val, title="In Sample", fig_name="experiment1_in_sample.png")
    # out-sample
    get_plot(trades_benchmark_out, trades_model_out, symbol_=args.symbol, impact_=impact_select,
             commission_=commission_select, start_cash=args.start_val, title="Out of Sample",
             fig_name="experiment1_out_sample.png")


if __name__ == "__main__":
    main()

