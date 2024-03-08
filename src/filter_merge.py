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
filter=[]
step=[]
remaining=[]
deleted=[]


filter.append('Starting')
step.append('Calls')
remaining.append(1704128)
deleted.append(' ')

filter.append(' ')
step.append('Puts')
remaining.append(1706268)
deleted.append(' ')

filter.append('All')
step.append(' ')
remaining.append(len(df))
deleted.append(' ')

df=filter_level1.clean_options_data(df)
remaining.append(len(df))
deleted.append(remaining[2]-len(df))
filter.append('Level 1 filters')
step.append('CleanOptionsData')

df=filter_level1.remove_duplicate_quotes(df)
remaining.append(len(df))
deleted.append(remaining[3]-len(df))
filter.append(' ')
step.append('RemoveDuplicateQuotes')

df=filter_level1.delete_zero_bid_filter(df)
remaining.append(len(df))
deleted.append(remaining[4]-len(df))
filter.append(' ')
step.append('DeleteZeroBidFilter')

df=filter_andy.DaystoMaturity_filter(df)
remaining.append(len(df))
deleted.append(remaining[5]-len(df))
filter.append('Level 2 filters')
step.append('DaystoMaturityFilter')

df=filter_andy.ExtremeIV_filter(df)
remaining.append(len(df))
deleted.append(remaining[6]-len(df))
filter.append(' ')
step.append('ExtremeIVFilter')

df=filter_2_3_ZS.moneyness_filter(df)
remaining.append(len(df))
deleted.append(remaining[7]-len(df))
filter.append(' ')
step.append('Moneyness(0.8~1.2)Filter')

df=filter_2_3_ZS.implied_interest_rate_filter(df)
remaining.append(len(df))
deleted.append(remaining[8]-len(df))
filter.append(' ')
step.append('ImpliedInterestRateFilter')

df=filter_2_3_ZS.IV_filter(df)
remaining.append(len(df))
deleted.append(remaining[9]-len(df))
filter.append('Level 3 filters')
step.append('IVFilter')

df=filter_2_3_ZS.parity_filter(df)
remaining.append(len(df))
deleted.append(remaining[10]-len(df))
filter.append(' ')
step.append('PutCallParityFilter')

#print(remaining)
#print(deleted)

summary = pd.DataFrame({
    'Level': step,  # 假设 step 是包含"Level"列数据的序列
    'Filter': filter,  # filter 是"Filter"列的数据
    'Deleted': deleted,  # deleted 是"Deleted"列的数据
    'Remaining': remaining  # remaining 是"Remaining"列的数据
}).set_index('Filter')

print(summary)
df.to_parquet('./data/data_filter_3.parquet')

summary.to_excel('./output/latex.xlsx')