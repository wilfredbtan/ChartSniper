import statistics
import time
import datetime as dt

from termcolor import colored
from excelwriter import get_df_row, save_dataframe_to_excel
from pprint import pprint
from Parser import parse_args
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
    sqns = []
    pnls = []
    trades = []
    # total_sqn = 0
    # total_pnl = 0
    # total_trades = 0
    # min_sqn = float("inf")
    # min_pnl = float("inf")
    # max_sqn = float("inf")
    # max_pnl = float("inf")

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
            cashperc=args.cashperc,
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

        # total_sqn += sqn
        # total_pnl += pnl
        # total_trades += result['trades']
        # min_sqn = min(min_sqn, sqn)
        # min_pnl = min(min_pnl, pnl)
        # max_sqn = max(max_sqn, sqn)
        # max_pnl = max(max_pnl, pnl)
        sqns.append(sqn)
        pnls.append(pnl)
        trades.append(result['trades'])

        count += 1

        current_sample_date += relativedelta(months=+step)
    
    # Final result
    print("+++++ Final Result +++++")
    min_pnl = min(pnls)
    max_pnl = max(pnls)
    avg_pnl = sum(pnls) / len(pnls)
    std_pnl = statistics.stdev(pnls)

    min_sqn = min(sqns)
    max_sqn = max(sqns)
    avg_sqn = sum(sqns) / len(sqns)
    std_sqn = statistics.stdev(sqns)

    min_trade = min(trades)
    max_trade = max(trades)
    avg_trade = sum(trades) / len(trades)
    std_trade = statistics.stdev(trades)

    print("PNL:")
    print(f"    min: {min_pnl : .2f}")
    print(f"    max: {max_pnl : .2f}")
    print(f"    avg: {avg_pnl : .2f}")
    print(f"    std: {std_pnl : .2f}")
    print("SQN:")
    print(f"    min: {min_sqn : .2f}")
    print(f"    max: {max_sqn : .2f}")
    print(f"    avg: {avg_sqn : .2f}")
    print(f"    std: {std_sqn : .2f}")
    print("TRADES:")
    print(f"    min: {min_trade : .2f}")
    print(f"    max: {max_trade : .2f}")
    print(f"    avg: {avg_trade : .2f}")
    print(f"    std: {std_trade : .2f}")

if __name__ == '__main__':
    start_time = time.time()
    run_test()
    print("--- %s seconds ---" % (time.time() - start_time))
