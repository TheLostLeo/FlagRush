from app import create_app, db
from app.models import User, Challenge, Submission
from werkzeug.security import generate_password_hash
import os

def create_admin_user():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        admin_email = os.environ.get('ADMIN_EMAIL', f'{admin_username}@ctf.com')
        
        if not admin_password:
            print("ERROR: ADMIN_PASSWORD environment variable is not set!")
            return
            
        if not admin:
            admin = User(
            username=admin_username,
            email=admin_email,
            is_admin=True
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"Admin user created: {admin_username} with pasword: {admin_password}")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    create_admin_user()
