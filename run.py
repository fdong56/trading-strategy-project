import pandas as pd
import datetime
from backend.app.utils import utility


def main():
    sd = datetime.datetime(2008, 1, 1)
    ed = datetime.datetime(2009, 1, 1)
    prices_train = utility.process_data("JPM", pd.date_range(sd, ed))
    print(prices_train.index.tz)



if __name__ == "__main__":
    main()

