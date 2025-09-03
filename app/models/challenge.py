from app import db
from datetime import datetime

class Challenge(db.Model):
    """Challenge model for CTF challenges"""
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # web, crypto, pwn, reverse, etc.
    points = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # File attachments (optional)
    file_url = db.Column(db.String(500))
    
    # Hints
    hint_1 = db.Column(db.Text)
    hint_2 = db.Column(db.Text)
    hint_3 = db.Column(db.Text)
    
    # Relationships
    submissions = db.relationship('Submission', backref='challenge')
    
    def check_flag(self, submitted_flag):
        """Check if submitted flag is correct"""
        return self.flag.strip() == submitted_flag.strip()
    
    def get_solve_count(self):
        """Get number of teams that solved this challenge"""
        from app.models.submission import Submission
        return Submission.query.filter_by(
            challenge_id=self.id, 
            is_correct=True
        ).distinct(Submission.team_id).count()
    
    def to_dict(self, include_flag=False):
        """Convert challenge to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'points': self.points,
            'author': self.author,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'file_url': self.file_url,
            'hint_1': self.hint_1,
            'hint_2': self.hint_2,
            'hint_3': self.hint_3,
            'solve_count': self.get_solve_count()
        }
        
        if include_flag:
            data['flag'] = self.flag
            
        return data
    
    def __repr__(self):
        return f'<Challenge {self.title}>'
