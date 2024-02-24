import pandas as pd
import numpy as np
import wrds

def remove_duplicate_quotes(df):
    """
    Removes duplicate observations from the OptionMetrics dataset.
    Duplicates are defined as quotes with the same option type, strike price,
    expiration date, and price.
    
    Parameters:
    df : pandas.DataFrame
        DataFrame containing the OptionMetrics dataset.

    Returns:
    pandas.DataFrame
        DataFrame with duplicate observations removed.
    """
    # Criteria for defining duplicates: option type, strike price, expiration date, and price
    cols_to_check = ['secid', 'cp_flag', 'strike_price','date','exdate', 'best_offer']
    
    # Remove duplicates, keeping the first occurrence
    df_unique = df.drop_duplicates(subset=cols_to_check, keep='first')
    
    return df_unique

def clean_options_data(df):
    """
    Cleans a DataFrame of options data by removing duplicates based on certain
    criteria (type, strike, maturity, date), while keeping the entry whose
    implied volatility is closest to the TBill based implied volatility of its
    moneyness neighbors.

    Parameters:
    - df: DataFrame containing options data with columns for 'secid', 'date',
          'cp_flag', 'strike_price', 'exdate', 'close', and 'impl_volatility'.

    Returns:
    - DataFrame with duplicates removed based on the specified logic.
    """
    # Calculate moneyness for each option
    df['moneyness'] = (df['strike_price'] / 1000) / df['close']

    # Identify all duplicates based on the given subset of columns
    duplicates_mask = df.duplicated(subset=['secid', 'date', 'cp_flag', 'strike_price', 'exdate'], keep=False)

    # Separate duplicates for further analysis
    df_duplicates = df[duplicates_mask]
    df_unique = df[~duplicates_mask]

    # Find moneyness neighbors and the implied volatility closest to TBill for each duplicate
    df_duplicates = df_duplicates.sort_values(by=['secid', 'cp_flag', 'date', 'exdate'])
    grouped = df_duplicates.groupby(['secid', 'cp_flag', 'date', 'exdate'])

    closest_to_tbill = grouped.apply(lambda x: x.loc[(x['moneyness'] - 1).abs().idxmin()])


    # Drop duplicates in the original duplicates DataFrame and keep only the closest entries
    df_cleaned_duplicates = closest_to_tbill.drop_duplicates(subset=['secid', 'date', 'cp_flag', 'strike_price', 'exdate'])

    # Combine the non-duplicate entries with the cleaned duplicates and sort
    df_final = pd.concat([df_unique, df_cleaned_duplicates]).sort_values(by=['secid', 'cp_flag', 'date', 'exdate']).reset_index(drop=True)

    # Cleanup: remove temporary columns if needed
    df_final.drop(['moneyness'], axis=1, inplace=True)

    return df_final

def delete_zero_bid_filter(df):
    """
    Filters out rows from the DataFrame where the 'best_bid' value is zero.
    Rows with a 'best_bid' of zero might be considered as having no active bids,
    which could be irrelevant for certain analyses focusing on active market participation.

    Parameters:
    df : pandas.DataFrame
        The DataFrame containing options data with a 'best_bid' column.

    Returns:
    pandas.DataFrame
        A filtered DataFrame with rows having non-zero 'best_bid' values.
    """
    filtered_df = df.query("best_bid != 0.0")
    return filtered_df

