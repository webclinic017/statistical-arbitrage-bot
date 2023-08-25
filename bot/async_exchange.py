import pandas as pd
from dotenv import load_dotenv
from settings import st_timeframe
from bot import ops
import ccxt.pro as ccxtpro
import os


class AsyncExchange:
    def __init__(self):
        load_dotenv()
        exchange_id = os.getenv('exchange')
        exchange_class = getattr(ccxtpro, exchange_id)
        self.__ccxtpro = exchange_class({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })

    async def load_markets(self):
        await self.__ccxtpro.load_markets()

    async def watch_close_price(self, symbol):
        close_price = ops.only_close_filter(await self.__watch_ohlcv(symbol)).rename(symbol)
        return ops.series_to_df(close_price)

    async def __watch_ohlcv(self, symbol):
        ohlcv = pd.DataFrame(await self.__ccxtpro.watch_ohlcv(symbol, timeframe=st_timeframe, limit=1))
        return ops.clean_ohlcv(ohlcv)

    async def close_connection(self):
        await self.__ccxtpro.close()
