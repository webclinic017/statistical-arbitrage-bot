import asyncio
from bot import Exchange
from bot import AsyncExchange
from bot import ops
from bot import screen
from settings import st_symbols
import pandas as pd


class Bot:
    def __init__(self):
        screen.welcome()
        self.__exchange = Exchange()
        self.__async_exchange = AsyncExchange()
        self.__positions_series = pd.DataFrame()
        self.__prices_df = pd.DataFrame()
        self.__setup_df = pd.DataFrame()

    def set_sandbox_mode(self, is_testnet=False, is_fake_orders=True):
        self.__exchange.set_sandbox_mode(is_testnet, is_fake_orders)

    def load_markets(self):
        self.__exchange.load_markets()

    def show_all_prices_update(self, show=False):
        self.__exchange.show['all_prices'] = show

    def show_last_price_update(self, show=False):
        self.__exchange.show['last_price'] = show

    def show_pairs_update(self, show=False):
        self.__exchange.show['pairs_update'] = show

    def show_positions_update(self, show=False):
        self.__exchange.show['positions_update'] = show

    def show_trades(self, show=True):
        self.__exchange.show['trades'] = show

    def set_base_currency(self, currency='USDT'):
        self.__exchange.base_currency = currency

    def set_percent_size(self, size_amount):
        self.__exchange.set_percent_size(size_amount)

    def set_fixed_size(self, size_amount):
        self.__exchange.set_fixed_size(size_amount)

    def set_leverage(self, leverage=1):
        self.__exchange.set_leverage(leverage)

    def run(self):
        screen.open_symbols_checking()
        self.__get_historical_data()
        asyncio.run(self.__websocket())

    def __get_historical_data(self):
        self.__prices_df = self.__exchange.fetch_initial_close_prices()
        self.__positions_series = self.__exchange.fetch_all_positions_side()

        open_symbols = self.__positions_series[self.__positions_series != 0]
        screen.has_open_symbols(open_symbols.index) if open_symbols.any() else screen.not_has_open_symbols()

    async def __get_updates(self, symbol):
        await self.__async_exchange.load_markets()

        while True:
            try:
                new_price_df = await self.__async_exchange.watch_close_price(symbol)
                self.__prices_df = ops.concat_prices(self.__prices_df, new_price_df)
                screen.prices_update(self.__prices_df) if self.__exchange.show['all_prices'] else None

                symbol1, symbol2, ratio = ops.get_pairs(symbol)

                prices_pair = self.__prices_df[[symbol1, symbol2]].copy()
                prices_pair['pair'] = prices_pair[symbol1] - prices_pair[symbol2] * ratio
                prices_zscore = ops.apply_zscore(prices_pair)
                screen.pairs_update(prices_zscore) if self.__exchange.show['pairs_update'] else None

                position1 = self.__positions_series[symbol1]
                position2 = self.__positions_series[symbol2]

                last_price = prices_zscore.iloc[-1]
                screen.last_price_update(last_price) if self.__exchange.show['last_price'] else None

                if not position1 and not position2 and ops.is_lower_zscore_open(last_price):
                    if self.__exchange.has_enough_balance():
                        entry1 = self.__exchange.long_entry(symbol1)
                        self.__positions_series[symbol1] = 1 if entry1 else print('order error')
                        entry2 = self.__exchange.short_entry(symbol2)
                        self.__positions_series[symbol2] = -1 if entry2 else print('order error')

                elif not position1 and not position2 and ops.is_higher_zscore_open(last_price):
                    if self.__exchange.has_enough_balance():
                        entry1 = self.__exchange.short_entry(symbol1)
                        self.__positions_series[symbol1] = -1 if entry1 else print('order error')
                        entry2 = self.__exchange.long_entry(symbol2)
                        self.__positions_series[symbol2] = 1 if entry2 else print('order error')

                elif (position1 == 1 or position2 == -1) and ops.is_crossup_zscore_close(last_price):
                    exit1 = self.__exchange.long_exit(symbol1)
                    self.__positions_series[symbol1] = 0 if exit1 else print('order error')
                    exit2 = self.__exchange.short_exit(symbol2)
                    self.__positions_series[symbol2] = 0 if exit2 else print('order error')

                elif (position1 == -1 or position2 == 1) and ops.is_crossdown_zscore_close(last_price):
                    exit1 = self.__exchange.short_exit(symbol1)
                    self.__positions_series[symbol1] = 0 if exit1 else print('order error')
                    exit2 = self.__exchange.long_exit(symbol2)
                    self.__positions_series[symbol2] = 0 if exit2 else print('order error')

                screen.positions_update(self.__positions_series) if self.__exchange.show['positions_update'] else None

            except Exception:
                screen.print_exception()

    async def __websocket(self):
        try:
            screen.new_trades_checking()
            loops = [self.__get_updates(symbol) for symbol in st_symbols]
            await asyncio.gather(*loops)

        except Exception:
            screen.print_exception()
            await self.__async_exchange.close_connection()
