from excelwriter import get_df_row, save_dataframe_to_excel
import os
from pprint import pprint
import time
import datetime as dt
from dateutil.relativedelta import relativedelta
from optimizer import optimize_strategy
from teststrategy import run_strategy, test_strategies
from strategies import StochMACD, WfaStochMACD

'''
1. Create wfa results directory
2. Create new folder with algo name
3. Create new sheet with date and time as name
4. for each (in-sample, out-sample) in samples:
    a. Run optimization on in-sample
    b. Store optimization param results
4. Run test on all out-samples using top 5 paramaters from optimization
5. Store results and average gain 
6. Return overall average from all out-samples
'''

current_directory = os.getcwd()
wfa_directory = os.path.join(current_directory, r'wfa')
algo_name = "stoch_macd_halfhalf"
algo_directory = os.path.join(wfa_directory, algo_name)
os.makedirs(algo_directory, exist_ok=True)

my_columns = ['In/Out', 'Start Date', 'End Date', 'SQN', 'Trades', 'PnL']
rows = []

def run_test():
    test_period = 12
    step = 3
    start_sample_date = dt.datetime(2018,2,1)
    end_sample_date = dt.datetime(2021,6,1)
    current_sample_date = start_sample_date
    dataset = 'btc_hourly'
    cash = 5000

    while (current_sample_date + relativedelta(months=+test_period) < end_sample_date):
        in_period = (current_sample_date, current_sample_date + relativedelta(months=+test_period))

        param_names = ['sqn', 'trades', 'pnl', 'macd1', 'macd2', 'macdsig', 'atrdist', 'reversal_sensitivity']

        print(f"=== run period {in_period[0]} to {in_period[1]}")

        result = run_strategy(
            strategy=StochMACD, 
            dataset=dataset,
            fromdate=in_period[0],
            todate=in_period[1],
            cash=cash,
        )

        print("==== results =====")
        print("sqn", result['sqn'])
        print("trades", result['trades'])
        print("pnl", result['pnl'])
        print("params", result['params'].__dict__)

        current_sample_date += relativedelta(months=+step)


if __name__ == '__main__':
    start_time = time.time()
    run_test()
    print("--- %s seconds ---" % (time.time() - start_time))
