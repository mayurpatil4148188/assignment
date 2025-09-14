#!/usr/bin/env python3
"""
Database Result Test Script for Student Platform API

This script reads student and application records from the database and validates
the highest status and highest intake logic to ensure it's working correctly.

Usage:
    python result_test.py                    # Test all students
    python result_test.py --student-id 1     # Test specific student
    python result_test.py --limit 10         # Test first 10 students
    python result_test.py --verbose          # Show detailed output
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dateutil import parser

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app
from models.student import Student
from models.application import Application
from database import db

class StudentLogicTester:
    """Test student highest status and highest intake logic"""
    
    def __init__(self, verbose: bool = False):
        self.app = create_app()
        self.app.app_context().push()
        self.verbose = verbose
        self.setup_logging()
        
        # Application status hierarchy with weightage
        self.status_hierarchy = {
            'Building Application': 1,
            'Application Submitted to University': 2,
            'Offer Received': 3,
            'Offer Accepted by Student': 4,
            'Visa Approved': 5,
            'Dropped': 0
        }
        
        # Test results
        self.test_results = {
            'total_students': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = f"result_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(os.path.dirname(__file__), log_filename)
        
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging to: {log_path}")
    
    def parse_intake_date(self, intake: str) -> Optional[datetime]:
        """Parse intake string to datetime for comparison"""
        try:
            return parser.parse(intake)
        except (ValueError, TypeError):
            return None
    
    def calculate_expected_highest_status(self, applications: List[Application]) -> Tuple[str, int]:
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
    
    def calculate_expected_highest_intake(self, applications: List[Application], highest_status: str) -> Optional[str]:
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
            if intake_date:
                if closest_date is None or intake_date < closest_date:
                    closest_date = intake_date
                    closest_intake = app.intake
        
        return closest_intake
    
    def test_student_logic(self, student: Student) -> Dict[str, Any]:
        """Test highest status and intake logic for a single student"""
        result = {
            'student_id': student.id,
            'student_name': student.name,
            'applications_count': len(student.applications),
            'expected_highest_status': None,
            'actual_highest_status': student.highest_status,
            'expected_highest_intake': None,
            'actual_highest_intake': student.highest_intake,
            'status_match': False,
            'intake_match': False,
            'applications': [],
            'errors': []
        }
        
        try:
            # Get all applications for this student
            applications = student.applications
            
            if not applications:
                result['errors'].append("No applications found for student")
                return result
            
            # Calculate expected values
            expected_status, max_weight = self.calculate_expected_highest_status(applications)
            expected_intake = self.calculate_expected_highest_intake(applications, expected_status)
            
            result['expected_highest_status'] = expected_status
            result['expected_highest_intake'] = expected_intake
            
            # Test highest status
            if expected_status == student.highest_status:
                result['status_match'] = True
            else:
                result['errors'].append(f"Highest status mismatch: expected '{expected_status}', got '{student.highest_status}'")
            
            # Test highest intake
            if expected_intake == student.highest_intake:
                result['intake_match'] = True
            else:
                result['errors'].append(f"Highest intake mismatch: expected '{expected_intake}', got '{student.highest_intake}'")
            
            # Store application details for debugging
            for app in applications:
                app_data = {
                    'id': app.id,
                    'university': app.university_name,
                    'program': app.program_name,
                    'intake': app.intake,
                    'status': app.status,
                    'status_weight': self.status_hierarchy.get(app.status, 0)
                }
                result['applications'].append(app_data)
            
            # Sort applications by status weight for display
            result['applications'].sort(key=lambda x: x['status_weight'], reverse=True)
            
        except Exception as e:
            result['errors'].append(f"Exception during testing: {str(e)}")
        
        return result
    
    def test_all_students(self, limit: Optional[int] = None, student_id: Optional[int] = None) -> Dict[str, Any]:
        """Test all students or specific student"""
        try:
            if student_id:
                students = Student.query.filter_by(id=student_id).all()
                if not students:
                    self.logger.error(f"❌ Student with ID {student_id} not found")
                    return self.test_results
            else:
                students = Student.query.limit(limit).all() if limit else Student.query.all()
            
            self.test_results['total_students'] = len(students)
            self.logger.info(f"🧪 Testing {len(students)} students...")
            
            for i, student in enumerate(students, 1):
                self.logger.info(f"   Testing student {i}/{len(students)}: {student.name} (ID: {student.id})")
                
                result = self.test_student_logic(student)
                
                if result['errors']:
                    self.test_results['failed_tests'] += 1
                    self.logger.error(f"❌ Student {student.name} (ID: {student.id}) - FAILED")
                    for error in result['errors']:
                        self.logger.error(f"      {error}")
                        self.test_results['errors'].append(f"Student {student.id} ({student.name}): {error}")
                else:
                    self.test_results['passed_tests'] += 1
                    self.logger.info(f"✅ Student {student.name} (ID: {student.id}) - PASSED")
                
                # Show detailed results if verbose
                if self.verbose:
                    self.show_detailed_result(result)
                
                self.logger.info("")  # Empty line for readability
            
        except Exception as e:
            self.logger.error(f"❌ Error during testing: {str(e)}")
            self.test_results['errors'].append(f"Testing error: {str(e)}")
        
        return self.test_results
    
    def show_detailed_result(self, result: Dict[str, Any]):
        """Show detailed test result for a student"""
        print(f"\n📊 Detailed Results for Student {result['student_id']} ({result['student_name']}):")
        print(f"   Applications: {result['applications_count']}")
        print(f"   Expected Highest Status: {result['expected_highest_status']}")
        print(f"   Actual Highest Status: {result['actual_highest_status']}")
        print(f"   Expected Highest Intake: {result['expected_highest_intake']}")
        print(f"   Actual Highest Intake: {result['actual_highest_intake']}")
        print(f"   Status Match: {'✅' if result['status_match'] else '❌'}")
        print(f"   Intake Match: {'✅' if result['intake_match'] else '❌'}")
        
        if result['applications']:
            print(f"\n   📝 Applications (sorted by status weight):")
            for app in result['applications']:
                print(f"      - {app['university']} | {app['program']} | {app['intake']} | {app['status']} (weight: {app['status_weight']})")
        
        if result['errors']:
            print(f"\n   ❌ Errors:")
            for error in result['errors']:
                print(f"      - {error}")
    
    def show_summary(self):
        """Show test summary"""
        print("\n" + "="*60)
        print("📊 STUDENT LOGIC TEST SUMMARY")
        print("="*60)
        
        total = self.test_results['total_students']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        
        print(f"Total Students Tested: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        
        if self.test_results['errors']:
            print(f"\n❌ Errors Found:")
            for error in self.test_results['errors'][:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.test_results['errors']) > 10:
                print(f"   ... and {len(self.test_results['errors']) - 10} more errors")
        
        print("="*60)
        
        if failed == 0:
            print("🎉 All tests passed! The highest status and intake logic is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get current database statistics"""
        try:
            student_count = Student.query.count()
            application_count = Application.query.count()
            
            return {
                "students": student_count,
                "applications": application_count
            }
        except Exception as e:
            self.logger.error(f"Error getting database stats: {str(e)}")
            return {"students": 0, "applications": 0}


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Student Platform API logic")
    parser.add_argument("--student-id", type=int, 
                       help="Test specific student by ID")
    parser.add_argument("--limit", type=int, 
                       help="Limit number of students to test")
    parser.add_argument("--verbose", action="store_true", 
                       help="Show detailed output")
    parser.add_argument("--stats", action="store_true", 
                       help="Show database statistics only")
    
    args = parser.parse_args()
    
    try:
        # Create tester
        tester = StudentLogicTester(verbose=args.verbose)
        
        # Show database stats
        stats = tester.get_database_stats()
        print(f"📊 Database Statistics:")
        print(f"   Students: {stats['students']}")
        print(f"   Applications: {stats['applications']}")
        
        if args.stats:
            return
        
        if stats['students'] == 0:
            print("❌ No students found in database. Please create some students first.")
            return
        
        # Run tests
        tester.test_all_students(limit=args.limit, student_id=args.student_id)
        
        # Show summary
        tester.show_summary()
        
    except KeyboardInterrupt:
        print("\n\n❌ Testing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
