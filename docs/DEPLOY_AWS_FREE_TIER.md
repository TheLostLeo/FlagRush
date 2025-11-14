# Deploy on AWS Free Tier (EC2 + RDS)

This guide helps you run FlagRush on AWS Free Tier with minimal costs, using:

- 1x EC2 t2.micro/t3.micro (Free Tier eligible)
- 1x RDS PostgreSQL db.t3.micro (Free Tier eligible)
- No load balancer (to avoid extra cost)

Admin API is bound to localhost; access it via SSH port forwarding for security.

## 1) Create RDS PostgreSQL (Free Tier)

- Engine: PostgreSQL (Free Tier eligible)
- Instance: db.t3.micro
- Storage: 20 GB GP3 (adjust as needed within free tier)
- Public access: No (recommended)
- VPC security groups: Allow inbound 5432 from the EC2 security group
- Note the endpoint, DB name, username, and password.

## 2) Launch EC2 instance (Free Tier)

- AMI: Amazon Linux 2023 (or Ubuntu 22.04 LTS)
- Instance: t2.micro or t3.micro
- Security Group inbound rules:
  - SSH 22 from your IP
  - HTTP 80 (optional, if using a reverse proxy/TLS)
  - Custom TCP 5000 from 0.0.0.0/0 (or your IP)
  - Custom TCP 5001 from 127.0.0.1/32 (admin stays local) — no external ingress
- Attach an IAM role with SSM (optional) if you want to pull env vars from Parameter Store.

## 3) Prepare the instance

SSH into EC2 and install dependencies:

```bash
# Amazon Linux 2023
sudo dnf update -y
sudo dnf install -y git python3 python3-venv gcc postgresql-devel

# Clone project
cd /home/ec2-user
git clone https://github.com/TheLostLeo/FlagRush.git
cd FlagRush

# Create venv and install requirements
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
```

## 4) Configure environment

Create an environment file `/etc/sysconfig/flagrush.env`:

```bash
sudo bash -c 'cat > /etc/sysconfig/flagrush.env' <<'EOF'
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me
JWT_ACCESS_TOKEN_EXPIRES=3600

# Prefer a single DATABASE_URL
DATABASE_URL=postgresql+pg8000://<db_user>:<db_pass>@<rds-endpoint>:5432/<db_name>

# Ports
PORT=5000
ADMIN_PORT=5001
DEBUG=False

# Admin bootstrap (used by init_db.py)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this
ADMIN_EMAIL=admin@example.com

# Optional AWS integrations (free-tier friendly)
AWS_REGION=us-east-1
# S3 bucket for attachments (create in S3 first)
S3_BUCKET=
# SQS queue URL for solve events (create in SQS first)
SQS_QUEUE_URL=
# Enable AWS X-Ray tracing (requires X-Ray daemon/agent)
AWS_XRAY_ENABLED=False
EOF
```

Reload the shell environment for immediate use:

```bash
set -a
source /etc/sysconfig/flagrush.env
set +a
```

## 5) Initialize admin user (one-time)

```bash
source .venv/bin/activate
python init_db.py
```

## 6) Run with Gunicorn via systemd

Update the systemd templates to use your paths:

- Edit `ops/systemd/flagrush-main.service` and `ops/systemd/flagrush-admin.service`
  - Replace `/path/to/project` with your repo path, e.g., `/home/ec2-user/FlagRush`
  - Replace `/path/to/venv` with your venv path, e.g., `/home/ec2-user/FlagRush/.venv`

Then install and start services:

```bash
sudo cp ops/systemd/flagrush-main.service /etc/systemd/system/
sudo cp ops/systemd/flagrush-admin.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable flagrush-main
sudo systemctl enable flagrush-admin
sudo systemctl start flagrush-main
sudo systemctl start flagrush-admin

# Check status
systemctl status flagrush-main --no-pager
systemctl status flagrush-admin --no-pager
```

Main API will listen on `0.0.0.0:5000`.
Admin API binds to `127.0.0.1:5001` for security. Use SSH port forwarding when needed:

```bash
ssh -i /path/to/key.pem -L 5001:127.0.0.1:5001 ec2-user@<ec2-public-ip>
# Now visit http://localhost:5001 locally for the admin API
```

## 7) Health checks

- `GET http://<ec2-public-ip>:5000/health` returns JSON with DB connectivity status
- Admin: `GET http://localhost:5001/health` (via SSH tunnel)

## 8) Optional: Nginx + TLS (Let’s Encrypt)

To serve HTTPS without an ALB, install Nginx and Certbot on EC2, proxy to 5000, and restrict 5000 to localhost.
This avoids ALB costs and keeps you within free tier (subject to modest egress).

## 9) Optional AWS enhancements (Free Tier)

- S3 attachments for challenges
  - Create an S3 bucket (e.g., `flagrush-attachments-<suffix>`)
  - Set `S3_BUCKET` and `AWS_REGION` in env
  - Use the admin endpoint to get a presigned upload URL:
    - POST `/api/admin/storage/presign-upload` with `{ "filename": "file.zip", "content_type": "application/zip" }`
    - Store returned `s3://bucket/key` into `Challenge.file_url`
  - Users can fetch a temporary download link:
    - GET `/api/challenges/<id>/attachment`

- SQS events for correct submissions
  - Create an SQS standard queue (free tier applies)
  - Set `SQS_QUEUE_URL` in env
  - On correct flags, the app publishes an event with user, challenge, points
  - You can subscribe a Lambda later to process these events (leaderboards, notifications)

- AWS X-Ray Tracing
  - Enable `AWS_XRAY_ENABLED=True` and install/configure the X-Ray daemon/agent
  - Useful for request tracing; optional and safe to leave off

Permissions tip: attach an IAM role to EC2 with policies:

- `AmazonS3FullAccess` (or a least-privilege policy for your bucket)
- `AmazonSQSFullAccess` (or least-privilege for your queue)
- `AWSXRayDaemonWriteAccess` if using X-Ray

## Notes

- Avoid Elastic Load Balancers in free tier due to potential charges.
- Prefer SSM Parameter Store over Secrets Manager to keep costs at $0 for standard parameters.
- RDS free tier includes limited storage and hours; monitor usage and stop dev instances when idle.
