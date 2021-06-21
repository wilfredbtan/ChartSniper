from excelwriter import get_df_row, save_dataframe_to_excel
import os
from pprint import pprint
import time
import datetime as dt
from dateutil.relativedelta import relativedelta
from optimizer import optimize_strategy
from teststrategy import run_strategy, test_strategies
from Strategies import StochMACD, WfaStochMACD

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

def run_wfa():
    months_in = 12
    months_out = 6
    start_sample_date = dt.datetime(2018,2,1)
    end_sample_date = dt.datetime(2021,6,1)
    current_sample_date = start_sample_date
    dataset = 'btc_hourly'
    cash = 5000

    # [(end_of_interval, interval_params), ...]
    out_params = []

    while (current_sample_date +
        relativedelta(months=+months_in) +
        relativedelta(months=+months_out) < end_sample_date):
        in_period = (current_sample_date, current_sample_date + relativedelta(months=+months_in))
        out_sample_date = current_sample_date + relativedelta(months=+months_in)
        out_period = (out_sample_date, out_sample_date + relativedelta(months=+months_out))

        param_names = ['sqn', 'trades', 'pnl', 'macd1', 'macd2', 'macdsig', 'atrdist', 'reversal_sensitivity', 'short_perc']

        print(f"=== optimization period {in_period[0]} to {in_period[1]}")

        optimized_results = optimize_strategy(
            strategy=StochMACD,
            dataset=dataset,
            fromdate=in_period[0],
            todate=in_period[1],
            cash=cash,
            macd1=range(7, 12),
            macd2=range(14, 26),
            macdsig=range(5, 9),
            # macd1=9,
            # macd2=21,
            # macdsig=8,
            # atrdist=range(1,10),
            # reversal_sensitivity=range(1, 20),
            reversal_sensitivity=19,
            short_perc=1,
            leverage=5,
        )

        print("==== Top results =====")
        for result in optimized_results:
            print("sqn", result['sqn'])
            print("trades", result['trades'])
            print("pnl", result['pnl'])
            print("params", result['params'].__dict__)
            # row = get_df_row(result, param_names)

        # save_opt_results(optimized_results)
        out_params.append(
            (out_period[1], optimized_results[0]['params'].__dict__)
        )
        
        print(f"=== Test period {out_period[0]} to {out_period[1]}")

        # optimized_params = map(lambda x: x['params'].__dict__, optimized_results)
        # test_results = test_strategies(dataset, cash, out_period, optimized_params)

        # for result in test_results:
        #     print("sqn", result['sqn'])
        #     print("trades", result['trades'])
        #     print("pnl", result['pnl'])
        #     print("params", result['params'].__dict__)

        # save_out_results(out_results)

        # Increase step by out sample size for a perfect stitch
        current_sample_date += relativedelta(months=+months_out)

    # calculate_overall_results(all_out_results)
    print("==== out params")
    pprint(out_params)

    out_start_date = start_sample_date + relativedelta(months=+months_in)
    # Out date is not the end of sample but when there is not enough time left for another (optimization + test) cycle
    out_end_date = out_params[-1][0]

    print("==== Run Strategy ====")
    print(f"from: {out_start_date} to: {out_end_date}")

    result = run_strategy(
        strategy=WfaStochMACD, 
        dataset=dataset,
        fromdate=out_start_date,
        todate=out_end_date,
        cash=cash,
        interval_params=out_params
    )

    print("==== Result", result)

if __name__ == '__main__':
    start_time = time.time()
    run_wfa()
    print("--- %s seconds ---" % (time.time() - start_time))
