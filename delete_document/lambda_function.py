import boto3
import json
from cors import cors
from botocore.exceptions import ClientError


def handler(event, context):
    body = event.get('body')
    if not body:
        return cors.with_cors_headers({
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing request body'})
        })

    body = json.loads(body)
    # Get temporary credentials from input
    aws_access_key_id = body.get('AccessKeyId')
    aws_secret_access_key = body.get('SecretKey')
    aws_session_token = body.get('SessionToken')

    if not (aws_access_key_id and aws_secret_access_key and aws_session_token):
        return cors.with_cors_headers({
            'statusCode': 400,
            'body': json.dumps({'error': 'Credentials required'})
        })

    # Create a Lambda client using temporary credentials
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token
    )

    payload = json.dumps(
        {
            'FileKey': body.get('FileKey')
        }
    )

    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName="ChatRAG-DeleteDocument",
            InvocationType='RequestResponse',  # Use 'Event' for async invocation
            Payload=payload
        )

        # Read the response
        response_payload = response['Payload'].read().decode('utf-8')
        return cors.with_cors_headers(json.loads(response_payload))
    except ClientError as e:
        # Handle invalid or expired credentials
        error_code = e.response['Error']['Code']

        if error_code == 'ExpiredToken':
            return cors.with_cors_headers({
                'statusCode': 401,
                'body': json.dumps({'error': 'Credentials have expired'})
            })
        elif error_code == 'InvalidClientTokenId':
            return cors.with_cors_headers({
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid credentials'})
            })
        else:
            # Handle any other errors
            return cors.with_cors_headers({
                'statusCode': 500,
                'body': json.dumps({'error': f"Unexpected error: {e}"})
            })
