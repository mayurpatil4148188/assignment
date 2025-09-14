from flask import Blueprint
from database import db
from utils.response_utils import ResponseUtils
from sqlalchemy import text

health_bp = Blueprint('health', __name__)

@health_bp.route('/')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return ResponseUtils.success_response(
            data={
                'status': 'healthy',
                'database': 'connected'
            },
            message='Student Platform API is running'
        )
    except Exception as e:
        return ResponseUtils.error_response(
            message='Database connection failed',
            errors=[str(e)],
            status_code=500,
            error_code='DATABASE_ERROR'
        )
