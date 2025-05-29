import boto3
import logging
import os
import json
from botocore.exceptions import ClientError
from cors import cors

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Cognito client
cognito_identity = boto3.client('cognito-identity')
IDENTITY_POOL_ID = os.environ['IDENTITY_POOL_ID']
PREDEFINED_PASSWORD = os.environ['PREDEFINED_PASSWORD']


@cors.cors_wrapper
def handler(event, context):
    logger.info(f'Received event: {event}')
    body = event.get('body')
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing request body'})
        }

    password = json.loads(body).get('password')
    if password != PREDEFINED_PASSWORD:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid password'})
        }

    # Generate Identity ID using Cognito
    try:
        response = cognito_identity.get_id(IdentityPoolId=IDENTITY_POOL_ID)
        identity_id = response['IdentityId']

        # Get temporary credentials for the generated identity ID
        credentials_response = cognito_identity.get_credentials_for_identity(
            IdentityId=identity_id
        )

        credentials = credentials_response['Credentials']

        return {
            'statusCode': 200,
            'body': json.dumps({
                'AccessKeyId': credentials['AccessKeyId'],
                'SecretKey': credentials['SecretKey'],
                'SessionToken': credentials['SessionToken'],
                'Expiration': credentials['Expiration'].isoformat()
            })
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
