from flask import Blueprint, request
from services.application_service import ApplicationService
from utils.response_utils import ResponseUtils
import logging

logger = logging.getLogger(__name__)
application_bp = Blueprint('applications', __name__)

@application_bp.route('/', methods=['POST'])
def create_application():
    """Create a new application for a student"""
    try:
        data = request.get_json()
        if not data:
            return ResponseUtils.validation_error_response(
                errors=['No JSON data provided']
            )
        
        student_id = data.get('student_id')
        if not student_id:
            return ResponseUtils.validation_error_response(
                errors=['student_id is required']
            )
        
        application, errors = ApplicationService.create_application(student_id, data)
        if errors:
            return ResponseUtils.validation_error_response(errors)
        
        return ResponseUtils.created_response(
            data=application.to_dict(),
            message='Application created successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in create_application: {str(e)}")
        return ResponseUtils.internal_error_response()

@application_bp.route('/', methods=['GET'])
def get_applications():
    """Get all applications with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        applications, errors = ApplicationService.get_all_applications(page, per_page)
        if errors:
            return ResponseUtils.internal_error_response()
        
        return ResponseUtils.paginated_response(
            items=[app.to_dict() for app in applications.items],
            page=applications.page,
            per_page=applications.per_page,
            total=applications.total,
            message='Applications retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in get_applications: {str(e)}")
        return ResponseUtils.internal_error_response()

@application_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """Get a specific application by ID"""
    try:
        application, errors = ApplicationService.get_application(application_id)
        if errors:
            if 'not found' in errors[0].lower():
                return ResponseUtils.not_found_response('Application')
            return ResponseUtils.internal_error_response()
        
        return ResponseUtils.success_response(
            data=application.to_dict(),
            message='Application retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in get_application: {str(e)}")
        return ResponseUtils.internal_error_response()

@application_bp.route('/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    """Update a specific application"""
    try:
        data = request.get_json()
        if not data:
            return ResponseUtils.validation_error_response(
                errors=['No JSON data provided']
            )
        
        application, errors = ApplicationService.update_application(application_id, data)
        if errors:
            if 'not found' in errors[0].lower():
                return ResponseUtils.not_found_response('Application')
            return ResponseUtils.validation_error_response(errors)
        
        return ResponseUtils.updated_response(
            data=application.to_dict(),
            message='Application updated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in update_application: {str(e)}")
        return ResponseUtils.internal_error_response()

@application_bp.route('/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """Delete a specific application"""
    try:
        success, errors = ApplicationService.delete_application(application_id)
        if errors:
            if 'not found' in errors[0].lower():
                return ResponseUtils.not_found_response('Application')
            return ResponseUtils.internal_error_response()
        
        return ResponseUtils.deleted_response(
            message='Application deleted successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in delete_application: {str(e)}")
        return ResponseUtils.internal_error_response()

@application_bp.route('/status-hierarchy', methods=['GET'])
def get_status_hierarchy():
    """Get the status hierarchy for reference"""
    try:
        hierarchy = ApplicationService.get_status_hierarchy()
        valid_statuses = ApplicationService.get_valid_statuses()
        
        return ResponseUtils.success_response(
            data={
                'status_hierarchy': hierarchy,
                'valid_statuses': valid_statuses
            },
            message='Status hierarchy retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in get_status_hierarchy: {str(e)}")
        return ResponseUtils.internal_error_response()
