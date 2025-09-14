from flask import Blueprint, request, jsonify
from services.student_service import StudentService
from services.application_service import ApplicationService
import logging

logger = logging.getLogger(__name__)
student_bp = Blueprint('students', __name__)

@student_bp.route('/', methods=['POST'])
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        student, errors = StudentService.create_student(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_student: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/', methods=['GET'])
def get_students():
    """Get all students with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        students, errors = StudentService.get_all_students(page, per_page)
        if errors:
            return jsonify({'errors': errors}), 500
        
        return jsonify({
            'students': [student.to_dict() for student in students.items],
            'pagination': {
                'page': students.page,
                'pages': students.pages,
                'per_page': students.per_page,
                'total': students.total,
                'has_next': students.has_next,
                'has_prev': students.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_students: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student by ID"""
    try:
        student, errors = StudentService.get_student(student_id)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Student not found'}), 404
            return jsonify({'errors': errors}), 500
        
        return jsonify({
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_student: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update a specific student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        student, errors = StudentService.update_student(student_id, data)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Student not found'}), 404
            return jsonify({'errors': errors}), 400
        
        return jsonify({
            'message': 'Student updated successfully',
            'student': student.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in update_student: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a specific student"""
    try:
        success, errors = StudentService.delete_student(student_id)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Student not found'}), 404
            return jsonify({'errors': errors}), 500
        
        return jsonify({
            'message': 'Student deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in delete_student: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/<int:student_id>/applications', methods=['GET'])
def get_student_applications(student_id):
    """Get all applications for a specific student"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10
        
        applications, errors = ApplicationService.get_applications_by_student(student_id, page, per_page)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Student not found'}), 404
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
        logger.error(f"Error in get_student_applications: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@student_bp.route('/<int:student_id>/highest-status', methods=['GET'])
def get_student_highest_status(student_id):
    """Get the highest status and intake for a specific student"""
    try:
        result, errors = StudentService.calculate_highest_status_and_intake(student_id)
        if errors:
            if 'not found' in errors[0].lower():
                return jsonify({'error': 'Student not found'}), 404
            return jsonify({'errors': errors}), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_student_highest_status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
