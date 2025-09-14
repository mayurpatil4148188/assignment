from flask import Blueprint, request, jsonify
from services.application_service import ApplicationService
import logging

logger = logging.getLogger(__name__)
application_bp = Blueprint('applications', __name__)

@application_bp.route('/', methods=['POST'])
def create_application():
    """Create a new application for a student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        student_id = data.get('student_id')
        if not student_id:
            return jsonify({'error': 'student_id is required'}), 400
        
        application, errors = ApplicationService.create_application(student_id, data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        return jsonify({
            'message': 'Application created successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_application: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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
            return jsonify({'errors': errors}), 500
        
        return jsonify({
            'applications': [app.to_dict() for app in applications.items],
            'pagination': {
                'page': applications.page,
                'pages': applications.pages,
                'per_page': applications.per_page,
                'total': applications.total,
                'has_next': applications.has_next,
                'has_prev': applications.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_applications: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@application_bp.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """Get a specific application by ID"""
    try:
        application, errors = ApplicationService.get_application(application_id)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Application not found'}), 404
            return jsonify({'errors': errors}), 500
        
        return jsonify({
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_application: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@application_bp.route('/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    """Update a specific application"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        application, errors = ApplicationService.update_application(application_id, data)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Application not found'}), 404
            return jsonify({'errors': errors}), 400
        
        return jsonify({
            'message': 'Application updated successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in update_application: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@application_bp.route('/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """Delete a specific application"""
    try:
        success, errors = ApplicationService.delete_application(application_id)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Application not found'}), 404
            return jsonify({'errors': errors}), 500
        
        return jsonify({
            'message': 'Application deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in delete_application: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@application_bp.route('/status-hierarchy', methods=['GET'])
def get_status_hierarchy():
    """Get the status hierarchy for reference"""
    try:
        hierarchy = ApplicationService.get_status_hierarchy()
        valid_statuses = ApplicationService.get_valid_statuses()
        
        return jsonify({
            'status_hierarchy': hierarchy,
            'valid_statuses': valid_statuses
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_status_hierarchy: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
