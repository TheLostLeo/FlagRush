# Import all route blueprints
from .auth import auth_bp
from .challenges import challenges_bp
from .submissions import submissions_bp

__all__ = ['auth_bp', 'challenges_bp', 'submissions_bp']
