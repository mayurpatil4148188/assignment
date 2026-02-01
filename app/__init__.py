from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from app.extensions import db
import os

# Initialize extensions
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from app.student import student_bp
    from app.application import application_bp
    from app.health import health_bp
    
    app.register_blueprint(student_bp, url_prefix='/api/students')
    app.register_blueprint(application_bp, url_prefix='/api/applications')
    app.register_blueprint(health_bp, url_prefix='/api/health')
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        from app.utils import ResponseUtils
        return ResponseUtils.error_response(
            message='Bad Request',
            errors=[str(error)],
            status_code=400,
            error_code='BAD_REQUEST'
        )
    
    @app.errorhandler(404)
    def not_found(error):
        from app.utils import ResponseUtils
        return ResponseUtils.error_response(
            message='Resource not found',
            status_code=404,
            error_code='NOT_FOUND'
        )
    
    @app.errorhandler(500)
    def internal_error(error):
        from app.utils import ResponseUtils
        db.session.rollback()
        return ResponseUtils.error_response(
            message='An unexpected error occurred',
            status_code=500,
            error_code='INTERNAL_ERROR'
        )
    
    return app
