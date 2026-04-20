import boto3
from botocore.exceptions import ClientError

from src.core.config import settings


def get_dynamodb():
    kwargs = {
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
    }
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
    return boto3.resource("dynamodb", **kwargs)


def get_users_table():
    db = get_dynamodb()
    return db.Table(settings.users_table)


def create_tables_if_not_exist():
    db = get_dynamodb()
    try:
        db.create_table(
            TableName=settings.users_table,
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceInUseException":
            raise
