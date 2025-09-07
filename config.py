import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Database configuration for AWS RDS PostgreSQL
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_USERNAME = os.environ.get('DB_USERNAME')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    
    # Construct SQLAlchemy database URI
    # Prefer a full DATABASE_URL (e.g. set by Docker secrets or deployment). If not present,
    # build a synchronous psycopg (psycopg v3) URI from components. Fall back to SQLite for
    # local development.
    DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif all([DB_HOST, DB_USERNAME, DB_PASSWORD, DB_NAME]):
        # Use a pure-Python driver (pg8000) for compatibility with Python 3.13
        # pg8000 avoids C-extension compile failures and is supported by SQLAlchemy.
        SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to SQLite for development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///ctf.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

