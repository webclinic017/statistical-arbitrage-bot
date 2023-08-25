import pandas as pd
import os

path = os.path.dirname(__file__)
settings_df = pd.read_csv(path + '/bot_input.csv')

st_timeframe = settings_df['timeframe'][0]
st_pairs = settings_df.drop(columns='timeframe')
st_symbols = st_pairs.iloc[:, 0:2].unstack().tolist()
