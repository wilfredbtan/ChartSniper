import backtrader as bt

# https://www.binance.com/en/support/faq/360033544231
class CommInfo_Futures_Perc(bt.CommInfoBase):
    params = (
      ('stocklike', True),  # Binance futures fees works more like stocks
      ('commtype', bt.CommInfoBase.COMM_PERC),  # Apply % Commission
      ('percabs', False),  # pass perc as xx% which is the default
    )

    def _getcommission(self, size, price, pseudoexec):
        return size * price * self.p.commission