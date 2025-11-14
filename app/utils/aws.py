import os
import json
import urllib.parse
from typing import Optional, Tuple

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

_BOTO_CONFIG = BotoConfig(retries={"max_attempts": 3, "mode": "standard"})


def _client(service: str):
    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if region:
        return boto3.client(service, region_name=region, config=_BOTO_CONFIG)
    return boto3.client(service, config=_BOTO_CONFIG)


def get_s3_client():
    return _client("s3")


def get_sqs_client():
    return _client("sqs")


def parse_s3_url(url: str) -> Optional[Tuple[str, str]]:
    """Parse s3://bucket/key to (bucket, key)."""
    if not url or not url.startswith("s3://"):
        return None
    without_scheme = url[len("s3://"):]
    parts = without_scheme.split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    return parts[0], parts[1]


def s3_presigned_put_url(bucket: str, key: str, content_type: str = "application/octet-stream", expires_in: int = 300) -> Optional[str]:
    """Generate a presigned PUT URL for direct upload to S3."""
    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires_in,
        )
    except (BotoCoreError, ClientError):
        return None


def s3_presigned_get_url(bucket: str, key: str, expires_in: int = 300) -> Optional[str]:
    """Generate a presigned GET URL for temporary download access."""
    try:
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
    except (BotoCoreError, ClientError):
        return None


def send_sqs_message(queue_url: str, payload: dict) -> bool:
    try:
        sqs = get_sqs_client()
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))
        return True
    except (BotoCoreError, ClientError):
        return False
