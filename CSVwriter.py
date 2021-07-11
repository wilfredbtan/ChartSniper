import csv

headers = ['dtopen', 'dtclose', 'dtopen_str', 'dtclose_str', 'size', 'avg_open_price', 'avg_close_price', 'pnl', 'pnlcomm']

def create_trades_csv(filename):
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

'''
Trade data is a list according to the columns
'''
def write_trade_to_csv(filename, trade_data):
    with open(filename, 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(trade_data)