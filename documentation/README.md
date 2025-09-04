# CTF Backend Documentation

This directory contains comprehensive documentation for the CTF Backend project.

## 📚 Documentation Index

### 📖 [API Documentation](./API_DOCUMENTATION.md)
Complete API reference with all endpoints, request/response formats, and examples.

**Contents:**
- Authentication endpoints (register, login, profile)
- Challenge management (CRUD operations)
- Flag submission system
- Leaderboard and statistics
- Response formats and error codes

### 🚀 [Setup & Deployment Guide](./SETUP_GUIDE.md)
Step-by-step instructions for local development and AWS deployment.

**Contents:**
- Local development setup
- AWS EC2 deployment
- AWS RDS PostgreSQL configuration
- Production security considerations
- Monitoring and troubleshooting

### 🏗️ [Project Architecture](./ARCHITECTURE.md)
Technical overview of the system design and architecture.

**Contents:**
- System overview and technology stack
- Database schema and relationships
- API design patterns
- Security architecture
- Scalability considerations

## 🔗 Quick Links

### For Developers
- **Getting Started**: See [Setup Guide](./SETUP_GUIDE.md#local-development-setup)
- **API Reference**: See [API Documentation](./API_DOCUMENTATION.md)
- **Architecture**: See [Architecture Overview](./ARCHITECTURE.md#system-overview)

### For System Administrators  
- **AWS Deployment**: See [AWS EC2 Deployment](./SETUP_GUIDE.md#aws-ec2-deployment)
- **Database Setup**: See [AWS RDS Setup](./SETUP_GUIDE.md#aws-rds-postgresql-setup)
- **Security**: See [Security Considerations](./SETUP_GUIDE.md#security-considerations)

### For API Users
- **Authentication**: See [Authentication Endpoints](./API_DOCUMENTATION.md#authentication-endpoints)
- **Challenges**: See [Challenge Endpoints](./API_DOCUMENTATION.md#challenge-endpoints)
- **Submissions**: See [Submission Endpoints](./API_DOCUMENTATION.md#submission-endpoints)

## 📋 Environment Configuration

### Required Environment Variables
```env
# Flask Configuration
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database Configuration
DB_HOST=your-database-host
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password
DB_NAME=ctf_database

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
ADMIN_EMAIL=admin@ctf.local
```

### Default Admin Account
After running `python init_db.py`, access the admin account with:
- **Username**: Value from `ADMIN_USERNAME` environment variable
- **Password**: Value from `ADMIN_PASSWORD` environment variable
- **Email**: Value from `ADMIN_EMAIL` environment variable

## 🛠️ Development Tools

### Testing the API
Use tools like Postman, curl, or any HTTP client:

```bash
# Health check
curl http://localhost:5000/health

# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### Database Operations
```bash
# Initialize database
python init_db.py

# Create migration (if using Flask-Migrate)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📞 Support

### Common Issues
1. **Database connection errors**: Check RDS security groups and credentials
2. **JWT token issues**: Verify SECRET_KEY configuration
3. **Permission errors**: Ensure proper admin user setup

### Getting Help
- Check the troubleshooting section in [Setup Guide](./SETUP_GUIDE.md#troubleshooting)
- Review error logs: `sudo journalctl -u ctf-backend -f`
- Verify environment configuration

## 📈 Performance Tips

### For Development
- Use SQLite fallback for quick local testing
- Enable DEBUG mode for detailed error messages
- Use shorter JWT token expiry times

### For Production
- Use AWS RDS with connection pooling
- Set appropriate Gunicorn worker count
- Monitor application performance metrics
- Implement proper logging and monitoring

## 🔐 Security Best Practices

### Essential Security Measures
- [ ] Change default admin credentials
- [ ] Use strong secret keys
- [ ] Enable HTTPS in production
- [ ] Restrict database access
- [ ] Regular security updates
- [ ] Monitor application logs

### Advanced Security
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Use AWS WAF for web protection
- [ ] Enable CloudTrail for audit logs
- [ ] Implement backup strategies

---

**Last Updated**: September 4, 2025  
**Version**: 1.0.0  
**Maintainer**: CTF Backend Team
