import os
from flask import jsonify
from app import create_main_app, create_admin_app

# Root routes will be added to each app when created
def add_root_routes(app, is_admin=False):
    """Add root routes to an application"""
    @app.route('/')
    def index():
        """API root endpoint"""
        if is_admin:
            return jsonify({
                'message': 'CTF Admin API',
                'version': '1.0.0',
                'endpoints': {
                    'auth': '/api/auth',
                    'admin': '/api/admin'
                }
            })
        else:
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
    
    def run_main_app():
        """Run the main user-facing application"""
        app = create_main_app()  # Create the main app with user routes
        add_root_routes(app, is_admin=False)  # Add root routes for main app
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        app.run(host='0.0.0.0', port=port, debug=debug)

    def run_admin_app():
        """Run the admin application"""
        app = create_admin_app()  # Create the admin app with admin routes
        add_root_routes(app, is_admin=True)  # Add root routes for admin app
        port = int(os.environ.get('ADMIN_PORT', 5001))
        debug = os.environ.get('DEBUG', 'True').lower() == 'true'
        app.run(host='0.0.0.0', port=port, debug=debug)
    
    # Create two processes for different applications
    main_process = Process(target=run_main_app)  # User-facing app
    admin_process = Process(target=run_admin_app)  # Admin-only app
    
    print(f"Starting main application on port {os.environ.get('PORT', 5000)}")
    print(f"Starting admin application on port {os.environ.get('ADMIN_PORT', 5001)}")
    
    # Start both processes
    main_process.start()
    admin_process.start()
    
    # Wait for processes to complete
    main_process.join()
    admin_process.join()
