# FlagRush CTF Backend - Documentation

**Table of Contents**

## Documentation Sections

### [Parallel Endpoints Architecture](./PARALLEL_ENDPOINTS.md)
Comprehensive guide to the dual-endpoint system
- Main and Admin API separation
- Security implementation
- Configuration and best practices
- Monitoring and logging

### [Setup & Installation Guide](./SETUP.md)
Complete setup instructions for AWS production deployment
- AWS EC2 instance configuration
- AWS RDS PostgreSQL setup
- Environment configuration
- Application deployment

### [API Documentation](./API_DOCUMENTATION.md)
Comprehensive API reference and usage examples
- Authentication endpoints
- Challenge management APIs
- Submission and scoring system
- Response formats and error handling
- Interactive documentation (Swagger UI)

### [Database Schema](./DATABASE_SCHEMA.md)
Complete database documentation and schema reference
- Table structures and relationships
- Database constraints and indexes
- Performance considerations
- Migration strategies

## Quick Start Links

| Task | Documentation |
|------|---------------|
| **Production Deployment** | [Setup Guide → AWS Production](./SETUP.md#production-setup) |
| **API Usage** | [API Documentation → Getting Started](./API_DOCUMENTATION.md#authentication) |
| **Database Schema** | [Database Schema → Table Structure](./DATABASE_SCHEMA.md#users-table) |

## Additional Resources

- **Postman Collection**: Available in project root (`FlagRush_API_Collection.json`)
- **Interactive API Docs**: `http://localhost:8000/docs` (when server is running)
- **Environment Examples**: See `.env.example` in project root
