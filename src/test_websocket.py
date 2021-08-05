import sys
import asyncio
from binance import ThreadedWebsocketManager, BinanceSocketManager, AsyncClient
from binance.client import Client
from config import BINANCE
from pprint import pprint

api_key = BINANCE.get("key")
api_secret = BINANCE.get("secret")

def main():

    symbol = 'BNBBTC'

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret, testnet=True)
    # twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)

    def handle_socket_message(msg):
        print(f"message type: {msg['e']}")
        pprint(msg)

    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    twm.start()
    # Fix needed to use testnet for futures_socket
    # https://github.com/sammchardy/python-binance/issues/929
    twm.start_futures_socket(
        callback=handle_socket_message, 
    )

    # start is required to initialise its internal loop
    # twm.start()

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    # streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    twm.join()


if __name__ == "__main__":
   main()

# async def main():
#     symbol = 'BNBBTC'
#     client = await AsyncClient.create(testnet=True)
#     # client = await AsyncClient.create(api_key, api_secret,{"verify": True, "timeout": 10000})
#     # client = await AsyncClient.create(api_key, api_secret,{"timeout": 10000})
#     # client = await AsyncClient.create(api_key, api_secret, testnet=True)
#     bm = BinanceSocketManager(client)
#     # start any sockets here, i.e a trade socket
#     ts = bm.trade_socket(symbol)
#     # ts = bm.futures_socket()
#     # then start receiving messages
#     async with ts as tscm:
#         while True:
#             res = await tscm.recv()
#             print(res)
# 
#     await client.close_connection()
# 
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
