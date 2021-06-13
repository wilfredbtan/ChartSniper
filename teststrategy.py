import backtrader as bt
from Datasets import *
from Strategies import StochMACD

def test_strategies(dataset, cash, period, parameter_sets):
    results = []
    for parameter_set in parameter_sets:
        result = run_strategy(dataset, period[0], period[1], cash, **parameter_set)
        results.append(result)
    return results

def run_strategy(dataset, fromdate, todate, cash, **kwargs):
    cerebro = bt.Cerebro(optreturn=False, quicknotify=True)
    cerebro.broker.set_shortcash(False)
    cerebro.broker.set_cash(cash)
    cerebro.broker.setcommission(commission=0.00015, leverage=5)

    dataname = DATASETS.get(dataset)
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
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
    cerebro.addstrategy(StochMACD, **kwargs)

    run = cerebro.run()

    strategy = run[0]

    PnL = round(strategy.broker.get_value() - cash, 2)
    sqn = strategy.analyzers.sqn.get_analysis()
    return {
        'sqn': sqn['sqn'],
        'trades': sqn['trades'],
        'pnl': PnL, 
        'params': strategy.p
    }
    # return [
    #     sqn['sqn'],
    #     sqn['trades'],
    #     PnL,
    #     # strategy.p.atrdist,
    #     # strategy.p.macd1,
    #     # strategy.p.macd2,
    #     # strategy.p.macdsig,
    #     # strategy.p.reversal_sensitivity,
    #     # strategy.p.short_perc,
    # ]
