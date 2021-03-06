# -*- coding: utf-8 -*-
"""
.. module: Serverless S3 Event Processor
    :platform: AWS    
.. moduleauthor:: Bruce Goldfeder
.. contactauthor:: bruce.goldfeder@asetpartners.com
"""

import os,sys
import numpy as np
import pandas as pd
import json
import boto3
import botocore
import psycopg2
import logging
from s3fs.core import S3FileSystem
import psycopg2
import psycopg2.extras as extras
from io import StringIO

# Initialize Logger
logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# Database configuration filename in S3 bucket
PG_CONF_NAME = "db_config.json"

s3 = boto3.client('s3')

def process_file(d):
    """ File process ingest driver function """
    
    params_dic = None
    
    if d['key']==PG_CONF_NAME:
        logging.info("Database Configuration file uploaded to S3")
        
    else:    
        # Read in the db config json from S3 file
        try:
            obj = s3.get_object(Bucket=d['bucket_name'], Key=PG_CONF_NAME)
            data_in = obj['Body'].read().decode('utf-8','ignore')
            logger.info(data_in)
            params_dic = json.loads(data_in)
            logger.info(params_dic)
            
        except Exception as e:
            logger.info("Error reading in db_config file from S3")
            logger.info(e)
            return False
    
        # Log the db_config or load the data into the database
        load_data(d['bucket_name'],d['key'],params_dic)
        
    return True
    
def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        logging.info('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        logging.info("Error connecting to database, error should follow")
        logging.error(error)
        raise
    logging.info("Connection successful")
    return conn

def execute_query(conn, query):
    """ Execute a single query """
    
    ret = 0 # Return value
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
        raise error

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
        logging.error("Error: %s" % error)
        conn.rollback()
        cursor.close()
        raise error
    logging.info("copy_from_stringio() done")
    cursor.close()


def load_data(s_bucket,s_key,params_dic):
    df = None 

    # Try reading csv from S3 file system
    try:
        s3 = S3FileSystem(anon=False)
        
        df = pd.read_csv(s3.open('{}/{}'.format(s_bucket, s_key),
                                mode='r')
                        )
        print(df)
    except Exception as e:
        logging.info(e)
        raise e
    conn = connect(params_dic)
    copy_from_stringio(conn, df, 'badgedata')
    logger.info("copied file into database successfully")
    logger.info(execute_query(conn, "select count(*) from badgedata;"))
    #print(execute_query(conn, "delete from badgedata where true;"))
    conn.close()
    return df

def log_upload_content(up_data):
    # Log output from db_config.json file in S3 bucket
    j_recs = []
    for key, value in up_data.items():
        rec = ""+key+ '->'+ value+"\n"
        j_recs.append(rec)
    logger.info(j_recs) 

def log_up_evt(uv,num_rcv):
    tot_rcv = len(uv.get('Proc_Items')) + len(uv.get('Err_Items'))
    if tot_rcv > 0:
        uv['status'] = True
        uv['TotalItems'] = { 'Received': num_rcv, \
                             'Processed': len(uv.get('Proc_Items')), \
                             'Errors': len(uv.get('Err_Items'))}
    
    logger.info(f"upload_event:{uv}")
    
    return uv

def lambda_handler(event, context):
    
    # Upload event metadata capture dictionary structure
    resp = {'status': False, 'TotalItems': {} , 'Proc_Items': [], 'Err_Items': [] }
    
    if 'Records' not in event:
        resp = {'status': False, "error_message" : 'No Records found in Event' }
        return resp
    
    # Capture the upload event metadata and log file content
    # Note: observed behavior in the cloudwatch logs are that each file uploaded
    #       creates its own event
    for rec in event.get('Records'):
        # Capture the metadata of the upload event and file(s)
        d = {}
        d['time']           = rec['eventTime']
        d['object_owner']   = rec['userIdentity']['principalId']
        d['bucket_name']    = rec['s3']['bucket']['name']
        d['key']            = rec['s3']['object']['key']
        msg = "Recieved in FILE "+d['key']+" num files uploaded "+str(len(event.get('Records')))
        logger.info(msg)
        # If file can't be processed it goes into error list
        # Read in the database configuration in file (could be encrypted in s3)
        if process_file(d):
            resp['Proc_Items'].append(d)
        else:
            resp['Err_Items'].append(d)

    # Log the upload event metadata
    resp = log_up_evt(resp,len(event.get('Records')))

    return resp

if __name__ == '__main__':
    lambda_handler(None, None)
