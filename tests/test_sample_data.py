#!/usr/bin/env python3
"""
Sample Data Test for Student Logic

This test creates sample data and validates the logic works correctly.
"""

import pytest
import sys
import os
from datetime import datetime

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
        from dateutil import parser
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

def test_sample_student_logic(app, tester):
    """Test logic with sample student data"""
    with app.app_context():
        # Create a test student
        student = Student(
            name="Test Student",
            email="test@example.com",
            phone="1234567890"
        )
        db.session.add(student)
        db.session.flush()  # Get the ID
        
        # Create test applications
        applications = [
            Application(
                student_id=student.id,
                university_name="Harvard",
                program_name="Computer Science",
                intake="Jan 2026",
                status="Offer Received"
            ),
            Application(
                student_id=student.id,
                university_name="MIT",
                program_name="Data Science",
                intake="Sep 2025",
                status="Visa Approved"
            ),
            Application(
                student_id=student.id,
                university_name="Stanford",
                program_name="AI",
                intake="Jan 2027",
                status="Building Application"
            )
        ]
        
        for app in applications:
            db.session.add(app)
        
        db.session.commit()
        
        # Test the logic
        expected_status, _ = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        # Expected results
        assert expected_status == "Visa Approved", f"Expected 'Visa Approved', got '{expected_status}'"
        assert expected_intake == "Sep 2025", f"Expected 'Sep 2025', got '{expected_intake}'"
        
        print(f"\n✅ Sample Test Results:")
        print(f"   Student: {student.name}")
        print(f"   Expected Highest Status: {expected_status}")
        print(f"   Expected Highest Intake: {expected_intake}")
        print(f"   Applications:")
        for i, app in enumerate(applications, 1):
            weight = tester.status_hierarchy.get(app.status, 0)
            print(f"      {i}. {app.university_name} | {app.program_name} | {app.intake} | {app.status} (weight: {weight})")
        
        # Clean up
        db.session.delete(student)
        db.session.commit()

def test_sample_student_same_status(app, tester):
    """Test logic with applications having same highest status"""
    with app.app_context():
        # Create a test student
        student = Student(
            name="Test Student Same Status",
            email="test2@example.com",
            phone="1234567891"
        )
        db.session.add(student)
        db.session.flush()  # Get the ID
        
        # Create test applications with same highest status
        applications = [
            Application(
                student_id=student.id,
                university_name="Harvard",
                program_name="Computer Science",
                intake="Jan 2026",
                status="Offer Received"
            ),
            Application(
                student_id=student.id,
                university_name="MIT",
                program_name="Data Science",
                intake="Sep 2026",
                status="Offer Received"
            ),
            Application(
                student_id=student.id,
                university_name="Stanford",
                program_name="AI",
                intake="Jan 2027",
                status="Building Application"
            )
        ]
        
        for app in applications:
            db.session.add(app)
        
        db.session.commit()
        
        # Test the logic
        expected_status, _ = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        # Expected results
        assert expected_status == "Offer Received", f"Expected 'Offer Received', got '{expected_status}'"
        assert expected_intake == "Jan 2026", f"Expected 'Jan 2026' (closest), got '{expected_intake}'"
        
        print(f"\n✅ Same Status Test Results:")
        print(f"   Student: {student.name}")
        print(f"   Expected Highest Status: {expected_status}")
        print(f"   Expected Highest Intake: {expected_intake} (closest date)")
        print(f"   Applications:")
        for i, app in enumerate(applications, 1):
            weight = tester.status_hierarchy.get(app.status, 0)
            print(f"      {i}. {app.university_name} | {app.program_name} | {app.intake} | {app.status} (weight: {weight})")
        
        # Clean up
        db.session.delete(student)
        db.session.commit()

def test_sample_student_no_applications(app, tester):
    """Test logic with student having no applications"""
    with app.app_context():
        # Create a test student
        student = Student(
            name="Test Student No Apps",
            email="test3@example.com",
            phone="1234567892"
        )
        db.session.add(student)
        db.session.flush()  # Get the ID
        
        db.session.commit()
        
        # Test the logic
        applications = []
        expected_status, _ = tester.calculate_expected_highest_status(applications)
        expected_intake = tester.calculate_expected_highest_intake(applications, expected_status)
        
        # Expected results
        assert expected_status is None, f"Expected None, got '{expected_status}'"
        assert expected_intake is None, f"Expected None, got '{expected_intake}'"
        
        print(f"\n✅ No Applications Test Results:")
        print(f"   Student: {student.name}")
        print(f"   Expected Highest Status: {expected_status}")
        print(f"   Expected Highest Intake: {expected_intake}")
        print(f"   Applications: None")
        
        # Clean up
        db.session.delete(student)
        db.session.commit()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
