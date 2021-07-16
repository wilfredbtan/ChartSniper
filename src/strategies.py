import logging
import math
import signal
import collections
import bisect
import time
import backtrader as bt

from telegram import ParseMode
from datetime import timezone, datetime
from pprint import pprint
from termcolor import colored
from Indicators import StochasticRSI, MACD, MFI, CMF
from config import PRODUCTION, SANDBOX, ENV
from utils import send_telegram_message, get_formatted_datetime_str, get_trade_analysis
from CSVwriter import create_trades_csv, write_trade_to_csv

logger = logging.getLogger("chart_sniper")

class StrategyBase(bt.Strategy):

    params = (
        ("lp_buffer_mult", 50),
        ("leverage", 5),
        ('isWfa', False),
        ("should_save", False),
        ("filename", None),
        ("default_loglevel", logging.DEBUG)
    )

    def handle_sigint(self, sig, frame):
        print("SIGINT received")
        # self.close_and_cancel_stops()
        self.env.runstop()
    
    def handle_sigusr1(self, sig, frame):
        print("SIGUSR1 received")
        # Portfolio value
        # open positions (if any)
        # Trade analysis?
        value_string = f'Portfolio value: {self.broker.getvalue(): .2f}'
        position_string = f'Postion:\n  Size: {self.position.size: .3f}\n  Price: {self.position.price}'
        ta_string = get_trade_analysis(self.analyzers.ta.get_analysis())
        txt = f'```\n{value_string}\n\n{position_string}\n\n{ta_string}```'
        print(txt)
        if ENV == PRODUCTION:
            send_telegram_message(message=txt, parse_mode=ParseMode.MARKDOWN)

    def __init__(self):
        self.logger = logging.getLogger("chart_sniper")

        if self.p.should_save and self.p.filename is not None:
            self.csv_filename = f'{self.p.filename}.csv'
            create_trades_csv(self.csv_filename)

        signal.signal(signal.SIGINT, self.handle_sigint)
        signal.signal(signal.SIGUSR1, self.handle_sigusr1)

        self.order = None
        self.status = "DISCONNECTED"
        # self.logged_order_ids = set()
        self.stop_orders = {}
        self.trade_sizes = {}

        self.last_buy_cost = None
        self.last_sell_cost = None

        # Retrieved on 25 Jun 2021 from https://www.binance.com/en/support/faq/b3c689c1f50a44cabb3a84e663b81d93 and https://www.binance.com/en/support/faq/360033162192
        self.tier_dict = collections.OrderedDict()
        self.tier_dict[50000] = (0.004, 0)
        self.tier_dict[250000] = (0.005, 50)
        self.tier_dict[1000000] = (0.01, 1300)
        self.tier_dict[5000000] = (0.025, 16300)
        self.tier_dict[20000000] = (0.05, 141300)
        self.tier_dict[50000000] = (0.1, 1141300)
        self.tier_dict[100000000] = (0.125, 2391300)
        self.tier_dict[200000000] = (0.15, 4891300)
        self.tier_dict[300000000] = (0.25, 24891300)
        self.tier_dict[500000000] = (0.5, 0)

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        logger.info(f"STATUS: {self.status}")
        if status == "LIVE":
            self.log("LIVE DATA - Ready to trade")
        
    def notify_order(self, order):
        # print("self")
        # s = dir(self)
        # pprint(s)

        # print("order")
        # print(order)
        # l = dir(order)
        # pprint(l)
        # print("order info")
        # pprint(order.info)

        # print("order info name")
        # pprint(order.info.name)
        # print("ccxt_order")
        # pprint(order.ccxt_order)

        close = self.dataclose[0]

        if order.status in [order.Submitted, order.Accepted]:
            return

        order_name = order.info.name

        if order.status in [order.Completed]:
            # if 'STOPLOSS' in order_name:
            #     txt = colored("====== STOPLOSS executed ======", 'red')
            #     print(txt)
            if 'STOPLOSS' in order_name and order.ref in self.stop_orders:
                # pprint(order.info)
                if order.info.is_liquidable:
                    txt = "============== LIQUIDABLE stoploss executed!!!! =============="
                    logger.warning(txt)
                del self.stop_orders[order.ref]

            if ENV == PRODUCTION:
                datetime_int = int(order.ccxt_order["timestamp"])
                datetime_int = datetime_int/1000 if datetime_int > 10000000000 else datetime_int
                datetime_str = get_formatted_datetime_str(datetime_int, format='%d %b %Y %H:%M:%S')

                order_id = order.ccxt_order["id"]
                order_cost = order.ccxt_order["cost"]

                # print("order ids: ", self.logged_order_ids)
                # if order_id in self.logged_order_ids:
                #     print("remove id: ", order_id)
                #     self.logged_order_ids.remove(order_id)
                #     return
                # else:
                #     print("add id: ", order_id)
                #     self.logged_order_ids.add(order_id)
                
                # BINANCE
                if order.ccxt_order["info"]["status"] == 'FILLED':
                # BITFINEX
                # if order.ccxt_order["filled"] == order.ccxt_order['amount']:
                    if order.isbuy():
                        self.log(
                            'BUY EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Date: %s' %
                            (order_name,
                            order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order_cost,
                            datetime_str),
                            send_telegram=True)
                            # No commission (fee) data available as at 12 June 2021
                        # print("BUY order id: ", order_id)
                        # if order_name == "CLOSE":
                        #     pnl = self.last_sell_cost - order_cost  
                        #     # print("===== NOTIFY_ORDER pnl")
                        #     self.log_profit(pnl)
                        #     # print("buy close broker cash")
                        #     # print("cerebro cash", self.broker.cash)
                        # else:
                        #     print("========= last_buy_cost", order_cost)
                        #     self.last_buy_cost = order_cost
                        
                        if order.info.should_stop:
                            self.submit_stop_for_buy(
                                price=order.ccxt_order["average"],
                                size=order.ccxt_order["amount"]
                            )
                    else:
                        self.log(
                            'SELL EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Date: %s' %
                            (order_name,
                            -order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order.ccxt_order["cost"],
                            datetime_str),
                            send_telegram=True)
                            # No commission (fee) data available as at 12 June 2021
                        # print("SELL order id: ", order_id)
                        # if order_name == "CLOSE":
                        #     pnl = order_cost - self.last_buy_cost
                        #     # print("===== NOTIFY_ORDER pnl")
                        #     self.log_profit(pnl)
                        #     # print("sell close broker cash")
                        #     # print("cerebro cash", self.broker.cash)
                        # else:
                        #     print("======= last_sell_cost", order_cost)
                        #     self.last_sell_cost = order_cost 

                        if order.info.should_stop:
                            self.submit_stop_for_sell(
                                price=order.ccxt_order["average"],
                                size=order.ccxt_order["amount"]
                            )
            else:
                if order.isbuy():
                    self.log('BUY EXECUTED: %s, Amount: %.2f, Price: %.4f, Cost: %.4f, Comm %.2f' %
                             (order_name,
                              order.executed.size,
                              order.executed.price,
                              order.executed.value,
                              order.executed.comm))

                    if order.info.should_stop:
                        self.submit_stop_for_buy(
                            price=order.executed.price,
                            size=order.executed.size
                        )
                else:  # Sell
                    self.log('SELL EXECUTED: %s, Amount: %.2f, Price: %.5f, Cost: %.5f, Comm %.5f' %
                             (order_name,
                              order.executed.size,
                              order.executed.price,
                              order.executed.value,
                              order.executed.comm))

                    if order.info.should_stop:
                        self.submit_stop_for_sell(
                            price=order.executed.price,
                            size=order.executed.size
                        )
                
        elif order.status in [order.Canceled]:
            self.log('Order Canceled: %s' % order_name, send_telegram=True)
        elif order.status in [order.Margin]:
            self.log('Order Margin: %s' % order_name, level=logging.WARNING, send_telegram=True)
        elif order.status in [order.Rejected]:
            self.log('Order Rejected: %s' % order_name, level=logging.WARNING, send_telegram=True)


    '''
    Trade structure:
        ref:28
        data:<backtrader.feeds.csvgeneric.GenericCSVData object at 0x12182beb0>
        tradeid:0
        size:0.0
        price:6309.0
        value:0.0
        commission:88.03578379161002
        pnl:2210.5608340882
        pnlcomm:2122.52505029659
        justopened:False
        isopen:False
        isclosed:True
        libaropen:6063
        dtopen:736978.5833333334
        barclose:6755
        dtclose:737007.4166666666
        barlen:692
        historyon:False
        history:[]
        status:2
    '''
    def notify_trade(self, trade):
        if not trade.isclosed:
            # Store size to refer to it when trade is closed
            if trade.ref in self.trade_sizes:
                self.trade_sizes[trade.ref] += trade.size
            else:
                self.trade_sizes[trade.ref] = trade.size
            return

        dtopen_float = trade.dtopen
        dtclose_float = trade.dtclose
        dtopen_str = trade.open_datetime().strftime('%Y-%m-%d %H:%M:%S')
        dtclose_str = trade.close_datetime().strftime('%Y-%m-%d %H:%M:%S')
        size = self.trade_sizes[trade.ref]
        pnl = trade.pnl
        pnlcomm = trade.pnlcomm
        avg_open_price = trade.price
        avg_close_price = (avg_open_price + pnl / size)
        trade_data = [dtopen_float, dtclose_float, dtopen_str, dtclose_str, size, avg_open_price, avg_close_price, pnl, pnlcomm]

        if self.p.should_save and self.p.filename is not None:
            write_trade_to_csv(filename=self.csv_filename, trade_data=trade_data)

        self.log_profit(pnl, pnlcomm)

        del self.trade_sizes[trade.ref]

    def get_maintenance_margin_rate_and_amt(self, notional_value):
        '''
        Returns the (maintenance_margin_rate, maintenance_margin_amount) for the corresponding notional value
        '''
        ind = bisect.bisect_left(list(self.tier_dict.keys()), notional_value)
        return list(self.tier_dict.values())[ind]
    
    # Calculation: https://www.binance.com/en/support/faq/b3c689c1f50a44cabb3a84e663b81d93
    def get_liquidation_price(self, side, pos_size, entry_price):
        pos_size = abs(pos_size)
        (mmr, mma) = self.get_maintenance_margin_rate_and_amt(notional_value=pos_size * entry_price)
        # print("side: ", side)
        # print("pos_size: ", pos_size)
        # print("entry price: ", entry_price)
        # print("Margin rate: ", mmr)
        # print("Margin amount: ", mma)
        # Wallet balance
        # Get value instead of cash as positions will only be reversed
        # wb = self.broker.cash
        wb = self.broker.getvalue()
        # Total maintenance margin. =0 if in isolated mode
        tmm = 0
        # Unrealized PNL of all other contracts. =0 if in isolated mode
        upnl = 0
        # Maintenance amount of BOTH position (one-way mode)
        cum_B = mma
        # Maintenance amount of LONG position (hedge mode)
        cum_L = 0
        # Maintenance amount of SHORT position (hedge mode)
        cum_S = 0
        # Direction of BOTH position, 1 as long position, -1 as short position
        side_BOTH = side
        # Absolute value of BOTH position size (one-way mode)
        pos_BOTH = pos_size
        # Entry price of BOTH position size (one-way mode)
        ep_BOTH = entry_price
        # Absolute value of LONG position size (hedge mode)
        pos_LONG = 0
        # Entry price of LONG position size (hedge mode)
        ep_LONG = 0
        # Absolute value of SHORT position size (hedge mode)
        pos_SHORT = 0
        # Entry price of SHORT position size (hedge mode)
        ep_SHORT = 0
        # Maintenance margin rate of BOTH position (one-way mode)
        mmr_B = mmr
        # Maintenance margin rate of LONG position (hedge mode)
        mmr_L = 0
        # Maintenance margin rate of SHORT position (hedge mode)
        mmr_S = 0

        # Liquidation price
        num = (wb - tmm + upnl + cum_B + cum_L + cum_S - side_BOTH * pos_BOTH * ep_BOTH - pos_LONG * ep_LONG + pos_SHORT * ep_SHORT) 
        den = (pos_BOTH * mmr_B + pos_LONG * mmr_L + pos_SHORT * mmr_S - side_BOTH * pos_BOTH - pos_LONG + pos_SHORT)

        lp = num / den

        return lp

    def close_and_cancel_stops(self):
        close_order = self.close()
        if close_order:
            close_order.addinfo(name="CLOSE")
        if len(self.stop_orders) > 0:
            # if len(self.stop_orders) > 1:
            #     print("====== STOPORDER > 1: ", self.stop_orders)
            for oref in self.stop_orders.keys():
                # print("-- remove ref: ", oref)
                self.cancel(self.stop_orders[oref])
            # print("Number of stop orders: ", len(self.stop_orders))
            self.stop_orders = {}
    
    def sell_with_stop_loss(self, price, size=None, multiplier=1, **kwargs):
        # sell_order = self.sell(size=size, transmit=False, kwargs=kwargs)
        sell_order = self.sell(size=size, kwargs=kwargs)
        sell_order.addinfo(name="ENTRY SHORT Order")
        sell_order.addinfo(should_stop=True)
        # self.submit_stop_for_sell(price, size=sell_order.size, parent=sell_order)

    def submit_stop_for_sell(self, price, size, parent=None):
        atrdist = self.params_to_use['atrdist'] if self.p.isWfa else self.p.atrdist
        stop_price = price + atrdist * self.atr[0]

        lp = self.get_liquidation_price(side=-1, pos_size=size, entry_price=price)
        lp_with_buffer = lp - self.atr[0] * self.p.lp_buffer_mult
        is_liquidable = lp_with_buffer < stop_price
        stop_price = min(stop_price, lp_with_buffer)

        if (stop_price <= price):
            # print(colored("ILLEGAL SELL STOP. stop price lower than close", 'red'))
            if (lp <= price):
                print(colored("==== ILLEGAL SELL LP, must be below close", 'magenta'))
            stop_price = lp

        stop_order = self.buy(
            exectype=bt.Order.StopLimit, 
            size=size, 
            price=stop_price, 
            stopPrice=stop_price,
            # parent=parent, 
            # transmit=True,
            #Binance
            reduceOnly='true'
        )

        stop_order.addinfo(name="STOPLOSS for SHORT")
        stop_order.addinfo(is_liquidable=is_liquidable)
        self.stop_orders[stop_order.ref] = stop_order

        self.log(f'stop submitted for SELL, Amount: {size:.2f} Price: {stop_price: .4f}')

        
    def buy_with_stop_loss(self, price, size=None, multiplier=1, **kwargs):
        # buy_order = self.buy(size=size, transmit=False, kwargs=kwargs)
        buy_order = self.buy(size=size, kwargs=kwargs)
        # Kwargs do not work in bt-ccxt
        buy_order.addinfo(name="ENTRY LONG Order")
        buy_order.addinfo(should_stop=True)
        # self.submit_stop_for_buy(price, size=buy_order.size, parent=buy_order)

    def submit_stop_for_buy(self, price, size, parent=None):
        atrdist = self.params_to_use['atrdist'] if self.p.isWfa else self.p.atrdist
        stop_price = price - atrdist * self.atr[0]

        lp = self.get_liquidation_price(side=1, pos_size=size, entry_price=price)
        # Liquidation price cannot be less than 0 for long
        lp = max(lp, 0)
        lp_with_buffer = lp + self.atr[0] * self.p.lp_buffer_mult
        is_liquidable = lp_with_buffer > stop_price
        stop_price = max(stop_price, lp_with_buffer)

        if (stop_price >= price):
            # print(colored("ILLEGAL BUY STOP. stop price higher than close", 'red'))
            if (lp >= price):
                print(colored("==== ILLEGAL BUY LP, must be below close", 'magenta'))
            stop_price = lp

        stop_order = self.sell(
            exectype=bt.Order.StopLimit,
            size=size,
            price=stop_price,
            stopPrice=stop_price,
            # parent=parent,
            # transmit=True,
            #Binance
            reduceOnly='true'
        )
        # Kwargs do not work in bt-ccxt
        stop_order.addinfo(name="STOPLOSS for LONG")
        stop_order.addinfo(is_liquidable=is_liquidable)
        self.stop_orders[stop_order.ref] = stop_order

        self.log(f'stop submitted for BUY, Amount: {size:.2f} Price: {stop_price: .4f}')

    # def log(self, txt, level=logging.DEBUG, send_telegram=False, color=None, dt=None):
    def log(self, txt, level=None, send_telegram=False, color=None, dt=None):
        level = self.p.default_loglevel if level is None else level
        log_txt = txt
        if color:
            log_txt = colored(txt, color)

        dt = dt or self.datas[0].datetime.date(0)
        hh = self.datas[0].datetime.time()

        self.logger.log(level, '%s %s, %s' % (dt.isoformat(), hh, log_txt))

        if send_telegram and ENV == PRODUCTION:
            telegram_txt = txt.replace(', ', '\n')
            # print("Telegram text: ", telegram_txt)
            send_telegram_message(telegram_txt, parse_mode=ParseMode.MARKDOWN)
    
    def log_profit(self, pnl, pnlcomm=None):
        color = 'red' if pnl < 0 else 'green'
        txt = 'OPERATION PROFIT: GROSS %.2f' % pnl

        if pnlcomm:
            color = 'red' if pnlcomm < 0 else 'green'
            txt += ' ; NET %.2f' % pnlcomm
        
        value = self.broker.getvalue()
        txt += f'\nPORTFOLIO VALUE: {value: .2f}'

        txt = f'*{txt}*'

        self.log(txt, send_telegram=True, color=color)


class TESTBUY(StrategyBase):
    # list of parameters which are configurable for the strategy
    lines = ('stochrsi','rsi')

    params = (
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        
        ('stoch_k_period', 3),
        ('stoch_d_period', 3),
        ('stoch_rsi_period', 14),
        ('stoch_period', 14),
        ('stoch_upperband', 80.0),
        ('stoch_lowerband', 20.0),
        
        ('rsi_upperband', 60.0),
        ('rsi_lowerband', 40.0),
        
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 5),   # ATR distance for stop price

        ('reversal_sensitivity', 20),
    )

    def __init__(self):
        StrategyBase.__init__(self)

        self.dataclose = self.datas[0].close

        if ENV == PRODUCTION:
            activation_txt = "== TESTBUY strategy activated =="
            logger.info(activation_txt)
            send_telegram_message(activation_txt)

        self.bought_once = False
        self.sold_once = False

        if SANDBOX != True:
            logger.warning("Using a test strategy in production")
            raise
    
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        self.stochrsi = StochasticRSI(k_period=self.p.stoch_k_period,
                                   d_period=self.p.stoch_d_period,
                                   rsi_period=self.p.stoch_rsi_period,
                                   stoch_period=self.p.stoch_period,
                                   upperband=self.p.stoch_upperband,
                                   lowerband=self.p.stoch_lowerband)

    def next(self):
        close = self.datas[0].close
        # print("d0 OHLC: ", self.datas[0].datetime.datetime(), self.datas[0].open[0], self.datas[0].high[0], self.datas[0].low[0], self.datas[0].close[0])

        if ENV == PRODUCTION and self.status != "LIVE":
            return

        print("LIVE NEXT")

        if self.position.size < 0:
            self.log("buy in testbuy", color='yellow')
            self.close_and_cancel_stops()
            self.buy_with_stop_loss(close)

            # Bitfinex derivative market buy
            # self.buy_stop_loss(close, type="MARKET", lev=self.p.leverage)
            # self.buy(type='MARKET', lev=self.p.leverage)
            # Btifnex V1
            # self.buy(type='market', lev=str(self.p.leverage))
        elif self.position.size > 0:
            self.log("sell in testbuy", color='yellow')
            self.close_and_cancel_stops()
            self.sell_with_stop_loss(close)

            # Bitfinex derivative market sell
            # self.sell_stop_loss(close, type="MARKET", lev=self.p.leverage)
            # self.sell(type='MARKET', lev=self.p.leverage)

            # Btifnex V1
            # self.sell(type='market', lev=str(self.p.leverage))
        else:
            self.log("STARTING in testbuy", color='yellow')
            self.buy_with_stop_loss(close)

            # Bitfinex derivative market buy
            # self.buy_stop_loss(close, type="MARKET", lev=self.p.leverage)
            # self.buy(type='MARKET', lev=self.p.leverage)

            # Btifnex V1
            # self.buy(type='market', lev=str(self.p.leverage))

class StochMACD(StrategyBase):
    # list of parameters which are configurable for the strategy
    lines = ('stochrsi','rsi')

    params = (
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        
        ('stoch_k_period', 3),
        ('stoch_d_period', 3),
        ('stoch_rsi_period', 14),
        ('stoch_period', 14),
        ('stoch_upperband', 80.0),
        ('stoch_lowerband', 20.0),
        
        ('rsi_upperband', 70.0),
        ('rsi_lowerband', 30.0),

        ('mfi_upperband', 80.0),
        ('mfi_lowerband', 20.0),

        ('cmf_period', 20),
        ('cmf_upperband', 0.2),
        ('cmf_lowerband', -0.2),
        
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 5),   # ATR distance for stop price

        ('reversal_sensitivity', 20),
        ('reversal_lowerband', 50),
        ('reversal_upperband', 50),
    )

    def __init__(self):
        StrategyBase.__init__(self)

        if ENV == PRODUCTION:
            activation_txt = "== StochMACD strategy activated =="
            logger.info(activation_txt)
            send_telegram_message(activation_txt)

        self.dataclose = self.datas[0].close
        
        self.stop_order = None
        
        self.macd = MACD(
            self.datas[0],
            period_me1=self.p.macd1,
            period_me2=self.p.macd2,
            period_signal=self.p.macdsig
        )

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.mcross.plotinfo.plot = False

        self.rsi = bt.ind.RSI(self.datas[0], period=self.p.stoch_rsi_period, safediv=True)
        
        self.atr = bt.indicators.ATR(self.datas[0], period=self.p.atrperiod)
        self.atr.plotinfo.plot = False

        self.stochrsi = StochasticRSI(
            self.datas[0],
            k_period=self.p.stoch_k_period,
            d_period=self.p.stoch_d_period,
            rsi_period=self.p.stoch_rsi_period,
            stoch_period=self.p.stoch_period,
            upperband=self.p.stoch_upperband,
            lowerband=self.p.stoch_lowerband,
        )
        self.stochrsi.plotinfo.plot = False

        if len(self.datas) > 1:
            self.alt_stochrsi = StochasticRSI(
                self.datas[1],
                k_period=self.p.stoch_k_period,
                d_period=self.p.stoch_d_period,
                rsi_period=self.p.stoch_rsi_period,
                stoch_period=self.p.stoch_period,
                upperband=self.p.stoch_upperband,
                lowerband=self.p.stoch_lowerband
            )
            self.alt_stochrsi.plotinfo.plot = False


        # self.mfi = MFI(self.datas[1], period=self.p.stoch_rsi_period)
        # self.cmf = CMF(self.datas[1], period=self.p.cmf_period)

    def next(self):        
        close = self.dataclose[0]
        currentStochRSI = self.stochrsi.l.fastk[0]

        # print("===== Values: =====")
        # dt0 = self.datas[0].datetime.datetime()
        # print("d0", dt0)
        # dt1 = self.datas[1].datetime.datetime()
        # print("d1", dt1)

        # print("d0 OHLC: ", self.datas[0].datetime.datetime(), self.datas[0].open[0], self.datas[0].high[0], self.datas[0].low[0], self.datas[0].close[0])
        # print("d1 OHLC: ", self.datas[1].datetime.datetime(), self.datas[1].open[0], self.datas[1].high[0], self.datas[1].low[0], self.datas[1].close[0])
        # print("")

        if len(self.datas) > 1:
            time_str = self.datas[1].datetime.time().strftime('%H:%M:%S')
            # print(time_str)
            minutes = int(time_str.split(':')[1])
            # print("minutes: ", minutes)
            # print(f"datetime: {dt}")
            if minutes != 0:
                return

        # print("is hourly")
        # dt = self.datas[1].datetime.date(0)
        # hh = self.datas[1].datetime.time()
        # print(f"datetime: {dt} {hh}")

        if ENV == PRODUCTION and self.status != "LIVE":
            return

        sizer_multiplier = 1

        lowerband_count = -4
        # lowerband_count = -2
        did_stochrsi_crossup = True
        while lowerband_count <= 0:
            if lowerband_count == 0:
                did_stochrsi_crossup = did_stochrsi_crossup and self.stochrsi.l.fastk[lowerband_count] >= self.p.stoch_lowerband
            else:
                did_stochrsi_crossup = did_stochrsi_crossup and self.stochrsi.l.fastk[lowerband_count] < self.p.stoch_lowerband
            lowerband_count += 1

        upperband_count = -4
        # upperband_count = -2
        did_stochrsi_crossdown = True
        while upperband_count <= 0:
            if upperband_count == 0:
                did_stochrsi_crossdown = did_stochrsi_crossdown and self.stochrsi.l.fastk[upperband_count] <= self.p.stoch_upperband
            else:
                did_stochrsi_crossdown = did_stochrsi_crossdown and self.stochrsi.l.fastk[upperband_count] > self.p.stoch_upperband
            upperband_count += 1

        # rsi_should_buy = self.rsi[0] > 50 or self.rsi[-1] > 50
        # rsi_should_sell = self.rsi[0] < 50 or self.rsi[-1] < 50
        rsi_should_buy = self.rsi[0] < self.p.rsi_upperband or self.rsi[-1] < self.p.rsi_upperband
        rsi_should_sell = self.rsi[0] > self.p.rsi_lowerband or self.rsi[-1] > self.p.rsi_lowerband

        # mfi_should_buy = self.mfi[0] < self.p.mfi_lowerband or self.mfi[-1] < self.p.mfi_lowerband
        # mfi_should_sell = self.mfi[0] > self.p.mfi_upperband or self.mfi[-1] < self.p.mfi_upperband
        # mfi_should_buy = self.mfi[0] < self.p.mfi_lowerband
        # mfi_should_sell = self.mfi[0] > self.p.mfi_upperband

        # cmf_should_buy = self.cmf[0] < self.p.cmf_lowerband or self.cmf[-1] < self.p.cmf_lowerband
        # cmf_should_sell = self.cmf[0] > self.p.cmf_upperband or self.cmf[-1] < self.p.cmf_upperband
        # cmf_should_buy = self.cmf[0] < self.p.cmf_lowerband / 100
        # cmf_should_sell = self.cmf[0] > self.p.cmf_upperband / 100

        # cmf_should_buy = self.cmf[0] < self.p.cmf_lowerband
        # cmf_should_sell = self.cmf[0] > self.p.cmf_upperband

        should_buy = (
            (self.mcross[0] > 0 or self.mcross[-1] > 0) and
            rsi_should_buy and
            # cmf_should_buy and
            # mfi_should_buy and
            did_stochrsi_crossup
        )
        
        should_sell = (
            (self.mcross[0] < 0 or self.mcross[-1] < 0) and
            rsi_should_sell and
            # cmf_should_sell and
            # mfi_should_sell and
            did_stochrsi_crossdown
        )

        if len(self.datas) > 1:
            alt_should_sell = (
                self.alt_stochrsi.l.fastk[-1] > self.alt_stochrsi.l.fastd[-1] and
                (self.alt_stochrsi.l.fastk[0] - self.alt_stochrsi.l.fastd[0]) <= 0
            )

            alt_should_buy = (
                self.alt_stochrsi.l.fastk[-1] < self.alt_stochrsi.l.fastd[-1] and
                (self.alt_stochrsi.l.fastk[0] - self.alt_stochrsi.l.fastd[0]) >= 0
            )

            # Higher chance of liquidation
            # if alt_should_sell and should_sell:
            #     # txt = colored("+++++++++++++ ALT SHOULD SELL AS WELL", 'magenta')
            #     # print(txt)
            #     sizer_multiplier *= 1.1

            # if alt_should_buy and should_buy:
            #     # txt = colored("+++++++++++++ ALT SHOULD BUY AS WELL", 'magenta')
            #     # print(txt)
            #     sizer_multiplier *= 1.1

        reversal_sensitivity = self.p.reversal_sensitivity

        # Need to sell
        if self.position.size > 0:
            within_upperrange = currentStochRSI > self.p.reversal_upperband and currentStochRSI < self.p.stoch_upperband
            did_reverse = (
                self.stochrsi.l.fastk[-2] > self.stochrsi.l.fastd[-2] and
                self.stochrsi.l.fastk[-1] > self.stochrsi.l.fastd[-1] and
                (self.stochrsi.l.fastk[0] - self.stochrsi.l.fastd[0]) <= -reversal_sensitivity
            )

            if within_upperrange:
                # If fast crosses slow downwards, trend reversal, sell
                if did_reverse:
                    self.close_and_cancel_stops()
                    self.log('INTERIM REVERSAL SELL, %.2f' % self.dataclose[0])
                    self.sell_with_stop_loss(price=close, multiplier=sizer_multiplier)   
            
            if should_sell:
                if not within_upperrange:
                    self.close_and_cancel_stops()
                self.log('REVERSAL SELL, %.2f' % self.dataclose[0])
                self.sell_with_stop_loss(price=close, multiplier=sizer_multiplier)
               
        # Need to buy
        elif self.position.size < 0:
            within_lowerrange = currentStochRSI > self.p.stoch_lowerband and currentStochRSI < self.p.reversal_lowerband
            did_reverse = (
                self.stochrsi.l.fastk[-2] < self.stochrsi.l.fastd[-2] and
                self.stochrsi.l.fastk[-1] < self.stochrsi.l.fastd[-1] and
                (self.stochrsi.l.fastk[0] - self.stochrsi.l.fastd[0]) >= reversal_sensitivity
            )

            if within_lowerrange:
                # If fast crosses slow upwards, trend reversal, buy
                if did_reverse:
                    self.close_and_cancel_stops()
                    self.log('INTERIM REVERSAL BUY, %.2f' % self.dataclose[0])
                    self.buy_with_stop_loss(price=close, multiplier=sizer_multiplier)
                    
            if should_buy:
                if not within_lowerrange:
                    self.close_and_cancel_stops()
                self.log('REVERSAL BUY, %.2f' % self.dataclose[0])
                self.buy_with_stop_loss(price=close, multiplier=sizer_multiplier)
                
        # if self.position.size == 0:
        else:
            if should_buy:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy_with_stop_loss(close, multiplier=sizer_multiplier)

            elif should_sell:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.sell_with_stop_loss(close, multiplier=sizer_multiplier)


class WfaStochMACD(StrategyBase):
    # list of parameters which are configurable for the strategy
    lines = ('stochrsi','rsi')

    dynamic_params = (
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
        
        ('stoch_k_period', 3),
        ('stoch_d_period', 3),
        ('stoch_rsi_period', 14),
        ('stoch_period', 14),
        ('stoch_upperband', 80.0),
        ('stoch_lowerband', 20.0),
        
        ('rsi_upperband', 60.0),
        ('rsi_lowerband', 40.0),
        
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 5),   # ATR distance for stop price

        ('reversal_sensitivity', 20),
    )

    params = (
        ('interval_params', [(999999999999999.0, dynamic_params)]),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.dataclose = self.datas[0].close
        
        self.interval_index = 0
        self.sorted_params = sorted(self.params.interval_params)
        # print("sorted: ", self.sorted_params)
        self.params_to_use = self.sorted_params[self.interval_index][1]
        # print("to use: ", self.params_to_use)
        self.p.isWfa = True

        self.stop_order = None
        
        self.macd = MACD(self.datas[0],
                         period_me1=self.params_to_use['macd1'],
                         period_me2=self.params_to_use['macd2'],
                         period_signal=self.params_to_use['macdsig'])

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
        self.atr = bt.indicators.ATR(self.datas[0], period=self.params_to_use['atrperiod'])

        self.rsi = bt.ind.RSI(self.datas[0], period=self.params_to_use['stoch_rsi_period'], safediv=True)

        self.stochrsi = StochasticRSI(
            self.datas[0],
            k_period=self.params_to_use['stoch_k_period'],
            d_period=self.params_to_use['stoch_d_period'],
            rsi_period=self.params_to_use['stoch_rsi_period'],
            stoch_period=self.params_to_use['stoch_period'],
            upperband=self.params_to_use['stoch_upperband'],
            lowerband=self.params_to_use['stoch_lowerband']
        )

        if len(self.datas) > 1:
            self.alt_stochrsi = StochasticRSI(
                self.datas[1],
                k_period=self.params_to_use['stoch_k_period'],
                d_period=self.params_to_use['stoch_d_period'],
                rsi_period=self.params_to_use['stoch_rsi_period'],
                stoch_period=self.params_to_use['stoch_period'],
                upperband=self.params_to_use['stoch_upperband'],
                lowerband=self.params_to_use['stoch_lowerband']
            )
        

    def get_params_for_time(self):
        dd = self.datas[0].datetime.date(0)
        hh = self.datas[0].datetime.time()
        # print(f'get params for datetime:')
        # print('%s %s' % (dd.isoformat(), hh))
        # print("interval date: ", self.sorted_params[self.interval_index][0])
        # print("converted interval date: ", self.sorted_params[self.interval_index][0].replace(tzinfo=timezone.utc).timestamp())
        time_now_string = f'{dd} {hh}'
        # print("time_now_string", time_now_string)
        time_now = time.mktime(time.strptime(time_now_string, "%Y-%m-%d %H:%M:%S"))
        interval_unix_time = self.sorted_params[self.interval_index][0].replace(tzinfo=timezone.utc).timestamp()
        if (interval_unix_time < time_now):
            print("time now string: ", time_now_string)
            print("time now: ", time_now)
            print("interval dt", self.sorted_params[self.interval_index][0])
            print("interval unix: ", interval_unix_time)
            self.interval_index += 1
            print(f"interval index: {self.interval_index}")
            self.log(f'Params changed to: {self.sorted_params[self.interval_index][1]}', level=logging.WARNING)
        return self.sorted_params[self.interval_index][1]

    def next(self):        

        self.params_to_use = self.get_params_for_time()
        close = self.dataclose[0]
        currentStochRSI = self.stochrsi.l.fastk[0]

        if len(self.datas) > 1:
            time_str = self.datas[1].datetime.time().strftime('%H:%M:%S')
            # print(time_str)
            minutes = int(time_str.split(':')[1])
            # print("minutes: ", minutes)
            # print(f"datetime: {dt}")
            if minutes != 0:
                return

        # if self.status == "LIVE":
        # print("===== Values: =====")
        # dt = self.datas[0].datetime.date(0)
        # hh = self.datas[0].datetime.time()
        # print(f"datetime: {dt} {hh}")
        # print("self.macd[0]                ", self.macd[0])
        # print("self.mcross[0]              ", self.mcross[0])
        # print("self.stochrsi.l.fastk[-3]   ", self.stochrsi.l.fastk[-3])
        # print("self.stochrsi.l.fastk[-2]   ", self.stochrsi.l.fastk[-2])
        # print("self.stochrsi.l.fastk[-1]   ", self.stochrsi.l.fastk[-1])
        # print("self.stochrsi.l.fastk[0]    ", self.stochrsi.l.fastk[0])
        # print("")

        '''
        uptrend = MACD > 0
        - If in uptrend, don’t reverse a buy to a short. Just close
        - If in downtrend, don’t reverse a short to a bit. Just close
        '''

        # print("Should buy:")
        # print("self.mcross[0] > 0.0", self.mcross[0] > 0.0)
        # print("self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband", self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband)
        # print("")

        # print("Should sell:")
        # print("self.mcross[0] < 0.0", self.mcross[0] < 0.0)
        # print("self.stochrsi.l.fastk[-3] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-3] > self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-2] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-2] > self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-1] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-1] > self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[0] <= self.p.stoch_lowerband", self.stochrsi.l.fastk[0] <= self.p.stoch_lowerband)
        # print("")

        if ENV == PRODUCTION and self.status != "LIVE":
            return

        sizer_multiplier = 1

        # macd_should_sell = (self.mcross[0] < 0.0 or 
        #     (self.macd[-1] > 0 and self.macd[0] <= 0) or
        #     (self.macd[-2] > 0 and self.macd[-1] <= 0))

        # macd_should_buy = (self.mcross[0] > 0.0 or 
        #     (self.macd[-1] < 0 and self.macd[0] >= 0) or
        #     (self.macd[-2] < 0 and self.macd[-1] >= 0))

        lowerband_count = -4
        did_stochrsi_crossup = True
        while lowerband_count <= 0:
            if lowerband_count == 0:
                did_stochrsi_crossup = did_stochrsi_crossup and self.stochrsi.l.fastk[lowerband_count] >= self.params_to_use['stoch_lowerband']
            else:
                did_stochrsi_crossup = did_stochrsi_crossup and self.stochrsi.l.fastk[lowerband_count] < self.params_to_use['stoch_lowerband']
            lowerband_count += 1

        upperband_count = -4
        did_stochrsi_crossdown = True
        while upperband_count <= 0:
            if upperband_count == 0:
                did_stochrsi_crossdown = did_stochrsi_crossdown and self.stochrsi.l.fastk[upperband_count] <= self.params_to_use['stoch_upperband']
            else:
                did_stochrsi_crossdown = did_stochrsi_crossdown and self.stochrsi.l.fastk[upperband_count] > self.params_to_use['stoch_upperband']
            upperband_count += 1

        rsi_should_buy = self.rsi[0] < 50 or self.rsi[-1] < 50
        rsi_should_sell = self.rsi[0] > 50 or self.rsi[-1] > 50

        should_buy = (
            (self.mcross[0] > 0 or self.mcross[-1] > 0) and
            rsi_should_buy and
            did_stochrsi_crossup
        )
        
        should_sell = (
            (self.mcross[0] < 0 or self.mcross[-1] < 0) and
            rsi_should_sell and
            did_stochrsi_crossdown
        )

        if len(self.datas) > 1:
            alt_should_sell = (
                self.alt_stochrsi.l.fastk[-1] > self.alt_stochrsi.l.fastd[-1] and
                (self.alt_stochrsi.l.fastk[0] - self.alt_stochrsi.l.fastd[0]) <= 0
            )

            alt_should_buy = (
                self.alt_stochrsi.l.fastk[-1] < self.alt_stochrsi.l.fastd[-1] and
                (self.alt_stochrsi.l.fastk[0] - self.alt_stochrsi.l.fastd[0]) >= 0
            )

            # Higher chance of liquidation
            if alt_should_sell and should_sell:
                # txt = colored("+++++++++++++ ALT SHOULD SELL AS WELL", 'magenta')
                # print(txt)
                sizer_multiplier *= 1.1

            if alt_should_buy and should_buy:
                # txt = colored("+++++++++++++ ALT SHOULD BUY AS WELL", 'magenta')
                # print(txt)
                sizer_multiplier *= 1.1
        
        reversal_sensitivity = self.params_to_use['reversal_sensitivity']
        should_stop_loss = True
        should_trade_on_reversal = True
        should_close_on_reversal = True
        
        # Need to sell
        if self.position.size > 0:
            if should_close_on_reversal:
                if currentStochRSI > self.params_to_use['reversal_upperband'] and currentStochRSI < self.params_to_use['stoch_upperband']:
                    # If fast crosses slow downwards, trend reversal, sell
                    if (
                        self.stochrsi.l.fastk[-2] > self.stochrsi.l.fastd[-2] and
                        self.stochrsi.l.fastk[-1] > self.stochrsi.l.fastd[-1] and
                        (self.stochrsi.l.fastk[0] - self.stochrsi.l.fastd[0]) <= -reversal_sensitivity
                        # and (rsi_should_buy)
                        ):

                        self.log('INTERIM REVERSAL SELL, %.2f' % self.dataclose[0])
                        self.close_and_cancel_stops()
                        if should_trade_on_reversal:
                            if should_stop_loss:
                                self.sell_with_stop_loss(close, multiplier=sizer_multiplier)   
                            else:
                                self.sell(name="ENTRY SHORT Order")
            
            if should_sell:
                self.log('REVERSAL SELL, %.2f' % self.dataclose[0])
                self.close_and_cancel_stops()
                if should_stop_loss:
                    self.sell_with_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.sell(name="ENTRY SHORT Order")
               
               
        # Need to buy
        if self.position.size < 0:
            if should_close_on_reversal:
                if currentStochRSI > self.params_to_use['stoch_lowerband'] and currentStochRSI < self.params_to_use['reversal_lowerband']:
                    # If fast crosses slow upwards, trend reversal, buy
                    if (
                        self.stochrsi.l.fastk[-2] < self.stochrsi.l.fastd[-2] and
                        self.stochrsi.l.fastk[-1] < self.stochrsi.l.fastd[-1] and 
                        (self.stochrsi.l.fastk[0] - self.stochrsi.l.fastd[0]) >= reversal_sensitivity
                        # and (rsi_should_sell)
                    ):
                        self.log('INTERIM REVERSAL BUY, %.2f' % self.dataclose[0])
                        self.close_and_cancel_stops()
                        if should_trade_on_reversal:
                            if should_stop_loss:
                                self.buy_with_stop_loss(close, multiplier=sizer_multiplier)
                            else:
                                self.buy(name="ENTRY LONG Order")
                    
            if should_buy:
                self.log('REVERSAL BUY, %.2f' % self.dataclose[0])
                self.close_and_cancel_stops()
                if should_stop_loss:                
                    self.buy_with_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.buy(name="ENTRY LONG Order")
                
        if self.position.size == 0:
            if should_buy:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                if should_stop_loss:
                    self.buy_with_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.buy(name="ENTRY LONG Order")
            

            if should_sell:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                if should_stop_loss:
                    self.sell_with_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.sell(name="ENTRY SHORT Order")
