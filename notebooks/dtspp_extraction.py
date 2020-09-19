import pandas as pd
import numpy as np
import netCDF4
from ftplib import FTP

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

def run_process():
    for i in range(2011, 2019):
        # grabbing data
        get_data(i)

run_process()