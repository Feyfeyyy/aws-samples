import logging
import os
from http import HTTPStatus

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ["TABLE_NAME"]

# Initialize the AWS SDK for Python
dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    """List S3 Objects Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    # Extract path parameter from request
    table_id = (
        event["pathParameters"]["id"] if "id" in event["pathParameters"] else None
    )
    if not table_id:
        return {"statusCode": HTTPStatus.BAD_REQUEST.value, "body": "id is required"}

    # Extract body from request
    body = event["body"] if "body" in event else ""

    # Put the item in the DynamoDB table
    try:
        dynamodb.put_item(
            TableName=TABLE_NAME, Item={"id": {"S": table_id}, "payload": {"S": body}}
        )
        return {"statusCode": HTTPStatus.OK.value, "body": "item saved"}
    except Exception as e:
        logger.exception(e)
        return {
            "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR.value,
            "body": "internal error",
        }
