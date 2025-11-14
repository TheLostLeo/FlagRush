import json
import os
import datetime
import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

LOG_BUCKET = os.environ.get("LOG_BUCKET")
LOG_PREFIX = os.environ.get("LOG_PREFIX", "logs/").strip("/") + "/"
# When True, include plaintext flag if present in the SQS message (use with care)
INCLUDE_FLAG = os.environ.get("INCLUDE_FLAG", "false").lower() == "true"


def _put_json(bucket: str, key: str, data: Dict[str, Any]):
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=(json.dumps(data, separators=(",", ":")) + "\n").encode("utf-8"),
        ContentType="application/json",
    )


def _object_exists(bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def _ensure_first_solver(bucket: str, challenge_id: Any, record: Dict[str, Any]):
    """Create a first_solver.json if it does not exist for this challenge.
    Not atomic across multiple consumers; set Lambda reserved concurrency to 1 for this function.
    """
    key = f"{LOG_PREFIX}challenges/{challenge_id}/first_solver.json"
    if not _object_exists(bucket, key):
        doc = {
            "challenge_id": challenge_id,
            "user_id": record.get("user_id"),
            "username": record.get("username"),
            "submission_id": record.get("submission_id"),
            "submitted_at": record.get("submitted_at"),
        }
        _put_json(bucket, key, doc)
        logger.info("First solver recorded at s3://%s/%s", bucket, key)


def _store_submission(bucket: str, record: Dict[str, Any]):
    """Write a per-submission JSON line file under S3 for audit and retrieval."""
    challenge_id = record.get("challenge_id", "unknown")
    submission_id = record.get("submission_id", "unknown")

    submitted_at = record.get("submitted_at")
    if not submitted_at:
        submitted_at = datetime.datetime.utcnow().isoformat()

    # Partition by date for manageability
    try:
        day = submitted_at[:10]  # YYYY-MM-DD
    except Exception:
        day = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    key = (
        f"{LOG_PREFIX}challenges/{challenge_id}/submissions/{day}/submission-{submission_id}.json"
    )

    # Optionally drop plaintext flag for safety
    payload = dict(record)
    if not INCLUDE_FLAG and "flag" in payload:
        payload.pop("flag", None)

    _put_json(bucket, key, payload)
    logger.info("Wrote submission record to s3://%s/%s", bucket, key)


def lambda_handler(event, context):
    if not LOG_BUCKET:
        logger.error("LOG_BUCKET not set")
        return {"status": "error", "reason": "missing LOG_BUCKET"}

    for rec in event.get("Records", []):
        body = rec.get("body")
        try:
            msg = json.loads(body)
        except Exception:
            logger.warning("Invalid JSON body: %s", body)
            continue

        evt = msg.get("event")
        if evt in ("flag_submission", "flag_submission_blocked", "challenge_solved"):
            # Always write per-submission logs when we have IDs
            if "submission_id" in msg:
                _store_submission(LOG_BUCKET, msg)

            # Keep a first solver marker for solved events
            if evt == "challenge_solved" and "challenge_id" in msg:
                try:
                    _ensure_first_solver(LOG_BUCKET, msg.get("challenge_id"), msg)
                except Exception as e:
                    logger.warning("first solver check failed: %s", e)
        else:
            logger.info("Ignoring event type: %s", evt)

    return {"status": "ok"}
