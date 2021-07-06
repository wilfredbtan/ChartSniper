import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTION = "production"
DEVELOPMENT = "development"

SANDBOX = True
ENV = os.getenv("ENVIRONMENT", PRODUCTION)
DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY")

'''
BINANCE
'''
# PROD_BINANCE_API_KEY=os.environ.get("PROD_BINANCE_API_KEY")
# PROD_BINANCE_SECRET=os.environ.get("PROD_BINANCE_SECRET")

# BINANCE = {
#   "key": PROD_BINANCE_API_KEY,
#   "secret": PROD_BINANCE_SECRET
# }

# COIN_TARGET = "BTC"
# COIN_REFER = "USDT"

TEST_BINANCE_FUTURE_API_KEY=os.environ.get("TEST_BINANCE_FUTURE_API_KEY")
TEST_BINANCE_FUTURE_SECRET=os.environ.get("TEST_BINANCE_FUTURE_SECRET")

BINANCE = {
  "name": "binanceusdm",
  "key": TEST_BINANCE_FUTURE_API_KEY,
  "secret": TEST_BINANCE_FUTURE_SECRET,
  "coin_target": "BTC",
  "coin_refer": "USDT"
}


'''
BITFINEX
'''
# COIN_TARGET = "TESTBTC"
# COIN_REFER = "TESTUSDT"

# COIN_TARGET = "TESTBTCF0"
# COIN_REFER = "TESTUSDTF0"

TEST_BITFINEX_API_KEY=os.environ.get("TEST_BITFINEX_API_KEY")
TEST_BITFINEX_SECRET=os.environ.get("TEST_BITFINEX_SECRET")

BITFINEX = {
  "name": "bitfinex2",
  "key": TEST_BITFINEX_API_KEY,
  "secret": TEST_BITFINEX_SECRET,
  "coin_target": "TESTBTCF0",
  "coin_refer": "TESTUSDTF0",
  "balance_type": "derivatives"
}

'''
KRAKEN (NOT FULLY WORKING)
'''
# COIN_TARGET = "BTC"
# COIN_REFER = "USDT"

# TEST_KRAKEN_API_KEY=os.environ.get("TEST_KRAKEN_API_KEY")
# TEST_KRAKEN_SECRET=os.environ.get("TEST_KRAKEN_SECRET")

# KRAKEN = {
#   "name": "kraken",
#   "key": TEST_KRAKEN_API_KEY,
#   "secret": TEST_KRAKEN_SECRET,
#   "coin_target": "BTC",
#   "coin_refer": "USDT"
# }

'''
FTX
'''

TEST_FTX_API_KEY=os.environ.get("TEST_FTX_API_KEY")
TEST_FTX_SECRET=os.environ.get("TEST_FTX_SECRET")

FTX = {
  "name": "ftx",
  "key": TEST_FTX_API_KEY,
  "secret": TEST_FTX_SECRET,
  "coin_target": "BTC",
  "coin_refer": "USDT"
}


EXCHANGE = BINANCE

TELEGRAM = {
  "chat_id": os.environ.get("TELEGRAM_CHAT_ID"),
  "bot": os.environ.get("TELEGRAM_BOT_KEY")
}

if ENV == PRODUCTION:
  print("ENV = ", ENV)