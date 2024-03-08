import pandas as pd
import numpy as np
import config
from pathlib import Path 

import time 
from datetime import datetime, timedelta

from pandas_market_calendars import get_calendar

from multiprocessing import Pool

OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)
WRDS_USERNAME = config.WRDS_USERNAME

exchange_code = "XNYS"
calendar = get_calendar(exchange_code)



def filter_repeated_options(df):
    """
    Filter the DataFrame to keep only rows where options share the same security ID,
    strike price, expiration date, and call/put flag. It ensures only options with duplicates
    (indicating repetition) are retained, and unique options (which could indicate missing data)
    are removed.

    Parameters:
    - data_frame: The input DataFrame containing options data.

    Returns:
    - DataFrame: Filtered DataFrame containing only repeated options.
    """
    # Define the columns that identify duplicate options.
    option_id = ['secid', 'strike_price' , 'exdate', 'cp_flag']
    bool_Dup = df.duplicated(subset = option_id, keep = False)
    df = df[bool_Dup]
    
    return df


def assign_trading_day_numbers(df):
    """
    Assigns a unique integer to each trading day in the DataFrame, facilitating the calculation
    of relative distances between trading days and expiration dates. It enhances the efficiency of 
    operations by replacing date differences with integer operations.

    Parameters:
    - df: The input DataFrame with options data. Requires 'date' and 'exdate' columns.

    Returns:
    - DataFrame: The modified DataFrame with additional columns for the integer representations
                 of trading days ('da_num') and expiration dates ('ex_num'), as well as the
                 time to expiration ('expTime').
    """

    startt = df['date'].min().date() 
    endd = df['date'].max().date()
    TradingDays =  calendar.valid_days(start_date=startt, end_date=endd , tz = None)	

    dfNewCal = pd.DataFrame({"date2": TradingDays})
    dfNewCal['da_num'] = list(range(len(dfNewCal)))

    df = pd.merge(df, dfNewCal, left_on='date', right_on='date2', how='inner')
    df = df.drop(columns = ["date2"])

    dfNewCal['ex_num'] = dfNewCal['da_num']
    dfNewCal = dfNewCal.drop(columns = ['da_num'])

    df = pd.merge(df, dfNewCal, left_on='exdate', right_on='date2', how='inner')
    df = df.drop(columns = ["date2"])

    df['expTime'] = df['ex_num']-df['da_num']

    return df

def create_lagged_columns(data=None, columns_to_lag=None, id_columns=None, lags=1, 
                         date_col='date', prefix='L'):

    all_dates = data[date_col].drop_duplicates().sort_values().reset_index(drop=True)
    date_to_lag_date = pd.concat([all_dates, all_dates.shift(-lags)], axis=1)
    date_to_lag_date.columns = [date_col, '_lagged_date']

    sub_df = data[[date_col, *id_columns, *columns_to_lag]]
    lag_sub_df = sub_df.merge(date_to_lag_date, on=[date_col])

    for col in columns_to_lag:
        lag_sub_df = lag_sub_df.rename(columns={col: f'{prefix}{lags}_' + col})

    lag_sub_df = lag_sub_df.drop(columns=[date_col])
    lag_sub_df = lag_sub_df.rename(columns={'_lagged_date':date_col})
    
    return lag_sub_df

def with_lagged_columns(data=None, columns_to_lag=None, id_columns=None, lags=1, 
                         date_col='date', prefix='L'):
    
    data_lag = create_lagged_columns(data=data, columns_to_lag=columns_to_lag, 
                                     id_columns=id_columns, lags=lags, 
                                     date_col=date_col, prefix=prefix)
    w_data_lag = data.merge(data_lag, on=[date_col, *id_columns], how='left')
    return w_data_lag

def daysLost(df): 
	
	option_id = ['secid', 'strike_price' , 'exdate', 'cp_flag']
	df = with_lagged_columns( df, columns_to_lag = ['da_num'], id_columns = option_id, 
		lags = -1, date_col = 'date', prefix = 'L')

	df['L-1_da_num'] = df['L-1_da_num'].fillna(df['ex_num'])

	df['days_lost'] = df['L-1_da_num'] - df['da_num']

	return df 

def adjust_expiration_dates(df):
    """
    Adjusts expiration dates in the DataFrame to the nearest previous trading day if they
    fall on a non-trading day.

    Parameters:
    df (pd.DataFrame): DataFrame with at least 'date' and 'exdate' columns.

    Returns:
    pd.DataFrame: DataFrame with adjusted expiration dates.
    """
    startt = df['date'].min().date() 
    endd = df['date'].max().date()
    TradingDays =  calendar.valid_days(start_date=startt, end_date=endd , tz = None)

    L = set(sorted(df['exdate'].unique()))
    L1 = set(TradingDays)

    daysf = sorted(L-L1)
    dfDays = pd.DataFrame({"date2": daysf})
    dfDays['shift'] = dfDays-timedelta(1)

    df = pd.merge(df, dfDays, left_on='exdate', right_on='date2', how='left')

    df['exdate'] = np.where(~df['shift'].isna(), df['shift'], df['exdate'])

    df = df.drop(columns=['date2', 'shift']) 

    return df

def adjust_weekend_expirations(df):
    """
    Adjusts options' expiration dates in the DataFrame from weekends to the previous Friday.

    Parameters:
    df (pd.DataFrame): DataFrame with at least 'exdate' columns, where 'exdate' are the expiration dates.

    Returns:
    pd.DataFrame: DataFrame with adjusted expiration dates.
    """
    startt = df['date'].min().date() 
    endd = df['date'].max().date()
    date_range = pd.date_range(start=startt, end=endd, freq='D')

    fridays = date_range[date_range.weekday == 4]

    for day in [5,6]: 
        saturdays = date_range[date_range.weekday == day] 
        dfSatCal = pd.DataFrame({"date2": saturdays})
        dfSatCal['fri'] = fridays


        df = pd.merge(df, dfSatCal, left_on='exdate', right_on='date2', how='left')


        df['exdate'] = np.where(~df['fri'].isna(), df['fri'], df['exdate'])

        df = df.drop(columns=['date2', 'fri']) 

    return df

def options_at_end_of_month(df): 
    startt = df['date'].min().date() 
    endd = df['date'].max().date()
    TradingDays =  calendar.valid_days(start_date=startt, end_date=endd , tz = None)	

    TDseries = TradingDays.to_series()

    ends = pd.to_datetime(TDseries.groupby(TDseries.dt.strftime('%Y-%m')).max())

    dfMonthCal = pd.DataFrame({"date2": ends})
    dfMonthCal['m'] = ends 


    df = pd.merge(df, dfMonthCal, left_on='exdate', right_on='date2', how='inner')
    df = df.drop(columns=['date2', 'm']) 

    return df

def analyze_options(df):
    
    dfExp = df[ df['days_lost'] == df['expTime']]
    expMissingDays = dfExp['days_lost'].sum()
    expOptions = int(len(dfExp)/(df.shape[1]**1.65))
    dfFound = df[ df['days_lost'] == 1]
    foundOptions = len(dfFound)

    dfMissing = df[ 1 <  df['days_lost']  ]


    missingOptions = int(len(dfMissing)/(df.shape[1]**1.6))

    return {"found": foundOptions, "miss": missingOptions, "exp": expOptions, }

def analyze_table2_info(df):
    rows_2 = ['All', 'Found', 'Missing', 'Expired']
    dT2 = pd.DataFrame(index = rows_2)
    dfc = df[df['cp_flag']=="C"]
    report = analyze_options(dfc)
    dT2['Calls'] = [len(dfc), report['found'], report['miss'], report['exp']]
    dfp = df[df['cp_flag']=="P"]
    report = analyze_options(dfp)
    dT2['Puts'] = [len(dfp), report['found'], report['miss'], report['exp']]

    dT2 = dT2.T

    return dT2

def table2_analysis(path='filter'): 
    save_path3 = DATA_DIR.joinpath(f"manual/data_{path}_3.parquet")
    df= pd.read_parquet(save_path3)
    df = df.reset_index()
    df = adjust_weekend_expirations(df)
    df = adjust_expiration_dates(df)
    df = assign_trading_day_numbers(df)
    df = daysLost(df)
    dfM = options_at_end_of_month(df)

    dT = analyze_table2_info(df)

    new_dT = dT.T
    new_dT.drop(index = 'All',inplace = True)

    sum1 = new_dT['Calls'].sum()
    sum2 = new_dT['Puts'].sum()

    new_column1_values = [new_dT.loc['Found','Calls']/sum1, 
                        new_dT.loc['Missing','Calls']/sum1,
                        new_dT.loc['Expired','Calls']/sum1]
    new_column2_values = [
                        new_dT.loc['Found','Puts']/sum2, 
                        new_dT.loc['Missing','Puts']/sum2,
                        new_dT.loc['Expired','Puts']/sum2]

    insert_index = 1

    new_dT.insert(insert_index, ' ', new_column1_values)
    new_dT.insert(insert_index + 2, '', new_column2_values)

    new_dT.to_excel(OUTPUT_DIR.joinpath(f"table2_all.xlsx"))

    dTM = analyze_table2_info(dfM)

    new_dTM = dTM.T
    new_dTM.drop(index = 'All',inplace = True)

    sum1 = new_dTM['Calls'].sum()
    sum2 = new_dTM['Puts'].sum()

    new_column1_values = [new_dTM.loc['Found','Calls']/sum1, 
                        new_dTM.loc['Missing','Calls']/sum1,
                        new_dTM.loc['Expired','Calls']/sum1]
    new_column2_values = [
                        new_dTM.loc['Found','Puts']/sum2, 
                        new_dTM.loc['Missing','Puts']/sum2,
                        new_dTM.loc['Expired','Puts']/sum2]

    insert_index = 1

    new_dTM.insert(insert_index, ' ', new_column1_values)
    new_dTM.insert(insert_index + 2, '', new_column2_values)

    new_dTM.to_excel(OUTPUT_DIR.joinpath(f"table2_month.xlxs"))
    
    
    return df, new_dT, new_dTM

if __name__ == "__main__":
     
     df1, dT1, dTM1 = table2_analysis()

     






