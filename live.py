import time
import datetime as dt
import backtrader as bt

from ccxtbt import CCXTStore, CCXTFeed
from config import BINANCE, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG
# from config import BITFINEX, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG
# from config import KRAKEN, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG

from utils import print_trade_analysis, print_sqn, send_telegram_message, get_formatted_datetime

from Strategies import StochMACD, TESTBUY
from Commissions import CommInfo_Futures_Perc
from Parser import parse_args
from Datasets import *

def main():
    # cerebro = bt.Cerebro(quicknotify=True)
    cerebro = bt.Cerebro()

    comminfo = CommInfo_Futures_Perc(
        commission=0.002,
        mult=5,
        margin=1000, # Margin is needed for futures-like instruments
    )
    cerebro.broker.addcommissioninfo(comminfo)

    if ENV == PRODUCTION:  # Live trading with Binance
        broker_config = {
            # 'apiKey': KRAKEN.get("key"),
            # 'secret': KRAKEN.get("secret"),
            # 'apiKey': BITFINEX.get("key"),
            # 'secret': BITFINEX.get("secret"),
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret"),
            # 'nonce': lambda: str(int(time.time() * 1000)),
            'nonce': lambda: str(int(time.time() * 1000)),
            'enableRateLimit': True,
        }

        store = CCXTStore(
            exchange='binanceusdm', 
            # exchange='bitfinex', 
            # exchange='kraken', 
            currency=COIN_REFER, 
            config=broker_config, 
            retries=5, 
            debug=DEBUG,
            sandbox=SANDBOX
        )

        # store.exchange.load_markets()
        # print(store.exchange.markets['BTC/USDT'])

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.StopLimit: 'stop_market'
            },
            'mappings': {
                'closed_order': {
                    'key': 'status',
                    'value': 'closed'
                },
                'canceled_order': {
                    'key': 'status',
                    'value': 'canceled'
                }
            }
        }

        broker = store.getbroker(broker_mapping=broker_mapping)
        cerebro.setbroker(broker)

        hist_start_date = dt.datetime.utcnow() - dt.timedelta(hours=1000)
        data = store.getdata(
            dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
            name='%s%s' % (COIN_TARGET, COIN_REFER),
            timeframe=bt.TimeFrame.Minutes,
            # timeframe=bt.TimeFrame.Days,
            fromdate=hist_start_date,
            # Max number of ticks before throttling occurs
            compression=60,
            ohlcv_limit=1000,
            # Prevents loading partial data from incomplete candles
            drop_newest=True
        )

        # Add the feed
        cerebro.adddata(data)

    else:  # Backtesting with CSV file

        dataname = DATASETS.get('btc_hourly')
        data = bt.feeds.GenericCSVData(
            dataname=dataname,
            fromdate=dt.datetime(2018,2,1),
            todate=dt.datetime(2021,6,1),
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
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)
        # cerebro.adddata(data)

        broker = cerebro.getbroker()
        # broker.setcommission(commission=0.001, name=COIN_TARGET)  # Simulating exchange fee
        broker.setcash(1000.0)

    # cerebro.addsizer(bt.sizers.PercentSizer, percents=50)
    cerebro.addsizer(bt.sizers.SizerFix, stake=0.001)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) x SquareRoot( number of trades )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Include Strategy
    # cerebro.addstrategy(StochMACD, 
    #     macd1=9,
    #     macd2=21,
    #     macdsig=8,
    #     atrdist=5
    # )

    cerebro.addstrategy(TESTBUY)

    # Starting backtrader bot
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    send_telegram_message("Chart Sniper initialized")
    result = cerebro.run()

    # Print analyzers - results
    final_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final_value)
    print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
    print_trade_analysis(result[0].analyzers.ta.get_analysis())
    print_sqn(result[0].analyzers.sqn.get_analysis())

    # if DEBUG:
    #     cerebro.plot()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        datetime_str = dt.datetime.now().strftime('%d %b %Y %H:%M:%S')
        print("Chart Sniper finished by user on %s" % datetime_str)
        send_telegram_message("Bot finished by user on %s" % datetime_str)
    except Exception as err:
        datetime_str = dt.datetime.now().strftime('%d %b %Y %H:%M:%S')
        send_telegram_message("Bot finished with error: %s on %s" % (err, datetime_str))
        print("Chart Sniper finished with error: ", err)
        raise
