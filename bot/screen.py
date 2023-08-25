import datetime as dt
import linecache
import sys
import pyfiglet

WHITESPACE = ' '
ASTERISK = '*'


def welcome():
    strategy_name = pyfiglet.figlet_format("P A I R S \n"
                                           "    T R A D I N G")
    print('\n')
    print(strategy_name)

    print('\n')
    print('Loading markets...')


def open_symbols_checking():
    print('Checking if there are pre opened symbols for this strategy...')


def has_open_symbols(symbols):
    print('\n')
    print('The bot has started with pre-opened orders for the above symbols:')
    [print(s) for s in symbols]
    print('\n')
    print('************************* !!! WARNING !!! *************************')
    print('***      The symbols above will be used as part of strategy!    ***')
    print("***      If they belongs to another strategy,                   ***")
    print('***      please close them after start these Bot!               ***')
    print('*******************************************************************')


def not_has_open_symbols():
    print('\n')
    print('No pre-orders founds!')
    print('The bot has started without previous order opened!')


def new_trades_checking():
    print('\n')
    print('Checking for pairs trading opportunity...')


def prices_update(prices_df):
    print('\n')
    print(prices_df)


def last_price_update(last_prices):
    print('\n')
    print(last_prices)


def pairs_update(pair_df):
    print('\n')
    print(pair_df)


def positions_update(positions_series):
    print('\n')
    print(positions_series)


def trades(symbol, side, tipe, amount, position):
    head = f"************ {symbol} ************"
    empty_line = f'**{(len(head) - 4) * WHITESPACE}**'

    print('\n')
    print(head)
    print(empty_line)
    print(__set_line('Symbol:', symbol, len(head)))
    print(__set_line('Side:', side, len(head)))
    print(__set_line('Type:', tipe, len(head)))
    print(__set_line('Amount:', str(amount), len(head)))
    print(__set_line('Position:', position, len(head)))
    print(__set_line('Time:', str(dt.datetime.now())[:-10], len(head)))
    print(empty_line)
    print(f'{len(head) * ASTERISK}')


def __set_line(text, value, len_head):
    return f'**   {text} {value}{(len_head - len(text) - len(value) - 9) * WHITESPACE} **'


def print_exception():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('\n')
    print('EXCEPTION IN (\n{}, LINE {} "{}"): \n{}'.format(filename, lineno, line.strip(), exc_obj))
