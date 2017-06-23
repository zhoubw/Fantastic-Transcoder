import boto3
import json
import time

def lambda_handler(event, context):

    client = boto3.client('sqs')
    queue = sqs.get_queue_by_name(QueueName='FT_convert_queue')
    epochnow = int(time.time())
    # Accept message from SQS
    message = client.receive_message(
        QueueUrl=queue,
        AttributeNames=[
            'All'
        ],
        MessageAttributeNames=[
            'string',
        ],
        MaxNumberOfMessages=100,
        VisibilityTimeout=600,
        WaitTimeSeconds=5,
        )
    print message
    # TODO: get conversionID from SQS message

    # Write to DynamoDB
    db = boto3.resource('dynamodb')
    table = dynamodb.Table('FT_VideoConversions')

    # TODO: This should be each because we can get multiple messages.
    # Check if this job has been done before.
    exists = table.get_item(hash_key=conversionID)

    # If we have not been here before, create a new row in DynamoDB. This triggers Lambda 2: Segment
    if exists is None:
        table.put_item(
           Item={
                'ConversionID': conversionID,
                'created': epochnow,
                'retries': 0
            }
        )
        print("PutItem succeeded:")
        print(json.dumps(response, indent=4, cls=DecimalEncoder))
    # If we have been here before, increment retries. This still triggers convert
    else if retries < 4:
        table.update_item(
            Key={
                'ConversionID': conversionID
            },
            UpdateExpression="set retries = retries + :val",
            ExpressionAttributeValues={
                ':val': decimal.Decimal(1),
            },
            'updated': epochnow
        )
    else:
    # If we've failed 3 times or are in some crazy unrecognizable state, move to deadletter queue

        queue.delete_message(

        )
        statusqueue.put_message(
        status: "failed"
        
        )