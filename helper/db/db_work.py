import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
import pandas as pd
import numpy as np
import datetime
import boto3
from helper import config

def get_db_instances():
    'Gets db instance params from RDS via boto3 client'
    try:
        session = boto3.Session(region_name=REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        client = boto3.client('rds')
        response = client.describe_db_instances()

        return response
    except Exception as e:
        raise e

def _buildConnection(database=None):
    try:
        conn = psycopg2.connect(host=config.RDS_HOST, user=config.RDS_USERNAME, password=config.RDS_PASSWORD,
                               port=config.RDS_PORT, database=config.RDS_DATABASE, cursor_factory=RealDictCursor)
    except Exception as e:
        print(e.args)
    finally:
        return conn

def run_query(conn, sql=None):
    if sql is None:
        raise ValueError('No sql query specified')
    try:
        conn = _buildConnection()
        cur = conn.cursor()
        print(sql)
        cur.execute(sql)
        conn.commit()
        output = cur.fetchall()
        print(output)
    except Exception as e:
        print(e.args())
    finally:
        conn.close()
        return output



def insert_table(table_name=None, df=None):
    try:
        conn = _buildConnection()
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        conn.close()
    except Exception as e:
        raise e

def _val_format(item):
    if item is None:
        return 'NULL'
    elif isinstance(item, (str)):
        item = item.replace("'", "''")
        if len(item)==0:
            return 'NULL'
        else:
            return f'\'{item}\''
    elif isinstance(item, (decimal.Decimal, int, float, complex)):
        return str(item)
    elif isinstance(item, datetime.datetime):
        item_string = item.strftime('%Y-%m-%d %H:%M:%S.%f')
        return f'\'{item_string}\''
    elif isinstance(item, datetime.timedelta):
        return f'\'{item}\''
    elif item.isnumeric():
        return item
    else:
        item = item.replace("'", "''")
        return f'\'{item}\''

def _clean_df(df):
    df = df.replace({np.nan: None})
    return df.where(pd.notnull(df), None)

if __name__=='__main__':
    # query="""SELECT count(*) FROM OCEAN_DATA"""
    run_query(_buildConnection())