import os,sys
import numpy as np
import pandas as pd
from s3fs.core import S3FileSystem
import psycopg2
import psycopg2.extras as extras
from io import StringIO


params_dic = {
    "host" : "lambda-test.cyb3keo6utm7.us-east-1.rds.amazonaws.com",
    "database" : "postgres",
    "user" : "postgres",
    "password" : "dashboard"
}

s_bucket = "serverless-s3-event-processor-eventbucket-kvjsay3gp8ie"
s_key = "sec_data.csv"

dat = { 'kiosk':'K1', 'tmstamp':'2020-08-24 08:00:02','emp_id':'emp111','fname':'George',\
    'middle':'Henry','lname':'Stevenson','emp_occupancy':'IN'}

def get_s3_data(bucket,key):
    df = None 

    # Try reading csv from S3 file system
    try:
        s3 = S3FileSystem(anon=False)
        
        df = pd.read_csv(s3.open('{}/{}'.format(s_bucket, s_key),
                                mode='rb')
                        )
        print(df)
    except Exception as e:
        print(e)
    return df

def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    print("Connection successful")
    return conn

def execute_query(conn, query):
    """ Execute a single query """
    
    ret = 0 # Return value
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1

    # If this was a select query, return the result
    if 'select' in query.lower():
        ret = cursor.fetchall()
    cursor.close()
    return ret

def copy_from_stringio(conn, df, table):
    """
    Here we are going save the dataframe in memory 
    and use copy_from() to copy it to the table
    """
    # save dataframe to an in memory buffer
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    
    cursor = conn.cursor()
    try:
        cursor.copy_from(buffer, table, sep=",")
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("copy_from_stringio() done")
    cursor.close()


# Run the execute_many strategy
df = get_s3_data(s_bucket,s_key)
print("got s3")
conn = connect(params_dic)
copy_from_stringio(conn, df, 'badgedata')
print("copied file")
print(execute_query(conn, "select count(*) from badgedata;"))
print(execute_query(conn, "delete from badgedata where true;"))