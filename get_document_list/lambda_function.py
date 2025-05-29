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
    try:
        # Invoke the first Lambda function
        response = lambda_client.invoke(
            FunctionName="ChatRAG-ListDocuments",
            InvocationType='RequestResponse',  # Use 'Event' for async invocation
            Payload=""
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
