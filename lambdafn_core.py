
import os
import os.path
import sys
import json
import logging
import time
import datetime

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
# logger=logging.getLogger(__name__)

from pip._internal import main
main(['install', 'boto3', '--target', '/tmp/'])
sys.path.insert(0,'/tmp/')
import boto3
from botocore.exceptions import ClientError

#sns_arn = os.environ['snsARN']  # Getting the SNS Topic ARN passed in by the environment variables.
sns_arn = 'arn:aws:sns:us-east-1:530470953206:MyMasterAcTopic'
#sns_arn = 'arn:aws:sns:us-east-1:530470953206:MyMasterAcTopic:74bbd750-6f5a-4ade-8375-842e09820bdb'
snsclient = boto3.client('sns')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# aws_account = os.environ["AWS_ACCOUNT"]
# aws_dr_region = os.environ["AWS_DR_REGION"]

#events Inside lambda
message = {"foo": "bar"}

def lambda_handler(event, context):
    def defaultdateformat(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    print("sys.path:"+str(sys.path))  
    print("boto3 version:"+boto3.__version__)
    print("Python version:"+sys.version)     
    print('## ENVIRONMENT VARIABLES')
    print(os.environ)
    print('## EVENT')
    print(event)
    print(json.dumps(event, default = defaultdateformat))
    
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
    print('## Sending Mail to SNS')

    
    client = boto3.client('sns')
    response1 = client.publish(
        TargetArn=sns_arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json',
        MessageAttributes={
                            'foo': {
                                'DataType': 'String',
                                'StringValue': 'bar'
                            }
                        },
    )
    print(response1)
    
    response2 = snsclient.publish(TargetArn=sns_arn, Subject='Evend Details for Lambda function', Message=json.dumps({'default': json.dumps(event)}, MessageStructure='json'))
    print(response2)

   