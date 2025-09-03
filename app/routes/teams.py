from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.team import Team
from app.models.user import User
from app.utils.helpers import success_response, error_response, validate_required_fields
from app.utils.decorators import admin_required

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/', methods=['GET'])
@jwt_required()
def get_teams():
    """Get all teams with their scores"""
    try:
        teams = Team.query.all()
        teams_data = []
        
        for team in teams:
            team_dict = team.to_dict()
            teams_data.append(team_dict)
        
        # Sort by score (descending)
        teams_data.sort(key=lambda x: x['score'], reverse=True)
        
        return success_response(data=teams_data)
        
    except Exception as e:
        return error_response(f"Failed to get teams: {str(e)}", 500)

@teams_bp.route('/<int:team_id>', methods=['GET'])
@jwt_required()
def get_team(team_id):
    """Get a specific team"""
    try:
        team = Team.query.get(team_id)
        
        if not team:
            return error_response("Team not found", 404)
        
        return success_response(data=team.to_dict())
        
    except Exception as e:
        return error_response(f"Failed to get team: {str(e)}", 500)

@teams_bp.route('/', methods=['POST'])
@jwt_required()
def create_team():
    """Create a new team"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        if user.team_id:
            return error_response("You are already in a team", 400)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name']
        validation_error = validate_required_fields(data, required_fields)
        if validation_error:
            return validation_error
        
        # Check if team name already exists
        if Team.query.filter_by(name=data['name']).first():
            return error_response("Team name already exists", 409)
        
        # Create new team
        team = Team(
            name=data['name'],
            description=data.get('description', ''),
            captain_id=user.id
        )
        
        db.session.add(team)
        db.session.flush()  # Get the team ID
        
        # Add user to team
        user.team_id = team.id
        
        db.session.commit()
        
        return success_response(
            data=team.to_dict(),
            message="Team created successfully",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create team: {str(e)}", 500)

@teams_bp.route('/<int:team_id>/join', methods=['POST'])
@jwt_required()
def join_team(team_id):
    """Join an existing team"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return error_response("User not found", 404)
        
        if user.team_id:
            return error_response("You are already in a team", 400)
        
        team = Team.query.get(team_id)
        
        if not team:
            return error_response("Team not found", 404)
        
        # Add user to team
        user.team_id = team.id
        db.session.commit()
        
        return success_response(
            data=team.to_dict(),
            message="Successfully joined team"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to join team: {str(e)}", 500)

@teams_bp.route('/leave', methods=['POST'])
@jwt_required()
def leave_team():
    """Leave current team"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.team_id:
            return error_response("You are not in a team", 400)
        
        team = Team.query.get(user.team_id)
        
        # Check if user is team captain
        if team.captain_id == user.id:
            # Find another member to be captain or delete team if no members
            other_members = User.query.filter_by(team_id=team.id).filter(User.id != user.id).all()
            
            if other_members:
                # Make the first other member the new captain
                team.captain_id = other_members[0].id
            else:
                # Delete team if no other members
                db.session.delete(team)
        
        # Remove user from team
        user.team_id = None
        db.session.commit()
        
        return success_response(message="Successfully left team")
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to leave team: {str(e)}", 500)

@teams_bp.route('/<int:team_id>', methods=['PUT'])
@jwt_required()
def update_team(team_id):
    """Update team (captain only)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        team = Team.query.get(team_id)
        
        if not team:
            return error_response("Team not found", 404)
        
        if team.captain_id != user.id:
            return error_response("Only team captain can update team", 403)
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            # Check if new name is already taken
            existing_team = Team.query.filter_by(name=data['name']).first()
            if existing_team and existing_team.id != team.id:
                return error_response("Team name already exists", 409)
            team.name = data['name']
        
        if 'description' in data:
            team.description = data['description']
        
        db.session.commit()
        
        return success_response(
            data=team.to_dict(),
            message="Team updated successfully"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to update team: {str(e)}", 500)

@teams_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get team leaderboard"""
    try:
        teams = Team.query.all()
        
        # Calculate scores for all teams
        for team in teams:
            team.calculate_score()
        
        # Get updated teams
        teams = Team.query.order_by(Team.score.desc()).all()
        leaderboard = [team.to_dict() for team in teams]
        
        return success_response(data=leaderboard)
        
    except Exception as e:
        return error_response(f"Failed to get leaderboard: {str(e)}", 500)
