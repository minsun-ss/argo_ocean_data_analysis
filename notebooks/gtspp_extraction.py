import pandas as pd
import numpy as np
import netCDF4
from ftplib import FTP
import os
import tarfile
import shutil
from shapely.geometry import shape, Point
import shapefile
import time
from helper import db
import math

def get_data(year):
    # extracts the tarzips from ftp for a specific year and dumps them into the data folder

    # this part to extract data and dump to folder
    url = 'ftp.nodc.noaa.gov'
    directory = '/pub/data.nodc/gtspp/best_nc'
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    ftp = FTP(url)
    ftp.login()
    ftp.cwd(directory)

    # this builds all the filenames needed to grab for the year
    file_names = [f'gtspp4_at{year}{i}.tgz' for i in month]

    try:
        for i in file_names:
            print(i)
            with open(f'../data/gtspp/{i}', 'wb') as fp:
                ftp.retrbinary(f'RETR {i}', fp.write)
        print('Done')
    except:
        raise

def extract_to_folder(location):
    # extracts tgz file to specified location
    file_list = [i for i in os.listdir('../data/gtspp') if 'tgz' in i]

    # right now only unzips 1 file at a time
    try:
        for i in file_list[-2:]:
            print(i)
            gtspp = tarfile.open(f'../data/gtspp/{i}')
            gtspp.extractall(location)
            print('Checking the contents of the folder')
            find_gulf_data(location, i)
            time.sleep(60)
            print('Deleting contents')
            delete_folder_contents(f'{location}/atlantic')
        print('Done.')
    except:
        raise

def find_gulf_data(location, filename):
    # start opening up the nc files and finding point data. Returns a dataframe with matching points
    # and accompanying data, uncleaned.
    r = shapefile.Reader('../assets/shapefile/iho.shap')
    gulf = shape(r.shapes()[0])

    gtspp_directory = f'{location}/atlantic'
    year_value = os.listdir(gtspp_directory)
    gtspp_directory = f'{gtspp_directory}/{year_value[0]}'
    month_value = os.listdir(gtspp_directory)
    gtspp_directory = f'{gtspp_directory}/{month_value[0]}'
    print(gtspp_directory)

    for file in os.listdir(gtspp_directory):
        data = netCDF4.Dataset(f'{gtspp_directory}/{file}')

        # first check to see if the point is within the area
        array_lat, array_long = data.variables['latitude'][:], data.variables['longitude'][:]
        lat, long = data.variables['latitude'][:][0], data.variables['longitude'][:][0]
        # print(lat, long)

        point = Point(long, lat)
        print(point)
        if gulf.contains(point):
            try:
                position_quality = data.variables['position_quality_flag'][:]
                position_quality = position_quality[position_quality.mask == False].data[0]
                station_id = data.variables['gtspp_station_id'][:]
                station_id = station_id[station_id.mask == False].data[0]
                measure_time = data.variables['time'][:]
                measure_time = measure_time[measure_time.mask == False].data[0][0]
                measure_time_quality = data.variables['time_quality_flag'][:]
                measure_time_quality = measure_time_quality[measure_time_quality.mask == False].data[0]

                salinity = data.variables['salinity'][:]
                salinity = salinity[salinity.mask == False].data.flatten(order='C')
                salinity_quality = data.variables['salinity_quality_flag'][:]
                salinity_quality = salinity_quality[salinity_quality.mask == False].data.flatten()
                depth = data.variables['z'][:]
                depth = depth[depth.mask == False].data.flatten()
                depth_quality = data.variables['z_variable_quality_flag'][:]
                depth_quality = depth_quality[depth_quality.mask == False].data.flatten()
                temperature = data.variables['temperature'][:]
                temperature = temperature[temperature.mask == False].data.flatten()
                temperature_quality = data.variables['temperature_quality_flag'][:]
                temperature_quality = temperature_quality[temperature_quality.mask == False].data.flatten()

                data_single_line = pd.DataFrame([long, lat, position_quality, station_id, measure_time, measure_time_quality]).transpose()
                data_single_line.columns = ['longitude', 'latitude', 'position_quality', 'station_id', 'measure_time',
                                            'measure_time_quality']
                data_multiple_value = pd.DataFrame(
                    list(zip(salinity, salinity_quality, depth, depth_quality, temperature, temperature_quality)))
                data_multiple_value.columns = ['salinity', 'salinity_quality', 'depth', 'depth_quality', 'temperature',
                                               'temperature_quality']
                data_single_line['merge'], data_multiple_value['merge'] = 0, 0
                final = data_single_line.merge(data_multiple_value, how='inner', on='merge')

                final.to_csv(f'../data/gtspp/csv_results/{filename}.csv', mode='a+', header=False)
            except:
                data.close()
                continue
        data.close()
    time.sleep(60)

def delete_folder_contents(location):
    # to remove files
    # location is usually '../data/gtspp/atlantic'
    shutil.rmtree(location)

def raw_database_dump():
    # takes cleaned files from the filtering and dumps raw to database for possible future use (if we need to
    # redo a calculation
    csv_folder_location = '../data/gtspp/csv_results'
    file_list = os.listdir(csv_folder_location)

    # opens each file, appends a header, cleans up miscellaneous columns, pushes to db
    for i in file_list[2:]:
        print(i)
        df = pd.read_csv(f'{csv_folder_location}/{i}', header=None)
        GTSSP_COL = ['index', 'longitude', 'latitude', 'position_quality', 'station_id', 'measure_time',
                     'measure_time_quality', 'merge', 'salinity', 'salinity_quality', 'depth', 'depth_quality',
                     'temperature', 'temperature_quality']
        df.columns = GTSSP_COL

        def to_time(days):
            try:
                # 1970 is 25569 in number of days... this field appears to be structured
                # to be used in excel. :(
                new_time = (days - 25569)
                return pd.Timestamp(new_time, unit='d')
            except:
                return np.nan

        df['measure_time'] = df['measure_time'].apply(to_time)
        df.drop(columns=['index', 'merge'], inplace=True)

        try:
            db.insert_table(table_name='gtspp', df=df)
        except:
            raise

def cleaned_database_dump():
    for i in range(2010, 2020):
        print(i)
        # so measurements of quality are done from 0 to 9, with 1 being good, 0 being no check,
        # 2-3 being probably good/bad,4 being bad, and everything else just please ignore - so
        # let's just filter everything for 1

        sql = f"""SELECT longitude, latitude, station_id, measure_time, salinity, depth, temperature FROM gtspp 
        WHERE EXTRACT(YEAR FROM measure_time)={i} AND position_quality=1 
        AND measure_time_quality=1 AND salinity_quality=1 AND depth_quality=1 AND temperature_quality=1;"""

        good_data_df = db.run_query(sql)

        # slice up the bins based on the max depth
        bin_max = (math.ceil(good_data_df['depth'].max() / 100) + 1) * 100
        cut_bins = [i for i in range(0, bin_max, 100)]

        good_data_df['depth_bin'] = pd.cut(good_data_df['depth'], cut_bins, right=False)
        good_data_df['depth_bin'] = good_data_df['depth_bin'].astype('str')
        grouped_df = good_data_df.groupby(['measure_time', 'latitude', 'longitude', 'station_id', 'depth_bin'])[
            ['salinity', 'temperature']].mean().reset_index()

        RENAME_COLUMNS = {'measure_time': 'data_date', 'station_id': 'floatid', 'depth_bin': 'depth'}
        grouped_df.rename(columns=RENAME_COLUMNS, inplace=True)
        grouped_df['data_source'] = 'GTSPP'

        print(grouped_df.shape)
        try:
            db.insert_table(table_name='ocean_data', df=grouped_df)
        except:
            raise

def count_measurements():
    file_list = [i for i in os.listdir('../data/gtspp') if 'tgz' in i]
    count=0
    # right now only unzips 1 file at a time
    try:
        for i in file_list:
            gtspp = tarfile.open(f'../data/gtspp/{i}')
            print(type(gtspp.getnames()))
            count += len(gtspp.getnames())
            print(i, count)
        print('Done')
    except:
        raise

def run_process():
    # collects data from ftp
    for i in range(2019, 2020):
        get_data(i)
    # unpacks data, filters for data in the gulf, outputs to csv
    extract_to_folder('../data/gtspp')
    raw_database_dump()
    cleaned_database_dump()

count_measurements()