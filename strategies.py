from pprint import pprint
import logging
import backtrader as bt
from datetime import datetime
from Indicators import StochasticRSI
from config import PRODUCTION, SANDBOX, ENV
from utils import send_telegram_message, get_formatted_datetime

class TESTBUY(bt.Strategy):
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
        self.dataclose = self.datas[0].close
        logging.basicConfig(level=self.p.loglevel, force=True)
        logging.info("TEST BUY ACTIVATED")

        self.bought_once = False
        self.sold_once = False
        self.stop_order = None
        # self.stop_orders = []

        if SANDBOX != True:
            print("Using a test strategy in production")
            raise
    
        self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        self.stochrsi = StochasticRSI(k_period=self.p.stoch_k_period,
                                   d_period=self.p.stoch_d_period,
                                   rsi_period=self.p.stoch_rsi_period,
                                   stoch_period=self.p.stoch_period,
                                   upperband=self.p.stoch_upperband,
                                   lowerband=self.p.stoch_lowerband)

    def log(self, txt, level=logging.DEBUG, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        hh = self.datas[0].datetime.time()
        logging.log(level, '%s %s, %s' % (dt.isoformat(), hh, txt))
        if level == logging.INFO and ENV == PRODUCTION:
            send_telegram_message(txt)
    
                
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

    def notify_order(self, order):
        print("order")
        print(order)
        l = dir(order)
        pprint(l)
        print("order info")
        pprint(order.info)
        print("order info name")
        pprint(order.info.name)
        print("ccxt_order")
        pprint(order.ccxt_order)

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if ENV == PRODUCTION:
                    # Access ccxt order instead
                    datetime_int =  oint(order.ccxt_order["timestamp"])
                    datetime_str = get_formatted_datetime()
                    if order.ccxt_order["info"]["status"] == 'FILLED':
                        self.log(
                            'BUY EXECUTED: %s, Amount: %.2f, AvgPrice: %.4f, Cost: %.4f, Time: %s' %
                            (order.info.name,
                            order.ccxt_order["amount"],
                            order.ccxt_order["average"],
                            order.ccxt_order["cost"],
                            datetime_str),
                            level=logging.INFO)
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
                self.log('SELL EXECUTED: %s, Price: %.5f, Cost: %.5f, Comm %.5f' %
                         (order.info.name,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm),
                          level=logging.INFO)
                
                self.log_trade()

            self.bar_executed = len(self)

        elif order.status in [order.Canceled]:
            self.log('Order Canceled: %s' % order.info.name, level=logging.INFO)
            self.log_trade()
        elif order.status in [order.Margin]:
            self.log('Order Margin: %s' % order.info.name, level=logging.INFO)
            self.log_trade()
        elif order.status in [order.Rejected]:
            self.log('Order Rejected: %s' % order.info.name, level=logging.INFO)
            self.log_trade()

    def notify_trade(self, trade):
        print("notify trade")
        if not trade.isclosed:
            return

        message = 'OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm)
        self.log(message, level=logging.INFO)

    def close_and_cancel_stops(self):
        # if self.position.size > 0:
        #     self.sell(name="CLOSE LONG using SHORT Order")
        # if self.position.size < 0:
        #     self.buy(name="CLOSE SHORT using LONG Order")
        print("Close")
        self.close()
        if self.stop_order:
            self.cancel(self.stop_order)
        # if self.stop_orders:
        #     for order in self.stop_orders:
        #         print("order name", order.info.name)
        #         self.cancel(order)

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
    
    def next(self):
        close = self.dataclose[0]
    
        if self.position.size <= 0 and not self.bought_once:
            print("second buy")
            # self.close_and_cancel_stops()
            # self.buy()
            self.buy_stop_loss(close)
            self.bought_once = True

        # if self.position.size >= 0 and not self.sold_once:
        #     self.close_and_cancel_stops()
        #     # self.sell()
        #     self.sell_stop_loss(close)
        #     self.sold_once = True

        if self.position.size != 0:
            # self.close()
            self.close_and_cancel_stops()



class StochMACD(bt.Strategy):
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
        logging.basicConfig(level=self.p.loglevel, force=True)
        self.dataclose = self.datas[0].close
        self.buyprice = None
        self.buycomm = None
        
        self.stop_order = None
        
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
        
    # def start(self):
    #     self.val_start = self.broker.get_cash()
    #     logging.info('Starting Portfolio Value: %.2f' % self.broker.getvalue())
    
    # def stop(self):
    #     logging.info('Ending Portfolio Value: %.2f' % self.broker.getvalue())
    #     self.roi = (self.broker.get_value() / self.val_start) - 1.0
    #     logging.info('ROI:        {:.2f}%'.format(100.0 * self.roi))

    def log(self, txt, level=logging.DEBUG, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        hh = self.datas[0].datetime.time()
        logging.log(level, '%s %s, %s' % (dt.isoformat(), hh, txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED: %s, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.info.name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.log_trade()
            else:  # Sell
                self.log('SELL EXECUTED: %s, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.info.name,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                
                self.log_trade()

            self.bar_executed = len(self)

        elif order.status in [order.Canceled]:
            self.log('Order Canceled: %s' % order.info.name)
            self.log_trade()
        elif order.status in [order.Margin]:
            self.log('Order Margin: %s' % order.info.name)
            self.log_trade()
        elif order.status in [order.Rejected]:
            self.log('Order Rejected: %s' % order.info.name)
            self.log_trade()

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm), level=logging.INFO)
            
    def log_trade(self):
        close = self.dataclose[0]
        self.log('Close, %.2f' % close)
        self.log("ATR: %.2f" % self.atr[0])
        self.log("mcross: %.2f" % self.mcross[0])
        self.log('previous stoch RSI: %.2f' % self.stochrsi[-1])
        self.log('current stoch RSI: %.2f' % self.stochrsi[0])
        self.log('fastk: %.2f' % self.stochrsi.l.fastk[0])
        self.log('fastd: %.2f' % self.stochrsi.l.fastd[0])
        self.log("")
        
    def close_and_cancel_stops(self):
        # if self.position.size > 0:
        #     self.sell(name="CLOSE LONG using SHORT Order")
        # if self.position.size < 0:
        #     self.buy(name="CLOSE SHORT using LONG Order")
        self.close()
        if self.stop_order:
            self.cancel(self.stop_order)
        
    def sell_stop_loss(self, close):
        sell_order = self.sell(
           transmit=False, 
           name="ENTRY SHORT Order"
        )

        stop_price = close + self.p.atrdist * self.atr[0]
        self.stop_order = self.buy(
            exectype=bt.Order.StopLimit, 
            price=stop_price, 
            stopPrice=stop_price,
            parent=sell_order, 
            transmit=True,
            name="STOPLOSS for SHORT"
        )
        
    def buy_stop_loss(self, close):
        buy_order = self.buy(
            transmit=False, 
            name="ENTRY LONG Order"
        )

        stop_price = close - self.p.atrdist * self.atr[0]
        self.stop_order = self.sell(
             exectype=bt.Order.StopLimit, 
             price=stop_price, 
             stopPrice=stop_price,
             parent=buy_order, 
             transmit=True,
             name="STOPLOSS for LONG"
        )

    def next(self):        
        close = self.dataclose[0]
        currentStochRSI = self.stochrsi.l.fastk[0]
        
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
