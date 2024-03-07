import pandas as pd

def DaystoMaturity_filter(df):
    df['exdate'] = pd.to_datetime(df['exdate'])
    df['date'] = pd.to_datetime(df['date'])
    df['T-t'] = (df['exdate'] - df['date']).dt.days
    df = df[df['T-t'] > 7]
    df = df[df['T-t'] < 180]
    return df

def ExtremeIV_filter(df):
    df = df[df['impl_volatility'] > 0.05]
    df = df[df['impl_volatility'] < 1.0]
    return df