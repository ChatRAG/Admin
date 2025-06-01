import boto3
import json
import logging
from cors import cors

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the Lambda client
lambda_client = boto3.client('lambda')


@cors.cors_wrapper
def handler(event, context):
    logger.log(logging.INFO, f"event: {event}, context: {context}")
    # Retrieve query parameters from the event
    queryStringParameters = event.get('queryStringParameters')
    if not queryStringParameters:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Missing required parameter: FileKey'
            })
        }

    file_key = queryStringParameters.get('FileKey')
    if not file_key:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Missing required parameter: FileKey'
            })
        }

    payload = json.dumps(
        {
            'FileKey': file_key
        }
    )

    try:
        # Invoke the first Lambda function
        response = lambda_client.invoke(
            FunctionName="ChatRAG-GetDocument",
            InvocationType='RequestResponse',  # Use 'Event' for async invocation
            Payload=payload
        )

        # Read the response
        response_payload = response['Payload'].read().decode('utf-8')
        return json.loads(response_payload)

    except Exception as e:
        logger.error(f"Error invoking the first Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
