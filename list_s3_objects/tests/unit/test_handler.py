from unittest.mock import MagicMock, patch

import pytest

from list_s3_objects.src.app import lambda_handler


@patch.dict("os.environ", {"S3_BUCKET": "your_bucket_name"})
@patch("boto3.client")
def test_lambda_handler_success(mock_boto3_client):
    mock_s3_client = MagicMock()
    mock_boto3_client.return_value = mock_s3_client
    mock_s3_client.list_objects.return_value = {
        "Contents": [{"Key": "object1"}, {"Key": "object2"}, {"Key": "object3"}]
    }

    event = {}
    context = MagicMock()

    response = lambda_handler(event, context)

    assert response["statusCode"] == 200
    assert response["message"] == "Successfully Pulled List of S3 Object from Bucket"
    mock_s3_client.list_objects.assert_called_once_with(Bucket="your_bucket_name")


@patch.dict("os.environ", {"S3_BUCKET": "your_bucket_name"})
@patch("boto3.client")
def test_lambda_handler_error(mock_boto3_client):
    mock_s3_client = MagicMock()
    mock_s3_client.list_objects.side_effect = Exception("Some error")
    mock_boto3_client.return_value = mock_s3_client

    event = {}
    context = MagicMock()

    with pytest.raises(Exception) as e:
        lambda_handler(event, context)

    assert "Error occurred during execution" in str(e.value)
