import pymysql
from pymysql.constants import CLIENT
import pandas as pd
import numpy as np
import datetime
import boto3

REGION = 'us-east-1'
DB = 'TBD'
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
host = ''
port= 3306
user='username'
pw = 'password'

def get_db_instances():
    'Gets db instance params from RDS via boto3 client'
    try:
        session = boto3.Session(region_name=REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        client = boto3.client('rds')
        response = client.describe_db_instances()

        print(response)
        return response
    except Exception as e:
        raise e

def _buildConnection(config, database):
    conn = pymysql.connect(host=config['host'], user=config['username'], password=config['password'],
                           database=database, client_flag=CLIENT.MULTI_STATEMENTS)
    return conn

def run_query(conn, sql):
    return pd.read_sql(sql, conn)
