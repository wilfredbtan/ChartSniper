import os

short_bull_date='--fromdate 2017-8-18 --todate 2018-12-18'
bear_date='--fromdate 2018-2-1 --todate 2019-2-1'
crab_date='--fromdate 2019-5-12 --todate 2020-5-12'
bull_date='--fromdate 2020-6-9 --todate 2021-6-9'
# 1 minute range
all_minute_date='--fromdate 2019-9-9 --todate 2021-6-9'
# hourly range
all_hourly_date='--fromdate 2017-8-18 --todate 2021-6-9'

cash = '--cash 5000'

cashperc = '--cashperc 50'

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

# reversal_lowerband = '--reversal_lowerband 50'
reversal_lowerband = '--reversal_lowerband 43'

# reversal_upperband = '--reversal_upperband 50'
reversal_upperband = '--reversal_upperband 48'

rsi_upperband = '--rsi_upperband 45'
# rsi_upperband = '--rsi_upperband 50'

rsi_lowerband = '--rsi_lowerband 49'
# rsi_lowerband = '--rsi_lowerband 50'

# lp_buffer_mult = '--lp_buffer_mult 1.54'
lp_buffer_mult = '--lp_buffer_mult 6.5'
# lp_buffer_mult = '--lp_buffer_mult 7.5'
# lp_buffer_mult = '--lp_buffer_mult 8.5'
# lp_buffer_mult = '--lp_buffer_mult 10'
# lp_buffer_mult = '--lp_buffer_mult 12.1'
# lp_buffer_mult = '--lp_buffer_mult 9.2'

# Optimization
# print("===== Short Bull (4 mths) =====")
# os.system(f'python3 backtest.py -o {short_bull_date}')
print("===== Bear =====")
os.system(f'python3 backtest.py -o {bear_date}')
print("===== Crab =====")
os.system(f'python3 backtest.py -o {crab_date}')
print("===== Bull =====")
os.system(f'python3 backtest.py -o {bull_date}')
print("===== All =====")
os.system(f'python3 backtest.py -o {all_hourly_date}')
# print("===== Test =====")
# os.system(f'python3 backtest.py -o {date}')

# Individual tests
# print("===== Short Bull (4 mths) =====")
# os.system(f'python3 backtest.py {lp_buffer_mult} {cash} {cashperc} {macd} {macd} {rsi_upperband} {rsi_lowerband} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {short_bull_date} {reversal_sensitivity}')
# print("===== Bear =====")
# os.system(f'python3 backtest.py {lp_buffer_mult} {cash} {cashperc} {macd} {rsi_upperband} {rsi_lowerband} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {bear_date} {reversal_sensitivity}')
# print("===== Crab =====")
# os.system(f'python3 backtest.py {lp_buffer_mult} {cash} {cashperc} {macd} {rsi_upperband} {rsi_lowerband} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {crab_date} {reversal_sensitivity}')
# print("===== Bull =====")
# os.system(f'python3 backtest.py {lp_buffer_mult} {cash} {cashperc} {macd} {rsi_upperband} {rsi_lowerband} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {bull_date} {reversal_sensitivity}')
# print("===== All =====")
# os.system(f'python3 backtest.py {lp_buffer_mult} {cash} {cashperc} {macd} {rsi_upperband} {rsi_lowerband} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {reversal_sensitivity}')
# print("===== Custom =====")
# os.system(f'python3 backtest.py {lp_buffer_mult} {cash} {cashperc} {macd} {rsi_upperband} {rsi_lowerband} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {reversal_sensitivity} {date} -d')

# print("===== Multiple Runs =====")
# os.system(f'python3 multiple_runs.py {lp_buffer_mult} {cash} {cashperc} {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {reversal_sensitivity}')

# buffer_mult_range = [1.54, 7.5, 9.2, 10.4]
# buffer_mult_range = [x * 0.1 for x in range(60, 70)]
# for b in buffer_mult_range:
#     buf_arg = f'--lp_buffer_mult {b}'
#     print(buf_arg)
#     os.system(f'python3 multiple_runs.py {buf_arg} {cash} {cashperc} {macd} {reversal_lowerband} {reversal_upperband} {atrdist} {leverage} {reversal_sensitivity}')

'''
### Multiple run LP_BUFFER = [x * 0.1 for x in range(70, 80)]
# BEST
1st of each month
--lp_buffer_mult 7.8
+++++ Final Result +++++
PNL:
    min:  2327.51
    max:  126661.41
    avg:  34063.86
    std:  29949.85
SQN:
    min:  0.33
    max:  2.23
    avg:  1.29
    std:  0.51
TRADES:
    min:  19.00
    max:  36.00
    avg:  27.36
    std:  4.34
 - Anything below or above has a lower average PNL. SQNs are relatively the same

15th of each month
--lp_buffer_mult 7.9
ILLEGAL SELL STOP. stop price lower than close
- 1 illegal sell stop
+++++ Final Result +++++
PNL:
    min:  2607.15
    max:  121509.57
    avg:  30168.68
    std:  24979.88
SQN:
    min:  0.35
    max:  2.28
    avg:  1.26
    std:  0.49
TRADES:
    min:  18.00
    max:  37.00
    avg:  27.30
    std:  4.37

### Multiple run LP_BUFFER = [1.54, 7.5, 9.2, 10.4]
--lp_buffer_mult 1.54
+++++ Final Result +++++
PNL:
    min:  1513.76
    max:  126661.41
    avg:  30237.27
    std:  27049.11
SQN:
    min:  0.26
    max:  2.23
    avg:  1.20
    std:  0.52
TRADES:
    min:  19.00
    max:  36.00
    avg:  27.36
    std:  4.34
--lp_buffer_mult 7.5
+++++ Final Result +++++
PNL:
    min:  2327.51
    max:  126661.41
    avg:  33608.08
    std:  29507.70
SQN:
    min:  0.33
    max:  2.23
    avg:  1.28
    std:  0.51
TRADES:
    min:  19.00
    max:  36.00
    avg:  27.36
    std:  4.34
--lp_buffer_mult 9.2
+++++ Final Result +++++
PNL:
    min:  2522.47
    max:  130362.70
    avg:  32949.31
    std:  29506.43
SQN:
    min:  0.35
    max:  2.23
    avg:  1.28
    std:  0.52
TRADES:
    min:  19.00
    max:  35.00
    avg:  27.24
    std:  4.15
--lp_buffer_mult 10.4
+++++ Final Result +++++
PNL:
    min: -4688.36   // NEGATIVE
    max:  126661.41
    avg:  27431.94
    std:  28348.16
SQN:
    min: -0.67      // NEGATIVE
    max:  2.23
    avg:  1.03
    std:  0.79
TRADES:
    min:  19.00
    max:  36.00
    avg:  27.36
    std:  4.34

### LP_BUFFER_MULT optimization [self.broker.cash]
===== Bear =====
[1.828262354020209, 106649.83, 4.9]
[1.8273766602630874, 106252.95, 4.800000000000001]
[1.8264740503951247, 105856.07, 4.7]
[1.82555425084278, 105459.19, 4.6000000000000005]
[1.8246169836698451, 105062.31, 4.5]

===== Crab =====
[1.050498065548794, 22691.32, 3.8000000000000003]
[1.0472984571503063, 22459.1, 3.7]
[1.0440416869695934, 22227.83, 3.6]
[1.0407267011497372, 21997.52, 3.5]
[1.0373524290950702, 21768.17, 3.4000000000000004]

===== Bull =====
[1.602988946593663, 43570.9, 1.8]
[1.6000623943414471, 43264.52, 1.7000000000000002]
[1.5970788064398056, 42958.13, 1.6]
[1.5940370098146077, 42651.75, 1.5]
[1.590935808031972, 42345.36, 1.4000000000000001]

===== All =====
[1.712561246496831, 2551996.11, 1.5]
[1.711034893107466, 2536249.96, 1.4000000000000001]
[1.7094677733237411, 2520503.81, 1.3]
[1.707858905304888, 2504757.66, 1.2000000000000002]
[1.7062072838389095, 2489011.51, 1.1]

### [self.broker.value]
lp_buffer_mult=[x * 0.1 for x in range(0, 200)],
===== Bear =====
[1.843673897978302, 128876.92, 18.2]
[1.838701212859677, 126935.01, 18.1]
[1.8335841363539305, 125011.63, 18.0]
[1.8283188747968124, 123106.7, 17.900000000000002]
[1.822901557353176, 121220.14, 17.8]

===== Crab =====
[1.41279790243275, 34472.9, 13.8]
[1.406869860930418, 34051.24, 13.700000000000001]
[1.4008081362647455, 33631.59, 13.600000000000001]
[1.3946103125476348, 33213.94, 13.5]
[1.3882739653037084, 32798.31, 13.4]

===== Bull =====
[1.5320716334643953, 37436.44, 0.0]
[1.5320716334643953, 37436.44, 0.1]
[1.5320716334643953, 37436.44, 0.2]
[1.5320716334643953, 37436.44, 0.30000000000000004]
[1.5320716334643953, 37436.44, 0.4]

===== All =====
[1.6671323320922486, 10243928.61, 10.4]
[1.6669336792120624, 9672323.85, 10.3]
[1.6668466767324304, 9307748.97, 10.200000000000001]
[1.6667558555001782, 8953528.04, 10.100000000000001]
[1.666661015393584, 8609463.15, 10.0]

### FIXED (stop loss not below/above close) [self.broker.value]
lp_buffer_mult=[x * 0.1 for x in range(0, 300)],
===== Bear =====
[1.8948760740098836, 121213.09, 20.3]
[1.8925447482415114, 119870.91, 20.200000000000003]
[1.8901332496493972, 118534.94, 20.1]
[1.8876388016927466, 117205.17, 20.0]
[1.8861783208410845, 116360.62, 19.900000000000002]

===== Crab =====
[1.41279790243275, 34472.9, 13.8]
[1.406869860930418, 34051.24, 13.700000000000001]
[1.4008081362647455, 33631.59, 13.600000000000001]
[1.3946103125476348, 33213.94, 13.5]
[1.3882739653037084, 32798.31, 13.4]

===== Bull =====
[1.7510858604041057, 69400.05, 18.5]
[1.6977527206772407, 56533.74, 16.8]
[1.6938552374375657, 55814.91, 16.7]
[1.6898578540152327, 55100.3, 16.6]
[1.6857577959942658, 54389.91, 16.5]

===== All =====
[1.6658262398559842, 6649538.46, 9.200000000000001]
[1.665703357123872, 6439317.89, 9.1]
[1.6655751996422286, 6233543.39, 9.0]
[1.6654414934906678, 6032167.44, 8.9]
[1.6653019472952635, 5835142.55, 8.8]

### FIXED (stop loss not below/above close AND stop loss set after order submitted) [self.broker.value]
lp_buffer_mult=[x * 0.1 for x in range(0, 200)],
------ optimize based on PnL -------
===== Bear =====
[1.8465360964956747, 112554.78, 19.900000000000002]
[1.8460449125094731, 112153.84, 19.8]
[1.845541257732617, 111752.89, 19.700000000000003]
[1.845024912098283, 111351.94, 19.6]
[1.8444956516940434, 110950.99, 19.5]
--- 62.71393013000488 seconds ---
===== Crab =====
[1.3979656004203052, 33043.53, 13.600000000000001]
[1.391955986881827, 32638.23, 13.5]
[1.3858135296149492, 32234.85, 13.4]
[1.379535871594831, 31833.41, 13.3]
[1.3731206485713245, 31433.9, 13.200000000000001]
--- 67.9794328212738 seconds ---
===== Bull =====
[1.509338760282926, 35864.04, 12.0]
[1.5085532363614238, 35810.74, 0.0]
[1.5085532363614238, 35810.74, 0.1]
[1.5085532363614238, 35810.74, 0.2]
[1.5085532363614238, 35810.74, 0.30000000000000004]
--- 68.49380803108215 seconds ---
===== All =====
[1.6494252886698673, 5137181.68, 8.200000000000001]
[1.6493882214210531, 5024897.97, 8.1]
[1.6493498956918118, 4913852.55, 8.0]
[1.6493102538196305, 4804045.41, 7.9]
[1.6492692347983264, 4695476.56, 7.800000000000001]







### Multiple runs 50% Cashperc
# self.broker.cash as liquidation
# Higher value may be due to broker.cash being more conservative i.e. when a position is open
# But broker.getvalue() is more accurate for the strategy
PNL:
    min:  2087.45
    max:  126661.41
    avg:  30805.87
    std:  27224.98
SQN:
    min:  0.33
    max:  2.23
    avg:  1.22
    std:  0.50
TRADES:
    min:  19.00
    max:  36.00
    avg:  27.36
    std:  4.34
  - No negative!
  - Best

# self.broker.value as liquidation
+++++ Final Result +++++
PNL:
    min:  1513.76
    max:  126661.41
    avg:  30237.27
    std:  27049.11
SQN:
    min:  0.26
    max:  2.23
    avg:  1.20
    std:  0.52
TRADES:
    min:  19.00
    max:  36.00
    avg:  27.36
    std:  4.34


### CMF 
cmf_upperband=range(2,9),
cmf_lowerband=range(-20,-9),

===== All =====
[1.2110214162475912, 1234429.67, 3, -10]
[1.2110214162475912, 1234429.67, 4, -10]
[1.2110214162475912, 1234429.67, 5, -10]
[1.2094826850703917, 420985.07, 7, -10]
[1.207309551765614, 682685.78, 3, -13]


With extra multiplier
+++++ Final Result +++++
Avg SQN:  0.80
Avg pnl:  20739.30
Avg trades:  23.18
--- 210.8942849636078 seconds ---

Without, 2 datasets
+++++ Final Result +++++
Avg SQN:  0.79
Avg pnl:  20209.80
Avg trades:  23.18
--- 209.44411492347717 seconds ---

Without, 1 dataset
+++++ Final Result +++++
Avg SQN:  0.80
Avg pnl:  21263.67
Avg trades:  23.52
--- 50.27589416503906 seconds ---


### RSI upper and lowerband: 
===== All Hourly =====
(40, 55): RSI > upperband ; RSI < lowerband
[1.139936767238418, 485637.1, 46, 48]
[1.139936767238418, 485637.1, 47, 48]
[1.139936767238418, 485637.1, 48, 48]
[1.1361779205317526, 222614.39, 45, 45]
[1.1360687646543994, 794446.99, 45, 48]

(40, 55): RSI < upperband ; RSI > lowerband
- Why is the upperband band lower than the lower band lol
[1.681991810795637, 572973.07, 45, 49]
[1.681991810795637, 572973.07, 45, 50]
[1.681991810795637, 572973.07, 45, 51]
[1.681991810795637, 572973.07, 46, 49]
[1.681991810795637, 572973.07, 46, 50]]

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