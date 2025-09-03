from app import db
from datetime import datetime

class Team(db.Model):
    """Team model for CTF teams"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    captain_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    captain = db.relationship('User', foreign_keys=[captain_id])
    
    def calculate_score(self):
        """Calculate team score based on successful submissions"""
        from app.models.submission import Submission
        from app.models.challenge import Challenge
        
        total_score = 0
        successful_submissions = Submission.query.filter_by(
            team_id=self.id, 
            is_correct=True
        ).all()
        
        for submission in successful_submissions:
            challenge = Challenge.query.get(submission.challenge_id)
            if challenge:
                total_score += challenge.points
        
        self.score = total_score
        db.session.commit()
        return total_score
    
    def to_dict(self):
        """Convert team to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'captain_id': self.captain_id,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'member_count': len(self.members)
        }
    
    def __repr__(self):
        return f'<Team {self.name}>'
