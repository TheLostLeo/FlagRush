from app import create_app, db
from app.models import User, Challenge, Submission
from werkzeug.security import generate_password_hash
import os

def create_admin_user():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            admin = User(
                username='admin',
                email='admin@ctf.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this password!
            
            db.session.add(admin)
            db.session.commit()
            
            print("Admin user created:")
            print("Username: admin")
            print("Password: admin123")
            print("IMPORTANT: Change the admin password immediately!")
        else:
            print("Admin user already exists")

def create_sample_challenges():
    """Create some sample challenges"""
    app = create_app()
    
    with app.app_context():
        # Sample challenges
        challenges = [
            {
                'title': 'Welcome to CTF',
                'description': 'This is a simple welcome challenge. The flag is hidden in plain sight!',
                'category': 'misc',
                'points': 50,
                'flag': 'flag{welcome_to_ctf}',
                'author': 'CTF Admin'
            },
            {
                'title': 'Basic Web Challenge',
                'description': 'Find the hidden flag in this simple web page.',
                'category': 'web',
                'points': 100,
                'flag': 'flag{inspect_element_is_useful}',
                'author': 'CTF Admin',
                'hint_1': 'Try looking at the page source'
            },
            {
                'title': 'Simple Crypto',
                'description': 'Decode this message: ROT13 cipher - "synt{pelfgb_vf_sha}',
                'category': 'crypto',
                'points': 150,
                'flag': 'flag{crypto_is_fun}',
                'author': 'CTF Admin',
                'hint_1': 'ROT13 is a simple letter substitution cipher'
            }
        ]
        
        for challenge_data in challenges:
            # Check if challenge already exists
            existing = Challenge.query.filter_by(title=challenge_data['title']).first()
            
            if not existing:
                challenge = Challenge(**challenge_data)
                db.session.add(challenge)
        
        db.session.commit()
        print("Sample challenges created!")

if __name__ == '__main__':
    create_admin_user()
    create_sample_challenges()
