import pymysql
from pymysql.constants import CLIENT
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

        print(response)
        return response
    except Exception as e:
        raise e

def _buildConnection(database='ocean'):
    conn = pymysql.connect(host=config.RDS_HOST, user=config.RDS_USERNAME, password=config.RDS_PASSWORD, port=config.RDS_PORT,
                           database=config.RDS_DATABASE, client_flag=CLIENT.MULTI_STATEMENTS)
    return conn

def run_query(conn, sql=None):
    sql="SHOW DATABASES"
    conn = _buildConnection(cfg, database='')
    cur = conn.cursor()
    cur.execute(sql)
    output = cur.fetchall()
    print(output)
    conn.close()

run_query(_buildConnection())