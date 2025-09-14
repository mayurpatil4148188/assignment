from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
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
        return {'error': 'Bad Request', 'message': str(error)}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5005)
