# CTF Backend - Setup & Deployment Guide

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (or AWS RDS PostgreSQL)
- Git

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd FlagRush
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   python init_db.py
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

---

## AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. **Create EC2 Instance:**
   - AMI: Amazon Linux 2 or Ubuntu 20.04+
   - Instance Type: t3.micro (for testing) or t3.small (for production)
   - Security Group: Allow ports 22 (SSH) and 5000 (Flask app)

2. **Security Group Rules:**
   ```
   Type: SSH, Port: 22, Source: Your IP
   Type: Custom TCP, Port: 5000, Source: 0.0.0.0/0
   ```

### Step 2: Connect and Setup Server

1. **Connect to EC2:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-public-ip
   ```

2. **Update system (Amazon Linux):**
   ```bash
   sudo yum update -y
   sudo yum install python3 python3-pip git postgresql -y
   ```

3. **Update system (Ubuntu):**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git postgresql-client -y
   ```

### Step 3: Deploy Application

1. **Clone repository:**
   ```bash
   git clone <your-repo-url>
   cd FlagRush
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your configuration
   ```

4. **Initialize database:**
   ```bash
   python3 init_db.py
   ```

5. **Run application:**
   ```bash
   python3 app.py
   ```

### Step 4: Production Setup with Gunicorn

1. **Install Gunicorn:**
   ```bash
   pip3 install gunicorn
   ```

2. **Run with Gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 3 app:app
   ```

3. **Run in background:**
   ```bash
   nohup gunicorn --bind 0.0.0.0:5000 --workers 3 app:app &
   ```

4. **Create systemd service (recommended):**
   ```bash
   sudo nano /etc/systemd/system/ctf-backend.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=CTF Backend
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/FlagRush
   Environment=PATH=/home/ec2-user/.local/bin
   ExecStart=/home/ec2-user/.local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ctf-backend
   sudo systemctl start ctf-backend
   sudo systemctl status ctf-backend
   ```

---

## AWS RDS PostgreSQL Setup

### Step 1: Create RDS Instance

1. **Go to AWS RDS Console**
2. **Create Database:**
   - Engine: PostgreSQL
   - Version: Latest stable
   - Instance Class: db.t3.micro (for testing)
   - Storage: 20 GB (minimum)

3. **Configuration:**
   - DB Instance Identifier: `ctf-database`
   - Master Username: `ctfadmin`
   - Master Password: (set a strong password)
   - Database Name: `ctf_database`

4. **Security:**
   - VPC Security Group: Allow PostgreSQL (port 5432) from your EC2 security group

### Step 2: Configure Environment Variables

Update your `.env` file with RDS details:

```env
# Database Configuration (AWS RDS PostgreSQL)
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432
DB_USERNAME=ctfadmin
DB_PASSWORD=your-rds-password
DB_NAME=ctf_database
```

### Step 3: Test Connection

```bash
# Test PostgreSQL connection from EC2
psql -h your-rds-endpoint.region.rds.amazonaws.com -U ctfadmin -d ctf_database
```

---

## Environment Variables

### Required Variables

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Database Configuration
DB_HOST=your-database-host
DB_PORT=5432
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password
DB_NAME=ctf_database

# Admin User Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-admin-password-in-production
ADMIN_EMAIL=admin@ctf.local
```

### Optional Variables

```env
# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES=3600  # Token expiry in seconds

# Server Configuration
PORT=5000
DEBUG=False
FLASK_ENV=production
```

---

## Security Considerations

### Production Security Checklist

- [ ] Change default admin password
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS (use AWS Application Load Balancer with SSL certificate)
- [ ] Restrict database access to application servers only
- [ ] Use AWS IAM roles instead of hardcoded credentials where possible
- [ ] Enable CloudWatch logging
- [ ] Implement rate limiting
- [ ] Regular security updates

### Database Security

- [ ] Use RDS security groups to restrict access
- [ ] Enable RDS encryption at rest
- [ ] Enable automated backups
- [ ] Use parameter groups for secure configuration
- [ ] Monitor database performance and logs

---

## Monitoring & Maintenance

### Application Monitoring

1. **Check application status:**
   ```bash
   sudo systemctl status ctf-backend
   ```

2. **View application logs:**
   ```bash
   sudo journalctl -u ctf-backend -f
   ```

3. **Restart application:**
   ```bash
   sudo systemctl restart ctf-backend
   ```

### Database Monitoring

1. **Monitor RDS metrics in AWS CloudWatch**
2. **Set up CloudWatch alarms for:**
   - High CPU usage
   - High connection count
   - Low free storage space

### Backup Strategy

1. **Database Backups:**
   - RDS automated backups (enabled by default)
   - Manual snapshots before major changes

2. **Application Backups:**
   - Code repository (Git)
   - Environment configuration files
   - Uploaded challenge files (if any)

---

## Troubleshooting

### Common Issues

1. **Connection refused on port 5000:**
   - Check if application is running: `sudo systemctl status ctf-backend`
   - Check security group allows port 5000
   - Verify application is binding to 0.0.0.0, not localhost

2. **Database connection errors:**
   - Verify RDS security group allows PostgreSQL from EC2
   - Check environment variables are correct
   - Test connection manually with psql

3. **JWT token errors:**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration time
   - Ensure client is sending proper Authorization header

4. **Permission denied errors:**
   - Check file permissions in application directory
   - Verify systemd service user permissions
   - Check Python package installation location

### Log Locations

- **Application logs:** `sudo journalctl -u ctf-backend`
- **System logs:** `/var/log/messages` (Amazon Linux) or `/var/log/syslog` (Ubuntu)
- **RDS logs:** Available in AWS RDS Console

### Performance Tuning

1. **Application:**
   - Adjust Gunicorn worker count based on CPU cores
   - Implement caching for frequently accessed data
   - Optimize database queries

2. **Database:**
   - Monitor query performance
   - Add database indexes for frequently queried columns
   - Scale RDS instance size if needed

3. **Infrastructure:**
   - Use AWS Application Load Balancer for high availability
   - Consider using Amazon ElastiCache for session storage
   - Implement CloudFront for static file delivery
