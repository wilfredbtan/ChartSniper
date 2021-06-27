import collections
import bisect
import time
from datetime import timezone
from pprint import pprint
from backtrader import position
from backtrader.dataseries import TimeFrame
from termcolor import colored
import logging
import backtrader as bt
from Indicators import StochasticRSI, MACD
from config import PRODUCTION, SANDBOX, ENV
from utils import send_telegram_message, get_formatted_datetime

class StrategyBase(bt.Strategy):

    params = (
        ("cashperc", 50),
        ("leverage", 5),
        ('loglevel', logging.WARNING),
        ('isWfa', False)
    )

    def __init__(self):
        self.order = None
        self.status = "DISCONNECTED"
        self.last_buy_price = None
        self.last_sell_price = None
        self.logged_order_ids = set()
        self.stop_orders = {}

        # Retrieved on 25 Jun 2021 from https://www.binance.com/en/support/faq/360033162192 and https://www.binance.com/en/support/faq/360033162192
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
        print("STATUS: ", self.status)
        if status == data.LIVE:
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
            if 'STOPLOSS' in order_name and order.ref in self.stop_orders:
                # pprint(order.info)
                if order.info.is_liquidable:
                    txt = colored("============== LIQUIDABLE stoploss executed!!!! ==============", 'yellow')
                    print(txt)
                del self.stop_orders[order.ref]

            if ENV == PRODUCTION:
                # Access ccxt order
                datetime_int = int(order.ccxt_order["timestamp"])
                datetime_int = datetime_int/1000 if datetime_int > 10000000000 else datetime_int
                datetime_str = get_formatted_datetime(datetime_int, format='%d %b %Y %H:%M:%S')

                order_id = order.ccxt_order["id"]
                order_cost = order.ccxt_order["cost"]

                print("order ids: ", self.logged_order_ids)
                if order_id in self.logged_order_ids:
                    self.logged_order_ids.remove(order_id)
                    return
                else:
                    self.logged_order_ids.add(order_id)
                
                if order.ccxt_order["info"]["status"] == 'FILLED':
                    if order.isbuy():
                        self.log(
                            'BUY EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Date: %s' %
                            (order_name,
                            order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order_cost,
                            datetime_str),
                            level=logging.INFO,
                            send_telegram=True)
                            # No commission (fee) data available as at 12 June 2021
                        if order_name == "CLOSE":
                            pnl = self.last_sell_price - order_cost  
                            self.log_profit(pnl)
                            # print("buy close broker cash")
                            # print("cerebro cash", self.broker.cash)
                        else:
                            self.last_buy_price = order_cost
                    else:
                        self.log(
                            'SELL EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Date: %s' %
                            (order_name,
                            -order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order.ccxt_order["cost"],
                            datetime_str),
                            level=logging.INFO,
                            send_telegram=True)
                            # No commission (fee) data available as at 12 June 2021
                        if order_name == "CLOSE":
                            pnl = self.last_buy_price - order_cost  
                            self.log_profit(pnl)
                            # print("sell close broker cash")
                            # print("cerebro cash", self.broker.cash)
                        else:
                            self.last_sell_price = order_cost 
            else:
                if order.isbuy():
                    self.log(
                        'BUY EXECUTED: %s, Amount: %.2f, Price: %.4f, Cost: %.4f, Comm %.2f' %
                        (order_name,
                        order.executed.size,
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm), 
                        level=logging.INFO)
                else:  # Sell
                    self.log('SELL EXECUTED: %s, Amount: %.2f, Price: %.5f, Cost: %.5f, Comm %.5f' %
                            (order_name,
                            order.executed.size,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm),
                            level=logging.INFO)
                
            self.log_trade()

        elif order.status in [order.Canceled]:
            self.log('Order Canceled: %s' % order_name, level=logging.INFO, send_telegram=True)
            self.log_trade()
        elif order.status in [order.Margin]:
            self.log('Order Margin: %s' % order_name, level=logging.INFO, send_telegram=True)
            self.log_trade()
        elif order.status in [order.Rejected]:
            self.log('Order Rejected: %s' % order_name, level=logging.INFO, send_telegram=True)
            self.log_trade()


    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log_profit(trade.pnl, trade.pnlcomm)

    def close_and_cancel_stops(self):
        # self.log("close broker cash")
        # self.log(f"close cerebro cash {self.broker.cash}")
        close_order = self.close()
        if close_order:
            close_order.addinfo(name="CLOSE")
        if len(self.stop_orders) > 0:
            # if len(self.stop_orders) > 1:
            #     print("NO")
            for oref in self.stop_orders.keys():
                # print("-- remove ref: ", oref)
                self.cancel(self.stop_orders[oref])
            # print("Number of stop orders: ", len(self.stop_orders))
            self.stop_orders = {}

    def get_maintenance_margin_rate_and_amt(self, notional_value):
        '''
        Returns the (maintenance_margin_rate, maintenance_margin_amount) for the corresponding notional value
        '''
        ind = bisect.bisect_left(list(self.tier_dict.keys()), notional_value)
        return list(self.tier_dict.values())[ind]
    
    def get_liquidation_price(self, side, pos_size, entry_price):
        (mmr, mma) = self.get_maintenance_margin_rate_and_amt(notional_value=pos_size * entry_price)
        # print("side: ", side)
        # print("pos_size: ", pos_size)
        # print("entry price: ", entry_price)
        # print("Margin rate: ", mmr)
        # print("Margin amount: ", mma)
        # Wallet balance
        wb = self.broker.cash
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


    def sell_stop_loss(self, close, multiplier=1):
        self.log(f"=== sell cerebro value {self.broker.getvalue()}")
        size = self.broker.getvalue()  * (self.p.cashperc / 100) * self.p.leverage / close
        self.log(f"=== sell size, {size}")

        # Binance minimum order size is 0.0001
        size = max(size * multiplier, 0.0001)

        sell_order = self.sell(
            size=size, 
            transmit=False, 
        )
        sell_order.addinfo(name="ENTRY SHORT Order")

        atrdist = self.params_to_use['atrdist'] if self.p.isWfa else self.p.atrdist
        stop_price = close + atrdist * self.atr[0]

        lp = self.get_liquidation_price(side=-1, pos_size=size, entry_price=close)
        lp_with_buffer = lp - self.atr[0] * 0.5
        # lp_with_buffer = lp - 100
        # lp_with_buffer = lp
        is_liquidable = lp_with_buffer < stop_price
        # if is_liquidable:
        #     txt = colored(f"===== STOP SHORT Liquidation price {lp_with_buffer} used instead of {stop_price}", 'cyan')
        #     print(txt)
        stop_price = min(stop_price, lp_with_buffer)

        stop_order = self.buy(
            exectype=bt.Order.StopLimit, 
            size=sell_order.size, 
            price=stop_price, 
            stopPrice=stop_price,
            parent=sell_order, 
            transmit=True,
        )

        stop_order.addinfo(name="STOPLOSS for SHORT")
        stop_order.addinfo(is_liquidable=is_liquidable)
        self.stop_orders[stop_order.ref] = stop_order
        
    def buy_stop_loss(self, close, multiplier=1):
        self.log(f"=== buy cerebro value {self.broker.getvalue()}")
        size = self.broker.getvalue()  * (self.p.cashperc / 100) * self.p.leverage / close
        # size = self.broker.cash  * (self.p.cashperc / 100) * self.p.leverage / close
        self.log(f"=== buy size, {size}")
        # Binance minimum order size
        size = max(size * multiplier, 0.0001)

        buy_order = self.buy(
            size=size,
            transmit=False, 
        )
        # Kwargs do not work in bt-ccxt
        buy_order.addinfo(name="ENTRY LONG Order")

        atrdist = self.params_to_use['atrdist'] if self.p.isWfa else self.p.atrdist
        stop_price = close - atrdist * self.atr[0]

        lp = self.get_liquidation_price(side=1, pos_size=size, entry_price=close)
        lp_with_buffer = lp + self.atr[0] * 0.5
        # lp_with_buffer = lp + 100
        # lp_with_buffer = lp
        is_liquidable = lp_with_buffer > stop_price
        # if is_liquidable:
        #     txt = colored(f"===== STOP LONG Liquidation price {lp_with_buffer} used instead of {stop_price}", 'cyan')
        #     print(txt)
        stop_price = max(stop_price, lp_with_buffer)

        stop_order = self.sell(
            exectype=bt.Order.StopLimit,
            size=buy_order.size,
            price=stop_price,
            stopPrice=stop_price,
            parent=buy_order,
            transmit=True,
        )
        # Kwargs do not work in bt-ccxt
        stop_order.addinfo(name="STOPLOSS for LONG")
        stop_order.addinfo(is_liquidable=is_liquidable)
        self.stop_orders[stop_order.ref] = stop_order

    def log(self, txt, level=logging.DEBUG, send_telegram=False, color=None, dt=None):
        log_txt = txt
        if color:
            log_txt = colored(txt, color)

        dt = dt or self.datas[0].datetime.date(0)
        hh = self.datas[0].datetime.time()

        logging.log(level, '%s %s, %s' % (dt.isoformat(), hh, log_txt))

        if send_telegram and ENV == PRODUCTION:
            telegram_txt = txt.replace(', ', '\n')
            print("Telegram text: ", telegram_txt)
            send_telegram_message(telegram_txt)
    
    def log_trade(self):
        close = self.dataclose[0]
        self.log('Close, %.2f' % close)
        self.log("ATR: %.2f" % self.atr[0])
        # self.log("mcross: %.2f" % self.mcross[0])
        self.log('previous stoch RSI: %.2f' % self.stochrsi[-1])
        self.log('current stoch RSI: %.2f' % self.stochrsi[0])
        self.log('fastk: %.2f' % self.stochrsi.l.fastk[0])
        self.log('fastd: %.2f' % self.stochrsi.l.fastd[0])
        self.log("")
    

    def log_profit(self, pnl, pnlcomm=None):
        color = 'green'
        if pnl < 0:
            color = 'red'
        txt = 'OPERATION PROFIT: GROSS %.2f' % pnl

        if pnlcomm:
            txt += ', NET %.2f' % pnlcomm
        
        value = self.broker.getvalue()
        txt += f'\nPORTFOLIO VALUE: {value}'

        self.log(txt, level=logging.INFO, send_telegram=True, color=color)


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

        logging.basicConfig(level=self.p.loglevel, force=True)
        logging.info("TEST BUY strategy activated")

        self.bought_once = False
        self.sold_once = False
        print("cash perc in test", self.p.cashperc)

        # if SANDBOX != True:
        #     print("Using a test strategy in production")
        #     raise
    
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
        close = self.dataclose[0]
        # print("Values: ")
        # print("self.mcross[0]", self.mcross[0])
        # print("self.stochrsi.l.fastk[-3]", self.stochrsi.l.fastk[-3])
        # print("self.stochrsi.l.fastk[-2]", self.stochrsi.l.fastk[-2])
        # print("self.stochrsi.l.fastk[-1]", self.stochrsi.l.fastk[-1])
        # print("self.stochrsi.l.fastk[0]", self.stochrsi.l.fastk[0])
        # print("")

        # txt = list()
        # txt.append('%04d' % len(self))
        # dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
        # txt.append('%s' % self.data.datetime.datetime(0).strftime(dtfmt))
        # txt.append('{}'.format(self.data.open[0]))
        # txt.append('{}'.format(self.data.high[0]))
        # txt.append('{}'.format(self.data.low[0]))
        # txt.append('{}'.format(self.data.close[0]))
        # txt.append('{}'.format(self.data.volume[0]))
        # print(', '.join(txt))

        if ENV == PRODUCTION and self.status != "LIVE":
            return

        print("LIVE NEXT")
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
    
        if self.position.size < 0 and not self.bought_once:
            print("buy")
            # self.buy(exectype=bt.Order.Limit, price=30000)
            self.close_and_cancel_stops()
            # self.buy()
            self.buy_stop_loss(close)
            self.bought_once = True

        if self.position.size > 0 and not self.sold_once:
            print("sell")
            # self.sell(exectype=bt.Order.Limit, price=60000)
            self.close_and_cancel_stops()
            # # self.sell()
            self.sell_stop_loss(close)
            self.sold_once = True

        if self.position.size == 0:
            print("SHOULD BUY")
            self.close_and_cancel_stops()
            # self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.buy_stop_loss(close)

        if self.position.size != 0 and self.bought_once and self.sold_once:
            self.close_and_cancel_stops()


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
        
        ('rsi_upperband', 60.0),
        ('rsi_lowerband', 40.0),
        
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 5),   # ATR distance for stop price

        ('reversal_sensitivity', 20),
        ('reversal_lowerband', 50),
        ('reversal_upperband', 50),
    )

    def __init__(self):
        StrategyBase.__init__(self)

        logging.basicConfig(level=self.p.loglevel, force=True)
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

        self.rsi = bt.ind.RSI(self.datas[0], period=self.p.stoch_rsi_period, safediv=True)
        
        self.atr = bt.indicators.ATR(self.datas[0], period=self.p.atrperiod)

        self.stochrsi = StochasticRSI(
            self.datas[0],
            k_period=self.p.stoch_k_period,
            d_period=self.p.stoch_d_period,
            rsi_period=self.p.stoch_rsi_period,
            stoch_period=self.p.stoch_period,
            upperband=self.p.stoch_upperband,
            lowerband=self.p.stoch_lowerband,
        )

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

    # def nextstart(self):
    #     print('--------------------------------------------------')
    #     print('nextstart called with len', len(self))
    #     print('--------------------------------------------------')

    #     super(StochMACD, self).nextstart()

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


        # if self.status == "LIVE":
        # print("===== Values: =====")
        # dt = self.datas[1].datetime.datetime()
        # print(f"datetime: {dt}")
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

        # print("Should buy: (cross up)")
        # # print("self.mcross[0] > 0.0", self.mcross[0] > 0.0)
        # print("self.stochrsi.l.fastk[-4] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-4] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband)
        # print("self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband", self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband)
        # print("")

        # print("Should sell: (cross down)")
        # # print("self.mcross[0] < 0.0", self.mcross[0] < 0.0)
        # print("self.stochrsi.l.fastk[-4] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-4] > self.p.stoch_lowerband)
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
                did_stochrsi_crossup = did_stochrsi_crossup and self.stochrsi.l.fastk[lowerband_count] >= self.p.stoch_lowerband
            else:
                did_stochrsi_crossup = did_stochrsi_crossup and self.stochrsi.l.fastk[lowerband_count] < self.p.stoch_lowerband
            lowerband_count += 1

        upperband_count = -4
        did_stochrsi_crossdown = True
        while upperband_count <= 0:
            if upperband_count == 0:
                did_stochrsi_crossdown = did_stochrsi_crossdown and self.stochrsi.l.fastk[upperband_count] <= self.p.stoch_upperband
            else:
                did_stochrsi_crossdown = did_stochrsi_crossdown and self.stochrsi.l.fastk[upperband_count] > self.p.stoch_upperband
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

        reversal_sensitivity = self.p.reversal_sensitivity
        should_stop_loss = True
        should_trade_on_reversal = True
        should_close_on_reversal = True

        # Need to sell
        if self.position.size > 0:
            if should_close_on_reversal:
                if currentStochRSI > self.p.reversal_upperband and currentStochRSI < self.p.stoch_upperband:
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
                                self.sell_stop_loss(close, multiplier=sizer_multiplier)   
                            else:
                                self.sell(name="ENTRY SHORT Order")
            
            if should_sell:
                self.log('REVERSAL SELL, %.2f' % self.dataclose[0])
                self.close_and_cancel_stops()
                if should_stop_loss:
                    self.sell_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.sell(name="ENTRY SHORT Order")
               
               
        # Need to buy
        if self.position.size < 0:
            if should_close_on_reversal:
                if currentStochRSI > self.p.stoch_lowerband and currentStochRSI < self.p.reversal_lowerband:
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
                                self.buy_stop_loss(close, multiplier=sizer_multiplier)
                            else:
                                self.buy(name="ENTRY LONG Order")
                    
            if should_buy:
                self.log('REVERSAL BUY, %.2f' % self.dataclose[0])
                self.close_and_cancel_stops()
                if should_stop_loss:                
                    self.buy_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.buy(name="ENTRY LONG Order")
                
        if self.position.size == 0:
            if should_buy:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                if should_stop_loss:
                    self.buy_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.buy(name="ENTRY LONG Order")
            

            if should_sell:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                if should_stop_loss:
                    self.sell_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.sell(name="ENTRY SHORT Order")


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
        logging.basicConfig(level=self.p.loglevel, force=True)
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
                                self.sell_stop_loss(close, multiplier=sizer_multiplier)   
                            else:
                                self.sell(name="ENTRY SHORT Order")
            
            if should_sell:
                self.log('REVERSAL SELL, %.2f' % self.dataclose[0])
                self.close_and_cancel_stops()
                if should_stop_loss:
                    self.sell_stop_loss(close, multiplier=sizer_multiplier)
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
                                self.buy_stop_loss(close, multiplier=sizer_multiplier)
                            else:
                                self.buy(name="ENTRY LONG Order")
                    
            if should_buy:
                self.log('REVERSAL BUY, %.2f' % self.dataclose[0])
                self.close_and_cancel_stops()
                if should_stop_loss:                
                    self.buy_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.buy(name="ENTRY LONG Order")
                
        if self.position.size == 0:
            if should_buy:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                if should_stop_loss:
                    self.buy_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.buy(name="ENTRY LONG Order")
            

            if should_sell:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                if should_stop_loss:
                    self.sell_stop_loss(close, multiplier=sizer_multiplier)
                else:
                    self.sell(name="ENTRY SHORT Order")
