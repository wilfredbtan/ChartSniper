import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

SANDBOX = True
ENV = os.getenv("ENVIRONMENT", DEVELOPMENT)
DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY")

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


# BITFINEX
# COIN_TARGET = "TESTBTC"
# COIN_REFER = "TESTUSD"

# TEST_BITFINEX_API_KEY=os.environ.get("TEST_BITFINEX_API_KEY")
# TEST_BITFINEX_SECRET=os.environ.get("TEST_BITFINEX_SECRET")

# BITFINEX = {
#   "key": TEST_BITFINEX_API_KEY,
#   "secret": TEST_BITFINEX_SECRET
# }

# COIN_TARGET = "BTC"
# COIN_REFER = "USDT"

# TEST_KRAKEN_API_KEY=os.environ.get("TEST_KRAKEN_API_KEY")
# TEST_KRAKEN_SECRET=os.environ.get("TEST_KRAKEN_SECRET")

# signature = hmac.new(base64.b64decode(TEST_KRAKEN_SECRET), hashlib.sha512)
# sigdigest = base64.b64encode(signature.digest())
# sigdigest = base64.b64encode(TEST_KRAKEN_SECRET)

# KRAKEN = {
#   "key": TEST_KRAKEN_API_KEY,
#   "secret": TEST_KRAKEN_SECRET
#   # "secret": sigdigest
# }

TELEGRAM = {
  "chat_id": os.environ.get("TELEGRAM_CHAT_ID"),
  "bot": os.environ.get("TELEGRAM_BOT_KEY")
}

print("ENV = ", ENV)