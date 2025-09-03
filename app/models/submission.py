from app import db
from datetime import datetime

class Submission(db.Model):
    """Submission model for flag submissions"""
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    submitted_flag = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships are defined in other models via backref
    
    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'challenge_id': self.challenge_id,
            'submitted_flag': self.submitted_flag,
            'is_correct': self.is_correct,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
    
    def __repr__(self):
        return f'<Submission {self.id} - {"Correct" if self.is_correct else "Incorrect"}>'
