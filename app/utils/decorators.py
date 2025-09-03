from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'message': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def team_member_required(f):
    """Decorator to require team membership"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.team_id:
            return jsonify({'message': 'Team membership required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
