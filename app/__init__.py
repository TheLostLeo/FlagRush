from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
import os
from sqlalchemy import text
import logging
from pythonjsonlogger import jsonlogger

# Module-level guard to avoid configuring logging twice
_LOGGING_CONFIGURED = False

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_main_app():
    """Create the main application instance (Port 5000)"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure JSON logging (once per process)
    global _LOGGING_CONFIGURED
    if not _LOGGING_CONFIGURED:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.handlers = [handler]
        _LOGGING_CONFIGURED = True
    
    # Optional AWS X-Ray instrumentation
    if os.environ.get('AWS_XRAY_ENABLED', 'false').lower() == 'true':
        try:
            from aws_xray_sdk.core import xray_recorder, patch_all
            from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
            xray_recorder.configure(service='FlagRush-Main')
            patch_all()
            XRayMiddleware(app, xray_recorder)
        except Exception:
            # Do not fail app startup if X-Ray is misconfigured
            pass
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    # CORS: allow all by default; restrict via CORS_ALLOW_ORIGINS (comma-separated) if provided
    origins = os.environ.get('CORS_ALLOW_ORIGINS')
    if origins:
        origin_list = [o.strip() for o in origins.split(',') if o.strip()]
        CORS(app, resources={r"/*": {"origins": origin_list}}, supports_credentials=True)
    else:
        CORS(app)
    
    # Register user-facing blueprints
    from app.routes.auth import auth_bp
    from app.routes.challenges import challenges_bp
    from app.routes.submissions import submissions_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(challenges_bp, url_prefix='/api/challenges')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    
    # Root routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'CTF Backend API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'challenges': '/api/challenges',
                'submissions': '/api/submissions'
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check with simple DB connectivity probe"""
        db_status = 'unknown'
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        return jsonify({'status': 'healthy', 'database': db_status})
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

def create_admin_app():
    """Create the admin application instance (Port 5001)"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure JSON logging (once per process)
    global _LOGGING_CONFIGURED
    if not _LOGGING_CONFIGURED:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.handlers = [handler]
        _LOGGING_CONFIGURED = True
    
    # Optional AWS X-Ray instrumentation
    if os.environ.get('AWS_XRAY_ENABLED', 'false').lower() == 'true':
        try:
            from aws_xray_sdk.core import xray_recorder, patch_all
            from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
            xray_recorder.configure(service='FlagRush-Admin')
            patch_all()
            XRayMiddleware(app, xray_recorder)
        except Exception:
            pass
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    origins = os.environ.get('CORS_ALLOW_ORIGINS')
    if origins:
        origin_list = [o.strip() for o in origins.split(',') if o.strip()]
        CORS(app, resources={r"/*": {"origins": origin_list}}, supports_credentials=True)
    else:
        CORS(app)
    
    # Register admin blueprints
    from app.routes.auth import auth_bp  # Admin still needs auth
    from app.routes.admin_challenges import admin_challenges_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_challenges_bp, url_prefix='/api/admin')
    
    # Root routes (admin)
    @app.route('/')
    def index():
        return jsonify({
            'message': 'CTF Admin API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'admin': '/api/admin'
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check with simple DB connectivity probe"""
        db_status = 'unknown'
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        return jsonify({'status': 'healthy', 'database': db_status})
    
    # Share the same database
    with app.app_context():
        db.create_all()
    
    return app

# For backwards compatibility
create_app = create_main_app
