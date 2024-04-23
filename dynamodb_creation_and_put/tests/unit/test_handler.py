import os
from unittest.mock import patch

import boto3
import pytest
from moto import mock_dynamodb2

from dynamodb_creation_and_put.src.app import lambda_handler


@mock_dynamodb2
def test_lambda_handler():
    # Mock DynamoDB table creation
    with mock_dynamodb2():
        # Initialize DynamoDB client
        dynamodb = boto3.client("dynamodb")

        # Create DynamoDB table
        dynamodb.create_table(
            TableName="TestTable",
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Test event
        event = {"pathParameters": {"id": "123"}, "body": "test payload"}

        # Set environment variable
        with patch.dict(os.environ, {"TABLE_NAME": "TestTable"}):
            # Invoke lambda handler
            response = lambda_handler(event, None)

        # Assert response
        assert response["statusCode"] == 200
        assert response["body"] == "item saved"

        # Get item from DynamoDB table
        response = dynamodb.get_item(TableName="TestTable", Key={"id": {"S": "123"}})

        # Assert item exists
        assert response["Item"]["id"]["S"] == "123"
        assert response["Item"]["payload"]["S"] == "test payload"

        # Test missing id parameter
        event = {"body": "test payload"}

        # Set environment variable
        with patch.dict(os.environ, {"TABLE_NAME": "TestTable"}):
            response = lambda_handler(event, None)

        assert response["statusCode"] == 400
        assert response["body"] == "id is required"

        # Test DynamoDB put_item failure
        with pytest.raises(Exception):
            # Mocking the put_item method to raise an exception
            with patch.object(
                dynamodb, "put_item", side_effect=Exception("Put item failed")
            ):
                # Set environment variable
                with patch.dict(os.environ, {"TABLE_NAME": "TestTable"}):
                    lambda_handler(event, None)
