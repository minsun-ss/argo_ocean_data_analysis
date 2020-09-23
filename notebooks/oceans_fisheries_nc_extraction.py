import pandas as pd
import numpy as np
import zipfile
from helper import db
import datetime
import math

def extract_raw():
    zip = zipfile.ZipFile('../data/LTTMP_1980_2019.zip')

    df = pd.DataFrame()
    for i in [i for i in zip.namelist() if 'csv' in i]:
        datafile = pd.read_csv(zip.open(i), encoding='cp437')
        datafile.columns = ['station_id', 'latitude', 'longitude', 'measure_time', 'depth', 'temperature', 'salinity']
        datafile['measure_time'] = pd.to_datetime(datafile['measure_time'])
        insert_raw(datafile)
        df = pd.concat([df, datafile])
    return df

def insert_raw(df):
    try:
        print(df.shape)
        db.insert_table(table_name='dfo_quebec', df=df)
    except:
        raise

def clean_data(df):
    df.dropna(inplace=True)

    # filter subset to the right daterange
    subset = df[df['measure_time'] >= datetime.datetime(2009, 1, 1)].copy()

    bin_max = (math.ceil(subset['depth'].max() / 100) + 1) * 100
    cut_bins = [i for i in range(0, bin_max, 100)]
    subset['depth_bin'] = pd.cut(subset['depth'], cut_bins, right=False)
    subset['depth_bin'] = subset['depth_bin'].astype('str')

    subset = subset.groupby(['station', 'latitude', 'longitude', 'measure_time', 'depth_bin'])[
        ['temperature', 'salinity']].mean().reset_index()
    subset['data_source'] = 'DFO Quebec'
    RENAME_COLUMNS = {'measure_time': 'data_date', 'station': 'floatid', 'depth_bin': 'depth'}
    subset.rename(columns=RENAME_COLUMNS, inplace=True)
    return subset

def insert_cleaned(df):
    try:
        db.insert_table(table_name='ocean_data', df=df)
    except:
        raise

def run_process():
    df = clean_data(extract_raw())
    # insert_cleaned(df)

run_process()