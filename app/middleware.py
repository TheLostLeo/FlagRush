import os
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def route_middleware():
    """Middleware to route requests between main and admin endpoints"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # Check if user is admin
                from app.models.user import User
                user = User.query.get(current_user_id)
                
                # If user is admin and request is coming to admin port
                if user and user.is_admin and request.environ.get('SERVER_PORT') == os.environ.get('ADMIN_PORT'):
                    return fn(*args, **kwargs)
                    
                # If user is not admin and request is coming to main port
                elif request.environ.get('SERVER_PORT') == os.environ.get('PORT'):
                    return fn(*args, **kwargs)
                    
                return jsonify({
                    'success': False,
                    'message': 'Unauthorized for this endpoint'
                }), 403
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        return decorator
    return wrapper
