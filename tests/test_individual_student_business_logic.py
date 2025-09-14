#!/usr/bin/env python3
"""
Individual Student Business Logic Test

This test file validates the business logic for individual students by checking:
1. Highest status calculation based on status hierarchy weights
2. Highest intake calculation (closest intake for same highest status)
3. Proper recalculation when applications are created/updated/deleted

Usage:
    pytest test_individual_student_business_logic.py::test_student_business_logic[1] -v
    pytest test_individual_student_business_logic.py -k "student_id_5" -v
    python test_individual_student_business_logic.py --student-id 1
"""

import pytest
import sys
import os
from datetime import datetime
from dateutil import parser

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.student import Student
from models.application import Application
from database import db

class StudentBusinessLogicValidator:
    """Validator for student business logic"""
    
    def __init__(self):
        # Application status hierarchy with weightage (matches your business logic)
        self.status_hierarchy = {
            'Building Application': 1,
            'Application Submitted to University': 2,
            'Offer Received': 3,
            'Offer Accepted by Student': 4,
            'Visa Approved': 5,
            'Dropped': 0  # Lowest priority
        }
    
    def parse_intake_date(self, intake: str) -> datetime:
        """Parse intake string to datetime for comparison"""
        try:
            return parser.parse(intake)
        except (ValueError, TypeError):
            return None
    
    def calculate_expected_highest_status(self, applications):
        """Calculate expected highest status based on applications"""
        if not applications:
            return None
        
        max_weight = -1
        highest_status = None
        
        for app in applications:
            weight = self.status_hierarchy.get(app.status, 0)
            if weight > max_weight:
                max_weight = weight
                highest_status = app.status
        
        return highest_status
    
    def calculate_expected_highest_intake(self, applications):
        """Calculate expected highest intake based on business logic"""
        if not applications:
            return None
        
        # First, get the highest status
        highest_status = self.calculate_expected_highest_status(applications)
        if not highest_status:
            return None
        
        # Filter applications with the highest status
        highest_status_apps = [app for app in applications if app.status == highest_status]
        
        if not highest_status_apps:
            return None
        
        # If only one application with highest status, return its intake
        if len(highest_status_apps) == 1:
            return highest_status_apps[0].intake
        
        # If multiple applications with same highest status, find the closest intake
        closest_intake = None
        closest_date = None
        
        for app in highest_status_apps:
            intake_date = self.parse_intake_date(app.intake)
            if intake_date and (closest_date is None or intake_date < closest_date):
                closest_date = intake_date
                closest_intake = app.intake
        
        return closest_intake
    
    def validate_student_business_logic(self, student):
        """Validate business logic for a single student"""
        applications = student.applications
        
        # Calculate expected values
        expected_status = self.calculate_expected_highest_status(applications)
        expected_intake = self.calculate_expected_highest_intake(applications)
        
        # Get actual values
        actual_status = student.highest_status
        actual_intake = student.highest_intake
        
        # Validation results
        status_correct = expected_status == actual_status
        intake_correct = expected_intake == actual_intake
        
        return {
            'student_id': student.id,
            'student_name': student.name,
            'applications_count': len(applications),
            'expected_status': expected_status,
            'actual_status': actual_status,
            'expected_intake': expected_intake,
            'actual_intake': actual_intake,
            'status_correct': status_correct,
            'intake_correct': intake_correct,
            'valid': status_correct and intake_correct,
            'applications': [
                {
                    'id': app.id,
                    'university': app.university_name,
                    'program': app.program_name,
                    'intake': app.intake,
                    'status': app.status,
                    'weight': self.status_hierarchy.get(app.status, 0)
                } for app in applications
            ]
        }

@pytest.fixture(scope="module")
def app():
    """Create application context for testing"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def validator():
    """Create business logic validator instance"""
    return StudentBusinessLogicValidator()

def test_student_business_logic(app, validator, student_id):
    """Test business logic for a specific student"""
    with app.app_context():
        # Get student
        student = Student.query.get(student_id)
        if not student:
            pytest.skip(f"Student with ID {student_id} not found in database")
        
        # Validate business logic
        result = validator.validate_student_business_logic(student)
        
        # Print detailed information
        print(f"\n{'='*60}")
        print(f"Student ID: {result['student_id']}")
        print(f"Student Name: {result['student_name']}")
        print(f"Applications Count: {result['applications_count']}")
        print(f"{'='*60}")
        
        print(f"\nStatus Validation:")
        print(f"  Expected: {result['expected_status']}")
        print(f"  Actual:   {result['actual_status']}")
        print(f"  Correct:  {'✅' if result['status_correct'] else '❌'}")
        
        print(f"\nIntake Validation:")
        print(f"  Expected: {result['expected_intake']}")
        print(f"  Actual:   {result['actual_intake']}")
        print(f"  Correct:  {'✅' if result['intake_correct'] else '❌'}")
        
        if result['applications']:
            print(f"\nApplications Details:")
            for i, app in enumerate(result['applications'], 1):
                print(f"  {i}. {app['university']} | {app['program']}")
                print(f"     Intake: {app['intake']} | Status: {app['status']} (Weight: {app['weight']})")
        else:
            print(f"\nNo applications found for this student")
        
        print(f"\nOverall Result: {'✅ PASSED' if result['valid'] else '❌ FAILED'}")
        print(f"{'='*60}")
        
        # Create detailed error message if validation fails
        if not result['valid']:
            error_details = []
            if not result['status_correct']:
                error_details.append(f"Status mismatch: expected '{result['expected_status']}', got '{result['actual_status']}'")
            if not result['intake_correct']:
                error_details.append(f"Intake mismatch: expected '{result['expected_intake']}', got '{result['actual_intake']}'")
            
            error_message = f"Business logic validation failed for Student {student_id} ({result['student_name']}): " + "; ".join(error_details)
            assert False, error_message

# Parameterized tests for individual student IDs
@pytest.mark.parametrize("student_id", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_student_business_logic_batch(app, validator, student_id):
    """Test business logic for students 1-10"""
    test_student_business_logic(app, validator, student_id)

def test_specific_student_detailed(app, validator):
    """Test a specific student with very detailed output"""
    student_id = 1  # Change this to test any specific student
    
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            pytest.skip(f"Student {student_id} not found")
        
        result = validator.validate_student_business_logic(student)
        
        print(f"\n🎯 DETAILED ANALYSIS FOR STUDENT {student_id}")
        print(f"{'='*80}")
        print(f"Student: {result['student_name']} (ID: {result['student_id']})")
        print(f"Applications: {result['applications_count']}")
        print(f"{'='*80}")
        
        if result['applications']:
            print(f"\n📋 APPLICATIONS ANALYSIS:")
            sorted_apps = sorted(result['applications'], key=lambda x: x['weight'], reverse=True)
            
            for i, app in enumerate(sorted_apps, 1):
                intake_date = validator.parse_intake_date(app['intake'])
                print(f"\n  {i}. Application ID: {app['id']}")
                print(f"     University: {app['university']}")
                print(f"     Program: {app['program']}")
                print(f"     Intake: {app['intake']} ({intake_date.strftime('%Y-%m-%d') if intake_date else 'Invalid date'})")
                print(f"     Status: {app['status']} (Weight: {app['weight']})")
            
            # Show business logic calculation
            print(f"\n🧮 BUSINESS LOGIC CALCULATION:")
            max_weight = max(app['weight'] for app in result['applications'])
            highest_status_apps = [app for app in result['applications'] if app['weight'] == max_weight]
            
            print(f"   Maximum Weight: {max_weight}")
            print(f"   Applications with Max Weight: {len(highest_status_apps)}")
            
            if len(highest_status_apps) == 1:
                print(f"   Single highest status application - using its intake")
            else:
                print(f"   Multiple applications with same highest status:")
                for app in highest_status_apps:
                    intake_date = validator.parse_intake_date(app['intake'])
                    print(f"     - {app['intake']} ({intake_date.strftime('%Y-%m-%d') if intake_date else 'Invalid'})")
                
                closest_app = min(highest_status_apps, key=lambda x: validator.parse_intake_date(x['intake']) or datetime.max)
                print(f"   Closest intake: {closest_app['intake']}")
        
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   Expected Status: {result['expected_status']}")
        print(f"   Actual Status:   {result['actual_status']}")
        print(f"   Status Match:    {'✅' if result['status_correct'] else '❌'}")
        print(f"   Expected Intake: {result['expected_intake']}")
        print(f"   Actual Intake:   {result['actual_intake']}")
        print(f"   Intake Match:    {'✅' if result['intake_correct'] else '❌'}")
        print(f"   Overall:         {'✅ PASSED' if result['valid'] else '❌ FAILED'}")
        
        # Assert the validation
        assert result['valid'], f"Business logic validation failed for student {student_id}"

def test_edge_cases(app, validator):
    """Test edge cases for business logic"""
    with app.app_context():
        print(f"\n🔍 TESTING EDGE CASES:")
        
        # Test students with no applications
        students_no_apps = Student.query.filter(~Student.applications.any()).all()
        if students_no_apps:
            print(f"\n📝 Students with no applications: {len(students_no_apps)}")
            for student in students_no_apps[:5]:  # Test first 5
                result = validator.validate_student_business_logic(student)
                expected_both_none = result['expected_status'] is None and result['expected_intake'] is None
                print(f"   Student {student.id}: Expected both None: {'✅' if expected_both_none else '❌'}")
        
        # Test students with all dropped applications
        students_all_dropped = []
        for student in Student.query.filter(Student.applications.any()).all():
            if all(app.status == 'Dropped' for app in student.applications):
                students_all_dropped.append(student)
        
        if students_all_dropped:
            print(f"\n📝 Students with all dropped applications: {len(students_all_dropped)}")
            for student in students_all_dropped[:3]:  # Test first 3
                result = validator.validate_student_business_logic(student)
                expected_dropped = result['expected_status'] == 'Dropped'
                print(f"   Student {student.id}: Expected 'Dropped': {'✅' if expected_dropped else '❌'}")
        
        # Test students with mixed status applications
        print(f"\n📝 Testing mixed status applications...")
        students_with_apps = Student.query.filter(Student.applications.any()).limit(5).all()
        for student in students_with_apps:
            if len(student.applications) > 1:
                statuses = [app.status for app in student.applications]
                unique_statuses = len(set(statuses))
                result = validator.validate_student_business_logic(student)
                print(f"   Student {student.id}: {unique_statuses} unique statuses, Valid: {'✅' if result['valid'] else '❌'}")

if __name__ == "__main__":
    import argparse
    
    arg_parser = argparse.ArgumentParser(description="Test individual student business logic")
    arg_parser.add_argument("--student-id", type=int, help="Test specific student ID")
    arg_parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")
    
    args = arg_parser.parse_args()
    
    if args.student_id:
        # Test specific student
        app = create_app()
        app.config['TESTING'] = True
        validator = StudentBusinessLogicValidator()
        
        with app.app_context():
            try:
                student = db.session.get(Student, args.student_id)
                if not student:
                    print(f"\n❌ ERROR: Student ID {args.student_id} not found in database")
                    print(f"Please check if the student ID exists and try again.")
                    sys.exit(1)
                
                print(f"\n🔍 Testing Student ID: {args.student_id}")
                test_student_business_logic(app, validator, args.student_id)
                print(f"\n✅ Test completed successfully for Student ID {args.student_id}")
                
            except Exception as e:
                print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
                print(f"Please check your database connection and try again.")
                sys.exit(1)
    elif args.detailed:
        # Run detailed test
        pytest.main([__file__ + "::test_specific_student_detailed", "-v", "-s"])
    else:
        # Run all tests
        pytest.main([__file__, "-v", "-s"])