import boto3
import json
from cors import cors
from botocore.exceptions import ClientError

# Create an SQS client
sqs = boto3.client('sqs')

# URL of your SQS queue
queue_url = 'https://sqs.ap-southeast-2.amazonaws.com/698446905433/chatrag-parse-queue'

@cors.cors_wrapper
def handler(event, context):
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing request body'})
        }

    body = json.loads(body)
    # Get temporary credentials from input
    aws_access_key_id = body.get('AccessKeyId')
    aws_secret_access_key = body.get('SecretKey')
    aws_session_token = body.get('SessionToken')

    if not (aws_access_key_id and aws_secret_access_key and aws_session_token):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Credentials required'})
        }

    # Create a Lambda client using temporary credentials
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )

    payload = json.dumps(
        {
            'FileName': body.get('FileName'),
            'FileData': body.get('FileData')
        }
    )

    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName="ChatRAG-CreateDocument",
            InvocationType='RequestResponse',  # Use 'Event' for async invocation
            Payload=payload
        )

        # Read the response
        response_payload = response['Payload'].read().decode('utf-8')

        # Send a message to MQ
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'key': 'value',
                'other_key': 'other_value'
            })
        )

        # Print the response from SQS (including the message ID)
        print(f"Message sent. response: {response}")

        return json.loads(response_payload)
    except ClientError as e:
        # Handle invalid or expired credentials
        error_code = e.response['Error']['Code']

        if error_code == 'ExpiredToken':
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Credentials have expired'})
            }
        elif error_code == 'InvalidClientTokenId':
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        else:
            # Handle any other errors
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"Unexpected error: {e}"})
            }
