import backtrader as bt

class CommInfo_Futures_Perc_Mult(bt.CommInfoBase):
    params = (
      ('stocklike', False),  # Futures
      ('commtype', bt.CommInfoBase.COMM_PERC),  # Apply % Commission
    # ('percabs', False),  # pass perc as xx% which is the default
    )

    def _getcommission(self, size, price, pseudoexec):
        return size * price * self.p.commission * self.p.mult