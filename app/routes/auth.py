from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.user import User
from app.utils.helpers import success_response, error_response, validate_required_fields

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return validation_error
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return error_response("Username already exists", 409)
        
        if User.query.filter_by(email=data['email']).first():
            return error_response("Email already exists", 409)
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            data=user.to_dict(),
            message="User registered successfully",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Registration failed: {str(e)}", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return validation_error
        
        # Find user
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return error_response("Invalid credentials", 401)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create access token (convert user.id to string for JWT subject)
        access_token = create_access_token(identity=str(user.id))
        
        return success_response(
            data={
                'user': user.to_dict(),
                'access_token': access_token
            },
            message="Login successful"
        )
        
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        return success_response(data=user.to_dict())
        
    except Exception as e:
        return error_response(f"Failed to get profile: {str(e)}", 500)

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return error_response("Email already exists", 409)
            user.email = data['email']
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return success_response(
            data=user.to_dict(),
            message="Profile updated successfully"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update profile: {str(e)}", 500)
