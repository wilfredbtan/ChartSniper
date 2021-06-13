import xlsxwriter
import pandas as pd

my_columns = ['Ticker', 'Price', 'One-Year Price Return', 'Number of Shares to Buy']

def get_df_row(results, param_names):
    row = {}
    for name in param_names:
        print('results', results)
        if name in results:
            row[name] = results[name]
        else:
            row[name] = results['params'].__dict__[name]
    return row


def save_to_dataframe(dataframe, results):

    df = pd.DataFrame([[1,2,3,4]], columns=my_columns)

    rows = []

    for symbol_string in symbol_strings:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=price,stats&token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(batch_api_call_url).json()
        for symbol in symbol_string.split(','):
            d = {
                'Ticker': symbol,
                'Price': data[symbol]['price'],
                'Number of Shares to Buy': 'N/A',
                'One-Year Price Return': data[symbol]['stats']['year1ChangePercent'],
                'One-Year Return Percentile': 'N/A',
                'Six-Month Price Return': data[symbol]['stats']['month6ChangePercent'],
                'Six-Month Return Percentile': 'N/A',
                'Three-Month Price Return': data[symbol]['stats']['month3ChangePercent'],
                'Three-Month Return Percentile': 'N/A',
                'One-Month Price Return': data[symbol]['stats']['month1ChangePercent'],
                'One-Month Return Percentile': 'N/A',
                'HQM Score': 'N/A'
            }
            
            rows.append(d)

    hqm_dataframe = pd.DataFrame(rows, columns=hqm_columns)
    hqm_dataframe

    hqm_dataframe.sort_values('HQM Score', ascending=False, inplace=True)
    hqm_dataframe = hqm_dataframe[:50]
    hqm_dataframe.reset_index(inplace=True, drop=True)
    hqm_dataframe

def save_dataframe_to_excel(dataframe, filename, sheetname):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    dataframe.to_excel(writer, sheet_name=sheetname, index = False)

    background_color = '#0a0a23'
    font_color = '#ffffff'

    string_template = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    dollar_template = writer.book.add_format(
            {
                'num_format':'$0.00',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    integer_template = writer.book.add_format(
            {
                'num_format':'0',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    percent_template = writer.book.add_format(
            {
                'num_format':'0.0%',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    column_formats = {
        'A': ['Ticker', string_template],
        'B': ['Price', dollar_template],
        'C': ['Number of Shares to Buy', integer_template],
        'D': ['One-Year Price Return', percent_template],
        'E': ['One-Year Return Percentile', percent_template],
        'F': ['Six-Month Price Return', percent_template],
        'G': ['Six-Month Return Percentile', percent_template],
        'H': ['Three-Month Price Return', percent_template],
        'I': ['Three-Month Return Percentile', percent_template],
        'J': ['One-Month Price Return', percent_template],
        'K': ['One-Month Return Percentile', percent_template],
        'L': ['HQM Score', percent_template]
    }

    for column in column_formats.keys():
        writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 25, column_formats[column][1])
        writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], column_formats[column][1])

    writer.save()