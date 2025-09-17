from flask import Blueprint

# Create application blueprint
application_bp = Blueprint('applications', __name__)

# Import routes to register them with the blueprint
from app.application import routes
