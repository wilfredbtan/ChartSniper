import os

bear_date='--fromdate 2018-2-1 --todate 2019-2-1'
crab_date='--fromdate 2019-5-12 --todate 2020-5-12'
bull_date='--fromdate 2020-6-9 --todate 2021-6-9'
# 1 minute range
all_minute_date='--fromdate 2019-9-8 --todate 2021-6-9'
# hourly range
all_hourly_date='--fromdate 2018-1-20 --todate 2021-6-9'

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


# All time
# Buggy leverage
macd = '--macd1 9 --macd2 21 --macdsig 8' # Does even better when shorts are divided by 2 and is buggy lol
# Actual
# macd = '--macd1 10 --macd2 16 --macdsig 5'

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
reversal_sensitivity = '--reversal_sensitivity 17'
# reversal_sensitivity = '--reversal_sensitivity 0'

# date = bear_date
# date = crab_date
# date = bull_date
# date = all_date
date = all_minute_date
# date = ''

short_perc = '--short_perc 1'


# Optimization
# print("===== Bear =====")
# os.system(f'python3 backtest.py -o {bear_date}')
# print("===== Crab =====")
# os.system(f'python3 backtest.py -o {crab_date}')
# print("===== Bull =====")
# os.system(f'python3 backtest.py -o {bull_date}')
print("===== All =====")
os.system(f'python3 backtest.py -o')
# print("===== Test =====")
# os.system(f'python3 backtest.py -o {date}')

# Individual tests
# Dividing short amount by 2 makes the profit much higher. Maybe more reliable for longs
# print("===== Bear =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {bear_date} {reversal_sensitivity} {short_perc}')
# print("===== Crab =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {crab_date} {reversal_sensitivity} {short_perc}')
# print("===== Bull =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {bull_date} {reversal_sensitivity} {short_perc}')
# print("===== All =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {short_perc} {reversal_sensitivity}')
# print("===== Test =====")
# os.system(f'python3 backtest.py {macd} {atrdist} {leverage} {short_perc} {reversal_sensitivity} {date}')

'''
### Short percentage
======= Non-Buggy Code (invests 50% of cash AFTER closing) =======
MACD 10, 16, 5

Bear:
[0.002426131419722992, 3111.21, 37]
[0.002425724241959075, 3110.35, 36]
[0.0024255557450334163, 3110.08, 38]
[0.0024243380393475632, 3107.53, 35]
[0.002423992847714904, 3106.98, 39]

Crab:
[0.010754108932875994, 77363.39, 99]
[0.010740809579583142, 77069.55, 98]
[0.010727048039014213, 76766.55, 97]
[0.010712824323291879, 76454.48, 96]
[0.010698138423723582, 76133.45, 95]

Bull:
[0.0019911886779043616, 5087.2, 79]
[0.0019911164798004093, 5086.99, 78]
[0.0019911006198658995, 5086.94, 80]
[0.001990885077401584, 5086.29, 77]
[0.0019908512568285854, 5086.2, 81]

All:
[0.004769127724817423, 305745.36, 62]
[0.004768957552490342, 305701.86, 63]
[0.0047687326137722365, 305643.74, 61]
[0.004768218457123885, 305512.36, 64]
[0.0047677757195374055, 305398.04, 60]

======= Buggy Code (invests 50% of remaining cash BEFORE closing) ========
MACD 9, 21, 8

Bear:
[0.00594613012457821, 16394.62, 53]
[0.005945951537581754, 16393.63, 52]
[0.005945513398944423, 16390.75, 54]
[0.0059449848770483475, 16387.8, 51]
[0.00594409379260695, 16381.96, 55]

Bear + 4 mths offset: (CRAB)
[0.011084137810392088, 84188.41, 88]
[0.011084082819054129, 84187.12, 89]
[0.011084037836962475, 84186.01, 87]
[0.011083872841446461, 84182.16, 90]
[0.011083782912085812, 84179.94, 86]

Bear + 10 mths offset: (BULL)
[0.00966615119725151, 55839.12, 1]
[0.009653202023853493, 55624.52, 2]
[0.00964016127093701, 55409.12, 3]
[0.009627027061954256, 55192.9, 4]
[0.009613797515847329, 54975.84, 5]

Crab:
[0.00691370360403633, 23376.83, 1]
[0.006877284107558368, 23083.12, 2]
[0.006840857763851995, 22792.29, 3]
[0.006804422747411869, 22504.3, 4]
[0.006767977222510569, 22219.12, 5]

Crab + 7 mths offset: (BEAR to start of BULL)
[0.004306866740012978, 8452.57, 1]
[0.004252811030908962, 8249.49, 2]
[0.004198546126729481, 8049.05, 3]
[0.00414406565746612, 7851.22, 4]
[0.004089362992559101, 7655.97, 5]

Bull:
[0.006090978579890741, 16923.43, 1]
[0.006070469092223557, 16796.24, 2]
[0.006049963644451918, 16669.8, 3]
[0.0060294606844541925, 16544.11, 4]
[0.006008958648571697, 16419.14, 5]

All:
[0.006824609430332208, 1596735.91, 1]
[0.006810334174131253, 1579133.46, 2]
[0.0067957805859195355, 1561380.77, 3]
[0.006780948497874229, 1543486.65, 4]
[0.006765837687587215, 1525459.87, 5]


Single Values:
======== Buggy =========

### 1 perc
===== Bear =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 16225.48
Profit 224.510%
===== Crab =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 29699.76
Profit 493.995%
===== Bull =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 21018.11
Profit 320.362%
===== All =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 1599219.79
Profit 31884.396%

### 99 perc
===== Bear =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 15746.93
Profit 214.939%
===== Crab =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 14710.18
Profit 194.204%
===== Bull =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 10994.35
Profit 119.887%
===== All =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 214777.96
Profit 4195.559%


======= Non-buggy =======
### 1 perc
===== Bear =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 6962.76
Profit 39.255%
===== Crab =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 19668.45
Profit 293.369%
===== Bull =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 8751.48
Profit 75.030%
===== All =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 85215.72
Profit 1604.314%

### 99 perc
===== Bear =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 4609.37
Profit -7.813%
===== Crab =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 81993.41
Profit 1539.868%
===== Bull =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 10013.29
Profit 100.266%
===== All =====
Starting Portfolio Value: 5000.00
Final Portfolio Value: 214252.60
Profit 4185.052%
'''