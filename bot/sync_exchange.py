import pandas as pd
from bot import screen
from settings import st_timeframe
from settings import st_symbols
from dotenv import load_dotenv
from bot import ops
import ccxt
import os


class Exchange:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv('api_key')
        api_secret = os.getenv('api_secret')
        exchange_id = os.getenv('exchange')

        exchange_class = getattr(ccxt, exchange_id)

        self.__private_ccxt = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future',
                        'createMarketBuyOrderRequiresPrice': False
                        },
        })
        self.__public_ccxt = exchange_class({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })
        self.__markets = None
        self.__base_currency = 'USDT'
        self.__size = {'type': 'percent',
                       'amount': 1
                       }
        self.show = {'all_prices': False,
                     'last_prices': False,
                     'pairs_update': False,
                     'positions_update': False,
                     'trades': True,
                     }

    def set_base_currency(self, base_currency):
        self.__base_currency = base_currency

    def set_sandbox_mode(self, is_demo=True):
        self.__private_ccxt.set_sandbox_mode(is_demo)

    def load_markets(self):
        self.__markets = self.__public_ccxt.load_markets()

    def set_percent_size(self, size_amount):
        size_type = 'percent'
        self.__set_size_and_type(size_amount, size_type)

    def set_fixed_size(self, size_amount):
        size_type = 'fixed'
        self.__set_size_and_type(size_amount, size_type)

    def __set_size_and_type(self, size_amount, size_type):
        self.__size['amount'] = size_amount
        self.__size['type'] = size_type

    def __get_future_symbol(self, symbol):
        return f'{symbol}:{self.__base_currency}'

    def set_leverage(self, leverage):
        [self.__set_symbol_leverage(leverage, symbol) for symbol in st_symbols]

    def __set_symbol_leverage(self, leverage, symbol):
        try:
            future_symbol = self.__get_future_symbol(symbol)
            self.__private_ccxt.set_leverage(leverage, symbol=future_symbol)

        except Exception:
            pass

    def __fetch_balance(self):
        return self.__private_ccxt.fetch_balance()

    def fetch_initial_close_prices(self):
        prices = pd.DataFrame()
        for symbol in st_symbols:
            prices[symbol] = self.fetch_close_price(symbol)
        return prices

    def fetch_close_price(self, symbol):
        return ops.only_close_filter(self.fetch_ohlcv(symbol))

    def fetch_ohlcv(self, symbol):
        ohlcv = pd.DataFrame(self.__public_ccxt.fetch_ohlcv(symbol, timeframe=st_timeframe, limit=50))
        return ops.clean_ohlcv(ohlcv)

    def has_enough_balance(self):
        balance = self.__fetch_balance()
        free_balance = float(balance[self.__base_currency]['free'])
        total_balance = float(balance[self.__base_currency]['total'])
        size_type = self.__size['type']
        size_amount = self.__size['amount']
        factor = 3

        amount_needed = size_amount / total_balance * factor if size_type == 'percent' else size_amount * factor
        return free_balance > amount_needed

    def long_entry(self, symbol):
        return self.__create_order(symbol, side='buy')

    def long_exit(self, symbol):
        return self.__create_order(symbol, side='sell', is_exit=True)

    def short_entry(self, symbol):
        return self.__create_order(symbol, side='sell')

    def short_exit(self, symbol):
        return self.__create_order(symbol, side='buy', is_exit=True)

    def __create_order(self, symbol, side, is_exit=False, tipe='market'):
        amount = self.__fetch_open_amount(symbol) if is_exit else self.__set_position_amount(symbol)
        screen.trades(symbol, side, tipe, amount, 'EXIT' if is_exit else 'ENTRY') if self.show['trades'] else None
        return self.__private_ccxt.create_order(symbol=symbol.replace('/', ''),
                                                side=side,
                                                type=tipe,
                                                amount=amount,
                                                params={'reduceOnly': True} if is_exit else {}
                                                )

    def fetch_all_positions_side(self):
        positions = pd.Series(name='positions', dtype=int)
        for symbol in st_symbols:
            new_position = pd.Series(data=self.__fetch_position_side(symbol), index=[symbol])
            positions = ops.concat_positions(positions, new_position)
        return positions

    def __fetch_position_side(self, symbol):
        side = self.__fetch_open_position(symbol)[0]['side']
        return 1 if side == 'long' else -1 if side == 'short' else 0

    def __fetch_open_amount(self, symbol):
        return float(self.__fetch_open_position(symbol)[0]['contracts'])

    def __fetch_open_position(self, symbol):
        # future_symbol = self.__get_future_symbol(symbol)
        return self.__private_ccxt.fetch_positions([symbol])

    def __set_position_amount(self, symbol):
        size_type = self.__size['type']
        if size_type == 'percent':
            return self.__set_percent_position(symbol)
        elif size_type == 'fixed':
            return self.__set_fixed_position(symbol)
        else:
            raise ValueError('Size Type must be "Fixed" or "Percent".')

    def __set_percent_position(self, symbol):
        total = float(self.__fetch_balance()[self.__base_currency]['total'])
        position_amount = (total / self.__get_last_price(symbol)) * (self.__size['amount'] / 100)
        return round(position_amount, self.__set_precision(symbol))

    def __set_fixed_position(self, symbol):
        position_amount = self.__size['amount'] / self.__get_last_price(symbol)
        return round(position_amount, self.__set_precision(symbol))

    def __get_last_price(self, symbol):
        future_symbol = self.__get_future_symbol(symbol)
        return self.__public_ccxt.fetch_ticker(future_symbol)['last']

    def __set_precision(self, symbol):
        future_symbol = self.__get_future_symbol(symbol)
        return int(self.__markets[future_symbol]['precision']['amount'])
