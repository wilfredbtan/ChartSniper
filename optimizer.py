import backtrader as bt
from backtrader.dataseries import TimeFrame
from Datasets import *
from Strategies import StochMACD

def optimize_strategy(dataset, fromdate, todate, cash, **kwargs):
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

    cerebro.optstrategy(StochMACD, **kwargs)

    optimized_runs = cerebro.run()

    final_results_list = []

    for run in optimized_runs:
        for strategy in run:
            PnL = round(strategy.broker.get_value() - cash, 2)
            sqn = strategy.analyzers.sqn.get_analysis()
            final_results_list.append({
                'sqn': sqn['sqn'],
                'trades': sqn['trades'],
                'pnl': PnL, 
                'params': strategy.p
            })
    sort_by_analyzer = sorted(final_results_list, key=lambda x: x['sqn'], reverse=True)
    top_five = sort_by_analyzer[:5]
    return top_five