import logging
import backtrader as bt
from datetime import datetime
from Strategies import StochMACD
from Commissions import CommInfo_Futures_Perc
from Parser import parse_args
from Datasets import *

def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(args.cash)
    # comminfo = cerebro.broker.setcommission(commission=0.001)
    comminfo = CommInfo_Futures_Perc(
        commission=args.commperc,
        mult=args.mult,
        margin=args.margin  # Margin is needed for futures-like instruments
    )
    cerebro.broker.addcommissioninfo(comminfo)

    fromdate = datetime.strptime(args.fromdate, '%Y-%m-%d')
    todate = datetime.strptime(args.todate, '%Y-%m-%d')

    dataname = DATASETS.get(args.dataset)
    data = bt.feeds.GenericCSVData(
        dataname=dataname,
        fromdate=fromdate,
        todate=todate,
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

    # cerebro.addsizer(bt.sizers.SizerFix, stake=args.stake)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=args.cashperc)

    cerebro.addstrategy(StochMACD, 
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
        atrperiod=args.atrperiod,
        atrdist=args.atrdist,
        # debug=args.debug
        loglevel=args.loglevel
    )

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Minutes, compression=60)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    runstrat()

# if __name__ == '__main__':
#     # Run Cerebro Engine
#     optimized_runs = cerebro.run()

#     final_results_list = []

#     for run in optimized_runs:
#         for strategy in run:
#             PnL = round(strategy.broker.get_value() - 1000, 2)
#             sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
#             final_results_list.append([strategy.params.stoch_upperband, strategy.params.stoch_lowerband, PnL, sharpe['sharperatio']])
#             sort_by_sharpe = sorted(final_results_list, key=lambda x: x[3], reverse=True)
#             for line in sort_by_sharpe[:5]:
#                 print(line)



