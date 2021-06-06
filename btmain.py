import datetime
import backtrader as bt
from strategies import *

# Instantiate Cerebro engine
cerebro = bt.Cerebro(optreturn=False)

# Set data parameters and add to Cerebro
data = bt.feeds.YahooFinanceCSVData(
    dataname='daily/TSLA.csv',
    fromdate=datetime.datetime(2016, 1, 1),
    todate=datetime.datetime(2017, 12, 25),
)
# settings for out-of-sample data
# fromdate=datetime.datetime(2018, 1, 1),
# todate=datetime.datetime(2019, 12, 25))

cerebro.adddata(data)

cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
cerebro.optstrategy(MAcrossover, pfast=range(5, 20), pslow=range(50, 100))

# Add strategy to Cerebro
# cerebro.addstrategy(MAcrossover)

# Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

if __name__ == '__main__':
    # Run Cerebro Engine
    optimized_runs = cerebro.run()

    final_results_list = []

    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - 10000, 2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            final_results_list.append([strategy.params['pfast'], strategy.params['pslow'], PnL, sharpe['sharperatio']])
            sort_by_sharpe = sorted(final_results_list, key=lambda x: x[3], reverse=True)

            for line in sort_by_sharpe[:5]:
                print(line)


    # end_portfolio_value = cerebro.broker.getvalue()
    # pnl = end_portfolio_value - start_portfolio_value
    # print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    # print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    # print(f'PnL: {pnl:.2f}')



