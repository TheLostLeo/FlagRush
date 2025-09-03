import os
from flask import jsonify
from app import create_app

# Create Flask application
app = create_app()

@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'message': 'CTF Backend API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'challenges': '/api/challenges',
            'teams': '/api/teams',
            'submissions': '/api/submissions'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
