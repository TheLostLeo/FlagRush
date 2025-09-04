from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.submission import Submission
from app.models.challenge import Challenge
from app.models.user import User
from app.utils.helpers import success_response, error_response, validate_required_fields
from app.utils.decorators import admin_required

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/', methods=['POST'])
@jwt_required()
def submit_flag():
    """Submit a flag for a challenge"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['challenge_id', 'flag']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return validation_error
        
        challenge = Challenge.query.get(data['challenge_id'])
        
        if not challenge or not challenge.is_active:
            return error_response("Challenge not found", 404)
        
        # Check if user has already solved this challenge
        existing_correct_submission = Submission.query.filter_by(
            user_id=user.id,
            challenge_id=challenge.id,
            is_correct=True
        ).first()
        
        if existing_correct_submission:
            return error_response("Challenge already solved", 400)
        
        # Check if flag is correct
        is_correct = challenge.check_flag(data['flag'])
        
        # Create submission record
        submission = Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            submitted_flag=data['flag'],
            is_correct=is_correct
        )
        
        db.session.add(submission)
        db.session.commit()
        
        message = "Correct flag! Well done!" if is_correct else "Incorrect flag. Try again!"
        
        return success_response(
            data={
                'submission': submission.to_dict(),
                'is_correct': is_correct,
                'points_earned': challenge.points if is_correct else 0
            },
            message=message
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to submit flag: {str(e)}", 500)

@submissions_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_submissions():
    """Get all submissions for current user"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        submissions = Submission.query.filter_by(user_id=user.id).all()
        submissions_data = []
        
        for submission in submissions:
            submission_dict = submission.to_dict()
            # Add challenge info
            challenge = Challenge.query.get(submission.challenge_id)
            if challenge:
                submission_dict['challenge_title'] = challenge.title
                submission_dict['challenge_points'] = challenge.points
            submissions_data.append(submission_dict)
        
        return success_response(data=submissions_data)
        
    except Exception as e:
        return error_response(f"Failed to get user submissions: {str(e)}", 500)

@submissions_bp.route('/challenge/<int:challenge_id>', methods=['GET'])
@jwt_required()
def get_challenge_submissions(challenge_id):
    """Get user's submissions for a specific challenge"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        submissions = Submission.query.filter_by(
            user_id=user.id,
            challenge_id=challenge_id
        ).all()
        
        submissions_data = [submission.to_dict() for submission in submissions]
        
        return success_response(data=submissions_data)
        
    except Exception as e:
        return error_response(f"Failed to get challenge submissions: {str(e)}", 500)

@submissions_bp.route('/all', methods=['GET'])
@admin_required
def get_all_submissions():
    """Get all submissions (admin only)"""
    try:
        submissions = Submission.query.all()
        submissions_data = []
        
        for submission in submissions:
            submission_dict = submission.to_dict()
            # Add user and challenge info
            user = User.query.get(submission.user_id)
            challenge = Challenge.query.get(submission.challenge_id)
            
            if user:
                submission_dict['username'] = user.username
            if challenge:
                submission_dict['challenge_title'] = challenge.title
                submission_dict['challenge_points'] = challenge.points
                
            submissions_data.append(submission_dict)
        
        return success_response(data=submissions_data)
        
    except Exception as e:
        return error_response(f"Failed to get all submissions: {str(e)}", 500)

@submissions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_submission_stats():
    """Get submission statistics"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # User stats
        total_submissions = Submission.query.filter_by(user_id=user.id).count()
        correct_submissions = Submission.query.filter_by(
            user_id=user.id, 
            is_correct=True
        ).count()
        
        # Calculate user score
        user_score = 0
        correct_submission_records = Submission.query.filter_by(
            user_id=user.id, 
            is_correct=True
        ).all()
        
        for submission in correct_submission_records:
            challenge = Challenge.query.get(submission.challenge_id)
            if challenge:
                user_score += challenge.points
        
        stats = {
            'total_submissions': total_submissions,
            'correct_submissions': correct_submissions,
            'incorrect_submissions': total_submissions - correct_submissions,
            'current_score': user_score,
            'accuracy': (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
        }
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(f"Failed to get submission stats: {str(e)}", 500)

@submissions_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get user leaderboard"""
    try:
        # Get all users with their scores
        users = User.query.filter_by(is_admin=False).all()
        leaderboard = []
        
        for user in users:
            # Calculate user score
            user_score = 0
            correct_submissions = Submission.query.filter_by(
                user_id=user.id, 
                is_correct=True
            ).all()
            
            for submission in correct_submissions:
                challenge = Challenge.query.get(submission.challenge_id)
                if challenge:
                    user_score += challenge.points
            
            leaderboard.append({
                'id': user.id,
                'username': user.username,
                'score': user_score,
                'solved_challenges': len(correct_submissions)
            })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        return success_response(data=leaderboard)
        
    except Exception as e:
        return error_response(f"Failed to get leaderboard: {str(e)}", 500)
