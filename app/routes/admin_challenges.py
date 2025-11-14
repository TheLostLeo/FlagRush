from flask import Blueprint, request
from app import db
from app.models.challenge import Challenge
from app.utils.helpers import success_response, error_response, validate_required_fields
from app.utils.decorators import admin_required
from app.middleware import route_middleware
from app.utils.aws import s3_presigned_put_url
import os
import uuid

admin_challenges_bp = Blueprint('admin_challenges', __name__)

@admin_challenges_bp.route('/challenges', methods=['POST'])
@admin_required
@route_middleware()
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


@admin_challenges_bp.route('/storage/presign-upload', methods=['POST'])
@admin_required
@route_middleware()
def presign_upload():
    """Generate a presigned S3 PUT URL for uploading challenge attachments.
    Body: { "filename": "file.zip", "content_type": "application/zip", "prefix": "optional/subfolder" }
    Requires env S3_BUCKET to be set.
    """
    try:
        bucket = os.environ.get('S3_BUCKET')
        if not bucket:
            return error_response("S3_BUCKET is not configured on the server", 500)

        data = request.get_json() or {}
        filename = data.get('filename')
        content_type = data.get('content_type', 'application/octet-stream')
        prefix = data.get('prefix', 'challenges')

        if not filename:
            return error_response("filename is required", 400)

        unique_id = str(uuid.uuid4())
        key = f"{prefix.rstrip('/')}/{unique_id}_{filename}"

        url = s3_presigned_put_url(bucket=bucket, key=key, content_type=content_type, expires_in=600)
        if not url:
            return error_response("Failed to generate presigned URL", 500)

        # Return s3:// URL reference for storing in Challenge.file_url
        return success_response({
            'upload_url': url,
            's3_url': f"s3://{bucket}/{key}",
            'expires_in': 600
        }, message="Presigned URL created")
    except Exception as e:
        return error_response(f"Failed to create presigned URL: {str(e)}", 500)

@admin_challenges_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@admin_required
@route_middleware()
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

@admin_challenges_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@admin_required
@route_middleware()
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

@admin_challenges_bp.route('/challenges', methods=['GET'])
@admin_required
@route_middleware()
def get_all_challenges():
    """Get all challenges including inactive ones (admin only)"""
    try:
        challenges = Challenge.query.all()
        challenges_data = [challenge.to_dict(include_flag=True) for challenge in challenges]
        
        return success_response(data=challenges_data)
        
    except Exception as e:
        return error_response(f"Failed to get challenges: {str(e)}", 500)

@admin_challenges_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@admin_required
@route_middleware()
def get_challenge(challenge_id):
    """Get a single challenge (admin only)"""
    try:
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return error_response("Challenge not found", 404)
        
        return success_response(data=challenge.to_dict(include_flag=True))
        
    except Exception as e:
        return error_response(f"Failed to get challenge: {str(e)}", 500)

@admin_challenges_bp.route('/challenges/<int:challenge_id>/status', methods=['PATCH'])
@admin_required
@route_middleware()
def toggle_challenge_status(challenge_id):
    """Toggle challenge active status (admin only)"""
    try:
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return error_response("Challenge not found", 404)
        
        data = request.get_json()
        
        if 'is_active' in data:
            challenge.is_active = data['is_active']
            db.session.commit()
            
            status = "activated" if challenge.is_active else "deactivated"
            return success_response(
                data=challenge.to_dict(include_flag=True),
                message=f"Challenge {status} successfully"
            )
        else:
            return error_response("is_active field is required", 400)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update challenge status: {str(e)}", 500)

@admin_challenges_bp.route('/challenges/<int:challenge_id>/stats', methods=['GET'])
@admin_required
@route_middleware()
def get_challenge_stats(challenge_id):
    """Get challenge statistics (admin only)"""
    try:
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return error_response("Challenge not found", 404)
        
        from app.models.submission import Submission
        
        total_attempts = Submission.query.filter_by(challenge_id=challenge.id).count()
        correct_attempts = Submission.query.filter_by(
            challenge_id=challenge.id, 
            is_correct=True
        ).count()
        unique_solvers = Submission.query.filter_by(
            challenge_id=challenge.id, 
            is_correct=True
        ).distinct(Submission.user_id).count()
        
        stats = {
            'challenge': challenge.to_dict(include_flag=True),
            'total_attempts': total_attempts,
            'correct_attempts': correct_attempts,
            'unique_solvers': unique_solvers,
            'success_rate': (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
        }
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(f"Failed to get challenge stats: {str(e)}", 500)
