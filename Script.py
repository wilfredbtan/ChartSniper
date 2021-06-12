import os

bear_date='--fromdate 2018-2-1 --todate 2019-2-1'
crab_date='--fromdate 2019-5-12 --todate 2020-5-12'
bull_date='--fromdate 2020-6-9 --todate 2021-6-9'

# print("Bear")
# os.system(f'python3 backtest.py -o {bear_date}')
# print("Crab")
# os.system(f'python3 backtest.py -o {crab_date}')
# print("Bull")
# os.system(f'python3 backtest.py -o {bull_date}')
# print("All")
# os.system(f'python3 backtest.py -o')

'''Reversal Sensitivity (MACD 9 21 8)'''
'''Thesis: A higher sensitivity works better in Bear and Bull markets. In Crab markets, lower sensitivity is better'''
'''Bear'''
# [0.00689532458065956, 23059.75, 17]
# [0.00670548433260313, 21581.89, 18]
# [0.00479636656754293, 10402.44, 19]
# [0.00411938793302593, 7728.08, 16]
# [-0.0003643100295929, -260.26, 15]
'''Actual bear'''
# [-0.0016600588198649232, -1425.24, 15]
# [-0.0018266707526717265, -1601.31, 16]
# [-0.0023339945466556745, -2200.05, 12]
# [-0.0023747166871661155, -2255.5, 14]
# [-0.0024488166673242947, -2361.15, 10]
'''Crab'''
# [0.008231021826217133, 36213.43, 4]
# [0.007368975139523879, 27288.03, 7]
# [0.007210632906502871, 25878.22, 5]
# [0.007066154944201103, 24643.34, 3]
# [0.00614901817524631, 17784.02, 6,]
'''Actual Crab'''
# [0.0017496608704953912, 1918.29, 19]
# [0.0015872308551880465, 1669.65, 3]
# [0.0006500736933698177, 529.12, 2]
# [-4.778438668193305e-05, -32.78, 1]
# [-0.00012415591598542773, -85.3, 5]
'''Bull'''
# [0.004879668529526089, 10558.76, 18]
# [0.004026607805554393, 7268.01, 17]
# [0.0037715048078425183, 6440.62, 19]
# [0.0008436769131072008, 712.61, 16]
# [-0.00019070770202055432, -129.01, 14]
'''Actual Bull'''
# [0.006891836680689853, 22504.62, 19]
# [0.006882193923036234, 22429.86, 18]
# [0.006072088781823609, 16808.63, 16]
# [0.006030048899157235, 16550.16, 17]
# [0.00353757174518233, 5743.27, 15]

'''MACD (reversal 19)'''
'''Bear'''
# [0.001889897967533443, 2137.44, 9, 15, 7]
# [0.0015410227879997366, 1599.28, 10, 16, 6]
# [0.0014690954025456705, 1497.52, 11, 14, 6]
# [0.0011527123511725981, 1081.86, 10, 14, 7]
# [0.0010356152207866866, 942.38, 9, 16, 7]
'''Crab'''
# [0.01136928355607498, 92054.78, 7, 14, 8]
# [0.01136928355607498, 92054.78, 8, 14, 7]
# [0.011351657105664917, 91601.55, 7, 16, 7]
# [0.01121950894212342, 88275.78, 7, 20, 5]
# [0.010766946065870878, 77647.95, 10, 16, 5]
'''Bull'''
# [0.009903147490187005, 58231.01, 11, 24, 8]
# [0.008785637998736709, 41640.28, 11, 25, 8]
# [0.008577067920400056, -4730.94, 7, 17, 5]
# [0.008014888912193095, 32684.91, 11, 17, 8]
# [0.0071237647755424665, 24363.25, 11, 22, 8]
'''All Time'''
# [0.004314087757964757, 207620.89, 10, 16, 5]
# [0.0037406937285448818, 124757.59, 11, 25, 8]
# [0.003494007806609151, 99527.3, 10, 18, 8]
# [0.003488842070251906, 99083.73, 7, 14, 8]
# [0.003488842070251906, 99083.73, 8, 14, 7]


# os.system('python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --fromdate 2019-5-1 --todate 2021-5-1')
# os.system('python3 backtest.py --macd1 11 --macd2 24 --macdsig 7 --fromdate 2018-4-1 --todate 2019-4-1')

''' Optimize for MACD. 9 21 8 seems the best for some reason lol'''
    # From 2018
# [0.004494863323081424, 9138.15, 5.0, 11, 25, 5]
# [0.0044013609731506425, 8771.79, 5.0, 11, 24, 7]
# [0.004198101472410856, 8006.65, 5.0, 11, 24, 5]
# [0.00398634725384348, 7261.15, 5.0, 10, 25, 5]
# [0.003786650116149551, 6602.89, 5.0, 10, 25, 7]

    # From 2019
# [0.002273390385830033, 9361.07, 5.0, 8, 25, 8]
# [0.002271509188889601, 9345.8, 5.0, 9, 21, 8]
# [0.002271509188889601, 9345.8, 5.0, 11, 20, 7]
# [0.002255731406488645, 9218.39, 5.0, 9, 22, 8]
# [0.0022306759365417917, 9018.59, 5.0, 10, 21, 7]

'''Optimize for ATR Dist (stop loss). 5 seems the best'''
    # From 2018
# [0.006238160707605604, 18257.07, 3, 9, 21, 8]
# [0.0060935861363389, 17314.97, 5, 9, 21, 8]
# [0.005703345674420665, 14954.11, 6, 9, 21, 8]
# [0.005636240010576195, 14574.94, 7, 9, 21, 8]
# [0.005598026217405897, 14360.11, 4, 9, 21, 8]

    # From 2019
# [0.004006155367781593, 33566.28, 13, 9, 21, 8]
# [0.003799702182121598, 29330.16, 5, 9, 21, 8]
# [0.0037421759269827023, 28230.39, 14, 9, 21, 8]
# [0.003465500011171479, 23395.88, 7, 9, 21, 8]
# [0.003263669278174703, 20304.24, 8, 9, 21, 8]

# Default
# macd = '--macd1 12 --macd2 26 --macdsig 9'
# 2018
# macd = '--macd1 11 --macd2 25 --macdsig 5'
# 2019
# macd = '--macd1 9 --macd2 23 --macdsig 8'
# All time
# macd = '--macd1 9 --macd2 21 --macdsig 8'
macd = '--macd1 10 --macd2 16 --macdsig 5'

atrdist = '--atrdist 5'
# atrdist = '--atrdist 3'
# atrdist = '--atrdist 13'

# leverage = '--leverage 1'
# leverage = '--leverage 4'
leverage = '--leverage 5'
# leverage = '--leverage 6'
# leverage = '--leverage 7'
# only for default MACD
# leverage = '--leverage 13'
# after this, negative or pnl goes down

# reversal_sensitivity = '--reversal_sensitivity 20'
reversal_sensitivity = '--reversal_sensitivity 19'


# Optimized
# os.system(f'python3 backtest.py {macd} --fromdate 2019-5-1 --todate 2021-5-1 {atrdist}')
# os.system(f'python3 backtest.py {macd} --fromdate 2018-4-1 --todate 2019-4-1 {atrdist}')
# os.system(f'python3 backtest.py {macd} {atrdist}')

date = bear_date
# date = crab_date
# date = bull_date
# date = ''

#Best so far
# Dividing short amount by 2 makes the profit much higher. Maybe more reliable for longs
print("===== Bear =====")
os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {bear_date} -v')
# print("===== Crab =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {crab_date}')
# print("===== Bull =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {bull_date}')
# print("===== All =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage}')

# python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --atrdist 5 --leverage 5
# python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --atrdist 5 --leverage 5 --fromdate 2019-5-1 --todate 2021-5-1 
# python3 backtest.py --macd1 9 --macd2 21 --macdsig 8 --atrdist 5 --leverage 5 --fromdate 2018-4-1 --todate 2019-4-1
