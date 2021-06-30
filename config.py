import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

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

TEST_BINANCE_FUTURE_API_KEY=os.environ.get("TEST_BINANCE_FUTURE_API_KEY")
TEST_BINANCE_FUTURE_SECRET=os.environ.get("TEST_BINANCE_FUTURE_SECRET")

BINANCE = {
  "key": TEST_BINANCE_FUTURE_API_KEY,
  "secret": TEST_BINANCE_FUTURE_SECRET
}


'''
BITFINEX
'''
# COIN_TARGET = "TESTBTC"
# COIN_REFER = "TESTUSDT"

# COIN_TARGET = "TESTBTCF0"
# COIN_REFER = "TESTUSDTF0"

# TEST_BITFINEX_API_KEY=os.environ.get("TEST_BITFINEX_API_KEY")
# TEST_BITFINEX_SECRET=os.environ.get("TEST_BITFINEX_SECRET")

# BITFINEX = {
#   "key": TEST_BITFINEX_API_KEY,
#   "secret": TEST_BITFINEX_SECRET
# }

'''
KRAKEN
'''
# COIN_TARGET = "BTC"
# COIN_REFER = "USDT"

# TEST_KRAKEN_API_KEY=os.environ.get("TEST_KRAKEN_API_KEY")
# TEST_KRAKEN_SECRET=os.environ.get("TEST_KRAKEN_SECRET")

# KRAKEN = {
#   "key": TEST_KRAKEN_API_KEY,
#   "secret": TEST_KRAKEN_SECRET
# }

# TEST_FTX_API_KEY=os.environ.get("TEST_FTX_API_KEY")
# TEST_FTX_SECRET=os.environ.get("TEST_FTX_SECRET")

# FTX = {
#   "key": TEST_FTX_API_KEY,
#   "secret": TEST_FTX_SECRET
# }

TELEGRAM = {
  "chat_id": os.environ.get("TELEGRAM_CHAT_ID"),
  "bot": os.environ.get("TELEGRAM_BOT_KEY")
}

if ENV == PRODUCTION:
  print("ENV = ", ENV)