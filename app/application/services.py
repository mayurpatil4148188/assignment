# Import db from app module when needed
from app.application.models import Application
from app.student.models import Student
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class ApplicationService:
    """Service class for Application business logic"""
    
    @staticmethod
    def create_application(student_id, data):
        """Create a new application with validation and update student's highest status/intake"""
        from app.extensions import db
        
        try:
            # Check if student exists
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            application = Application(
                student_id=student_id,
                university_name=data.get('university_name', '').strip(),
                program_name=data.get('program_name', '').strip(),
                intake=data.get('intake', '').strip(),
                status=data.get('status', '').strip()
            )
            
            # Validate application data
            errors = application.validate()
            if errors:
                return None, errors
            
            db.session.add(application)
            db.session.commit()
            
            # Update student's highest status and intake
            from app.student.services import StudentService
            StudentService.calculate_highest_status_and_intake(student_id)
            
            logger.info(f"Created application: {application.id} for student: {student_id}")
            return application, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating application: {str(e)}")
            return None, ['Database integrity error']
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating application: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def get_application(application_id):
        """Get application by ID"""
        try:
            application = Application.query.get(application_id)
            if not application:
                return None, ['Application not found']
            return application, None
        except Exception as e:
            logger.error(f"Error getting application {application_id}: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def get_applications_by_student(student_id, page=1, per_page=10):
        """Get all applications for a student with pagination"""
        try:
            # Check if student exists
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            applications = Application.query.filter_by(student_id=student_id).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            return applications, None
        except Exception as e:
            logger.error(f"Error getting applications for student {student_id}: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def get_all_applications(page=1, per_page=10):
        """Get all applications with pagination"""
        try:
            applications = Application.query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            return applications, None
        except Exception as e:
            logger.error(f"Error getting applications: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def update_application(application_id, data):
        """Update application with validation and update student's highest status/intake"""
        from app.extensions import db
        
        try:
            application = Application.query.get(application_id)
            if not application:
                return None, ['Application not found']
            
            # Update fields
            if 'university_name' in data:
                application.university_name = data['university_name'].strip()
            if 'program_name' in data:
                application.program_name = data['program_name'].strip()
            if 'intake' in data:
                application.intake = data['intake'].strip()
            if 'status' in data:
                application.status = data['status'].strip()
            
            # Validate updated data
            errors = application.validate()
            if errors:
                return None, errors
            
            application.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Update student's highest status and intake
            StudentService.calculate_highest_status_and_intake(application.student_id)
            
            logger.info(f"Updated application: {application_id}")
            return application, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error updating application {application_id}: {str(e)}")
            return None, ['Database integrity error']
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating application {application_id}: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def delete_application(application_id):
        """Delete application and update student's highest status/intake"""
        from app.extensions import db
        
        try:
            application = Application.query.get(application_id)
            if not application:
                return False, ['Application not found']
            
            student_id = application.student_id
            
            # Delete application
            db.session.delete(application)
            db.session.commit()
            
            # Update student's highest status and intake
            from app.student.services import StudentService
            StudentService.calculate_highest_status_and_intake(student_id)
            
            logger.info(f"Deleted application: {application_id}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting application {application_id}: {str(e)}")
            return False, ['An unexpected error occurred']
    
    @staticmethod
    def get_status_hierarchy():
        """Get the status hierarchy for reference"""
        return Application.STATUS_HIERARCHY
    
    @staticmethod
    def get_valid_statuses():
        """Get list of valid statuses"""
        return Application.get_valid_statuses()
