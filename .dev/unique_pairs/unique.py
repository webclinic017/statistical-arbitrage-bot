import os
import pandas as pd


def get_unique_pairs(df):
    df_unique = df.drop_duplicates(subset='currency1', keep='first', inplace=False).drop_duplicates(subset='currency2', keep='first', inplace=False)

    weaker_pairs = df_unique.apply(lambda x: df_unique.loc[df_unique['currency2'] == x['currency1'], 'ratio'].max() >= x['ratio'] or
                                             df_unique.loc[df_unique['currency1'] == x['currency2'], 'ratio'].max() >= x['ratio'], axis=1)
    return df_unique[~weaker_pairs]


def get_absolute_path():
    return os.path.dirname(__file__)


def join_paths(path1, path2):
    return os.path.join(path1, path2)


loaded_pairs = pd.read_csv(join_paths(get_absolute_path(), "../data/bot_input-multiple.csv"))
df = get_unique_pairs(loaded_pairs)
df.to_csv('./bot_input_unique.csv')
