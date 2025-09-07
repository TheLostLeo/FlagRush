from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_main_app():
    """Create the main application instance (Port 5000)"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register user-facing blueprints
    from app.routes.auth import auth_bp
    from app.routes.challenges import challenges_bp
    from app.routes.submissions import submissions_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(challenges_bp, url_prefix='/api/challenges')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def create_admin_app():
    """Create the admin application instance (Port 5001)"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register admin blueprints
    from app.routes.auth import auth_bp  # Admin still needs auth
    from app.routes.admin_challenges import admin_challenges_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_challenges_bp, url_prefix='/api/admin')
    
    # Share the same database
    with app.app_context():
        db.create_all()
    
    return app

# For backwards compatibility
create_app = create_main_app
