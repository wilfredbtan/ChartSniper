from termcolor import colored
from excelwriter import get_df_row, save_dataframe_to_excel
import os
from pprint import pprint
from Parser import parse_args
import time
import datetime as dt
from dateutil.relativedelta import relativedelta
from teststrategy import run_strategy
from strategies import StochMACD

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

# current_directory = os.getcwd()
# wfa_directory = os.path.join(current_directory, r'wfa')
# algo_name = "stoch_macd"
# algo_directory = os.path.join(wfa_directory, algo_name)
# os.makedirs(algo_directory, exist_ok=True)

my_columns = ['In/Out', 'Start Date', 'End Date', 'SQN', 'Trades', 'PnL']
rows = []

def run_test(args=None):
    args = parse_args(args)

    test_period = 12
    step = 1
    start_sample_date = dt.datetime(2017,9,1)
    end_sample_date = dt.datetime(2021,6,1)
    current_sample_date = start_sample_date
    dataset = 'btc_hourly'
    cash = 5000

    count = 0
    total_sqn = 0
    total_pnl = 0
    total_trades = 0
    min_sqn = float("inf")
    min_pnl = float("inf")

    while (current_sample_date + relativedelta(months=+test_period) < end_sample_date):
        in_period = (current_sample_date, current_sample_date + relativedelta(months=+test_period))

        param_names = ['sqn', 'trades', 'pnl', 'macd1', 'macd2', 'macdsig', 'atrdist', 'reversal_sensitivity']

        print(f"=== run period {in_period[0].date()} to {in_period[1].date()}")

        result = run_strategy(
            strategy=StochMACD, 
            dataset=dataset,
            fromdate=in_period[0],
            todate=in_period[1],
            cash=cash,
            macd1=args.macd1,
            macd2=args.macd2,
            macdsig=args.macdsig,
            stoch_k_period=args.stoch_k_period,
            stoch_d_period=args.stoch_d_period,
            stoch_rsi_period=args.stoch_rsi_period,
            stoch_period=args.stoch_period,
            stoch_upperband=args.stoch_upperband,
            stoch_lowerband=args.stoch_lowerband,
            rsi_upperband=args.rsi_upperband,
            rsi_lowerband=args.rsi_lowerband,
            # cmf_upperband=0.03,
            # cmf_lowerband=-0.1,
            atrperiod=args.atrperiod,
            atrdist=args.atrdist,
            reversal_sensitivity=args.reversal_sensitivity,
            reversal_lowerband=args.reversal_lowerband,
            reversal_upperband=args.reversal_upperband,
            loglevel=args.loglevel,
            leverage=args.leverage,
            cashperc=args.cashperc,
            isWfa=False
        )

        print("==== results =====")
        sqn = result['sqn']
        print(f"sqn: {sqn}")

        pnl = result['pnl']
        pnl_txt = f'pnl: {pnl}'
        if result['pnl'] < 0:
            pnl_txt = colored(pnl_txt, 'red')
        print(pnl_txt)
        print(f"trades: {result['trades']}")
        # print("params", result['params'].__dict__)

        total_sqn += sqn
        total_pnl += pnl
        total_trades += result['trades']
        min_sqn = min(min_sqn, sqn)
        min_pnl = min(min_pnl, pnl)

        count += 1

        current_sample_date += relativedelta(months=+step)
    
    # Final result
    print("+++++ Final Result +++++")
    print(f"Avg SQN: {total_sqn / count : .2f}")
    print(f"Min SQN: {min_sqn : .2f}")
    print(f"Avg pnl: {total_pnl / count : .2f}")
    print(f"Min pnl: {min_pnl : .2f}")
    print(f"Avg trades: {total_trades / count: .2f}")


if __name__ == '__main__':
    start_time = time.time()
    run_test()
    print("--- %s seconds ---" % (time.time() - start_time))
