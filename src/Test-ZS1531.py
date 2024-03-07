import pandas as pd
import pyarrow
import pandas as pd
import pyarrow.parquet as pq
import datetime as dt
import numpy as np
import warnings
warnings.filterwarnings("ignore")


import filter_level1
import filter_andy
import filter_2_3_ZS

parquet_file = pq.ParquetFile('OptionMetrics.parquet')
df = parquet_file.read().to_pandas()

#print(df.head())


df=filter_level1.clean_options_data(df)

df=filter_level1.remove_duplicate_quotes(df)

df=filter_level1.delete_zero_bid_filter(df)

df=filter_andy.DaystoMaturity_filter(df)

df=filter_andy.ExtremeIV_filter(df)

df=filter_2_3_ZS.moneyness_filter(df)

df=filter_2_3_ZS.implied_interest_rate_filter(df)

df=filter_2_3_ZS.IV_filter(df)

df=filter_2_3_ZS.parity_filter(df)

#print(df)
df.to_parquet('./data/filtered_for_HY.parquet')