import pandas as pd
import pyarrow
import pandas as pd
import pyarrow.parquet as pq
import datetime as dt
import numpy as np
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")


import filter_level1
import filter_level2
import filter_level3



df_filtered= pd.read_parquet('./data/data_filter_3.parquet')


## 这个地址需要修改成DATA_DIR / "pulled" / "OptionsMetrics.parquet"
parquet_file = pq.ParquetFile('./data/pulled/OptionMetrics.parquet')

df_raw= parquet_file.read().to_pandas()

def iv_plt():

    plt.figure(figsize=(15, 6))

    plt.subplot(1, 2, 1)
    plt.hist(df_filtered['impl_volatility'], bins=30, alpha=0.5, color='blue')
    plt.title('Filtered impl_volatility Distribution')
    plt.xlabel('impl_volatility')
    plt.ylabel('Frequency')

    plt.subplot(1, 2, 2)
    plt.hist(df_raw['impl_volatility'], bins=30, alpha=0.5, color='green')
    plt.title('Raw impl_volatility Distribution')
    plt.xlabel('impl_volatility')
    plt.ylabel('Frequency')

    plt.tight_layout()

    plt.savefig('./output/iv_plt.png')

    plt.show()

def ttm_plt():
    df_raw['exdate'] = pd.to_datetime(df_raw['exdate'])
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    df_raw['ttm'] = (df_raw['exdate'] - df_raw['date']).dt.days

    plt.figure(figsize=(15, 6))

    plt.subplot(1, 2, 1)
    plt.hist(df_filtered['T-t'], bins=30, alpha=0.5, color='blue')
    plt.title('Filtered DaystoMaturity Distribution')
    plt.xlabel('DaystoMaturity')
    plt.ylabel('Frequency')

    plt.subplot(1, 2, 2)
    plt.hist(df_raw['ttm'], bins=30, alpha=0.5, color='green')
    plt.title('Raw DaystoMaturity Distribution')
    plt.xlabel('DaystoMaturity')
    plt.ylabel('Frequency')

    plt.tight_layout()

    plt.savefig('./output/ttm_plt.png')

    plt.show()


parquet_file_raw = pq.ParquetFile('./data/pulled/OptionMetrics.parquet')
df_raw = parquet_file_raw.read().to_pandas()

parquet_file_new = pq.ParquetFile('./data/data_filter_3.parquet')
df_new = parquet_file_new.read().to_pandas()

df_raw['ratio'] = df_raw['close'] / df_raw['strike_price']*1000

df_new['ratio'] = df_new['close'] / df_new['strike_price']

def moneyness_plt():

    plt.figure(figsize=(15, 6))
    
    plt.subplot(1, 2, 1)
    plt.hist(df_new['ratio'], bins=30, alpha=0.5, color='blue')
    plt.title('Filtered Moneyness Distribution')
    plt.xlabel('Moneyness')
    plt.ylabel('Frequency')

    plt.subplot(1, 2, 2)
    plt.hist(df_raw['ratio'], bins=30, alpha=0.5, color='green')
    plt.xlim(0, 5)
    plt.title('Raw Moneyness Distribution')
    plt.xlabel('Moenyness')
    plt.ylabel('Frequency')

    plt.tight_layout()

    plt.savefig('./output/moneyness_plt.png')

    plt.show()




if __name__ == "__main__":
    iv_plt()
    ttm_plt()
    moneyness_plt()
    