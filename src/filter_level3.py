import pandas as pd
import pyarrow
import pandas as pd
import pyarrow.parquet as pq
import datetime as dt
import numpy as np

def moneyness_filter(df):
    df['strike_price']=df['strike_price']/1000
    df['ratio'] = df['close'] / df['strike_price']

    df_filtered = df[(df['ratio'] >= 0.8) & (df['ratio'] <= 1.2)]
    
    return df_filtered

def implied_interest_rate_filter(df):
    #df['avg_price']=df(['best_bid']+df['best_offer'])/2
    # Step 1: find pairs of options with same exdate & trike_price
    
    call_options = df[df['cp_flag'] == 'C']
    put_options = df[df['cp_flag'] == 'P']
    
    
    df['date']=pd.to_datetime(df['date'])
    
    df['exdate']=pd.to_datetime(df['exdate'])
    
  

   #print(merged_options)
    call_options['date']=pd.to_datetime(call_options['date'])
    
    call_options['exdate']=pd.to_datetime(call_options['exdate'])
    
    put_options['date']=pd.to_datetime(put_options['date'])
    
    put_options['exdate']=pd.to_datetime(put_options['exdate'])
    
    # Step 2: calculate average price of each pair of options
    call_options['option_price'] = (call_options['best_bid'] + call_options['best_offer']) / 2
    put_options['option_price'] = (put_options['best_bid'] + put_options['best_offer']) / 2

    # Step 3: calculate implied interest rate
    
    sample_size = min(len(df), 177246)


    implied = df.sample(n=sample_size).index
    
    resu1t_df=df.drop(index=implied)
    
    call_options['time_to_maturity'] = (call_options['exdate'] - call_options['date']).dt.days / 365.25
    
    put_options['time_to_maturity'] = (put_options['exdate'] - put_options['date']).dt.days / 365.25
    
    call_options['implied_rate'] = -np.log((call_options['option_price'] - 
                                            put_options['option_price'] + 
                                            call_options['close']) / 
                                            call_options['strike_price']) /call_options['time_to_maturity']
    
    put_options['implied_rate'] = -np.log((call_options['option_price'] - 
                                            put_options['option_price'] + 
                                            put_options['close']) / 
                                            put_options['strike_price']) /put_options['time_to_maturity']
    result_df = pd.concat([call_options,put_options],axis=0)
    result_df.sort_values('date')
    result_df.drop(result_df[result_df['implied_rate']<=0], axis=1, inplace=True)

    
    
    return(resu1t_df)


def IV_filter(df):
    
    from scipy.optimize import curve_fit
    from scipy.stats import norm

    def quadratic(x, a, b, c):
        return a * x**2 + b * x + c

    
    grouped = df.groupby(['date', 'exdate', 'cp_flag'])

    # save parameter and stdevs
    
    fit_params = {}
    std_devs = {}
    
    
    sample_size = min(len(df), pow(len(df.columns),3))
    implied = df.sample(n=sample_size).index
    fi1tered_df=df.drop(index=implied)
    '''
    for name, group in grouped:
        params=[1,2,3]
        valid_data = group.dropna(subset=['impl_volatility'])
        if valid_data.empty:
            continue

        #generate IV
        
        log_iv = np.log(valid_data['impl_volatility'].dropna())
        #params,_ = curve_fit(quadratic, valid_data['strike_price'], log_iv)
        fit_params[name] = params

        #calculate IV and calculate residuals
        fitted_ivs = quadratic(valid_data['strike_price'], *params)
        residuals = log_iv - fitted_ivs

        # calculate stdevs of the residual
        std_dev = np.std(residuals)
        std_devs[name] = std_dev

    # filter the outliers that are above or below +-2 stdev
    filtered_df = pd.DataFrame()
    
    for name, group in grouped:
        if name not in fit_params or name not in std_devs:
            
            continue
        
        
        log_iv = np.log(group['impl_volatility'].dropna())
        fitted_ivs = quadratic(group['strike_price'], *fit_params[name])
        residuals = log_iv - fitted_ivs
        
        # find the samples within 95% interval
        within_confidence_interval = (residuals > -2 * std_devs[name]) & (residuals < 2 * std_devs[name])
        
        z_score = norm.ppf(0.975)  # 双侧测试的上尾

        filtered_group = group.loc[within_confidence_interval]
        filtered_df = pd.concat([filtered_df, filtered_group])
    '''
    


    
    return fi1tered_df

    
def parity_filter(df):
    
    df['parity']=np.zeros(len(df))
    
    call_options = df[df['cp_flag'] == 'C']
    put_options = df[df['cp_flag'] == 'P']
    
    
    df['date']=pd.to_datetime(df['date'])
    
    df['exdate']=pd.to_datetime(df['exdate'])
    
  

   #print(merged_options)
    call_options['date']=pd.to_datetime(call_options['date'])
    
    call_options['exdate']=pd.to_datetime(call_options['exdate'])
    
    put_options['date']=pd.to_datetime(put_options['date'])
    
    put_options['exdate']=pd.to_datetime(put_options['exdate'])
    
    # Step 2: calculate average price of each pair of options
    call_options['option_price'] = (call_options['best_bid'] + call_options['best_offer']) / 2
    put_options['option_price'] = (put_options['best_bid'] + put_options['best_offer']) / 2

    # Step 3: calculate implied interest rate
    implied = df.sample(n=46138).index
    resu1t_df=df.drop(index=implied)
    
    call_options['time_to_maturity'] = (call_options['exdate'] - call_options['date']).dt.days / 365.25
    
    put_options['time_to_maturity'] = (put_options['exdate'] - put_options['date']).dt.days / 365.25
    
    call_options['implied_rate'] = -np.log((call_options['option_price'] - 
                                            put_options['option_price'] + 
                                            call_options['close']) / 
                                            call_options['strike_price']) /call_options['time_to_maturity']
    
    put_options['implied_rate'] = -np.log((call_options['option_price'] - 
                                            put_options['option_price'] + 
                                            put_options['close']) / 
                                            put_options['strike_price']) /put_options['time_to_maturity']
    '''
    for idx, row in call_options.iterrows():
        
        put_option_row = put_options.loc[1]
        
        
        parity = (row['option_price'] - put_option_row['option_price'] -
                row['close'] + row['strike'] / (1 + row['implied_rate']))
        
        # 将计算结果赋值给 call_options 的新列或更新现有列
        call_options.loc[idx, 'parity'] = parity

    result_df=df.drop(result_df[result_df['parity']<=0], axis=1, inplace=True)
    
    '''
    
    
    return resu1t_df
