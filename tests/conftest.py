import os

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["DYNAMODB_ENDPOINT_URL"] = ""


@pytest.fixture(scope="function")
def aws_mock():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield dynamodb


@pytest.fixture(scope="function")
def client(aws_mock):
    from src.main import app

    with TestClient(app) as c:
        yield c
