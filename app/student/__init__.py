from flask import Blueprint

# Create student blueprint
student_bp = Blueprint('students', __name__)

# Import routes to register them with the blueprint
from app.student import routes
