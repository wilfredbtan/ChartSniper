import backtrader as bt
from Datasets import *
from strategies import WfaStochMACD
from Commissions import CommInfo_Futures_Perc
from Sizers import PercValue

def test_strategies(dataset, cash, period, parameter_sets):
    results = []
    for parameter_set in parameter_sets:
        result = run_strategy(WfaStochMACD, dataset, period[0], period[1], cash, **parameter_set)
        results.append(result)
    return results

def run_wfa(wfastrategy, dataset, fromdate, todate, cash, cashperc, interval_params):
    cerebro = bt.Cerebro(optreturn=False, quicknotify=True)
    cerebro.broker.set_shortcash(False)
    cerebro.broker.set_cash(cash)
    futures_perc = CommInfo_Futures_Perc(commission=0.02, leverage=interval_params['leverage'])
    cerebro.broker.addcommissioninfo(futures_perc)
    cerebro.addsizer(PercValue, perc=cashperc, min_size=0.0001)

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
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=240)

    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    cerebro.addstrategy(wfastrategy, interval_params, isWfa=True)

    run = cerebro.run()

    result = run[0]

    PnL = round(result.broker.get_value() - cash, 2)
    sqn = result.analyzers.sqn.get_analysis()
    return {
        'sqn': sqn['sqn'],
        'trades': sqn['trades'],
        'pnl': PnL, 
        'params': result.p.__dict__
    }

def run_strategy(strategy, dataset, fromdate, todate, cash, cashperc, **kwargs):
    cerebro = bt.Cerebro(optreturn=False, quicknotify=True)
    cerebro.broker.set_shortcash(False)
    cerebro.broker.set_cash(cash)
    futures_perc = CommInfo_Futures_Perc(commission=0.02, leverage=kwargs['leverage'])
    cerebro.broker.addcommissioninfo(futures_perc)
    cerebro.addsizer(PercValue, perc=cashperc, min_size=0.0001)

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
    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=240)

    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    cerebro.addstrategy(strategy, **kwargs)

    run = cerebro.run()

    result = run[0]

    PnL = round(result.broker.get_value() - cash, 2)
    sqn = result.analyzers.sqn.get_analysis()
    return {
        'sqn': sqn['sqn'],
        'trades': sqn['trades'],
        'pnl': PnL, 
        'params': result.p
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
    # ]
