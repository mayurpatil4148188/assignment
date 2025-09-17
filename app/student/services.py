from app.student.models import Student
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class StudentService:
    """Service class for Student business logic"""
    
    @staticmethod
    def create_student(data):
        """Create a new student with validation"""
        from app.extensions import db
        
        try:
            student = Student(
                name=data.get('name', '').strip(),
                email=data.get('email', '').strip(),
                phone=data.get('phone', '').strip()
            )
            
            # Validate student data
            errors = student.validate()
            if errors:
                return None, errors
            
            # Check for duplicate email
            existing_student = Student.query.filter_by(email=student.email).first()
            if existing_student:
                return None, ['Email already exists']
            
            db.session.add(student)
            db.session.commit()
            
            logger.info(f"Created student: {student.id}")
            return student, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating student: {str(e)}")
            return None, ['Database integrity error']
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating student: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def get_student(student_id):
        """Get student by ID"""
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            return student, None
        except Exception as e:
            logger.error(f"Error getting student {student_id}: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def get_all_students(page=1, per_page=10):
        """Get all students with pagination"""
        try:
            students = Student.query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            return students, None
        except Exception as e:
            logger.error(f"Error getting students: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def update_student(student_id, data):
        """Update student with validation"""
        from app.extensions import db
        
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            # Update fields
            if 'name' in data:
                student.name = data['name'].strip()
            if 'email' in data:
                student.email = data['email'].strip()
            if 'phone' in data:
                student.phone = data['phone'].strip()
            
            # Validate updated data
            errors = student.validate()
            if errors:
                return None, errors
            
            # Check for duplicate email (excluding current student)
            if 'email' in data:
                existing_student = Student.query.filter(
                    Student.email == student.email,
                    Student.id != student_id
                ).first()
                if existing_student:
                    return None, ['Email already exists']
            
            student.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Updated student: {student_id}")
            return student, None
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error updating student {student_id}: {str(e)}")
            return None, ['Database integrity error']
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating student {student_id}: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def delete_student(student_id):
        """Delete student and all associated applications"""
        from app.extensions import db
        
        try:
            student = Student.query.get(student_id)
            if not student:
                return False, ['Student not found']
            
            # Delete student (applications will be deleted due to cascade)
            db.session.delete(student)
            db.session.commit()
            
            logger.info(f"Deleted student: {student_id}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting student {student_id}: {str(e)}")
            return False, ['An unexpected error occurred']
    
    @staticmethod
    def calculate_highest_status_and_intake(student_id):
        """Calculate and update student's highest status and intake"""
        from app.extensions import db
        
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            from app.application.models import Application
            applications = Application.query.filter_by(student_id=student_id).all()
            
            if not applications:
                # No applications, reset to None
                student.highest_status = None
                student.highest_intake = None
            else:
                # Find application with highest status
                highest_app = None
                highest_weight = -1
                
                for app in applications:
                    weight = app.get_status_weight()
                    if weight > highest_weight:
                        highest_weight = weight
                        highest_app = app
                    elif weight == highest_weight and highest_app:
                        # Same weight, compare intake dates (closest wins)
                        current_intake_date = app.parse_intake_date(app.intake)
                        highest_intake_date = highest_app.parse_intake_date(highest_app.intake)
                        
                        if current_intake_date and highest_intake_date:
                            if current_intake_date < highest_intake_date:
                                highest_app = app
                
                if highest_app:
                    student.highest_status = highest_app.status
                    student.highest_intake = highest_app.intake
                else:
                    student.highest_status = None
                    student.highest_intake = None
            
            student.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Updated highest status/intake for student: {student_id}")
            return {
                'highest_status': student.highest_status,
                'highest_intake': student.highest_intake
            }, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error calculating highest status/intake for student {student_id}: {str(e)}")
            return None, ['An unexpected error occurred']
