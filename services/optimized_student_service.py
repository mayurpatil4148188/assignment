#!/usr/bin/env python3
"""
Optimized Student Service with improved algorithms for highest status and intake calculation
"""

from database import db
from models.student import Student
from models.application import Application
from datetime import datetime
from sqlalchemy import text, func
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class OptimizedStudentService:
    """Optimized student service with improved algorithms"""
    
    @staticmethod
    @lru_cache(maxsize=1000)
    def _parse_intake_date_cached(intake):
        """Cached intake date parsing to avoid repeated parsing"""
        try:
            from dateutil import parser
            return parser.parse(intake.strip())
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def calculate_highest_status_and_intake_v1(student_id):
        """
        Version 1: Optimized Single Pass Algorithm
        - Early exit optimization for highest status
        - Reduced memory usage
        - Single database query
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            # Get applications with minimal data
            applications = db.session.query(
                Application.id,
                Application.status,
                Application.intake
            ).filter_by(student_id=student_id).all()
            
            if not applications:
                # No applications, reset to None
                student.highest_status = None
                student.highest_intake = None
            else:
                # Single pass with early exit optimization
                best_app = None
                best_weight = -1
                best_date = None
                
                for app_id, status, intake in applications:
                    weight = Application.STATUS_HIERARCHY.get(status, 0)
                    
                    # Early exit if we find the highest possible weight
                    if weight == 5:  # Visa Approved is highest
                        if best_app is None or weight > best_weight:
                            best_app = (app_id, status, intake)
                            best_weight = weight
                            best_date = OptimizedStudentService._parse_intake_date_cached(intake)
                        elif weight == best_weight:
                            # Same highest weight, compare dates
                            current_date = OptimizedStudentService._parse_intake_date_cached(intake)
                            if current_date and (best_date is None or current_date < best_date):
                                best_app = (app_id, status, intake)
                                best_date = current_date
                        break  # Early exit - can't get higher than 5
                    
                    # Regular processing for other weights
                    if weight > best_weight:
                        best_app = (app_id, status, intake)
                        best_weight = weight
                        best_date = OptimizedStudentService._parse_intake_date_cached(intake)
                    elif weight == best_weight and best_app:
                        # Same weight, compare intake dates
                        current_date = OptimizedStudentService._parse_intake_date_cached(intake)
                        if current_date and (best_date is None or current_date < best_date):
                            best_app = (app_id, status, intake)
                            best_date = current_date
                
                # Update student
                if best_app:
                    student.highest_status = best_app[1]
                    student.highest_intake = best_app[2]
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
    
    @staticmethod
    def calculate_highest_status_and_intake_v2(student_id):
        """
        Version 2: Database-Level Optimization
        - Uses SQL for sorting and filtering
        - Minimal memory usage
        - Best performance for large datasets
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            # Use SQL to find the highest status application
            query = text("""
                WITH ranked_applications AS (
                    SELECT 
                        id,
                        status,
                        intake,
                        CASE status
                            WHEN 'Visa Approved' THEN 5
                            WHEN 'Offer Accepted by Student' THEN 4
                            WHEN 'Offer Received' THEN 3
                            WHEN 'Application Submitted to University' THEN 2
                            WHEN 'Building Application' THEN 1
                            WHEN 'Dropped' THEN 0
                            ELSE 0
                        END as weight,
                        CASE 
                            WHEN intake ~ '^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{4}$'
                            THEN to_date(intake, 'Mon YYYY')
                            ELSE NULL
                        END as intake_date
                    FROM applications 
                    WHERE student_id = :student_id
                ),
                highest_weight AS (
                    SELECT MAX(weight) as max_weight
                    FROM ranked_applications
                )
                SELECT status, intake
                FROM ranked_applications r
                CROSS JOIN highest_weight h
                WHERE r.weight = h.max_weight
                ORDER BY intake_date ASC NULLS LAST
                LIMIT 1
            """)
            
            result = db.session.execute(query, {'student_id': student_id}).fetchone()
            
            if result:
                student.highest_status = result[0]
                student.highest_intake = result[1]
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
    
    @staticmethod
    def calculate_highest_status_and_intake_v3(student_id):
        """
        Version 3: Cached Optimization
        - Uses LRU cache for date parsing
        - Best for high-frequency updates
        - Optimized memory usage
        """
        try:
            student = Student.query.get(student_id)
            if not student:
                return None, ['Student not found']
            
            # Get applications with minimal data
            applications = db.session.query(
                Application.id,
                Application.status,
                Application.intake
            ).filter_by(student_id=student_id).all()
            
            if not applications:
                student.highest_status = None
                student.highest_intake = None
            else:
                # Use cached date parsing
                best_app = None
                best_weight = -1
                best_date = None
                
                for app_id, status, intake in applications:
                    weight = Application.STATUS_HIERARCHY.get(status, 0)
                    
                    if weight > best_weight:
                        best_app = (app_id, status, intake)
                        best_weight = weight
                        best_date = OptimizedStudentService._parse_intake_date_cached(intake)
                    elif weight == best_weight and best_app:
                        current_date = OptimizedStudentService._parse_intake_date_cached(intake)
                        if current_date and (best_date is None or current_date < best_date):
                            best_app = (app_id, status, intake)
                            best_date = current_date
                
                if best_app:
                    student.highest_status = best_app[1]
                    student.highest_intake = best_app[2]
                else:
                    student.highest_status = None
                    student.highest_intake = None
            
            student.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'highest_status': student.highest_status,
                'highest_intake': student.highest_intake
            }, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error calculating highest status/intake for student {student_id}: {str(e)}")
            return None, ['An unexpected error occurred']
    
    @staticmethod
    def calculate_highest_status_batch(student_ids):
        """
        Batch processing for multiple students
        - Processes multiple students in single transaction
        - Reduces database round trips
        - Optimized for bulk operations
        """
        try:
            if not student_ids:
                return {}, []
            
            # Get all applications for all students in one query
            applications = db.session.query(
                Application.student_id,
                Application.id,
                Application.status,
                Application.intake
            ).filter(Application.student_id.in_(student_ids)).all()
            
            # Group applications by student
            student_apps = {}
            for student_id, app_id, status, intake in applications:
                if student_id not in student_apps:
                    student_apps[student_id] = []
                student_apps[student_id].append((app_id, status, intake))
            
            # Process each student
            results = {}
            for student_id in student_ids:
                if student_id in student_apps:
                    apps = student_apps[student_id]
                    best_app = None
                    best_weight = -1
                    best_date = None
                    
                    for app_id, status, intake in apps:
                        weight = Application.STATUS_HIERARCHY.get(status, 0)
                        
                        if weight > best_weight:
                            best_app = (app_id, status, intake)
                            best_weight = weight
                            best_date = OptimizedStudentService._parse_intake_date_cached(intake)
                        elif weight == best_weight and best_app:
                            current_date = OptimizedStudentService._parse_intake_date_cached(intake)
                            if current_date and (best_date is None or current_date < best_date):
                                best_app = (app_id, status, intake)
                                best_date = current_date
                    
                    results[student_id] = {
                        'highest_status': best_app[1] if best_app else None,
                        'highest_intake': best_app[2] if best_app else None
                    }
                else:
                    results[student_id] = {
                        'highest_status': None,
                        'highest_intake': None
                    }
            
            # Update all students in batch
            students = Student.query.filter(Student.id.in_(student_ids)).all()
            for student in students:
                if student.id in results:
                    student.highest_status = results[student.id]['highest_status']
                    student.highest_intake = results[student.id]['highest_intake']
                    student.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Updated highest status/intake for {len(student_ids)} students in batch")
            return results, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in batch calculation: {str(e)}")
            return {}, ['An unexpected error occurred']
    
    @staticmethod
    def benchmark_algorithms(student_id, iterations=100):
        """
        Benchmark different algorithms for performance comparison
        """
        import time
        
        algorithms = {
            'V1_Optimized': OptimizedStudentService.calculate_highest_status_and_intake_v1,
            'V2_Database': OptimizedStudentService.calculate_highest_status_and_intake_v2,
            'V3_Cached': OptimizedStudentService.calculate_highest_status_and_intake_v3
        }
        
        results = {}
        
        for name, algorithm in algorithms.items():
            times = []
            for _ in range(iterations):
                start_time = time.time()
                algorithm(student_id)
                end_time = time.time()
                times.append(end_time - start_time)
            
            results[name] = {
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times)
            }
        
        return results

# Factory function to get the best algorithm based on use case
def get_optimal_algorithm(use_case='default'):
    """
    Factory function to return the optimal algorithm based on use case
    
    Args:
        use_case (str): 'default', 'large_dataset', 'high_frequency', 'batch'
    
    Returns:
        function: The optimal algorithm function
    """
    algorithms = {
        'default': OptimizedStudentService.calculate_highest_status_and_intake_v1,
        'large_dataset': OptimizedStudentService.calculate_highest_status_and_intake_v2,
        'high_frequency': OptimizedStudentService.calculate_highest_status_and_intake_v3,
        'batch': OptimizedStudentService.calculate_highest_status_batch
    }
    
    return algorithms.get(use_case, OptimizedStudentService.calculate_highest_status_and_intake_v1)
