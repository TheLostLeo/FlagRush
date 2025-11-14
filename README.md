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


## Documentation

Find detailed documentation in the [documentation](./documentation/) folder.

- Proposed Methodology: [documentation/Proposed_Methodology.md](documentation/Proposed_Methodology.md)
- Architecture Diagram: [documentation/Architecture_Diagram.md](documentation/Architecture_Diagram.md)
- Workflows: [documentation/Workflow.md](documentation/Workflow.md)
- Implementation, Results, and Conclusion: [documentation/Implementation_Results_Conclusion.md](documentation/Implementation_Results_Conclusion.md)

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

## Docker (local)

Run the backend (main + admin), Postgres, and the static frontend with Docker:

```bash
# Build images and start stack
docker compose up --build -d

# Tail logs
docker compose logs -f --tail=100
```

What you get:

- Frontend: <http://localhost:8080>
- Main API: <http://localhost:5000>
- Admin API: <http://localhost:5001>
- Postgres: localhost:5432 (user: flaguser, pass: flagpass, db: flagrush by default)

Notes:

- The frontend defaults to calling the API at <http://localhost:5000> via `frontend/config.js`.
- CORS is allowed for <http://localhost:8080> by default in `docker-compose.yml` (override via `CORS_ALLOW_ORIGINS`).
- To seed an admin user in Docker, you can exec into the main API container and run the init script:

```bash
docker compose exec api-main python init_db.py
```


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
