import os
from pprint import pprint
import datetime as dt
from dateutil.relativedelta import relativedelta
from optimizer import optimize_strategy
from teststrategy import test_strategies

'''
1. Create wfa results directory
2. Create new folder with algo name
3. Create new sheet with date and time as name
4. for each (in-sample, out-sample) in samples:
    a. Run optimization on in-sample
    b. Store optimization param results
    c. Run test on out-sample using top 5 paramaters from optimization
    d. Store results and average gain 
5. Return overall average from all out-samples
'''

current_directory = os.getcwd()
wfa_directory = os.path.join(current_directory, r'wfa')
algo_name = "stoch_macd_halfhalf"
algo_directory = os.path.join(wfa_directory, algo_name)
os.makedirs(algo_directory, exist_ok=True)

'''
((in_sample_fromdate, period (months)), (out_sample_fromdate, period(months)))
'''
def run_wfa():
    months_in = 6
    months_out = 3
    start_sample_date = dt.datetime(2018,2,1)
    end_sample_date = dt.datetime(2021,6,1)
    current_sample_date = start_sample_date
    dataset = 'btc_hourly'
    cash = 5000

    # six_months = date.today() + relativedelta(months=+6)
    while (current_sample_date +
        relativedelta(months=+months_in) +
        relativedelta(months=+months_out) < end_sample_date):
        in_period = (current_sample_date, current_sample_date + relativedelta(months=+months_in))
        out_sample_date = current_sample_date + relativedelta(months=+months_in)
        out_period = (out_sample_date, out_sample_date + relativedelta(months=+months_out))

        print(f"=== optimization period {in_period[0]} to {in_period[1]}")

        optimized_results = optimize_strategy(
            dataset=dataset,
            fromdate=in_period[0],
            todate=in_period[1],
            cash=cash,
            macd1=range(7, 12),
            macd2=range(14, 26),
            macdsig=range(5, 9),
            # atrdist=range(1,10),
            # reversal_sensitivity=range(1, 20),
            reversal_sensitivity=19,
            # short_perc=range(1,100),
            leverage=5,
        )

        print("Top results")
        for line in optimized_results:
            print("sqn", line['sqn'])
            print("trades", line['trades'])
            print("pnl", line['pnl'])
            print("params", line['params'])

        # save_opt_results(optimized_results)
        
        print(f"=== Test period {out_period[0]} to {out_period[1]}")

        optimized_params = map(lambda x: x['params'], optimized_results)
        test_results = test_strategies(dataset, cash, out_period, optimized_params)

        for line in test_results:
            print(line)

        # save_out_results(out_results)

        current_sample_date += relativedelta(months=+months_in) + relativedelta(months=+months_out)

    # calculate_overall_results(all_out_results)
if __name__ == '__main__':
    run_wfa()
