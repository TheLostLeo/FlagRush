# CTF Backend

A Flask-based backend for Capture The Flag (CTF) competitions, designed to run on AWS EC2 with AWS RDS database.

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
- Port 5000 (Custom TCP) - for the Flask application
- Port 5432 (PostgreSQL) - if connecting to RDS from your local machine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
