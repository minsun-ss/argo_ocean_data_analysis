import pandas as pd
import numpy as np
import netCDF4
from helper import db
from shapely.geometry import shape, Point
import shapefile

# this is to take the argo data and add in a field to limit the mapping to shape since the
# initial round of data were done in a rectangular boundary and not shape boundary

def update_argo_data():
    r = shapefile.Reader('../assets/shapefile/iho.shap')
    gulf = shape(r.shapes()[0])

    def check_point(row):
        long, lat = row['longitude'], row['latitude']
        point = Point(long, lat)
        if gulf.contains(point):
            return 1
        else:
            return 0

    for i in range(2010, 2020):
        print(i)
        sql=f"""
        SELECT id, latitude, longitude FROM ocean_data
        WHERE EXTRACT(YEAR FROM data_date)={i} AND data_source='Argo Project'"""

        df = db.run_query(sql)
        df['in_gulf'] = df.apply(check_point, axis=1)
        final_df = df[df['in_gulf']==1]
        print(final_df.shape)

        # update data
        try:
            db.upsert(table_name='ocean_data', df=final_df, keys=['id'])
        except:
            raise

update_argo_data()