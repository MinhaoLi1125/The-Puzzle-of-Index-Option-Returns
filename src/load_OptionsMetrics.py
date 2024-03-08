from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path 


import pandas as pd
import numpy as np
import wrds

import config


OUTPUT_DIR = Path(config.OUTPUT_DIR)
DATA_DIR = Path(config.DATA_DIR)
WRDS_USERNAME = config.WRDS_USERNAME
START_DATE = config.START_DATE
END_DATE = config.END_DATE
db = wrds.Connection(wrds_username=WRDS_USERNAME)

def pull_Option_price(start_date=START_DATE, end_date=END_DATE): 
    # https://wrds-www.wharton.upenn.edu/data-dictionary/optionm_all/opprcd2023/
    df = []
    year_list = [1996, 1997, 1998, 1999, 
             2000, 2001, 2002, 2003, 
             2004, 2005, 2006, 2007, 
             2008, 2009, 2010, 2011, 2012]
    
    for year in year_list:
    
        query = f"""
            SELECT 
                opp.date, opp.secid, opp.exdate,  
                opp.cp_flag, opp.strike_price, 
                opp.forward_price, opp.impl_volatility, 
                opp.volume, opp.contract_size, 
                opp.best_bid, opp.best_offer
            
            FROM
                optionm_all.opprcd{year} AS opp
            
            WHERE
                (opp.secid = 108105)
            
        """ 
        
        data = db.raw_sql(query, date_cols=["date"])
        df.append(data)
            
    df = pd.concat(df, ignore_index=True)
    df = df[df['date'] <= end_date]
    return df


def pull_Security_price(end_date=END_DATE):
    df = []
    year_list = [1996, 1997, 1998, 1999, 
             2000, 2001, 2002, 2003, 
             2004, 2005, 2006, 2007, 
             2008, 2009, 2010, 2011, 2012]
    
    for year in year_list:
    
        query = f"""
            SELECT
                sec.date, sec.secid, sec.open, sec.close

            FROM
                optionm_all.secprd{year} AS sec

            WHERE
                sec.secid = 108105

        """
    
        data = db.raw_sql(query, date_cols=["date"])
        df.append(data)
        
    df = pd.concat(df, ignore_index=True)
    df = df[df['date'] <= end_date] 
    
    return df



def pull_TB_int_rate(wrds_username=WRDS_USERNAME, start_date="1995-12-04", end_date=END_DATE):
    query = f"""
		SELECT
			rd.date, rd.tb_m3

		FROM
			frb_all.rates_daily AS rd
		
  		WHERE
			rd.date >= '{start_date}' AND 
        	rd.date <= '{end_date}'
        
    """
    
    df = db.raw_sql(query, date_cols=["date"]).set_index('date')
    
    df = df.loc['1996-01-04':]
    df = df.drop(df.index[0])
    df = df.reset_index().rename(columns={'index': 'date'})
    
    return df 


def merge_data():
    
    df1 = pull_Option_price()
    df2 = pull_Security_price()
    df3 = pull_TB_int_rate()
    
    df = pd.merge(df1, df2, on=['date', 'secid'])
    df = pd.merge(df, df3, on=['date'])
    
    return df

def load_OptionMetrics(data_dir=DATA_DIR):
    path = data_dir / 'pulled'/ 'OptionMetrics.parquet'
    df = pd.read_parquet(path)
    
    return df

def _demo():
    OptionMetrics = load_OptionMetrics(data_dir=DATA_DIR)

if __name__ == "__main__":

    OptionMetrics = merge_data()
    path = Path(DATA_DIR) / 'pulled' / 'OptionMetrics.parquet'
    OptionMetrics.to_parquet(path)
    db.close()
