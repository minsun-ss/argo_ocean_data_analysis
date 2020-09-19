import pandas as pd
import numpy as np
import netCDF4
from ftplib import FTP
import os
import tarfile
import shutil
from shapely.geometry import shape, Point
import shapefile

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
        for i in file_list[38:39]:
            print(i)
            gtspp = tarfile.open(f'../data/gtspp/{i}')
            gtspp.extractall(location)
            'Checking the contents of the folder'
            find_gulf_data(location)
            'Deleting contents'
            delete_folder_contents(f'{location}/atlantic')
        print('Done.')
    except:
        raise

def find_gulf_data(location):
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
        print(lat, long)

        point = Point(long, lat)
        if gulf.contains(point):
            position_quality = data.variables['position_quality_flag'][:]
            position_quality = position_quality[position_quality.mask == False].data[0]
            station_id = data.variables['gtspp_station_id'][:]
            station_id = station_id[station_id.mask == False].data[0]
            measure_time = data.variables['time'][:]
            measure_time = measure_time[measure_time.mask == False].data[0][0]
            measure_time_quality = data.variables['time_quality_flag'][:]
            measure_time_quality = time_quality[time_quality.mask == False].data[0]

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

            return final

def delete_folder_contents(location):
    # to remove files
    # location is usually '../data/gtspp/atlantic'
    shutil.rmtree(location)

def run_process():
    for i in range(2011, 2019):
        # grabbing data
        get_data(i)

print(extract_to_folder('../data/gtspp'))

