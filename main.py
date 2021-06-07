from datetime import datetime
import backtrader as bt
from Strategies import StochMACD, MAcrossover
from Commissions import CommInfo_Futures_Perc

# Instantiate Cerebro engine
cerebro = bt.Cerebro(optreturn=False)
# cerebro = bt.Cerebro()

cerebro.broker.setcommission(commission=0.001)
#     cerebro.broker.set_coo(True)

#     comminfo = CommInfo_Futures_Perc(
#         commission=0.02,  # 0.1%
#         mult=3,
#         margin=1000  # Margin is needed for futures-like instruments
#     )

#     cerebro.broker.addcommissioninfo(comminfo)

datapath = './crypto/reversed_BTC_1H.csv'

data = bt.feeds.GenericCSVData(
    dataname=datapath,
    fromdate=datetime(2021,5,1),
    todate=datetime(2021,6,1),
    timeframe=bt.TimeFrame.Minutes,
    nullvalue=0.0,
    datetime=0,
    open=4,
    high=5,
    low=6,
    close=7,
    volume=8,
    compression=60,
    headers=True,
)

cerebro.adddata(data)
# sharpe = bt.analyzers.SharpeRatio(timeframe=bt.TimeFrame.Years)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')

# Add strategy to Cerebro
# cerebro.addstrategy(MAcrossover)

# cerebro.optstrategy(MAcrossover, pfast=range(5, 20), pslow=range(50, 100))
cerebro.optstrategy(StochMACD, stoch_upperband=range(75,80), stoch_lowerband=range(20,25))

# Default position size
cerebro.addsizer(bt.sizers.SizerFix, stake=3)

if __name__ == '__main__':
    # Run Cerebro Engine
    optimized_runs = cerebro.run()

    final_results_list = []

    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - 1000, 2)
            sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
            print(sharpe)

            # final_results_list.append([strategy.params['stoch_upperband'], strategy.params['stoch_lowerband'], PnL, sharpe['sharperatio']])
            # print("params")
            # print(strategy.params.stoch_upperband)
            # print("sharpe")
            # print(sharpe['sharperatio'])
            final_results_list.append([strategy.params.stoch_upperband, strategy.params.stoch_lowerband, PnL, sharpe['sharperatio']])
            # sort_by_sharpe = sorted(final_results_list, key=lambda x: x[3], reverse=True)
            sort_by_sharpe = sorted(final_results_list, key=lambda x: x[2], reverse=True)

            for line in sort_by_sharpe[:5]:
                print(line)


    # end_portfolio_value = cerebro.broker.getvalue()
    # pnl = end_portfolio_value - start_portfolio_value
    # print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    # print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    # print(f'PnL: {pnl:.2f}')



