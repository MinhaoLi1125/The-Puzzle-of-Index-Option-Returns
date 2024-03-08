import pandas as pd
import filter_level1
from pandas.testing import assert_frame_equal

def test_remove_duplicate_quotes():
    # Create a sample DataFrame with duplicate observations
    data = {'secid': [1, 1, 2, 2],
            'cp_flag': ['C', 'C', 'P', 'P'],
            'strike_price': [100, 100, 110, 110],
            'date': ['2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07'],
            'exdate': ['2024-03-14', '2024-03-14', '2024-03-21', '2024-03-21'],
            'best_offer': [1.5, 1.5, 2.0, 2.0]}
    df = pd.DataFrame(data)

    # Apply the function to the sample DataFrame
    result_df = filter_level1.remove_duplicate_quotes(df)
    result_df.reset_index(drop=True, inplace=True)
    
    # Check if the result DataFrame has the expected number of rows after removing duplicates
    assert len(result_df) == 2
    
    # Check if the duplicates are properly removed based on the specified columns
    expected_data = {'secid': [1, 2],
                     'cp_flag': ['C', 'P'],
                     'strike_price': [100, 110],
                     'date': ['2024-03-07', '2024-03-07'],
                     'exdate': ['2024-03-14', '2024-03-21'],
                     'best_offer': [1.5, 2.0]}
    expected_df = pd.DataFrame(expected_data)
    assert_frame_equal(result_df, expected_df)

def test_clean_options_data():
    # Create a sample DataFrame with options data
    data = {'secid': [1, 1, 1, 2, 2, 2, 3],
            'date': ['2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07'],
            'cp_flag': ['C', 'C', 'C', 'P', 'P', 'P', 'C'],
            'strike_price': [100, 100, 110, 110, 120, 120, 130],
            'exdate': ['2024-03-14', '2024-03-14', '2024-03-14', '2024-03-14', '2024-03-21', '2024-03-21', '2024-03-14'],
            'close': [10, 10, 10, 10, 10, 10, 10],
            'impl_volatility': [0.2, 0.3, 0.4, 0.25, 0.35, 0.45, 0.5]}
    df = pd.DataFrame(data)

    # Apply the function to the sample DataFrame
    result_df = filter_level1.clean_options_data(df)

    # Check if the result DataFrame has the expected number of rows after removing duplicates
    assert len(result_df) == 5
    
    # Check if the duplicates are properly removed based on the specified columns
    expected_data = {'secid': [1, 1, 2, 2, 3],
                     'date': ['2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07', '2024-03-07'],
                     'cp_flag': ['C', 'C', 'P', 'P', 'C'],
                     'strike_price': [110, 100, 110, 120,130],
                     'exdate': ['2024-03-14', '2024-03-14', '2024-03-14', '2024-03-21', '2024-03-14'],
                     'close': [10, 10, 10, 10, 10],
                     'impl_volatility': [0.4, 0.2, 0.25, 0.35, 0.5]}
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_delete_zero_bid_filter():
    # Create a sample DataFrame with options data
    data = {'secid': [1, 1, 2, 2],
            'cp_flag': ['C', 'P', 'C', 'P'],
            'strike_price': [100, 110, 120, 130],
            'exdate': ['2024-03-14', '2024-03-14', '2024-03-21', '2024-03-14'],
            'best_bid': [0.0, 1.5, 2.0, 0.0]}
    df = pd.DataFrame(data)

    # Apply the function to the sample DataFrame
    result_df = filter_level1.delete_zero_bid_filter(df)
    result_df.reset_index(drop=True, inplace=True)
    
    # Check if the result DataFrame has the expected number of rows after filtering
    assert len(result_df) == 2
    
    # Check if the rows with zero 'best_bid' values are properly filtered out
    expected_data = {'secid': [1, 2],
                     'cp_flag': ['P', 'C'],
                     'strike_price': [110, 120],
                     'exdate': ['2024-03-14', '2024-03-21'],
                     'best_bid': [1.5, 2.0]}
    expected_df = pd.DataFrame(expected_data)
    assert_frame_equal(result_df, expected_df)
