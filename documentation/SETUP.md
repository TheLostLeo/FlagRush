# FlagRush CTF Backend - Setup & Installation Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Verification & Testing](#verification--testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **AWS EC2**: Instance running Linux (Ubuntu 20.04+ recommended)
- **AWS RDS**: PostgreSQL database instance

### AWS Services Required
- **EC2 Instance**: For hosting the application
- **RDS PostgreSQL**: For database storage
- **Security Groups**: For network access control
- **IAM**: For access permissions (optional for advanced features)

## Local Development Setup

### Step 1: Clone the Repository
```bash
# Clone the project
git clone https://github.com/TheLostLeo/FlagRush.git

# Navigate to project directory
cd FlagRush

# Verify files are present
ls -la
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment named 'FlagRush'
python3 -m venv FlagRush

# Activate virtual environment
# On Linux/macOS:
source FlagRush/bin/activate

# On Windows:
# FlagRush\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Ensure virtual environment is activated
# Update pip to latest version
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

## Environment Configuration

### Step 4: Setup Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit environment file with your settings
nano .env  # or use your preferred editor
```

### Environment File Configuration
Edit `.env` file with the following required settings:

#### Required Changes for AWS Deployment
```env
# Database Configuration (AWS RDS)
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password
DB_NAME=your-database-name

# Security Configuration (REQUIRED - Change these!)
SECRET_KEY=your-unique-secret-key-here
JWT_SECRET_KEY=your-unique-jwt-secret-here

# Admin User Configuration (REQUIRED - Change these!)
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-admin-password
ADMIN_EMAIL=your-admin@example.com

# Application Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

#### Critical Security Notes
- **DB_HOST**: Replace with your AWS RDS endpoint
- **DB_USERNAME/DB_PASSWORD**: Use your RDS credentials
- **SECRET_KEY**: Generate a strong, unique key (32+ characters)
- **JWT_SECRET_KEY**: Generate a different strong, unique key
- **ADMIN_PASSWORD**: Use a strong password (12+ characters, mixed case, numbers, symbols)
- **ENVIRONMENT**: Set to `production` for AWS deployment
- **DEBUG**: Set to `false` for production

## Running the Application

### Step 5: Initialize Database
```bash
# Ensure virtual environment is activated
source FlagRush/bin/activate

# Initialize database with tables and admin user
python3 init_db.py
```

Expected output:
```
Initializing CTF Backend Database (PostgreSQL)...
==================================================
Database: your-rds-endpoint.region.rds.amazonaws.com:5432/your-database-name
Environment: production

1. Testing PostgreSQL connection...
SUCCESS: PostgreSQL connection successful!
2. Creating database tables...
SUCCESS: Database tables created successfully!
3. Creating admin user...
SUCCESS: Admin user 'your-admin-username' created successfully!

Database initialization completed successfully!
```

### Step 6: Start the FastAPI Server
```bash
# Ensure virtual environment is activated
source FlagRush/bin/activate

# Start the application
python3 app.py
```

Expected output:
```
Loaded configuration for production environment
Database: PostgreSQL - your-rds-endpoint.region.rds.amazonaws.com:5432/your-database-name
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 7: Run as Background Service (Optional)
For production deployment, run the application as a background service:

```bash
# Install screen or tmux for background running
sudo apt install screen

# Start application in background session
screen -S flagrush
source FlagRush/bin/activate
python3 app.py

# Detach from screen (Ctrl+A, then D)
# To reattach: screen -r flagrush
```

### Access Points
Once running, your application will be available at:
- **Main API**: http://your-ec2-public-ip:8000
- **Interactive Docs**: http://your-ec2-public-ip:8000/docs
- **Health Check**: http://your-ec2-public-ip:8000/health


