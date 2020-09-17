import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
import pandas as pd
import numpy as np
import datetime
import boto3
from helper import config
from helper import sclog
import decimal

sclog.logging_to_file('logging.txt')

def get_db_instances():
    'Gets db instance params from RDS via boto3 client'
    try:
        session = boto3.Session(region_name=REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        client = boto3.client('rds')
        response = client.describe_db_instances()

        return response
    except Exception as e:
        sclog.log_exception(e)

def _buildConnection(database=None):
    try:
        conn = psycopg2.connect(host=config.RDS_HOST, user=config.RDS_USERNAME, password=config.RDS_PASSWORD,
                               port=config.RDS_PORT, database=config.RDS_DATABASE, cursor_factory=DictCursor)
    except Exception as e:
        sclog.log_exception(e)
    finally:
        return conn

def run_query(sql=None):
    if sql is None:
        raise ValueError('No sql query specified')
    try:
        conn = _buildConnection()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        output = cur.fetchall()
        if len(output)>0:
            column_names = [desc[0] for desc in cur.description]
            dict_set = map(lambda x:dict(zip(column_names, x)), output)
            return pd.DataFrame(dict_set)
        else:
            column_names = [desc[0] for desc in cur.description]
            return pd.DataFrame(columns=column_names)
    except Exception as e:
        sclog.log_exception(e)
    finally:
        conn.close()

def insert_table(table_name=None, df=None):
    try:
        conn = _buildConnection()
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        conn.close()
    except Exception as e:
        print(e)

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
