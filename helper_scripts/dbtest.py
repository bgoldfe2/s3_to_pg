import os
import json
import boto3
import botocore
import psycopg2
import logging
import sys

t_host = "lambda-test.cyb3keo6utm7.us-east-1.rds.amazonaws.com"
t_port = 5432
t_dbname = "postgres"
t_user = "postgres"
t_pw = "dashboard"

#db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)
myConnection = psycopg2.connect( host=t_host, user=t_user, password=t_pw, dbname=t_dbname )
cursor = myConnection.cursor()
print(myConnection.get_dsn_parameters(),"\n")

cursor.execute("SELECT NOW();")
print(cursor.fetchall())

print("Hooray, got this far!!!")
    # Trap errors for copying the array to our database
#try:
#    db_cursor.copy_from(f_contents, "tbl_users", columns=('t_name_user', 't_email'), sep=",")
#except psycopg2.Error as e:
#    t_message = "Database error: "
#    logger.info(t_message)
#    raise e

# It got this far: Success!

# Clean up by closing the database cursor and connection
cursor.close()
myConnection.close()
    