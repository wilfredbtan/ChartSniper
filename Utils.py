import pandas as pd
from datetime import datetime

def reverse_and_clean(input_name, output_name):
    # load csv and use row 0 as headers
    df = pd.read_csv(input_name, header = 0)

    df['unix'] = [x/1000 if x > 10000000000 else x for x in df['unix']]
    dt = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in df['unix']]

    df.insert(loc=0, column='datetime', value=dt)
    df.drop_duplicates(subset='datetime', inplace=True)

    # reverse data and save
    df=df.iloc[::-1]
    df.set_index('datetime', inplace=True)
    df.to_csv(output_name)

reverse_and_clean(input_name='./crypto/Binance_BTCUSDT_d.csv', output_name='./crypto/reversed_BTC_d.csv')