from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
from database import db
import os

# Initialize extensions
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from routes.student_routes import student_bp
    from routes.application_routes import application_bp
    from routes.health_routes import health_bp
    
    app.register_blueprint(student_bp, url_prefix='/api/students')
    app.register_blueprint(application_bp, url_prefix='/api/applications')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        from utils.response_utils import ResponseUtils
        return ResponseUtils.error_response(
            message='Bad Request',
            errors=[str(error)],
            status_code=400,
            error_code='BAD_REQUEST'
        )
    
    @app.errorhandler(404)
    def not_found(error):
        from utils.response_utils import ResponseUtils
        return ResponseUtils.error_response(
            message='Resource not found',
            status_code=404,
            error_code='NOT_FOUND'
        )
    
    @app.errorhandler(500)
    def internal_error(error):
        from utils.response_utils import ResponseUtils
        db.session.rollback()
        return ResponseUtils.error_response(
            message='An unexpected error occurred',
            status_code=500,
            error_code='INTERNAL_ERROR'
        )
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
    
    # Get configuration values
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5005)
    debug = app.config.get('DEBUG', True)
    
    print(f"🚀 Starting {app.config.get('APP_NAME', 'Student Platform API')}")
    print(f"📍 Server running on http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    
    app.run(debug=debug, host=host, port=port)
