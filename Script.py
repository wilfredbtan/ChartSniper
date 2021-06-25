import os

short_bull_date='--fromdate 2017-8-18 --todate 2018-12-18'
bear_date='--fromdate 2018-2-1 --todate 2019-2-1'
crab_date='--fromdate 2019-5-12 --todate 2020-5-12'
bull_date='--fromdate 2020-6-9 --todate 2021-6-9'
# 1 minute range
all_minute_date='--fromdate 2019-9-9 --todate 2021-6-9'
# hourly range
all_hourly_date='--fromdate 2017-8-18 --todate 2021-6-9'

# All time
# Buggy leverage
macd = '--macd1 9 --macd2 21 --macdsig 8' # Does even better when shorts are divided by 2 and is buggy lol
# macd = '--macd1 8 --macd2 21 --macdsig 5' # Some youtuber lol. Does well when crabbing. Otherwise meh
# macd = '--macd1 8 --macd2 21 --macdsig 9' # test
# Top bear (NOPE)
# macd = '--macd1 8 --macd2 25 --macdsig 9'
# Top crab (NOPE)
# macd = '--macd1 7 --macd2 18 --macdsig 7'
# Top bull and all
# macd = '--macd1 8 --macd2 21 --macdsig 9'

atrdist = '--atrdist 5'
# atrdist = '--atrdist 3'
# atrdist = '--atrdist 13'

# leverage = '--leverage 1'
# leverage = '--leverage 3'
# leverage = '--leverage 4'
leverage = '--leverage 5'
# leverage = '--leverage 6'
# leverage = '--leverage 7'
# only for default MACD
# leverage = '--leverage 13'
# after this, negative or pnl goes down

# reversal_sensitivity = '--reversal_sensitivity 20'
reversal_sensitivity = '--reversal_sensitivity 17'
# reversal_sensitivity = '--reversal_sensitivity 16' #Higher SQN but lower PnL?
# reversal_sensitivity = '--reversal_sensitivity 0'

# date = bear_date
# date = crab_date
# date = bull_date
date = all_hourly_date
# date = all_minute_date
# date = ''

short_perc = '--short_perc 1'

reversal_lowerband = '--reversal_lowerband 43'
# reversal_lowerband = '--reversal_lowerband 50'

reversal_upperband = '--reversal_upperband 48'
# reversal_upperband = '--reversal_upperband 50'


# Optimization
# print("===== Short Bull (4 mths) =====")
# os.system(f'python3 backtest.py -o {short_bull_date}')
# print("===== Bear =====")
# os.system(f'python3 backtest.py -o {bear_date}')
# print("===== Crab =====")
# os.system(f'python3 backtest.py -o {crab_date}')
# print("===== Bull =====")
# os.system(f'python3 backtest.py -o {bull_date}')
# print("===== All =====")
# os.system(f'python3 backtest.py -o {all_hourly_date}')
# print("===== Test =====")
# os.system(f'python3 backtest.py -o {date}')

# Individual tests
# Dividing short amount by 2 makes the profit much higher. Maybe more reliable for longs
print("===== Short Bull (4 mths) =====")
os.system(f'python3 backtest.py {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {short_bull_date} {reversal_sensitivity} {short_perc}')
print("===== Bear =====")
os.system(f'python3 backtest.py {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {bear_date} {reversal_sensitivity} {short_perc}')
print("===== Crab =====")
os.system(f'python3 backtest.py {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {crab_date} {reversal_sensitivity} {short_perc}')
print("===== Bull =====")
os.system(f'python3 backtest.py {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {bull_date} {reversal_sensitivity} {short_perc}')
print("===== All =====")
os.system(f'python3 backtest.py {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {short_perc} {reversal_sensitivity}')
# print("===== Custom =====")
# os.system(f'python3 backtest.py {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {short_perc} {reversal_sensitivity} {date} -v')

'''
### 16 Reversal Sensitivity
===== Short Bull (4 mths) =====
[0.36963485268010376, 3069.39, 5.0, 9, 21, 8, 16.0, 43.0, 48.0]
===== Bear =====
[1.1314725590711165, 38204.56, 5.0, 9, 21, 8, 16.0, 43.0, 48.0]
===== Crab =====
[0.6021465189141539, 11233.54, 5.0, 9, 21, 8, 16.0, 43.0, 48.0]
===== Bull =====
[1.637185487209027, 22511.21, 5.0, 9, 21, 8, 16.0, 43.0, 48.0]
===== All =====
[1.8192814018516947, 200399.51, 5.0, 9, 21, 8, 16.0, 43.0, 48.0]

### 17 Reversal Sensitivity
===== Short Bull (4 mths) =====
[0.2631195710109405, 9579.55, 5.0, 9, 21, 8, 17.0, 43.0, 48.0]
===== Bear =====
[1.600384153666921, 89756.82, 5.0, 9, 21, 8, 17.0, 43.0, 48.0]
===== Crab =====
[0.6021465189141539, 11233.54, 5.0, 9, 21, 8, 17.0, 43.0, 48.0]
===== Bull =====
[1.3625423248835735, 16667.54, 5.0, 9, 21, 8, 17.0, 43.0, 48.0]
===== All =====
[1.6470884127706085, 462804.75, 5.0, 9, 21, 8, 17.0, 43.0, 48.0]

### Optimize Reversal sensitivity
===== Short Bull (4 mths) =====
[0.36963485268010376, 3069.39, 16]
[0.26383275670259937, 9590.54, 18]
[0.2631195710109405, 9579.55, 17]
[0.1772016686464381, 2689.28, 11]
[0.020464152090036748, 146.08, 15]
--- 21.543615102767944 seconds ---
===== Bear =====
[1.6012396305690584, 89828.22, 18]
[1.600384153666921, 89756.82, 17]
[1.2750854569457892, 11225.02, 13]
[1.2162907461766719, 24687.81, 15]
[1.182913442315194, 9635.55, 12]
--- 16.653862237930298 seconds ---
===== Crab =====
[0.9285724587605005, 20593.3, 14]
[0.9119122276099856, 20007.64, 13]
[0.887738524820314, 34582.04, 19]
[0.87026585852503, 17377.89, 5]
[0.8581549218065982, 17830.73, 15]
--- 17.32618808746338 seconds ---
===== Bull =====
[1.637185487209027, 22511.21, 16]
[1.3625423248835735, 16667.54, 17]
[1.2623904603644616, 19624.48, 18]
[1.0680308938759724, 10864.59, 19]
[0.4437130172902241, 2286.22, 11]
--- 17.85008978843689 seconds ---
===== All =====
[1.8192814018516947, 200399.51, 16]
[1.6470884127706085, 462804.75, 17]
[1.456917841922472, 382865.74, 18]
[1.3496677609219174, 183632.19, 19]
[0.8289398544053597, 31817.5, 11]

### Optimize MACD value for loosened crossover
===== Bear =====
[1.7280813452587378, 100386.69, 8, 25, 8]
[1.7088522463379094, 89675.55, 7, 23, 9]
[1.7088522463379094, 89675.55, 7, 24, 9]
[1.7088522463379094, 89675.55, 8, 23, 8]
[1.7088522463379094, 89675.55, 8, 24, 8]
--- 42.535221099853516 seconds ---
===== Crab =====
[0.6295844306270235, 19426.11, 7, 18, 7]
[0.6021465189141539, 11233.54, 7, 25, 9]
[0.6021465189141539, 11233.54, 8, 21, 9]
[0.6021465189141539, 11233.54, 8, 22, 9]
[0.6021465189141539, 11233.54, 8, 24, 8]
--- 44.68603301048279 seconds ---
===== Bull =====
[1.2887123073118756, 14825.69, 8, 21, 9]
[1.2887123073118756, 14825.69, 8, 22, 9]
[1.2887123073118756, 14825.69, 9, 18, 9]
[1.2887123073118756, 14825.69, 9, 19, 9]
[1.2887123073118756, 14825.69, 9, 21, 8]
--- 42.40656590461731 seconds ---
===== All =====
[1.6116111106534121, 423039.04, 8, 21, 9]
[1.6116111106534121, 423039.04, 9, 21, 8]
[1.6077561939245673, 339911.79, 8, 22, 9]
[1.6077561939245673, 339911.79, 9, 22, 8]
[1.6077561939245673, 339911.79, 11, 20, 7]


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