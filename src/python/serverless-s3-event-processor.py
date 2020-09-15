# -*- coding: utf-8 -*-
"""
.. module: Serverless S3 Event Processor
    :platform: AWS    
.. moduleauthor:: Bruce Goldfeder
.. contactauthor:: bruce.goldfeder@asetpartners.com zarro_boogs
"""

import os
import json
import boto3
import botocore
import psycopg2
import logging
import sys

# Initialize Logger
logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# Database configuration filename in S3 bucket
pg_conf_name = "db_config.json"
db_config = {}

s3 = boto3.client('s3')

def process_file(d):
    if d['key'] == pg_conf_name:
        return process_conf_file(d)
    # Read in the db config json file
    try:
        obj = s3.get_object(Bucket=d['bucket_name'], Key=d['key'])
        data_in = obj['Body'].read().decode('utf-8','ignore')
        logger.info(data_in)
        
        # Save data off to database
        # TODO
        
    except Exception as e:
        logger.info(e)
        return False
    
    return True

def process_conf_file(d):
# Read in the db config json file
    try:
        obj = s3.get_object(Bucket=d['bucket_name'], Key=d['key'])
        json_conf = obj['Body'].read().decode('utf-8','ignore')
        logger.info(json_conf)
        db_dict = json.loads(json_conf)
        log_upload_content(db_dict)
    
    except Exception as e:
        logger.info(e)
        return False
    
    return True

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
    for rec in event.get('Records'):
        # Capture the metadata of the upload event and file(s)
        d = {}
        d['time']           = rec['eventTime']
        d['object_owner']   = rec['userIdentity']['principalId']
        d['bucket_name']    = rec['s3']['bucket']['name']
        d['key']            = rec['s3']['object']['key']
        
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
