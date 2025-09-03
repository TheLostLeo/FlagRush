# CTF Backend

A Flask-based backend for Capture The Flag (CTF) competitions, designed to run on AWS EC2 with AWS RDS database.

## Features

- **JWT Authentication**: Secure user authentication with JSON Web Tokens
- **Environment Configuration**: Loads configuration from environment variables
- **AWS RDS Integration**: Connects to AWS RDS MySQL database
- **User Management**: User registration, login, and profile management
- **Team System**: Create and join teams for collaborative competition
- **Challenge Management**: Admin can create, update, and manage challenges
- **Flag Submission**: Teams can submit flags and track their progress
- **Leaderboard**: Real-time scoring and team rankings
- **RESTful API**: Clean REST endpoints for all operations

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-JWT-Extended
- **Database**: MySQL (AWS RDS)
- **Deployment**: AWS EC2, Nginx, Gunicorn
- **Authentication**: JWT tokens
- **Environment**: Python-dotenv for configuration

## Project Structure

```
FlagRush/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── challenge.py
│   │   └── submission.py
│   ├── routes/              # API blueprints
│   │   ├── auth.py
│   │   ├── challenges.py
│   │   ├── teams.py
│   │   └── submissions.py
│   └── utils/               # Utility functions
│       ├── decorators.py
│       └── helpers.py
├── config.py                # Configuration classes
├── app.py                   # Main application file
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── deploy.sh               # Deployment script for EC2
└── init_db.py              # Database initialization script
```

## Setup Instructions

### Quick Start on AWS EC2

1. **Launch EC2 Instance**
   - Use Ubuntu 20.04+ 
   - Configure Security Group to allow ports 22 (SSH) and 5000 (Flask app)

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip -y
   ```

3. **Clone and Setup**
   ```bash
   git clone <your-repo-url>
   cd FlagRush
   pip3 install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database details
   nano .env
   ```

5. **Initialize Database**
   ```bash
   python3 init_db.py
   ```

6. **Run the Application**
   ```bash
   python3 app.py
   ```

The application will be available at `http://your-ec2-ip:5000`

### Environment Configuration

Edit `.env` file with your AWS RDS details:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Database Configuration (AWS RDS)
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=3306
DB_USERNAME=your-db-username
DB_PASSWORD=your-db-password
DB_NAME=ctf_database

# Server Configuration
PORT=5000
DEBUG=False
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Teams
- `GET /api/teams/` - Get all teams
- `POST /api/teams/` - Create new team
- `GET /api/teams/<id>` - Get specific team
- `POST /api/teams/<id>/join` - Join team
- `POST /api/teams/leave` - Leave current team
- `GET /api/teams/leaderboard` - Get leaderboard

### Challenges
- `GET /api/challenges/` - Get all challenges
- `GET /api/challenges/<id>` - Get specific challenge
- `POST /api/challenges/` - Create challenge (admin only)
- `PUT /api/challenges/<id>` - Update challenge (admin only)
- `DELETE /api/challenges/<id>` - Delete challenge (admin only)

### Submissions
- `POST /api/submissions/` - Submit flag
- `GET /api/submissions/team` - Get team submissions
- `GET /api/submissions/stats` - Get submission statistics

## Default Admin User

After running `python3 init_db.py`, a default admin user is created:
- Username: `admin`
- Password: `admin123`

**IMPORTANT**: Change this password immediately after first login!

## EC2 Security Group Settings

Make sure your EC2 Security Group allows:
- Port 22 (SSH) - for server access
- Port 5000 (Custom TCP) - for the Flask application
- Port 3306 (MySQL) - if connecting to RDS from your local machine

## Running in Background (Optional)

To keep the app running after closing SSH:

```bash
nohup python3 app.py &
```

To stop the background process:
```bash
pkill -f "python3 app.py"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
