import os
import os.path
import sys
import json
import logging
import time

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)


logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)

from pip._internal import main
main(['install', 'boto3', '--target', '/tmp/'])
sys.path.insert(0,'/tmp/')
import boto3
from botocore.exceptions import ClientError

#sns_arn = os.environ['snsARN']  # Getting the SNS Topic ARN passed in by the environment variables.
sns_arn = 'arn:aws:sns:us-east-1:530470953206:MyMasterAcTopic'
snsclient = boto3.client('sns')

# aws_account = os.environ["AWS_ACCOUNT"]
# aws_dr_region = os.environ["AWS_DR_REGION"]

def lambda_handler(event, context):
     print("sys.path:"+str(sys.path))  
     print("boto3 version:"+boto3.__version__)
     print("Python version:"+sys.version)     
     print('## ENVIRONMENT VARIABLES')
     print(os.environ)
     print('## EVENT')
     print(event)
     print ('## LOGGER INFORMATION')
     logger.setLevel(logging.DEBUG)
     logger.debug("This is a sample DEBUG message.. !!")
     logger.error("This is a sample ERROR message.... !!")
     logger.info("This is a sample INFO message.. !!")
     logger.critical("This is a sample 5xx error message.. !!")

     print('## CONTEXT INFORMATION')
     print("Lambda function ARN:", context.invoked_function_arn)
     print("CloudWatch log stream name:", context.log_stream_name)
     print("CloudWatch log group name:",  context.log_group_name)
     print("Lambda Request ID:", context.aws_request_id)
     print("Lambda function memory limits in MB:", context.memory_limit_in_mb)
     snsclient.publish(TargetArn=sns_arn, Subject=f'Execution error for Lambda - {lambda_func_name[3]}', Message=message)

######


import base64
import boto3
import gzip
import json
import logging
import os

from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def logpayload(event):
    logger.setLevel(logging.DEBUG)
    logger.debug(event['awslogs']['data'])
    compressed_payload = base64.b64decode(event['awslogs']['data'])
    uncompressed_payload = gzip.decompress(compressed_payload)
    log_payload = json.loads(uncompressed_payload)
    return log_payload


def error_details(payload):
    error_msg = ""
    log_events = payload['logEvents']
    logger.debug(payload)
    loggroup = payload['logGroup']
    logstream = payload['logStream']
    lambda_func_name = loggroup.split('/')
    logger.debug(f'LogGroup: {loggroup}')
    logger.debug(f'Logstream: {logstream}')
    logger.debug(f'Function name: {lambda_func_name[3]}')
    logger.debug(log_events)
    for log_event in log_events:
        error_msg += log_event['message']
    logger.debug('Message: %s' % error_msg.split("\n"))
    return loggroup, logstream, error_msg, lambda_func_name


def publish_message(loggroup, logstream, error_msg, lambda_func_name):
    sns_arn = os.environ['snsARN']  # Getting the SNS Topic ARN passed in by the environment variables.
    snsclient = boto3.client('sns')
    try:
        message = ""
        message += "\nLambda error  summary" + "\n\n"
        message += "##########################################################\n"
        message += "# LogGroup Name:- " + str(loggroup) + "\n"
        message += "# LogStream:- " + str(logstream) + "\n"
        message += "# Log Message:- " + "\n"
        message += "# \t\t" + str(error_msg.split("\n")) + "\n"
        message += "##########################################################\n"

        # Sending the notification...
        snsclient.publish(TargetArn=sns_arn, Subject=f'Execution error for Lambda - {lambda_func_name[3]}', Message=message)
    except ClientError as e:
        logger.error("An error occured: %s" % e)


def lambda_handler(event, context):
    pload = logpayload(event)
    lgroup, lstream, errmessage, lambdaname = error_details(pload)
    publish_message(lgroup, lstream, errmessage, lambdaname)