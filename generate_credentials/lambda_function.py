import boto3
import json
import logging
import os
from cors import cors

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the S3 client
s3 = boto3.client('s3')


def handler(event, context):
    # Get the bucket name and file key from the event
    bucket_name = os.environ['BUCKET_NAME']

    try:
        logger.debug(f"Listing documents in S3 bucket: {bucket_name}")

        prefix = 'uploads/'  # Specify the folder path under which files are stored

        # List objects in the 'uploads/' folder of the S3 bucket
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            Delimiter='/'
        )

        # Extract and log the file names under the uploads/ folder
        documents = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # Extract the file key (path) and file name
                file_key = obj['Key']
                file_name = file_key[len(prefix):]  # Remove the prefix to get the file name
                documents.append(
                    {
                        "key": file_key,
                        "name": file_name
                    }
                )

        # Return the list of document names in the response
        return cors.with_cors_headers({
            'statusCode': 200,
            'body': json.dumps({
                'documents': documents
            })
        })
    except Exception as e:
        logger.error(f"Error listing documents in bucket {bucket_name}: {str(e)}")
        return cors.with_cors_headers({
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        })
