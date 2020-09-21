import os
import json
import boto3
import botocore
import psycopg2
import logging
import sys

import pandas as pd
from s3fs.core import S3FileSystem
# Since we want to benchmark the efficiency of each insert strategy
from timeit import default_timer as timer

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

# Try reading csv from S3 file system
try:
    s3 = S3FileSystem(anon=False)
    
    df = pd.read_csv(s3.open('{}/{}'.format(s_bucket, s_key),
                            mode='rb')
                    )
    print(df)
except Error as e:
    print(e)

#asdf
# Trap errors for copying the array to our database
conn = None
try:
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect( **params_dic )
    cursor = conn.cursor()

    #print(conn.get_dsn_parameters(),"\n")
    #cursor.execute("SELECT NOW();")
    #print(cursor.fetchall())
    cursor.execute('insert into "badgedata" ("kiosk","tmstamp","emp_id","fname","middle",\
        "lname","emp_occupancy") values (%s, %s,%s, %s,%s, %s,%s)',(dat['kiosk'],dat['tmstamp'],\
            dat['emp_id'],dat['fname'],dat['middle'],dat['lname'],dat['emp_occupancy']))
    conn.commit()

    cursor.close()
except psycopg2.Error as e:
    t_message = "Database error: "
    print(t_message)
    raise e

print("Connection successful")

# Clean up by closing the database cursor and connection
conn.close()
    