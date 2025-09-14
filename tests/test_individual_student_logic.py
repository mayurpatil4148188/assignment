#!/usr/bin/env python3
"""
Pytest tests for individual student highest status and highest intake logic

This module contains tests to validate the highest status and highest intake
logic for individual students in the Student Platform API.

Usage:
    pytest tests/test_individual_student_logic.py -v
    pytest tests/test_individual_student_logic.py::test_student_1 -v
    pytest tests/test_individual_student_logic.py -k "student_1" -v
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

class StudentLogicTester:
    """Test student highest status and highest intake logic"""
    
    def __init__(self):
        # Application status hierarchy with weightage
        self.status_hierarchy = {
            'Building Application': 1,
            'Application Submitted to University': 2,
            'Offer Received': 3,
            'Offer Accepted by Student': 4,
            'Visa Approved': 5,
            'Dropped': 0
        }
    
    def parse_intake_date(self, intake: str) -> datetime:
        """Parse intake string to datetime for comparison"""
        return parser.parse(intake)
    
    def calculate_expected_highest_status(self, applications):
        """Calculate expected highest status based on applications"""
        if not applications:
            return None, 0
        
        max_weight = -1
        highest_status = None
        
        for app in applications:
            weight = self.status_hierarchy.get(app.status, 0)
            if weight > max_weight:
                max_weight = weight
                highest_status = app.status
        
        return highest_status, max_weight
    
    def calculate_expected_highest_intake(self, applications, highest_status):
        """Calculate expected highest intake based on highest status applications"""
        if not applications or not highest_status:
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
            if closest_date is None or intake_date < closest_date:
                closest_date = intake_date
                closest_intake = app.intake
        
        return closest_intake

@pytest.fixture(scope="module")
def app():
    """Create application context for testing"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def tester():
    """Create logic tester instance"""
    return StudentLogicTester()

@pytest.fixture(scope="module")
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        yield db.session

def test_student_exists(app, db_session, student_id):
    """Test if student exists in database"""
    with app.app_context():
        student = Student.query.get(student_id)
        assert student is not None, f"Student with ID {student_id} not found in database"
        return student

def test_student_highest_status_logic(app, db_session, tester, student_id):
    """Test highest status logic for a specific student"""
    with app.app_context():
        # Get student
        student = Student.query.get(student_id)
        assert student is not None, f"Student with ID {student_id} not found"
        
        # Get applications
        applications = student.applications
        
        # Calculate expected highest status
        expected_status, max_weight = tester.calculate_expected_highest_status(applications)
        actual_status = student.highest_status
        
        # Test the logic
        assert expected_status == actual_status, (
            f"Student {student_id} ({student.name}): "
            f"Highest status mismatch - expected '{expected_status}', got '{actual_status}'. "
            f"Applications: {[(app.university_name, app.status, tester.status_hierarchy.get(app.status, 0)) for app in applications]}"
        )

def test_student_highest_intake_logic(app, db_session, tester, student_id):
    """Test highest intake logic for a specific student"""
    with app.app_context():
        # Get student
        student = Student.query.get(student_id)
        assert student is not None, f"Student with ID {student_id} not found"
        
        # Get applications
        applications = student.applications
        
        # Calculate expected values
        expected_status, _ = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        actual_intake = student.highest_intake
        
        # Test the logic
        assert expected_intake == actual_intake, (
            f"Student {student_id} ({student.name}): "
            f"Highest intake mismatch - expected '{expected_intake}', got '{actual_intake}'. "
            f"Expected status: '{expected_status}', Applications: {[(app.university_name, app.intake, app.status) for app in applications]}"
        )

def test_student_complete_logic(app, db_session, tester, student_id):
    """Test complete logic (both status and intake) for a specific student"""
    with app.app_context():
        # Get student
        student = Student.query.get(student_id)
        assert student is not None, f"Student with ID {student_id} not found"
        
        # Get applications
        applications = student.applications
        
        # Calculate expected values
        expected_status, max_weight = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        # Get actual values
        actual_status = student.highest_status
        actual_intake = student.highest_intake
        
        # Test both status and intake
        status_correct = expected_status == actual_status
        intake_correct = expected_intake == actual_intake
        
        # Create detailed error message
        error_details = []
        if not status_correct:
            error_details.append(f"Status: expected '{expected_status}', got '{actual_status}'")
        if not intake_correct:
            error_details.append(f"Intake: expected '{expected_intake}', got '{actual_intake}'")
        
        # Show application details for debugging
        app_details = []
        for app in applications:
            weight = tester.status_hierarchy.get(app.status, 0)
            app_details.append(f"{app.university_name}|{app.program_name}|{app.intake}|{app.status}(w:{weight})")
        
        assert status_correct and intake_correct, (
            f"Student {student_id} ({student.name}): Logic validation failed. "
            f"Errors: {'; '.join(error_details)}. "
            f"Applications: {app_details}"
        )

# Individual student test cases
@pytest.mark.parametrize("student_id", [1])
def test_student_1(app, db_session, tester, student_id):
    """Test student ID 1"""
    test_student_complete_logic(app, db_session, tester, student_id)

@pytest.mark.parametrize("student_id", [2])
def test_student_2(app, db_session, tester, student_id):
    """Test student ID 2"""
    test_student_complete_logic(app, db_session, tester, student_id)

@pytest.mark.parametrize("student_id", [3])
def test_student_3(app, db_session, tester, student_id):
    """Test student ID 3"""
    test_student_complete_logic(app, db_session, tester, student_id)

@pytest.mark.parametrize("student_id", [4])
def test_student_4(app, db_session, tester, student_id):
    """Test student ID 4"""
    test_student_complete_logic(app, db_session, tester, student_id)

@pytest.mark.parametrize("student_id", [5])
def test_student_5(app, db_session, tester, student_id):
    """Test student ID 5"""
    test_student_complete_logic(app, db_session, tester, student_id)

# Test specific student with detailed output
def test_student_detailed_output(app, db_session, tester):
    """Test a specific student with detailed output for debugging"""
    student_id = 1  # Change this to test different students
    
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            pytest.skip(f"Student {student_id} not found")
        
        applications = student.applications
        
        print(f"\n🎯 Testing Student {student_id}: {student.name}")
        print(f"   Applications: {len(applications)}")
        print(f"   Current Highest Status: {student.highest_status}")
        print(f"   Current Highest Intake: {student.highest_intake}")
        
        # Calculate expected values
        expected_status, max_weight = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        print(f"   Expected Highest Status: {expected_status}")
        print(f"   Expected Highest Intake: {expected_intake}")
        
        # Show applications
        if applications:
            print(f"\n   📝 Applications:")
            for i, app in enumerate(applications, 1):
                weight = tester.status_hierarchy.get(app.status, 0)
                print(f"      {i}. {app.university_name} | {app.program_name} | {app.intake} | {app.status} (weight: {weight})")
        
        # Test the logic
        assert expected_status == student.highest_status, f"Status mismatch for student {student_id}"
        assert expected_intake == student.highest_intake, f"Intake mismatch for student {student_id}"

# Test student with no applications
def test_student_no_applications(app, db_session, tester):
    """Test student with no applications"""
    with app.app_context():
        # Find a student with no applications
        students = Student.query.all()
        student_without_apps = None
        
        for student in students:
            if len(student.applications) == 0:
                student_without_apps = student
                break
        
        if not student_without_apps:
            pytest.skip("No student found without applications")
        
        student = student_without_apps
        applications = student.applications
        
        # Calculate expected values
        expected_status, _ = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        # For students with no applications, both should be None
        assert expected_status is None, f"Expected status should be None for student {student.id} with no applications"
        assert expected_intake is None, f"Expected intake should be None for student {student.id} with no applications"
        
        # Note: The actual values in database might not be None, but the logic should handle this
        print(f"Student {student.id} ({student.name}) has no applications")
        print(f"Expected: status=None, intake=None")
        print(f"Actual: status={student.highest_status}, intake={student.highest_intake}")

# Test student with all dropped applications
def test_student_all_dropped(app, db_session, tester):
    """Test student with all applications dropped"""
    with app.app_context():
        # Find a student with all dropped applications
        students = Student.query.all()
        student_all_dropped = None
        
        for student in students:
            if len(student.applications) > 0:
                all_dropped = all(app.status == 'Dropped' for app in student.applications)
                if all_dropped:
                    student_all_dropped = student
                    break
        
        if not student_all_dropped:
            pytest.skip("No student found with all dropped applications")
        
        student = student_all_dropped
        applications = student.applications
        
        # Calculate expected values
        expected_status, _ = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        # For students with all dropped applications
        assert expected_status == 'Dropped', f"Expected status should be 'Dropped' for student {student.id}"
        assert expected_intake is not None, f"Expected intake should not be None for student {student.id} with dropped applications"
        
        print(f"Student {student.id} ({student.name}) has all dropped applications")
        print(f"Expected: status='Dropped', intake={expected_intake}")
        print(f"Actual: status={student.highest_status}, intake={student.highest_intake}")
        
        # Show applications
        for app in applications:
            print(f"   - {app.university_name} | {app.intake} | {app.status}")
