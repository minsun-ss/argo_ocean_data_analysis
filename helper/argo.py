import pandas as pd
import numpy as np
import netCDF4
from db import insert_table
from ftplib import FTP
import os


def utf_decoding(array):
    return [x.decode('UTF-8') for x in array.data]

def masked_arrays_decoding(masked_array):
    lst = []
    for idx, row in enumerate(masked_array):
        number = ''.join(utf_decoding(row)).strip()
        lst.append(number)
    return lst

def param_masked_arrays_decoding(masked_array):
    # TODO: improve this horrendous function. The scientific calibrations have 4 dimensions which complicate a bit the automation.
    calibration = []
    for arrays in range(len(masked_array)):
        lst = []
        for idx, row in enumerate(masked_array[arrays].data):
            temp = []
            for x in range(len(row)):
                temp.append(''.join([y.decode('UTF-8') for y in row[x]]).strip())
            lst.append(temp)
        calibration.append(lst)
    return calibration

def unnesting(df, columns):
    '''Unnest the parameter data for Pressure, Salinity and Temperature. Pressure will be used to calculate depth.'''
    idx = df.index.repeat(df[columns[0]].str.len())
    df1 = pd.concat([pd.DataFrame({x: np.concatenate(df[x].values)}) for x in columns], axis=1)
    df1.index = idx

    return df1.join(df.drop(columns, 1), how='left')

def param(columns):
    '''Removes NaN values (99999.00) and select measured parameter when the adjusted parameters is NaN.'''
    non_adjusted = columns[0]
    adjusted = columns[1]
    param = []
    for x in range(len(columns[0])):
        if adjusted.iloc[x] >= 99999:
            param.append(non_adjusted.iloc[x])
        elif adjusted.iloc[x] >= 99999:
            param.append("NaN")
        else:
            param.append(non_adjusted.iloc[x])
    return param

class argo_manipulation:
    def __init__(self, fname=None, fdate=None):
        self.fname = fname
        self.fdate = fdate
        self.argo = netCDF4.Dataset(self.fname)

    def unmask_variables(self):
        '''Unmask variables from the NetCDF format and create a dataframe'''
        variables_dic = {}
        for var in list(self.argo.variables.keys())[:52]:
            '''
            ['HISTORY_INSTITUTION', 'HISTORY_STEP', 'HISTORY_SOFTWARE', 'HISTORY_SOFTWARE_RELEASE', 'HISTORY_REFERENCE',
            'HISTORY_DATE', 'HISTORY_ACTION', 'HISTORY_PARAMETER', 'HISTORY_START_PRES', 'HISTORY_STOP_PRES', 
            'HISTORY_PREVIOUS_VALUE', 'HISTORY_QCTEST'] (argo.variables.key()[52:]) are empty so we should not bother with them.
            '''
            if len(self.argo.variables[var][:]) <= 16:
                # Deals with the first variables which have a single information in them e.g. ['DATA_TYPE', 'FORMAT_VERSION', 'HANDBOOK_VERSION', 'REFERENCE_DATE_TIME', 'DATE_CREATION', 'DATE_UPDATE']
                variables_dic[var] = ''.join(utf_decoding(self.argo.variables[var][:])).strip()
            elif self.argo.variables[var][:].dtype != '|S1' and self.argo.variables[var][:].ndim == 1:
                variables_dic[var] = self.argo.variables[var][:]
            elif self.argo.variables[var][:].dtype != '|S1' and self.argo.variables[var][:].ndim > 1:
                variables_dic[var] = list(self.argo.variables[var][:].data)
            elif self.argo.variables[var][:].ndim == 1:
                variables_dic[var] = utf_decoding(self.argo.variables[var][:])
            elif self.argo.variables[var][:].ndim == 2:
                variables_dic[var] = masked_arrays_decoding(self.argo.variables[var][:])
            elif self.argo.variables[var][:].ndim == 3:
                variables_dic[var] = [masked_arrays_decoding(x) for x in self.argo.variables[var][:]]
            else:
                variables_dic[var] = param_masked_arrays_decoding(self.argo.variables[var][:])

        self.argo_df = pd.DataFrame(variables_dic)

    def select_columns(self):
        '''Restrict floats to region surrounding the St Lawrence Estuary. This is a fairly large area but can be further filtered if needed.
         Keep only columns we will need and rename columns that will be retained after processing.'''
        latitude_limits = (self.argo_df["LATITUDE"] > 38) & (self.argo_df["LATITUDE"] < 59)
        longitude_limits = (self.argo_df["LONGITUDE"] > -70) & (self.argo_df["LONGITUDE"] < -35)
        self.argo_df = (self.argo_df[latitude_limits & longitude_limits]
                   [["CYCLE_NUMBER", "PLATFORM_NUMBER", "LATITUDE", "LONGITUDE", "PRES", "PRES_ADJUSTED",
                     "TEMP", "TEMP_ADJUSTED",
                     "PSAL", "PSAL_ADJUSTED", "PROJECT_NAME"]]
                   .rename(columns={"PLATFORM_NUMBER": "floatid", "LATITUDE": "latitude", "LONGITUDE": "longitude",
                                    "PROJECT_NAME": "data_source"})
                   )

        # Create date column based on file name
        file_date = self.fdate.split("_")[0]
        self.argo_df["date"] = file_date
        self.argo_df["data_date"] = pd.to_datetime(self.argo_df["date"])

    def unnest_param(self):
        '''Parameters are list of all measures taken in a cycle. We need to unnest the data to get a single value per row.
        By default, NaN values are stored as 99999.000 so we are dropping these as they indicate no measure was taken.'''
        to_unnest = ['PRES', 'PRES_ADJUSTED', 'PSAL', 'PSAL_ADJUSTED', 'TEMP', 'TEMP_ADJUSTED']

        unnested_argo = unnesting(self.argo_df, to_unnest)
        unnested_argo["temperature"] = param([unnested_argo["TEMP"], unnested_argo["TEMP_ADJUSTED"]])
        unnested_argo["salinity"] = param([unnested_argo["PSAL"], unnested_argo["PSAL_ADJUSTED"]])
        # For every 10 meters you go down, the pressure increases by one atmosphere (approx 1 decibar) so with pressure recorded
        # in decibar we can assume depth is equivalent.
        unnested_argo["depth"] = param([unnested_argo["PRES"], unnested_argo["PRES_ADJUSTED"]])
        unnested_argo = unnested_argo[["data_date", "floatid", "latitude", "longitude", "depth", "temperature", "salinity"]]
        self.argo_df = unnested_argo[unnested_argo != 99999].dropna()

    def depth_bins(self):
        '''Bin the depth by levels of 100m and average temperature and salinity per bin. Also add data source as Argo Project.'''
        bins = range(0,int(self.argo_df["depth"].max()+100),100)
        self.argo_df = self.argo_df.groupby(["data_date", "floatid", pd.cut(self.argo_df.depth, bins)]).mean().drop("depth", axis=1).reset_index().dropna()
        # Change type from category to string to avoid issues when writing to db
        self.argo_df["depth"] = self.argo_df["depth"].astype(str)
        self.argo_df["data_source"] = "Argo Project"

    def manipulation_pipeline(self):
        self.unmask_variables()
        self.select_columns()
        self.unnest_param()
        self.depth_bins()

def main():
    '''For each file in the years we are interested in, run pipeline. For local testing, use files in data folder'''

    for year in range(2009, 2011):
        with FTP("usgodae.org") as ftp:
            ftp.login()
            ftp.cwd(f'/pub/outgoing/argo/geo/atlantic_ocean/{year}')
            for month in ftp.nlst()[:2]:
                ftp.cwd(f'{month}')
                for daily_file in ftp.nlst()[:2]:
                    with open('argo_daily_file', "wb") as fp:
                        ftp.retrbinary(f"RETR {daily_file}", fp.write)
                        myobject = argo_manipulation(fname = "argo_daily_file", fdate=daily_file)
                        myobject.manipulation_pipeline()
                        insert_table("ocean_data", myobject.argo_df)
                ftp.cwd("../")
            ftp.cwd("../")
        ftp.quit()

if __name__ == '__main__':
    main()