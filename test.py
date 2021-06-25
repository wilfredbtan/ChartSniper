import collections
import bisect

tier_dict = collections.OrderedDict()
tier_dict[50000] = (0.004, 0)
tier_dict[250000] = (0.005, 50)
tier_dict[1000000] = (0.01, 1300)
tier_dict[5000000] = (0.025, 16300)
tier_dict[20000000] = (0.05, 141300)
tier_dict[50000000] = (0.1, 1141300)
tier_dict[100000000] = (0.125, 2391300)
tier_dict[200000000] = (0.15, 4891300)
tier_dict[300000000] = (0.25, 24891300)
tier_dict[500000000] = (0.5, 0)

def get_maintenance_margin_rate_and_amt(notional_value):
    ind = bisect.bisect_left(list(tier_dict.keys()), notional_value)
    print(ind)
    return list(tier_dict.values())[ind]

# (mmr, mma) = get_maintenance_margin_rate_and_amt(notional_value=3500032.458)


# print(mmr)
# print(mma)

def get_liquidation_price(side, pos_size, entry_price):
    (mmr, mma) = get_maintenance_margin_rate_and_amt(notional_value=pos_size * entry_price)
    print(mmr)
    print(mma)
    # Wallet balance
    wb = 5000
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

    print(num)
    print(den)

    lp = num / den

    return lp

p = get_liquidation_price(
    side=1,
    pos_size=10,
    entry_price=32481.980
)

print(p)