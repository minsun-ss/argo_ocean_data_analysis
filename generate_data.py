import pandas as pd
import json
from helper import db

# setting up the data for the heroku visualization away from the flask app itself

# this is the old tester data
def get_fish_data():
    fish_data = pd.read_csv('testfiles/test.csv') # dummy query to avoid hitting up RDS for testing
    fish_data.date = pd.to_datetime(fish_data.date).dt.year # will need to import date as year
    fish_data['total'] = fish_data.iloc[:, 5:-1].sum(axis=1) # we need to calculate total population as well
    return fish_data

def get_fish_info():
    fish_info = pd.read_excel('testfiles/fish_desc.xlsx')
    return fish_info

def get_fish_aggregate(**kwargs):
    query = """
    SELECT YEAR, COALESCE(fish_type, 'total') AS fish_type, avg_depth, fish_total FROM 
    (SELECT EXTRACT(YEAR FROM DATE) AS YEAR, fish_type, avg(DEPTH) AS avg_depth, sum(fish_count) AS fish_total
    FROM fish_data
    WHERE fish_count>0
    GROUP by YEAR, rollup(fish_type)) AS t1"""

    try:
        fish_data = db.run_query(query)
    except:
        fish_data = pd.read_csv('testfiles/fish_aggregate.csv')

    # test aggregate file for now
    fish_data['year'] = fish_data['year'].astype('int')
    return fish_data

def get_fish_locations():
    query = """
    SELECT extract(year from DATE) AS year, longitude, latitude, fish_type 
    FROM fish_data
    WHERE fish_count>0;
    """

    try:
        fish_locations = db.run_query(fish_data)
    except:
        fish_locations = pd.read_csv('testfiles/fish_locations.csv')

    fish_locations['year'] = fish_locations['year'].astype('int')
    return fish_locations

def get_param_data():
    try:
        param_data = build_param_data()
    except:
        param_data = pd.read_csv('testfiles/sample_param_data.csv')
    return param_data

def correlation_table(fish_df, param_df):
    df = fish_df.merge(param_df, on='year')[['year', 'fish_type', 'fish_total', 'depth_range', 'temperature', 'salinity']]
    return df

def make_categorical(df):
    '''Generates intervals of type '0-100' then map them to the depth column to make it categorical.'''
    intervals = ["{}-{}".format(i * 100, (i + 1) * 100) for i in range(60)]

    cat_type = CategoricalDtype(categories=intervals, ordered=True)
    df["depth_range"] = df["depth_range"].astype(cat_type)
    return df

def build_param_data():
    '''Return a dataframe with average temperature and salinity by depth and year,
    temperature and salinity evolution compared to 2009 and year over year temperature and salinity evolution.
    The SQL query filters outlier data (e.g. temperature below -2.5 or above 40 degrees celsius) and only takes values
    for the months of April to September (2009-2018) since these are the months the fish live in the Estuary.'''

    # The regex will remove brackets and parentheses from the depth column and avoid (0, 100], [0, 100) issues.
    # Include 'AND in_gulf = 1' to the filter when the gstpp data is all added.
    query = """
    SELECT
    extract(year from data_date) as year,
    REGEXP_REPLACE(depth, '[\[\]\(\)]', '', 'g') as depth_range,
    ROUND(AVG(temperature), 3) as temperature,
    ROUND(AVG(salinity), 3) as salinity
    FROM OCEAN_DATA
    WHERE data_date BETWEEN '2009-01-01' AND '2018-12-31'
    AND salinity BETWEEN 30 and 41
    AND temperature BETWEEN -2.5 and 40
    AND to_char(data_date,'Mon') in ('Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep')
    AND depth <> 'nan'
    AND in_gulf = 1
    GROUP BY year, depth_range
    ORDER BY year, temperature;
    """
    param_df = db.run_query(query)

    # Turn the depth_range column values back into categories. Start by replacing commas by hyphen and removing the white space.
    param_df['depth_range'] = param_df['depth_range'].str.replace(r"\, ", "-")
    param_df = make_categorical(param_df)

    # Change temp and salinity to floats
    param_df["temperature"] = param_df["temperature"].astype(float)
    param_df["salinity"] = param_df["salinity"].astype(float)

    # Make the year column a string
    param_df['year'] = param_df['year'].astype(int).astype(str)

    return param_df.reset_index(drop=True)