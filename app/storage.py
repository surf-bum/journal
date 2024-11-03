from app.utils import setup_logger
import boto3
from botocore.exceptions import ClientError
from app.config import settings

s3 = boto3.resource("s3")
s3_client = boto3.client("s3")

bucket_name = settings.S3_BUCKET

logger = setup_logger(__name__)


def delete_file(key: str):
    logger.debug("delete_file %s" , key)
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
    except ClientError as e:
        logger.error(e)


def store_file(file, key: str) -> None:
    logger.debug("store_file %s %s", file, key)
    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=file)
    except ClientError as e:
        logger.error(e)


def retrieve_file(key: str):
    logger.debug("retrieve_file %s", key)
    try:
        reference = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_stream = reference["Body"]
        return file_stream
    except ClientError as e:
        logger.error(e)
