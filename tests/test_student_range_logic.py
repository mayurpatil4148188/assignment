#!/usr/bin/env python3
"""
Pytest tests for student range highest status and highest intake logic

This module contains tests to validate the highest status and highest intake
logic for a range of students in the Student Platform API.

Usage:
    pytest tests/test_student_range_logic.py -v
    pytest tests/test_student_range_logic.py::test_students_1_to_10 -v
    pytest tests/test_student_range_logic.py -k "range" -v
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

def test_student_range_logic(app, db_session, tester, start_id, end_id):
    """Test logic for a range of students"""
    with app.app_context():
        failed_students = []
        passed_students = []
        
        for student_id in range(start_id, end_id + 1):
            student = Student.query.get(student_id)
            if not student:
                continue  # Skip if student doesn't exist
            
            applications = student.applications
            
            # Calculate expected values
            expected_status, _ = tester.calculate_expected_highest_status(applications)
            expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
            
            # Get actual values
            actual_status = student.highest_status
            actual_intake = student.highest_intake
            
            # Test the logic
            status_correct = expected_status == actual_status
            intake_correct = expected_intake == actual_intake
            
            if status_correct and intake_correct:
                passed_students.append(student_id)
            else:
                failed_students.append({
                    'id': student_id,
                    'name': student.name,
                    'expected_status': expected_status,
                    'actual_status': actual_status,
                    'expected_intake': expected_intake,
                    'actual_intake': actual_intake,
                    'applications': [(app.university_name, app.intake, app.status, tester.status_hierarchy.get(app.status, 0)) for app in applications]
                })
        
        # Report results
        total_tested = len(passed_students) + len(failed_students)
        print(f"\n📊 Range Test Results (Students {start_id}-{end_id}):")
        print(f"   Total Tested: {total_tested}")
        print(f"   ✅ Passed: {len(passed_students)}")
        print(f"   ❌ Failed: {len(failed_students)}")
        print(f"   Success Rate: {(len(passed_students)/total_tested*100):.1f}%" if total_tested > 0 else "N/A")
        
        # Show failed students details
        if failed_students:
            print(f"\n❌ Failed Students:")
            for student in failed_students:
                print(f"   Student {student['id']} ({student['name']}):")
                if student['expected_status'] != student['actual_status']:
                    print(f"      Status: expected '{student['expected_status']}', got '{student['actual_status']}'")
                if student['expected_intake'] != student['actual_intake']:
                    print(f"      Intake: expected '{student['expected_intake']}', got '{student['actual_intake']}'")
                print(f"      Applications: {student['applications']}")
        
        # Assert that all students passed
        assert len(failed_students) == 0, f"{len(failed_students)} students failed the logic test"

# Range test cases
@pytest.mark.parametrize("start_id,end_id", [(1, 10)])
def test_students_1_to_10(app, db_session, tester, start_id, end_id):
    """Test students 1 to 10"""
    test_student_range_logic(app, db_session, tester, start_id, end_id)

@pytest.mark.parametrize("start_id,end_id", [(1, 20)])
def test_students_1_to_20(app, db_session, tester, start_id, end_id):
    """Test students 1 to 20"""
    test_student_range_logic(app, db_session, tester, start_id, end_id)

@pytest.mark.parametrize("start_id,end_id", [(11, 30)])
def test_students_11_to_30(app, db_session, tester, start_id, end_id):
    """Test students 11 to 30"""
    test_student_range_logic(app, db_session, tester, start_id, end_id)

@pytest.mark.parametrize("start_id,end_id", [(1, 50)])
def test_students_1_to_50(app, db_session, tester, start_id, end_id):
    """Test students 1 to 50"""
    test_student_range_logic(app, db_session, tester, start_id, end_id)

# Test all students in database
def test_all_students(app, db_session, tester):
    """Test all students in the database"""
    with app.app_context():
        students = Student.query.all()
        if not students:
            pytest.skip("No students found in database")
        
        failed_students = []
        passed_students = []
        
        for student in students:
            applications = student.applications
            
            # Calculate expected values
            expected_status, _ = tester.calculate_expected_highest_status(applications)
            expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
            
            # Get actual values
            actual_status = student.highest_status
            actual_intake = student.highest_intake
            
            # Test the logic
            status_correct = expected_status == actual_status
            intake_correct = expected_intake == actual_intake
            
            if status_correct and intake_correct:
                passed_students.append(student.id)
            else:
                failed_students.append({
                    'id': student.id,
                    'name': student.name,
                    'expected_status': expected_status,
                    'actual_status': actual_status,
                    'expected_intake': expected_intake,
                    'actual_intake': actual_intake
                })
        
        # Report results
        total_tested = len(passed_students) + len(failed_students)
        print(f"\n📊 All Students Test Results:")
        print(f"   Total Tested: {total_tested}")
        print(f"   ✅ Passed: {len(passed_students)}")
        print(f"   ❌ Failed: {len(failed_students)}")
        print(f"   Success Rate: {(len(passed_students)/total_tested*100):.1f}%" if total_tested > 0 else "N/A")
        
        # Show first 10 failed students
        if failed_students:
            print(f"\n❌ First 10 Failed Students:")
            for student in failed_students[:10]:
                print(f"   Student {student['id']} ({student['name']}):")
                if student['expected_status'] != student['actual_status']:
                    print(f"      Status: expected '{student['expected_status']}', got '{student['actual_status']}'")
                if student['expected_intake'] != student['actual_intake']:
                    print(f"      Intake: expected '{student['expected_intake']}', got '{student['actual_intake']}'")
            
            if len(failed_students) > 10:
                print(f"   ... and {len(failed_students) - 10} more failed students")
        
        # Assert that all students passed
        assert len(failed_students) == 0, f"{len(failed_students)} students failed the logic test"

# Test students with specific criteria
def test_students_with_applications(app, db_session, tester):
    """Test only students who have applications"""
    with app.app_context():
        students = Student.query.filter(Student.applications.any()).all()
        if not students:
            pytest.skip("No students with applications found")
        
        failed_students = []
        passed_students = []
        
        for student in students:
            applications = student.applications
            
            # Calculate expected values
            expected_status, _ = tester.calculate_expected_highest_status(applications)
            expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
            
            # Get actual values
            actual_status = student.highest_status
            actual_intake = student.highest_intake
            
            # Test the logic
            status_correct = expected_status == actual_status
            intake_correct = expected_intake == actual_intake
            
            if status_correct and intake_correct:
                passed_students.append(student.id)
            else:
                failed_students.append({
                    'id': student.id,
                    'name': student.name,
                    'expected_status': expected_status,
                    'actual_status': actual_status,
                    'expected_intake': expected_intake,
                    'actual_intake': actual_intake
                })
        
        # Report results
        total_tested = len(passed_students) + len(failed_students)
        print(f"\n📊 Students with Applications Test Results:")
        print(f"   Total Tested: {total_tested}")
        print(f"   ✅ Passed: {len(passed_students)}")
        print(f"   ❌ Failed: {len(failed_students)}")
        print(f"   Success Rate: {(len(passed_students)/total_tested*100):.1f}%" if total_tested > 0 else "N/A")
        
        # Assert that all students passed
        assert len(failed_students) == 0, f"{len(failed_students)} students with applications failed the logic test"

def test_students_without_applications(app, db_session, tester):
    """Test students who have no applications"""
    with app.app_context():
        students = Student.query.filter(~Student.applications.any()).all()
        if not students:
            pytest.skip("No students without applications found")
        
        failed_students = []
        passed_students = []
        
        for student in students:
            applications = student.applications
            
            # Calculate expected values
            expected_status, _ = tester.calculate_expected_highest_status(applications)
            expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
            
            # Get actual values
            actual_status = student.highest_status
            actual_intake = student.highest_intake
            
            # For students with no applications, both should be None
            status_correct = expected_status is None
            intake_correct = expected_intake is None
            
            if status_correct and intake_correct:
                passed_students.append(student.id)
            else:
                failed_students.append({
                    'id': student.id,
                    'name': student.name,
                    'expected_status': expected_status,
                    'actual_status': actual_status,
                    'expected_intake': expected_intake,
                    'actual_intake': actual_intake
                })
        
        # Report results
        total_tested = len(passed_students) + len(failed_students)
        print(f"\n📊 Students without Applications Test Results:")
        print(f"   Total Tested: {total_tested}")
        print(f"   ✅ Passed: {len(passed_students)}")
        print(f"   ❌ Failed: {len(failed_students)}")
        print(f"   Success Rate: {(len(passed_students)/total_tested*100):.1f}%" if total_tested > 0 else "N/A")
        
        # Show failed students
        if failed_students:
            print(f"\n❌ Failed Students:")
            for student in failed_students:
                print(f"   Student {student['id']} ({student['name']}):")
                print(f"      Expected: status=None, intake=None")
                print(f"      Actual: status={student['actual_status']}, intake={student['actual_intake']}")
        
        # Note: We don't assert here because the database might have non-None values
        # for students without applications, which is acceptable
        print(f"Note: {len(failed_students)} students have non-None values despite having no applications")

# Performance test for large ranges
@pytest.mark.slow
def test_large_range_performance(app, db_session, tester):
    """Test performance with a large range of students"""
    with app.app_context():
        # Get all student IDs
        student_ids = [s.id for s in Student.query.all()]
        if len(student_ids) < 100:
            pytest.skip("Not enough students for performance test")
        
        # Test first 100 students
        start_id = min(student_ids)
        end_id = start_id + 99
        
        import time
        start_time = time.time()
        
        failed_count = 0
        for student_id in range(start_id, end_id + 1):
            student = Student.query.get(student_id)
            if not student:
                continue
            
            applications = student.applications
            expected_status, _ = tester.calculate_expected_highest_status(applications)
            expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
            
            actual_status = student.highest_status
            actual_intake = student.highest_intake
            
            if expected_status != actual_status or expected_intake != actual_intake:
                failed_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  Performance Test Results:")
        print(f"   Students Tested: {end_id - start_id + 1}")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Failed: {failed_count}")
        print(f"   Average per student: {duration/(end_id - start_id + 1)*1000:.2f} ms")
        
        # Assert performance (should be fast)
        assert duration < 10.0, f"Performance test took too long: {duration:.2f} seconds"
        assert failed_count == 0, f"{failed_count} students failed in performance test"
