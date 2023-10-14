import pandas as pd
import os

EXCHANGE = 'BINANCE'

def single_expression(x):
    currency1 = x['currency1'].replace("/", '')
    currency2 = x['currency2'].replace("/", '')
    expressions = f"{EXCHANGE}:{currency1}.P-{EXCHANGE}:{currency2}.P*{x['ratio']}"
    print(expressions)
    return 0
def get_tradingview_expressions(df):
    return df.apply(single_expression,axis=1)

def get_absolute_path():
    return os.path.dirname(__file__)


def join_paths(path1, path2):
    return os.path.join(path1, path2)


loaded_pairs = pd.read_csv(join_paths(get_absolute_path(), "../../settings/bot_input.csv"))
expressions = get_tradingview_expressions(loaded_pairs)

