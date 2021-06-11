import os

# print("From 2019")
# os.system('python3 backtest.py -o --fromdate 2019-5-1 --todate 2021-5-1 --cashperc 50')
# print("From 2018")
# os.system('python3 backtest.py -o --fromdate 2018-4-1 --todate 2019-4-1  --cashperc 50')

# os.system('python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --fromdate 2019-5-1 --todate 2021-5-1')
# os.system('python3 backtest.py --macd1 11 --macd2 24 --macdsig 7 --fromdate 2018-4-1 --todate 2019-4-1')

''' Optimize for MACD. 9 21 8 seems the best for some reason lol'''
    # From 2019
# [0.002273390385830033, 9361.07, 5.0, 8, 25, 8]
# [0.002271509188889601, 9345.8, 5.0, 9, 21, 8]
# [0.002271509188889601, 9345.8, 5.0, 11, 20, 7]
# [0.002255731406488645, 9218.39, 5.0, 9, 22, 8]
# [0.0022306759365417917, 9018.59, 5.0, 10, 21, 7]

    # From 2018
# [0.004494863323081424, 9138.15, 5.0, 11, 25, 5]
# [0.0044013609731506425, 8771.79, 5.0, 11, 24, 7]
# [0.004198101472410856, 8006.65, 5.0, 11, 24, 5]
# [0.00398634725384348, 7261.15, 5.0, 10, 25, 5]
# [0.003786650116149551, 6602.89, 5.0, 10, 25, 7]

'''Optimize for ATR Dist (stop loss). 5 seems the best'''
    # From 2019
# [0.004006155367781593, 33566.28, 13, 9, 21, 8]
# [0.003799702182121598, 29330.16, 5, 9, 21, 8]
# [0.0037421759269827023, 28230.39, 14, 9, 21, 8]
# [0.003465500011171479, 23395.88, 7, 9, 21, 8]
# [0.003263669278174703, 20304.24, 8, 9, 21, 8]
    # From 2018
# [0.006238160707605604, 18257.07, 3, 9, 21, 8]
# [0.0060935861363389, 17314.97, 5, 9, 21, 8]
# [0.005703345674420665, 14954.11, 6, 9, 21, 8]
# [0.005636240010576195, 14574.94, 7, 9, 21, 8]
# [0.005598026217405897, 14360.11, 4, 9, 21, 8]

# macd = '--macd1 12 --macd2 26 --macdsig 9'
# macd = '--macd1 11 --macd2 20 --macdsig 7'
macd = '--macd1 9 --macd2 21 --macdsig 8'

atrdist = '--atrdist 5'
# atrdist = '--atrdist 3'
# atrdist = '--atrdist 13'

# mult = '--mult 1'
# mult = '--mult 4'
mult = '--mult 5'
# after this, negative or pnl goes down

# Optimized
# os.system(f'python3 backtest.py {macd} --fromdate 2019-5-1 --todate 2021-5-1 {atrdist}')
# os.system(f'python3 backtest.py {macd} --fromdate 2018-4-1 --todate 2019-4-1 {atrdist}')
# os.system(f'python3 backtest.py {macd} {atrdist}')

# date = '--fromdate 2019-5-1 --todate 2021-5-1'
# date = '--fromdate 2018-4-1 --todate 2019-4-1'
date = ''

#Best so far
os.system(f'python3 backtest.py {macd} {atrdist} {mult} {date}')

# python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --atrdist 5 --mult 5
# python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --atrdist 5 --mult 5 --fromdate 2019-5-1 --todate 2021-5-1 
# python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --atrdist 5 --mult 5 --fromdate 2018-4-1 --todate 2019-4-1
