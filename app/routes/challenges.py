from flask import Blueprint
from flask_jwt_extended import jwt_required
from app import db
from app.models.challenge import Challenge
from app.utils.helpers import success_response, error_response
from app.utils.aws import parse_s3_url, s3_presigned_get_url
import os

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


@challenges_bp.route('/<int:challenge_id>/attachment', methods=['GET'])
@jwt_required()
def get_challenge_attachment(challenge_id):
    """Return a short-lived URL to download the challenge attachment if available."""
    try:
        challenge = Challenge.query.get(challenge_id)
        if not challenge or not challenge.is_active:
            return error_response("Challenge not found", 404)

        if not challenge.file_url:
            return error_response("No attachment for this challenge", 404)

        # If it's an s3:// URL, return a presigned GET; otherwise return as-is if http(s)
        s3_ref = parse_s3_url(challenge.file_url)
        if s3_ref:
            bucket, key = s3_ref
            url = s3_presigned_get_url(bucket, key, expires_in=600)
            if not url:
                return error_response("Unable to generate download URL", 500)
            return success_response({'download_url': url, 'expires_in': 600})

        if challenge.file_url.startswith('http://') or challenge.file_url.startswith('https://'):
            return success_response({'download_url': challenge.file_url})

        return error_response("Unsupported attachment URL", 400)
    except Exception as e:
        return error_response(f"Failed to get attachment: {str(e)}", 500)

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
