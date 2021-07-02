import logging
import sys
import signal
import time
import datetime as dt
from typing import final
import backtrader as bt

from pprint import pprint

from ccxtbt import CCXTStore, CCXTFeed
from config import BINANCE, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG
# from config import BITFINEX, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG
# from config import KRAKEN, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG
# from config import FTX, ENV, PRODUCTION, SANDBOX, COIN_TARGET, COIN_REFER, DEBUG

from utils import get_trade_analysis, get_sqn, send_telegram_message 

from strategies import StochMACD, TESTBUY
from Parser import parse_args
from Datasets import *

def main():
    cerebro = bt.Cerebro(quicknotify=True)
    # cerebro = bt.Cerebro()
    cerebro.broker.set_shortcash(False)

    leverage = 5

    cerebro.broker.setcommission(commission=0.00015, leverage=leverage)

    if ENV == PRODUCTION:  # Live trading with Binance
        broker_config = {
            # 'apiKey': FTX.get("key"),
            # 'secret': FTX.get("secret"),
            # 'apiKey': KRAKEN.get("key"),
            # 'secret': KRAKEN.get("secret"),
            # 'apiKey': BITFINEX.get("key"),
            # 'secret': BITFINEX.get("secret"),
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret"),
            'nonce': lambda: str(int(time.time() * 1000)),
            'enableRateLimit': True,
            # 'verbose': True,
        }

        store = CCXTStore(
            exchange='binanceusdm', 
            # exchange='bitfinex2', 
            # exchange='kraken', 
            # exchange='ftx', 
            # Must have that currency available in order to trade it
            currency=COIN_REFER, 
            #BitFinex. Might need to pull and edit to get the correct currency using fetchBalance(margin)
            # currency='TESTUSDT', 
            config=broker_config, 
            retries=5, 
            debug=DEBUG,
            # For Bitfinex
            # balance_type='derivatives',
            sandbox=SANDBOX
        )

        # print("exchange methods")
        # pprint(dir(store.exchange))

        symbol = f'{COIN_TARGET}/{COIN_REFER}'
        # symbol = 'BTC-PERP'
        market = store.exchange.market(symbol)
        # pprint(store.exchange.markets[symbol])

        # balance = store.exchange.fetch_balance({'type': 'margin'})
        # pprint(balance)

        dual_response = store.exchange.fapiPrivate_get_positionside_dual()
        if dual_response['dualSidePosition']:
            print('You are in Hedge Mode')
        else:
            print('You are in One-way Mode')
        
        # Set margin type
        # type_response = store.exchange.fapiPrivate_post_margintype ({
        #     'symbol': market['id'],
        #     'marginType': 'ISOLATED',
        # })
        # print(type_response)

        # Set leverage multiplier
        leverage_response = store.exchange.fapiPrivate_post_leverage({
            'symbol': market['id'],
            'leverage': leverage,
        })

        pprint(leverage_response)

        #Test get trades

        # print("GET Trades")
        # trades_response = store.exchange.fapiPrivate_get_usertrades ({
        #     'symbol': market['id'],
        #     'limit': 10,
        # })
        # pprint(trades_response)

        broker_mapping = {
            'order_types': {
                bt.Order.Market: 'market',
                bt.Order.Limit: 'limit',
                bt.Order.StopLimit: 'stop_market'
                # Bitfinex
                # bt.Order.Market: 'MARKET',
                # bt.Order.Limit: 'LIMIT',
                # bt.Order.StopLimit: 'STOP LIMIT'
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

        # hist_start_date = dt.datetime.utcnow() - dt.timedelta(hours=1000)
        hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=1000)
        data = store.getdata(
            dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
            name='%s%s' % (COIN_TARGET, COIN_REFER),
            timeframe=bt.TimeFrame.Minutes,
            fromdate=hist_start_date,
            # compression=60,
            # compression=1,
            # Max number of ticks before throttling occurs
            ohlcv_limit=999,
            # Prevents loading partial data from incomplete candles
            # drop_newest=True
        )

        # Add the feed
        cerebro.adddata(data)

    else:  # Backtesting with CSV file
        cerebro.broker.setcommission(commission=0.0002, leverage=5)

        dataname = DATASETS.get('btc_hourly')
        data = bt.feeds.GenericCSVData(
            dataname=dataname,
            fromdate=dt.datetime(2018,2,1),
            todate=dt.datetime(2021,6,9),
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
        broker = cerebro.getbroker()
        broker.setcash(5000.0)

    cashperc = 50

    # Analyzers to evaluate trades and strategies
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # Include Strategy
    # cerebro.addstrategy(
    #     StochMACD,
    #     macd1=9,
    #     macd2=21,
    #     macdsig=8,
    #     atrdist=5,
    #     reversal_sensitivity=17,
    #     rsi_upperband=45,
    #     rsi_lowerband=49,
    #     reversal_lowerband=43,
    #     reversal_upperband=48,
    #     cashperc=cashperc,
    #     leverage=leverage
    # )

    cerebro.addstrategy(TESTBUY,
                        cashperc=cashperc,
                        leverage=leverage)

    # Starting backtrader bot
    initial_value = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial_value)
    send_telegram_message("===== Chart Sniper initialized =====")
    result = cerebro.run()

    # Print analyzers - results
    final_value = cerebro.broker.getvalue()
    final_value_string = 'Final Portfolio Value: %.2f' % final_value
    profit_string = 'Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100)
    ta_string = get_trade_analysis(result[0].analyzers.ta.get_analysis())
    sqn_string = get_sqn(result[0].analyzers.sqn.get_analysis())

    logging.warning(final_value_string)
    logging.warning(profit_string)
    logging.warning(ta_string)
    logging.warning(sqn_string)

    if ENV == PRODUCTION:
        telegram_txt = f'{final_value_string}\n{profit_string}\n{ta_string}\n{sqn_string}'
        datetime_str = dt.datetime.now().strftime('%d %b %Y %H:%M:%S')
        print("Chart Sniper finished by user on %s" % datetime_str)
        send_telegram_message(telegram_txt)
        send_telegram_message("Bot finished by user on %s" % datetime_str)


    # if DEBUG:
    #     cerebro.plot()

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        datetime_str = dt.datetime.now().strftime('%d %b %Y %H:%M:%S')
        send_telegram_message("Bot finished with error: %s on %s" % (err, datetime_str))
        print("Chart Sniper finished with error: ", err)
        raise
