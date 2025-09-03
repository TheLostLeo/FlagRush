from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.challenge import Challenge
from app.models.submission import Submission
from app.models.user import User
from app.utils.helpers import success_response, error_response, validate_required_fields
from app.utils.decorators import admin_required

challenges_bp = Blueprint('challenges', __name__)

@challenges_bp.route('/', methods=['GET'])
@jwt_required()
def get_challenges():
    """Get all active challenges"""
    try:
        challenges = Challenge.query.filter_by(is_active=True).all()
        challenges_data = [challenge.to_dict() for challenge in challenges]
        
        return success_response(data=challenges_data)
        
    except Exception as e:
        return error_response(f"Failed to get challenges: {str(e)}", 500)

@challenges_bp.route('/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge(challenge_id):
    """Get a specific challenge"""
    try:
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge or not challenge.is_active:
            return error_response("Challenge not found", 404)
        
        return success_response(data=challenge.to_dict())
        
    except Exception as e:
        return error_response(f"Failed to get challenge: {str(e)}", 500)

@challenges_bp.route('/', methods=['POST'])
@admin_required
def create_challenge():
    """Create a new challenge (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'category', 'points', 'flag']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return validation_error
        
        # Create new challenge
        challenge = Challenge(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            points=data['points'],
            flag=data['flag'],
            author=data.get('author'),
            file_url=data.get('file_url'),
            hint_1=data.get('hint_1'),
            hint_2=data.get('hint_2'),
            hint_3=data.get('hint_3')
        )
        
        db.session.add(challenge)
        db.session.commit()
        
        return success_response(
            data=challenge.to_dict(include_flag=True),
            message="Challenge created successfully",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create challenge: {str(e)}", 500)

@challenges_bp.route('/<int:challenge_id>', methods=['PUT'])
@admin_required
def update_challenge(challenge_id):
    """Update a challenge (admin only)"""
    try:
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return error_response("Challenge not found", 404)
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'category', 'points', 'flag', 
            'author', 'file_url', 'hint_1', 'hint_2', 'hint_3', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(challenge, field, data[field])
        
        db.session.commit()
        
        return success_response(
            data=challenge.to_dict(include_flag=True),
            message="Challenge updated successfully"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update challenge: {str(e)}", 500)

@challenges_bp.route('/<int:challenge_id>', methods=['DELETE'])
@admin_required
def delete_challenge(challenge_id):
    """Delete a challenge (admin only)"""
    try:
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return error_response("Challenge not found", 404)
        
        db.session.delete(challenge)
        db.session.commit()
        
        return success_response(message="Challenge deleted successfully")
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to delete challenge: {str(e)}", 500)

@challenges_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all challenge categories"""
    try:
        categories = db.session.query(Challenge.category).distinct().all()
        categories_list = [cat[0] for cat in categories]
        
        return success_response(data=categories_list)
        
    except Exception as e:
        return error_response(f"Failed to get categories: {str(e)}", 500)
