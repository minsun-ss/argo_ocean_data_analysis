import psycopg2
from psycopg2.extras import DictCursor
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
                               port=config.RDS_PORT, database='oceandb', cursor_factory=DictCursor)
    except Exception as e:
        print(e.args)
    finally:
        return conn

def run_query(conn, sql=None):
    sql="SELECT * from pg_catalog.pg_tables where schemaname != 'pg_catalog' and schemaname != 'information_schema';"
    try:
        conn = _buildConnection()
        cur = conn.cursor()
        cur.execute(sql)
        output = cur.fetchall()
    except Exception as e:
        print(e.args())
        raise e
    finally:
        conn.close()
        print(output)
        return output


run_query(_buildConnection())