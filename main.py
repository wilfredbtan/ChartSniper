import backtrader as bt
from datetime import datetime

from backtrader.cerebro import OptReturn
from Strategies import StochMACD
from Commissions import CommInfo_Futures_Perc
from Parser import parse_args
from Datasets import *

def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro(optreturn=(not args.optimize))
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

    # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Minutes, compression=60)
    # cerebro.addanalyzer(bt.analyzers.Returns, _name='returns', timeframe=bt.TimeFrame.Minutes, compression=60)
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr', timeframe=bt.TimeFrame.Minutes, compression=60)

    if args.optimize:
        # cerebro = bt.Cerebro(optreturn=False)
        # cerebro.optstrategy(MAcrossover, pfast=range(5, 20), pslow=range(50, 100))  
        # cerebro.optstrategy(StochRSI, stoch_upperband=range(75,80), stoch_lowerband=range(20,25))

        #   
        cerebro.optstrategy(StochMACD, 
            # macd1=range(7, 12),
            # macd2=range(14, 26),
            # macdsig=range(5, 9),
            macd1=9,
            macd2=21,
            macdsig=8,
            stoch_k_period=args.stoch_k_period,
            stoch_d_period=args.stoch_d_period,
            stoch_rsi_period=args.stoch_rsi_period,
            stoch_period=args.stoch_period,
            stoch_upperband=args.stoch_upperband,
            stoch_lowerband=args.stoch_lowerband,
            rsi_upperband=args.rsi_upperband,
            rsi_lowerband=args.rsi_lowerband,
            atrperiod=args.atrperiod,
            # atrdist=args.atrdist,
            atrdist=5,
            loglevel=args.loglevel
        )

        optimized_runs = cerebro.run()

        final_results_list = []

        for run in optimized_runs:
            for strategy in run:
                PnL = round(strategy.broker.get_value() - args.cash, 2)
                # sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
                # returns = strategy.analyzers.returns.get_analysis()
                vwr = strategy.analyzers.vwr.get_analysis()
                final_results_list.append(
                    [
                        vwr['vwr'],
                        # returns['rtot'],
                        # returns['ravg'],
                        # sharpe['sharperatio']
                        PnL, 
                        strategy.p.atrdist,
                        strategy.p.macd1, 
                        strategy.p.macd2, 
                        strategy.p.macdsig, 
                    ]
                )
        sort_by_analyzer = sorted(final_results_list, key=lambda x: x[0], reverse=True)
        for line in sort_by_analyzer[:5]:
            print(line)

    else:
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
            loglevel=args.loglevel
        )

        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

        if args.plot:
            cerebro.plot()

if __name__ == '__main__':
    runstrat()

