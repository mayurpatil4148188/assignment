from app import create_app
from app.extensions import db
import os

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
