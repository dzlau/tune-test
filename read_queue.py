import boto3
import json
import sys
import os
import sqlite3
import time
import logging, logging.handlers
from dotenv import load_dotenv, find_dotenv

#load environment variables
load_dotenv(find_dotenv())

queue_url = os.environ['QUEUE_URL']
baseOutFileName= 'log.txt'

def init_logger(logLevel):
    """ Inits the logger and returns the logger object """
    global baseOutFileName
    lgr = logging.getLogger('sqsReader')
    lgr.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=baseOutFileName)
    handler.setLevel(logLevel)
    lgr.addHandler(handler)
    return lgr

def read(logger):
    """
    read object from SQS queue, and delete from queue
    """

    try:
        message = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        VisibilityTimeout=0,
        WaitTimeSeconds=0
        )
    except:
        logger.exception ('No available messages in queue')
        return None
    #delete message from sqs queue
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message.get('Messages')[0].get('ReceiptHandle'))
    return message.get('Messages')[0]

def write(data_dict, logger,conn):
    """
    write dictionary data to sqllite db
    """
    body_data = json.loads(data_dict.get('Body'))
    req_connection_speed = body_data.get('req_connection_speed')
    currency = body_data.get('currency')
    click_url = body_data.get('click_url')
    country_code = body_data.get('country_code')
    timezone = body_data.get('timezone')
    offer_expires = body_data.get('offer_expires')
    aff_sub = body_data.get('aff_sub')
    payout_type = body_data.get('payout_type')
    event_id = body_data.get('event_id')
    source = body_data.get('source')
    is_click_unique = body_data.get('is_click_unique')
    affiliate_manager_id = body_data.get('affiliate_manager_id')
    status_code = body_data.get('status_code')
    session_on_impression = body_data.get('session_on_impression')
    transaction_id = body_data.get('transaction_id')
    offer_id = body_data.get('offer_id')
    revenue_type = body_data.get('revenue_type')
    revenue_group_id = body_data.get('revenue_group_id')
    payout_group_id = body_data.get('payout_group_id')
    affiliate_id = body_data.get('affiliate_id')
    network_id = body_data.get('network_id')
    mobile_carrier = body_data.get('mobile_carrier')
    user_agent = body_data.get('user_agent')
    action = body_data.get('action')
    sql_query = """INSERT INTO firehose VALUES
                    (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")""" %(
                    req_connection_speed,
                    currency,
                    click_url,
                    country_code,
                    timezone,
                    offer_expires,
                    aff_sub,
                    payout_type,
                    event_id,
                    source,
                    is_click_unique,
                    affiliate_manager_id,
                    status_code,
                    session_on_impression,
                    transaction_id,
                    offer_id,
                    revenue_type,
                    revenue_group_id,
                    payout_group_id,
                    affiliate_id,
                    network_id,
                    mobile_carrier,
                    user_agent,
                    action)
    #initialize cursor
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        # Save (commit) the changes
        conn.commit()
    except Exception,e:
        print e
        logger.error('Database write failed \"%s\"', e)


if __name__ == '__main__':
    #Init the logger
    logger = init_logger(logging.INFO)
    #connect to db
    try:
        conn = sqlite3.connect('example.db')
    except Exception,e:
        logger.error('Unable to connect to db \"%s\"', e)
        sys.exit()
    #Get the SQS connection
    try:
        sqs = boto3.client('sqs',
                            region_name=os.environ['AWS_REGION'],
                            aws_access_key_id=os.environ['AWS_KEY'],
                            aws_secret_access_key=os.environ['AWS_SECRET'],
                            )
    except Exception, e:
        logger.error('Unable to connect to queue \"%s\"', e)
        sys.exit()
    #Iterate until messages are exhausted

    while True:
        data_dict = read(logger)
        #If there are no available messages, sleep a second and try again
        if data_dict is not None:
            write(data_dict,logger,conn)
        else:
            time.sleep(1)

    conn.close()
