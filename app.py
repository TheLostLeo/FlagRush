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
    from multiprocessing import Process
    
    def run_app(host, port, debug):
        app = create_app()
        app.run(host=host, port=port, debug=debug)
    
    # Configuration for both instances
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    main_port = int(os.environ.get('PORT', 5000))
    admin_port = int(os.environ.get('ADMIN_PORT', 5001))
    
    # Create two processes for different ports
    main_process = Process(target=run_app, args=('0.0.0.0', main_port, debug))
    admin_process = Process(target=run_app, args=('0.0.0.0', admin_port, debug))
    
    # Start both processes
    main_process.start()
    admin_process.start()
    
    # Wait for processes to complete
    main_process.join()
    admin_process.join()
