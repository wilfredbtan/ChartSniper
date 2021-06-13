import argparse
import logging
from Datasets import *

def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Stochastic RSI with MACD Crossover Strategy')

    parser.add_argument('--dataset', required=False, action='store',
                        default='btc_hourly', choices=DATASETS.keys(),
                        help='Choose one of the predefined data sets')

    parser.add_argument('--fromdate', required=False,
                        default='2018-02-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False,
                        default='2021-06-09',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=5000,
                        help=('Cash to start with'))

    parser.add_argument('--cashperc', required=False, action='store',
                        type=float, default=50,
                        help=('Percentage of cash to use for each trade', 
                              '20 -> 20%%, 1 -> 1%%'))

    parser.add_argument('--stake', required=False, action='store',
                        type=float, default=0.3,
                        help=('Amount of security to allocate for ops'))

    parser.add_argument('--commperc', required=False, action='store',
                        type=float, default=0.0002,
                        help=('Perc (abs) commision in each operation. '
                              '0.001 -> 0.1%%, 0.01 -> 1%%'))

    parser.add_argument('--leverage', required=False, action='store',
                        type=float, default=5,
                        help=('Leverage when using margin'))

    parser.add_argument('--margin', required=False, action='store',
                        type=float, default=1000,
                        help=('Margin required from broker'))


    # Single runs
    parser.add_argument('--macd1', required=False, action='store',
                        type=int, default=12,
                        help=('MACD Period 1 value'))

    parser.add_argument('--macd2', required=False, action='store',
                        type=int, default=26,
                        help=('MACD Period 2 value'))

    parser.add_argument('--macdsig', required=False, action='store',
                        type=int, default=9,
                        help=('MACD Signal Period value'))

    parser.add_argument('--stoch_k_period', required=False, action='store',
                        type=int, default=3,
                        help=('k for stochastic'))

    parser.add_argument('--stoch_d_period', required=False, action='store',
                        type=int, default=3,
                        help=('d for stochastic'))

    parser.add_argument('--stoch_rsi_period', required=False, action='store',
                        type=int, default=14,
                        help=('rsi period for stochastic'))

    parser.add_argument('--stoch_period', required=False, action='store',
                        type=int, default=14,
                        help=('stochastic period'))

    parser.add_argument('--stoch_upperband', required=False, action='store',
                        type=float, default=80.0,
                        help=('upperband for stochastic'))

    parser.add_argument('--stoch_lowerband', required=False, action='store',
                        type=float, default=20.0,
                        help=('lowerband for stochastic'))

    parser.add_argument('--rsi_upperband', required=False, action='store',
                        type=float, default=60.0,
                        help=('upperband for rsi'))

    parser.add_argument('--rsi_lowerband', required=False, action='store',
                        type=float, default=40.0,
                        help=('lowerband for rsi'))

    parser.add_argument('--atrperiod', required=False, action='store',
                        type=int, default=14,
                        help=('ATR Period To Consider'))

    parser.add_argument('--atrdist', required=False, action='store',
                        type=float, default=5.0,
                        help=('ATR Factor for stop price calculation'))

    parser.add_argument('--reversal_sensitivity', required=False, action='store',
                        type=float, default=20.0,
                        help=('Sensitivity for a reversal in Stoch RSI to be recognized', 
                        'Calculated as fastk - fastk'))

    parser.add_argument('--short_perc', required=False, action='store',
                        type=float, default=50,
                        help=('Percentage to short out of intended position'))

    parser.add_argument('--plot', '-p', action='store_true',
                    help='Plot the read data')

    parser.add_argument(
        '-o', '--optimize',
        action='store_const',
        const=True,
        default=False,
        help=('Optimizes the strategy over a range of parameters')
    )

    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Be verbose",
        action="store_const", dest="loglevel", const=logging.INFO,
    )
    
    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()

