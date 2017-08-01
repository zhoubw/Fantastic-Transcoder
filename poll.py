import boto3, json, time

def lambda_handler(event, context):

    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='FT_convert_queue')
   # statusqueue = sqs.get_queue_by_name(QueueName='FT_status_queue')
    epochnow = int(time.time())
    # Accept message from SQS
    messages = queue.receive_messages(
        AttributeNames=[
            'All'
        ],
        MessageAttributeNames=[
            'string',
        ],
        MaxNumberOfMessages=10,
        VisibilityTimeout=600,
        WaitTimeSeconds=5,
        )
    for m in messages:
        if m is not None:
            # Load SQS Message as dictionary
            body = json.loads(m.body)

            ConversionID = body['uploadID']
            RequestedFormats = body['sizeFormat']
            VideoURL = body['s3_url']
            QueueMessageID = m.message_id

            # Write to DynamoDB
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('FT_VideoConversions')

            # Check if this job has been done before.
            # If we have not been here before, create a new row in DynamoDB. This triggers Lambda 2: Segment
            entry = table.get_item(Key={'ConversionID' : ConversionID})
            if entry is None:
                table.put_item(
                   Item={
                        'ConversionID': ConversionID,
                        'Created': epochnow,
                        'Updated': epochnow,
                        'QueueMessageID': QueueMessageID,
                        'RequestedFormats': RequestedFormats,
                        'Retries': 0,
                        'VideoURL': VideoURL
                    }
                )
                print("PutItem succeeded:")
                print(json.dumps(response, indent=4, cls=DecimalEncoder))
                '''
                sqs.put_message(
                    QueueUrl=statusqueue
                    status='Waiting for Encoder'
                )'''
                # If we have been here before, increment retries. This still triggers convert
            elif entry['Retries'] < 4:
                table.update_item(
                Key={
                    'ConversionID': conversionID
                },
                UpdateExpression="set retries = retries + :val",
                ExpressionAttributeValues={
                    ':val': decimal.Decimal(1)
                }
                )
                # If we've failed 3 times or are in some crazy unrecognizable state, move to deadletter queue
            else:
                raise Exception("Redrive policy should have run.")
