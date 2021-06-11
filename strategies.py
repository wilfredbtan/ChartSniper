from pprint import pprint
from termcolor import colored
import logging
import backtrader as bt
from datetime import datetime
from Indicators import StochasticRSI
from config import PRODUCTION, SANDBOX, ENV
from utils import send_telegram_message, get_formatted_datetime

class StrategyBase(bt.Strategy):
    def __init__(self):
        self.order = None
        # self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        # self.bar_executed = 0
        # self.buy_price_close = None
        # self.soft_sell = False
        # self.hard_sell = False
        # self.log("Base strategy initialized")
        self.data_once = False

    def reset_sell_indicators(self):
        self.soft_sell = False
        self.hard_sell = False
        self.buy_price_close = None

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        print("STATUS: ", self.status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")
        
        
        print("Data")
        # if not self.data_once:
        #     self.data_once = True
        #     print("Values: ")
        #     print("self.mcross[0]", self.mcross[0])
        #     print("self.stochrsi.l.fastk[-3]", self.stochrsi.l.fastk[-3])
        #     print("self.stochrsi.l.fastk[-2]", self.stochrsi.l.fastk[-2])
        #     print("self.stochrsi.l.fastk[-1]", self.stochrsi.l.fastk[-1])
        #     print("self.stochrsi.l.fastk[0]", self.stochrsi.l.fastk[0])
        #     print("")

        #     print("Should buy:")
        #     print("self.mcross[0] > 0.0", self.mcross[0] > 0.0)
        #     print("self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband)
        #     print("self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband)
        #     print("self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband", self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband)
        #     print("self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband", self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband)
        #     print("")

        #     print("Should sell:")
        #     print("self.mcross[0] < 0.0", self.mcross[0] < 0.0)
        #     print("self.stochrsi.l.fastk[-3] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-3] > self.p.stoch_lowerband)
        #     print("self.stochrsi.l.fastk[-2] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-2] > self.p.stoch_lowerband)
        #     print("self.stochrsi.l.fastk[-1] > self.p.stoch_lowerband", self.stochrsi.l.fastk[-1] > self.p.stoch_lowerband)
        #     print("self.stochrsi.l.fastk[0] <= self.p.stoch_lowerband", self.stochrsi.l.fastk[0] <= self.p.stoch_lowerband)
        #     print("")
        

    # def short(self):
    #     if self.last_operation == "SELL":
    #         return

    #     if ENV == DEVELOPMENT:
    #         self.log("Sell ordered: $%.2f" % self.data0.close[0])
    #         return self.sell()

    #     cash, value = self.broker.get_wallet_balance(COIN_TARGET)
    #     amount = value*0.99
    #     self.log("Sell ordered: $%.2f. Amount %.6f %s - $%.2f USDT" % (self.data0.close[0],
    #                                                                    amount, COIN_TARGET, value), True)
    #     return self.sell(size=amount)

    # def long(self):
    #     if self.last_operation == "BUY":
    #         return

    #     self.log("Buy ordered: $%.2f" % self.data0.close[0], True)
    #     self.buy_price_close = self.data0.close[0]
    #     price = self.data0.close[0]

    #     if ENV == DEVELOPMENT:
    #         return self.buy()

    #     cash, value = self.broker.get_wallet_balance(COIN_REFER)
    #     amount = (value / price) * 0.99  # Workaround to avoid precision issues
    #     self.log("Buy ordered: $%.2f. Amount %.6f %s. Ballance $%.2f USDT" % (self.data0.close[0],
    #                                                                           amount, COIN_TARGET, value), True)
        # return self.buy(size=amount)

    def notify_order(self, order):
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

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if ENV == PRODUCTION:
                    # Access ccxt order instead
                    datetime_int = int(order.ccxt_order["timestamp"])
                    datetime_int = datetime_int/1000 if datetime_int > 10000000000 else datetime_int
                    datetime_str = get_formatted_datetime(datetime_int, format='%d %b %Y %H:%M:%S')
                    if order.ccxt_order["info"]["status"] == 'FILLED':
                        self.log(
                            'BUY EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Date: %s' %
                            (order.info.name,
                            order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order.ccxt_order["cost"],
                            datetime_str),
                            level=logging.INFO,
                            send_telegram=True)
                            # Commission is zero for some reason
                else:
                    self.log(
                        'BUY EXECUTED: %s, Price: %.4f, Cost: %.4f, Comm %.2f' %
                        (order.info.name,
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm), 
                        level=logging.INFO)

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.log_trade()
            else:  # Sell
                if ENV == PRODUCTION:
                    # Access ccxt order instead
                    datetime_int = int(order.ccxt_order["timestamp"])
                    datetime_int = datetime_int/1000 if datetime_int > 10000000000 else datetime_int
                    datetime_str = get_formatted_datetime(datetime_int, format='%d %b %Y %H:%M:%S')
                    if order.ccxt_order["info"]["status"] == 'FILLED':
                        self.log(
                            'SELL EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Date: %s' %
                            (order.info.name,
                            order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order.ccxt_order["cost"],
                            datetime_str),
                            level=logging.INFO,
                            send_telegram=True)
                            # Commission is zero for some reaso
                else:
                    self.log('SELL EXECUTED: %s, Price: %.5f, Cost: %.5f, Comm %.5f' %
                            (order.info.name,
                            order.executed.price,
                            order.executed.value,
                            order.executed.comm),
                            level=logging.INFO)
                
                self.log_trade()

            # self.bar_executed = len(self)

        elif order.status in [order.Canceled]:
            self.log('Order Canceled: %s' % order.info.name, level=logging.INFO, send_telegram=True)
            self.log_trade()
        elif order.status in [order.Margin]:
            self.log('Order Margin: %s' % order.info.name, level=logging.INFO, send_telegram=True)
            self.log_trade()
        elif order.status in [order.Rejected]:
            self.log('Order Rejected: %s' % order.info.name, level=logging.INFO, send_telegram=True)
            self.log_trade()

    def log_profit(self, pnl, pnlcomm):
        color = 'green'
        if pnl < 0:
            color = 'red'

        self.log(colored('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (pnl, pnlcomm), color), level=logging.INFO, send_telegram=True)

    def notify_trade(self, trade):
        # print("notify trade")
        # if not trade.isclosed:
        #     return
        self.log_profit(trade.pnl, trade.pnlcomm)

    def close_and_cancel_stops(self):
        close_order = self.close()
        if close_order:
            close_order.addinfo(name="CLOSE")
        if self.stop_order:
            self.cancel(self.stop_order)

    def sell_stop_loss(self, close):
        sell_order = self.sell(
           transmit=False, 
        )
        sell_order.addinfo(name="ENTRY SHORT Order")

        stop_price = close + self.p.atrdist * self.atr[0]
        self.stop_order = self.buy(
            exectype=bt.Order.StopLimit, 
            price=stop_price, 
            stopPrice=stop_price,
            parent=sell_order, 
            transmit=True,
        )
        self.stop_order.addinfo(name="STOPLOSS for SHORT")
        # self.stop_orders.append(stop_order)
        # for order in self.stop_orders:
        #     print("order name", order.info.name)
        
    def buy_stop_loss(self, close):
        buy_order = self.buy(
            transmit=False, 
        )
        # Kwargs do not work in bt-ccxt
        buy_order.addinfo(name="ENTRY LONG Order")

        stop_price = close - self.p.atrdist * self.atr[0]
        self.stop_order = self.sell(
             exectype=bt.Order.StopLimit, 
             size=buy_order.size,
             price=stop_price, 
             stopPrice=stop_price,
             parent=buy_order, 
             transmit=True,
        )
        # Kwargs do not work in bt-ccxt
        self.stop_order.addinfo(name="STOPLOSS for LONG")

    def log(self, txt, level=logging.DEBUG, send_telegram=False, color=None, dt=None):
        if color:
            txt = colored(txt, color)

        dt = dt or self.datas[0].datetime.date(0)
        hh = self.datas[0].datetime.time()

        logging.log(level, '%s %s, %s' % (dt.isoformat(), hh, txt))
        if send_telegram and ENV == PRODUCTION:
            telegram_txt = txt.replace(', ', '\n')
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
        
        ('loglevel', logging.INFO)
    )

    def __init__(self):
        StrategyBase.__init__(self)

        self.dataclose = self.datas[0].close

        logging.basicConfig(level=self.p.loglevel, force=True)
        logging.info("TEST BUY strategy activated")

        self.bought_once = False
        self.sold_once = False

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

        print("Values: ")
        print("self.mcross[0]", self.mcross[0])
        print("self.stochrsi.l.fastk[-3]", self.stochrsi.l.fastk[-3])
        print("self.stochrsi.l.fastk[-2]", self.stochrsi.l.fastk[-2])
        print("self.stochrsi.l.fastk[-1]", self.stochrsi.l.fastk[-1])
        print("self.stochrsi.l.fastk[0]", self.stochrsi.l.fastk[0])
        print("")

        txt = list()
        txt.append('%04d' % len(self))
        dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
        txt.append('%s' % self.data.datetime.datetime(0).strftime(dtfmt))
        txt.append('{}'.format(self.data.open[0]))
        txt.append('{}'.format(self.data.high[0]))
        txt.append('{}'.format(self.data.low[0]))
        txt.append('{}'.format(self.data.close[0]))
        txt.append('{}'.format(self.data.volume[0]))
        print(', '.join(txt))

        if ENV == PRODUCTION and self.status != "LIVE":
            return

        print("CHECK")
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
    
        # if self.position.size <= 0 and not self.bought_once:
        #     print("buy")
        #     self.buy(exectype=bt.Order.Limit, price=30000)
        #     # self.close_and_cancel_stops()
        #     # self.buy()
        #     # self.buy_stop_loss(close)
        #     self.bought_once = True

        if self.position.size >= 0 and not self.sold_once:
            print("sell")
            # self.sell(exectype=bt.Order.Limit, price=60000)
            # self.close_and_cancel_stops()
            # # self.sell()
            self.sell_stop_loss(close)
            self.sold_once = True

        if self.position.size != 0:
            print("close")
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
        
        ('loglevel', logging.WARNING)
    )

    def __init__(self):
        StrategyBase.__init__(self)
        logging.basicConfig(level=self.p.loglevel, force=True)
        self.dataclose = self.datas[0].close
        self.buyprice = None
        self.buycomm = None
        
        self.stop_order = None
        
        self.count = 0
        
        self.macd = bt.indicators.MACD(self.data,
                               period_me1=self.p.macd1,
                               period_me2=self.p.macd2,
                               period_signal=self.p.macdsig)

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

#         self.rsi = bt.ind.RSI(period=self.p.stoch_rsi_period)
        
        self.stochrsi = StochasticRSI(k_period=self.p.stoch_k_period,
                                   d_period=self.p.stoch_d_period,
                                   rsi_period=self.p.stoch_rsi_period,
                                   stoch_period=self.p.stoch_period,
                                   upperband=self.p.stoch_upperband,
                                   lowerband=self.p.stoch_lowerband)
        
    def next(self):        
        close = self.dataclose[0]
        currentStochRSI = self.stochrsi.l.fastk[0]
        self.count += 1

        # if self.status == "LIVE":
        # print("Values: ")
        # print("self.mcross[0]", self.mcross[0])
        # print("self.stochrsi.l.fastk[-3]", self.stochrsi.l.fastk[-3])
        # print("self.stochrsi.l.fastk[-2]", self.stochrsi.l.fastk[-2])
        # print("self.stochrsi.l.fastk[-1]", self.stochrsi.l.fastk[-1])
        # print("self.stochrsi.l.fastk[0]", self.stochrsi.l.fastk[0])
        # print("")

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
        
        should_buy = (
            self.mcross[0] > 0.0 and
            self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband and 
            self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband and 
            self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband and 
            self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband
#             self.stochrsi.l.fastk[-3] < self.p.stoch_lowerband and 
#             self.stochrsi.l.fastk[-2] < self.p.stoch_lowerband and 
#             self.stochrsi.l.fastk[-1] < self.p.stoch_lowerband and 
#             (self.stochrsi.l.fastk[0] >= self.p.stoch_lowerband or self.stochrsi.l.fastk[-1] >= self.p.stoch_lowerband) and
#             (self.mcross[0] > 0.0 or self.mcross[-1] > 0.0)
        )
        
        should_sell = (
            self.mcross[0] < 0.0 and
            self.stochrsi.l.fastk[-3] > self.p.stoch_upperband and 
            self.stochrsi.l.fastk[-2] > self.p.stoch_upperband and 
            self.stochrsi.l.fastk[-1] > self.p.stoch_upperband and 
            self.stochrsi.l.fastk[0] <= self.p.stoch_upperband
#             self.stochrsi.l.fastk[-3] > self.p.stoch_upperband and 
#             self.stochrsi.l.fastk[-2] > self.p.stoch_upperband and 
#             self.stochrsi.l.fastk[-1] > self.p.stoch_upperband and 
#             (self.stochrsi.l.fastk[0] <= self.p.stoch_upperband or self.stochrsi.l.fastk[-1] <= self.p.stoch_upperband) and
#             (self.mcross[0] < 0.0 or self.mcross[-1] < 0.0)
        )
        
        reversal_sensitivity = self.p.reversal_sensitivity
        should_stop_loss = True
        should_trade_on_reversal = True
        should_close_on_reversal = True
        
        # Need to sell
        if self.position.size > 0:
            if should_close_on_reversal:
                if currentStochRSI > 50 and currentStochRSI < self.p.stoch_upperband:
                    # If fast crosses slow downwards, trend reversal, sell
                    if (self.stochrsi.l.fastk[-1] > self.stochrsi.l.fastd[-1] and 
                        (self.stochrsi.l.fastk[0] - self.stochrsi.l.fastd[0]) <= -reversal_sensitivity):

                        self.close_and_cancel_stops()
                        self.log('INTERIM REVERSAL SELL, %.2f' % self.dataclose[0])

                        if should_trade_on_reversal:
                            if should_stop_loss:
                                self.sell_stop_loss(close)   
                            else:
                                self.sell(name="ENTRY SHORT Order")
            
            if should_sell:
                self.close_and_cancel_stops()

                self.log('REVERSAL SELL, %.2f' % self.dataclose[0])
                
                if should_stop_loss:
                    self.sell_stop_loss(close)
                else:
                    self.sell(name="ENTRY SHORT Order")
               
               
        # Need to buy
        if self.position.size < 0:
            if should_close_on_reversal:
                if currentStochRSI > self.p.stoch_lowerband and currentStochRSI < 50:
                    # If fast crosses slow upwards, trend reversal, buy
                    if (self.stochrsi.l.fastk[-1] < self.stochrsi.l.fastd[-1] and 
                        (self.stochrsi.l.fastk[0] - self.stochrsi.l.fastd[0]) >= reversal_sensitivity):

                        self.close_and_cancel_stops()
                        self.log('INTERIM REVERSAL BUY, %.2f' % self.dataclose[0])

                        if should_trade_on_reversal:
                            if should_stop_loss:
                                self.buy_stop_loss(close)
                            else:
                                self.buy(name="ENTRY LONG Order")
                    
            if should_buy:
                self.close_and_cancel_stops()
                self.log('REVERSAL BUY, %.2f' % self.dataclose[0])
                
                if should_stop_loss:                
                    self.buy_stop_loss(close)
                else:
                    self.buy(name="ENTRY LONG Order")

           
                
        if self.position.size == 0:
            if should_buy:
                self.close_and_cancel_stops()
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                
                if should_stop_loss:
                    self.buy_stop_loss(close)
                else:
                    self.buy(name="ENTRY LONG Order")
            

            if should_sell:
                self.close_and_cancel_stops()
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                
                if should_stop_loss:
                    self.sell_stop_loss(close)
                else:
                    self.sell(name="ENTRY SHORT Order")
