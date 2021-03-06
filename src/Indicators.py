import backtrader as bt
from backtrader.indicators import Indicator, MovAv, RelativeStrengthIndex, Highest, Lowest

class StochasticRSI(Indicator):
    """
    K - The time period to be used in calculating the %K. 3 is the default.
    D - The time period to be used in calculating the %D. 3 is the default.
    RSI Length - The time period to be used in calculating the RSI
    Stochastic Length - The time period to be used in calculating the Stochastic
  
    Formula:
    %K = SMA(100 * (RSI(n) - RSI Lowest Low(n)) / (RSI HighestHigh(n) - RSI LowestLow(n)), smoothK)
    %D = SMA(%K, periodD)
  
    """
    lines = ('fastk', 'fastd',)
  
    params = (
        ('k_period', 3),
        ('d_period', 3),
        ('rsi_period', 14),
        ('stoch_period', 14),
        ('movav', MovAv.Simple),
        ('rsi', RelativeStrengthIndex),
        ('upperband', 80.0),
        ('lowerband', 20.0),
    )
  
    plotlines = dict(percD=dict(_name='%D', ls='--'),
                     percK=dict(_name='%K'))
  
    def _plotlabel(self):
        plabels = [self.p.k_period, self.p.d_period, self.p.rsi_period, self.p.stoch_period]
        plabels += [self.p.movav] * self.p.notdefault('movav')
        return plabels
  
    def _plotinit(self):
        self.plotinfo.plotyhlines = [self.p.upperband, self.p.lowerband]
  
    def __init__(self):
        rsi = bt.ind.RSI(period=self.p.rsi_period, safediv=True)
        rsi_ll = bt.ind.Lowest(rsi, period=self.p.rsi_period)
        rsi_hh = bt.ind.Highest(rsi, period=self.p.rsi_period)
        stochrsi = bt.DivByZero((rsi - rsi_ll), (rsi_hh - rsi_ll), zero=0)
        # stochrsi = (rsi - rsi_ll) / (rsi_hh - rsi_ll)
        # print("StochRSI: ", stochrsi)

        self.l.fastk = k = self.p.movav(100.0 * stochrsi, period=self.p.k_period)
        self.l.fastd = self.p.movav(k, period=self.p.d_period)

class MACD(bt.indicators.MACD):

    def changeParams(self, period_me1, period_me2, period_signal):
        self.p.period_me1 = period_me1
        self.p.period_me2 = period_me2
        self.p.period_signal = period_signal


# Volume indicators
class MFI(bt.Indicator):
    lines = ('mfi',)
    params = dict(period=14)

    alias = ('MoneyFlowIndicator',)

    def __init__(self):
        tprice = (self.data.close + self.data.low + self.data.high) / 3.0
        mfraw = tprice * self.data.volume

        flowpos = bt.ind.SumN(mfraw * (tprice > tprice(-1)), period=self.p.period)
        flowneg = bt.ind.SumN(mfraw * (tprice < tprice(-1)), period=self.p.period)

        mfiratio = bt.ind.DivByZero(flowpos, flowneg, zero=100.0)
        self.l.mfi = 100.0 - 100.0 / (1.0 + mfiratio)

class CMF(bt.Indicator):

    alias = ('ChaikinMoneyFlow',)
 
    lines = ('money_flow',)
    params = (
        ('period', 20),
    )
 
    plotlines = dict(
        money_flow=dict(
            _name='CMF',
            color='green',
            alpha=0.50
        )
    )
 
    def __init__(self):
        # Let the indicator get enough data
        self.addminperiod(self.p.period)
 
        # Plot horizontal Line
        self.plotinfo.plotyhlines = [0]
 
        # Aliases to avoid long lines
        c = self.data.close
        h = self.data.high
        l = self.data.low
        v = self.data.volume
        
        self.data.ad = bt.If(bt.Or(bt.And(c == h, c == l), h == l), 0, (bt.ind.DivByZero((2*c-l-h),(h-l),zero=0.0))*v)
        self.lines.money_flow = bt.ind.DivByZero(bt.indicators.SumN(self.data.ad, period=self.p.period), bt.indicators.SumN(self.data.volume, period=self.p.period), zero=0.0)