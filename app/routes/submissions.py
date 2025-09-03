from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.submission import Submission
from app.models.challenge import Challenge
from app.models.user import User
from app.models.team import Team
from app.utils.helpers import success_response, error_response, validate_required_fields
from app.utils.decorators import team_member_required, admin_required

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/', methods=['POST'])
@team_member_required
def submit_flag():
    """Submit a flag for a challenge"""
    try:
        current_user_id = get_jwt_identity()
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
        
        # Check if team has already solved this challenge
        existing_correct_submission = Submission.query.filter_by(
            team_id=user.team_id,
            challenge_id=challenge.id,
            is_correct=True
        ).first()
        
        if existing_correct_submission:
            return error_response("Challenge already solved by your team", 400)
        
        # Check if flag is correct
        is_correct = challenge.check_flag(data['flag'])
        
        # Create submission record
        submission = Submission(
            user_id=user.id,
            team_id=user.team_id,
            challenge_id=challenge.id,
            submitted_flag=data['flag'],
            is_correct=is_correct
        )
        
        db.session.add(submission)
        
        # If correct, update team score
        if is_correct:
            team = Team.query.get(user.team_id)
            team.calculate_score()
        
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

@submissions_bp.route('/team', methods=['GET'])
@team_member_required
def get_team_submissions():
    """Get all submissions for current user's team"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        submissions = Submission.query.filter_by(team_id=user.team_id).all()
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
        return error_response(f"Failed to get team submissions: {str(e)}", 500)

@submissions_bp.route('/challenge/<int:challenge_id>', methods=['GET'])
@team_member_required
def get_challenge_submissions(challenge_id):
    """Get team's submissions for a specific challenge"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        submissions = Submission.query.filter_by(
            team_id=user.team_id,
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
            team = Team.query.get(submission.team_id)
            
            if user:
                submission_dict['username'] = user.username
            if challenge:
                submission_dict['challenge_title'] = challenge.title
                submission_dict['challenge_points'] = challenge.points
            if team:
                submission_dict['team_name'] = team.name
                
            submissions_data.append(submission_dict)
        
        return success_response(data=submissions_data)
        
    except Exception as e:
        return error_response(f"Failed to get all submissions: {str(e)}", 500)

@submissions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_submission_stats():
    """Get submission statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.team_id:
            # Team stats
            total_submissions = Submission.query.filter_by(team_id=user.team_id).count()
            correct_submissions = Submission.query.filter_by(
                team_id=user.team_id, 
                is_correct=True
            ).count()
            
            team = Team.query.get(user.team_id)
            current_score = team.score if team else 0
            
            stats = {
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions,
                'incorrect_submissions': total_submissions - correct_submissions,
                'current_score': current_score,
                'accuracy': (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
            }
        else:
            stats = {
                'total_submissions': 0,
                'correct_submissions': 0,
                'incorrect_submissions': 0,
                'current_score': 0,
                'accuracy': 0
            }
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(f"Failed to get submission stats: {str(e)}", 500)
