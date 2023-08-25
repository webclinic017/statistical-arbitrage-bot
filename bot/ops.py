import pandas as pd
from settings import st_symbols
from settings import st_pairs


def concat_positions(position, new_position):
    return pd.concat([position, new_position])


def series_to_df(series):
    df = pd.DataFrame(columns=st_symbols)
    df[series.name] = series
    return df


def concat_prices(df, new_df):
    return __update_existing_row(df, new_df) if new_df.index.isin(df.index) else __crete_new_row(df, new_df)


def __update_existing_row(df, new_df):
    return new_df.combine_first(df)


def __crete_new_row(df, new_df):
    return pd.concat([df[~df.index.isin(new_df.index)], new_df])


def clean_ohlcv(ohlcv):
    ohlcv = ohlcv.iloc[:, :6]
    ohlcv.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    ohlcv = ohlcv.set_index('time')
    ohlcv.index = pd.to_datetime(ohlcv.index, unit='ms')
    ohlcv = ohlcv.astype(float)
    return ohlcv


def only_close_filter(cleaned_ohlcv):
    return cleaned_ohlcv.close


def get_pairs(symbol):
    return [pair for pair in st_pairs.values if symbol in pair][0]

def apply_zscore(df):
    mean = df.pair.rolling(center=False, window=21).mean()
    std = df.pair.rolling(center=False, window=21).std()
    x = df.pair.rolling(center=False, window=1).mean()
    df['zscore'] = (x - mean) / std
    return df


def is_lower_zscore_open(df):
    return df.zscore <= -2.0


def is_higher_zscore_open(df):
    return df.zscore >= 2.0


def is_crossup_zscore_close(df):
    return df.zscore >= 0.0


def is_crossdown_zscore_close(df):
    return df.zscore <= 0.0


