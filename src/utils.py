import os
import requests
import pandas as pd
from datetime import datetime
from config import ENV, PRODUCTION, TELEGRAM
from telegram_bot import Telegram_Bot

def create_dir(name):
    current_directory = os.getcwd()
    directory = os.path.join(current_directory, name)
    os.makedirs(directory, exist_ok=True)

def get_formatted_datetime_str(unix, format='%Y-%m-%d %H:%M:%S'):
    return datetime.utcfromtimestamp(unix).strftime(format)

def reverse_and_clean(input_name, output_name):
    # load csv and use row 0 as headers
    df = pd.read_csv(input_name, header = 0)

    df['unix'] = [x/1000 if x > 10000000000 else x for x in df['unix']]
    dt = [get_formatted_datetime_str(x) for x in df['unix']]

    df.insert(loc=0, column='datetime', value=dt)
    df.drop_duplicates(subset='datetime', inplace=True)

    # reverse data and save
    df=df.iloc[::-1]
    df.set_index('datetime', inplace=True)
    df.to_csv(output_name)

# filename = 'binance_BTCUSDT_1h.csv'
# reverse_and_clean(input_name=f'./src/crypto/{filename}', output_name=f'./src/crypto/reversed_{filename}')

def get_trade_analysis(analyzer):
    # Get the results we are interested in
    if (not analyzer.get("total") or 
        analyzer['total']['total'] == 0 or 
        not isinstance(analyzer.pnl.net.total, float)):
        return "No trades"

    total_open = analyzer.total.open
    total_closed = analyzer.total.closed
    total_won = analyzer.won.total
    total_lost = analyzer.lost.total
    win_streak = analyzer.streak.won.longest
    lose_streak = analyzer.streak.lost.longest
    pnl_net = round(analyzer.pnl.net.total, 2)
    strike_rate = round((total_won / total_closed) * 2)

    # Designate the rows
    h1 = ['Total Open', 'Total Closed', 'Total Won', 'Total Lost']
    h2 = ['Strike Rate', 'Win Streak', 'Losing Streak', 'PnL Net']
    r1 = [total_open, total_closed, total_won, total_lost]
    r2 = [strike_rate, win_streak, lose_streak, pnl_net]

    # Check which set of headers is the longest.
    if len(h1) > len(h2):
        header_length = len(h1)
    else:
        header_length = len(h2)

    # Print the rows
    print_list = [h1, r1, h2, r2]
    row_format = "{:<15}" * (header_length + 1)
    txt = "Trade Analysis Results:"
    for row in print_list:
        txt += '\n' + row_format.format('', *row)
    return txt


def get_sqn(analyzer):
    sqn = round(analyzer.sqn, 2)
    return 'SQN: {}'.format(sqn)


def send_telegram_message(message="", parse_mode=None):
    base_url = "https://api.telegram.org/bot%s" % TELEGRAM.get("bot")
    params = {
        'chat_id': TELEGRAM.get("chat_id"),
        'text': message,
    }
    if parse_mode is not None:
        params['parse_mode'] = parse_mode

    return requests.get(f"{base_url}/sendMessage", params=params)

if ENV == PRODUCTION:
    response = send_telegram_message("== Initializing utils ==")
    if not response.json()['ok']:
        bot = Telegram_Bot()
        bot.run()
