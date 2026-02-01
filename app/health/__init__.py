from flask import Blueprint

# Create health blueprint
health_bp = Blueprint('health', __name__)

# Import routes to register them with the blueprint
from app.health import routes
