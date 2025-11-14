# SQS Events for Auditing and Automation

FlagRush can publish events to Amazon SQS on flag submissions and solved challenges. This is useful for audit logs, security monitoring, dashboards, and downstream automation.

## Enable events

- Create a Standard SQS queue (Free Tier eligible)
- Set `SQS_QUEUE_URL` in your environment
- Ensure the EC2 instance role has permission to `sqs:SendMessage` for that queue

## Event schemas

On any submission (correct or incorrect), an audit message is sent (if configured):

```json
{
    "event": "flag_submission",
    "submission_id": 123,
    "user_id": 7,
    "username": "ctf_user",
    "challenge_id": 4,
    "challenge_title": "Intro Crypto",
    "is_correct": false,
    "points_awarded": 0,
    "flag_sha256": "f5d1278e8109edd94e1e4197e04873b9...",
    "submitted_at": "2025-11-13T12:34:56.000000",
    "client_ip": "198.51.100.10",
    "user_agent": "curl/7.81.0"
}
```

On correct submissions, a separate message can be sent for downstream reactions:

```json
{
  "event": "challenge_solved",
  "submission_id": 123,
  "user_id": 7,
  "username": "ctf_user",
  "challenge_id": 4,
  "challenge_title": "Intro Crypto",
  "points": 100,
  "submitted_at": "2025-11-13T12:34:56.000000"
}
```

Optionally, when a submission is blocked (e.g., user already solved it), an audit message may be sent:

```json
{
    "event": "flag_submission_blocked",
    "reason": "already_solved",
    "user_id": 7,
    "username": "ctf_user",
    "challenge_id": 4,
    "challenge_title": "Intro Crypto",
    "client_ip": "198.51.100.10",
    "user_agent": "Mozilla/5.0 ..."
}
```

## Sample AWS Lambda consumer (Python)

This example logs the events for auditing. Attach it to your queue as an event source (Lambda free tier applies).

```python
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Optional: look up external services/DB here
# e.g., connect to RDS using credentials from env/Secrets Manager

def handle_challenge_solved(evt: dict):
    user_id = evt.get('user_id')
    username = evt.get('username')
    challenge_id = evt.get('challenge_id')
    challenge_title = evt.get('challenge_title')
    points = evt.get('points')

    logger.info(
        "User %s solved challenge %s (%s) for %s points",
        username, challenge_id, challenge_title, points,
    )

    # Teaching ideas:
    # 1) Unlock a new challenge in your DB
    # 2) Send email via SES / notification via SNS
    # 3) Write a progress record in your DB (RDS/DynamoDB)
    # 4) Post to a webhook for a classroom dashboard


def lambda_handler(event, context):
    # SQS event format: Records list
    for record in event.get('Records', []):
        body = record.get('body')
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.warning("Skipping invalid JSON body: %s", body)
            continue

        evt_type = payload.get('event')
        if evt_type == 'challenge_solved':
            handle_challenge_solved(payload)
        elif evt_type in ('flag_submission', 'flag_submission_blocked'):
            logger.info("Audit: %s", json.dumps(payload))
        else:
            logger.info("Ignoring event type: %s", evt_type)

    return {"status": "ok"}
```

## S3 logging consumer (per-submission files and first-solver marker)

If you want an S3 log, deploy the sample Lambda in `docs/lambda_s3_logger.py` and set these environment variables:

- `LOG_BUCKET`: S3 bucket name to store logs
- `LOG_PREFIX`: Optional prefix (default `logs/`)
- `INCLUDE_FLAG`: `true` to keep the plaintext flag in S3 records (default `false`)

Recommended:

- Use a single Lambda reserved concurrency of 1 to avoid race conditions for "first solver" marker
- Use separate queues: one for audit (flag_submission, flag_submission_blocked) and one for solved (challenge_solved)

S3 layout written by the logger:

- `s3://<bucket>/<prefix>/challenges/<challenge_id>/submissions/YYYY-MM-DD/submission-<submission_id>.json`
- `s3://<bucket>/<prefix>/challenges/<challenge_id>/first_solver.json` (created if not exists)

## Least-privilege IAM

- App (EC2) role: allow `sqs:SendMessage` to the audit and/or solved queue ARN
- Lambda role: allow reading from the SQS queue and logging to CloudWatch
- If using S3 logging, also allow `s3:PutObject`, `s3:HeadObject` on the log bucket/prefix

## Local debugging

You can also run a small worker on EC2 to poll the queue and process events. Lambda is simpler and usually free within the free tier; prefer Lambda unless you need long-running tasks.
