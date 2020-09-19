import pandas as pd
import numpy as np
import netCDF4
from ftplib import FTP
import os
import tarfile
import shutil
from shapely.geometry import shape, Point

def get_data(year):
    # extracts the tarzips from ftp for a specific year and dumps them into the data folder

    # this part to extract data and dump to folder
    url = 'ftp.nodc.noaa.gov'
    directory = '/pub/data.nodc/gtspp/best_nc'
    month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    from ftplib import FTP
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
        for i in file_list[:1]:
            print(i)
            gtspp = tarfile.open(f'../data/gtspp/{i}')
            gtspp.extractall(location)
        print('Done.')
    except:
        raise

def find_gulf_data():
    # start opening up the nc files and finding point data. Returns a dataframe with matching points
    # and accompanying data, uncleaned.
    r = shapefile.Reader('../assets/shapefile/iho.shp')
    gulf = shape(r.shapes()[0])
    print(shapes)

    gstpp_directory = '../data/gtspp/atlantic/2009/01'
    latitude, longitude = [], []
    for file in os.listdir(gstpp_directory):
        cdf_coordinates = netCDF4.Dataset(f'{gstpp_directory}/{file}')

        # first check to see if the point is within the area
        array_lat, array_long = cdf_coordinates.variables['latitude'][:], cdf_coordinates.variables['longitude'][:]
        lat = array_lat[array_lat.mask == False].data[0].tolist()[0]
        long = array_long[array_long.mask == False].data[0].tolist()[0]
        print(long, lat)
        point = Point(long, lat)

        if gulf.contains(point):
            print(lat, long)
            break

def delete_folder_contents(location):
    # to remove files
    # location is usually '../data/gtspp/atlantic'
    shutil.rmtree(location)

def run_process():
    for i in range(2011, 2019):
        # grabbing data
        get_data(i)

extract_to_folder('../data/gtspp')