import boto3
import json
import os
# Create SQS client
sqs = boto3.client('sqs',
                    region_name=os.environ['AWS_REGION'],
                    aws_access_key_id=os.environ['AWS_KEY'],
                    aws_secret_access_key=os.environ['AWS_SECRET'],
                    )
queue_url = os.environ['QUEUE_URL']


def handler(event, context):
    '''This AWS lambda function accepts Tune Firehose's data set
    and pushes it to an SQS queue
    '''

    message_payload = json.dumps(event, indent=2)
    transaction_id = event.get('transaction_id')
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=message_payload,
        DelaySeconds=123,
        MessageAttributes={
            'id': {
                'DataType': 'String',
                'StringValue': transaction_id
                },
        },
    )

    if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
        return {
            'statusCode': '200',
        }
    else:
        return {
            'statusCode': '400',
            'body': json.dumps(response),
            'headers': {
                'Content-Type': 'application/json',
            },
        }
