import backtrader as bt

class CommInfo_Futures_Perc(bt.CommInfoBase):
    params = (
        ('stocklike', False),
        ('commtype', bt.CommInfoBase.COMM_PERC),
    )