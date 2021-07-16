import sys
from binance import ThreadedWebsocketManager
from config import BINANCE
from pprint import pprint

# def main():
#     def handle_trade_socket(msg):
#         print("==== TRADE SOCKET MESSAGE RECEIVED")
#         print(msg)

#     twm = ThreadedWebsocketManager(
#         api_key=BINANCE.get("key"), 
#         api_secret=BINANCE.get("secret"), 
#         testnet=True
#     )

#     try:
#         twm.start()
#     except KeyboardInterrupt:
#         sys.exit(0)

#     twm.start_futures_socket(
#         callback=handle_trade_socket, 
#     )

#     twm.join()
    
# if __name__ == "__main__":
#     main()

api_key = BINANCE.get("key")
api_secret = BINANCE.get("secret")

def main():

    symbol = 'BNBBTC'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, testnet=True)
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        print(f"message type: {msg['e']}")
        pprint(msg)

    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    twm.start_futures_socket(
        callback=handle_socket_message, 
    )

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    # streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    twm.join()


if __name__ == "__main__":
   main()