# CTF Backend

A Flask-based backend for Capture The Flag (CTF) competitions, designed to run on AWS EC2 with AWS RDS database. Features parallel endpoints for separated admin and user interfaces.

## Key Features

- User and admin interfaces on separate ports for enhanced security
- JWT-based authentication
- AWS RDS PostgreSQL database integration
- Comprehensive challenge management
- Real-time leaderboard
- Flag submission and verification
- User statistics and tracking

## Architecture

The platform runs as two separate applications:

### Main Application (Port 5000)
- User-facing API endpoints
- Challenge viewing and flag submissions
- User profile management
- Real-time leaderboard
- Supports regular CTF participants
- Available endpoints:
  - `/api/auth` - Authentication
  - `/api/challenges` - View available challenges
  - `/api/submissions` - Submit flags and view progress

### Admin Application (Port 5001)
- Administrative operations only
- Challenge management (CRUD operations)
- System monitoring and stats
- Complete admin control
- Available endpoints:
  - `/api/auth` - Admin authentication
  - `/api/admin/challenges` - Challenge management
  - More admin endpoints detailed in documentation

## Documentation

Find detailed documentation in the [documentation](./documentation/) folder.

## Default Admin User

After running `python3 init_db.py`, a default admin user is created:
- Username: `admin`
- Password: `admin123`

**IMPORTANT**: Change this password immediately after first login!

## EC2 Security Group Settings

Make sure your EC2 Security Group allows:
- Port 22 (SSH) - for server access
- Port 5000 (Custom TCP) - for the main Flask application
- Port 5001 (Custom TCP) - for the admin interface
- Port 5432 (PostgreSQL) - if connecting to RDS from your local machine

## Development Setup

1. Set up your environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your settings:
   PORT=5000              # Main application port
   ADMIN_PORT=5001        # Admin application port
   DEBUG=True             # Enable debug mode
   ```

3. Initialize the database:
   ```bash
   python init_db.py      # Creates tables and admin user
   ```

4. Start both applications:
   ```bash
   python app.py
   ```

5. Verify the setup:
   ```bash
   # Check main application
   curl http://localhost:5000/health
   
   # Check admin application
   curl http://localhost:5001/health
   ```

## API Usage Examples

### Main Application (Port 5000)
```bash
# User login
curl -X POST http://localhost:5000/api/auth/login \
  -d '{"username": "user", "password": "password"}'

# View challenges
curl http://localhost:5000/api/challenges \
  -H "Authorization: Bearer <token>"

# Submit flag
curl -X POST http://localhost:5000/api/submissions \
  -H "Authorization: Bearer <token>" \
  -d '{"challenge_id": 1, "flag": "flag{...}"}'
```

### Admin Application (Port 5001)
```bash
# Admin login
curl -X POST http://localhost:5001/api/auth/login \
  -d '{"username": "admin", "password": "admin123"}'

# Create new challenge
curl -X POST http://localhost:5001/api/admin/challenges \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "title": "Web Challenge",
    "description": "Find the hidden flag",
    "category": "web",
    "points": 100,
    "flag": "flag{secret}"
  }'

# Update challenge
curl -X PUT http://localhost:5001/api/admin/challenges/1 \
  -H "Authorization: Bearer <admin_token>" \
  -d '{"points": 200}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
