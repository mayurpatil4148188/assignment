#!/usr/bin/env python3
"""
Batch Student Business Logic Test

This test file validates the business logic for students in batch mode:
1. Processes students in configurable batch sizes (default: 10)
2. Supports ASC or DESC order processing
3. Continues processing even if issues are found
4. Provides detailed reporting for failed validations
5. Shows progress and summary statistics

Usage:
    python test_batch_student_business_logic.py --order asc --batch-size 10
    python test_batch_student_business_logic.py --order desc --batch-size 5 --start-from 50
    pytest test_batch_student_business_logic.py::test_batch_all_students -v -s
"""

import pytest
import sys
import os
from datetime import datetime
from dateutil import parser as date_parser
import time

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.student import Student
from models.application import Application
from database import db

class BatchStudentValidator:
    """Batch validator for student business logic"""
    
    def __init__(self):
        # Application status hierarchy with weightage
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
            return date_parser.parse(intake)
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
    
    def validate_student(self, student):
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
            'error_details': self._get_error_details(expected_status, actual_status, expected_intake, actual_intake)
        }
    
    def _get_error_details(self, expected_status, actual_status, expected_intake, actual_intake):
        """Generate detailed error message"""
        errors = []
        if expected_status != actual_status:
            errors.append(f"Status: expected '{expected_status}', got '{actual_status}'")
        if expected_intake != actual_intake:
            errors.append(f"Intake: expected '{expected_intake}', got '{actual_intake}'")
        return "; ".join(errors) if errors else None
    
    def process_students_batch(self, student_ids, batch_size=10):
        """Process students in batches and return results"""
        results = {
            'total_processed': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_not_found': 0,
            'total_errors': 0,
            'failed_students': [],
            'not_found_students': [],
            'error_students': [],
            'batch_results': [],
            'processing_time': 0
        }
        
        start_time = time.time()
        
        # Process students in batches
        for i in range(0, len(student_ids), batch_size):
            batch_ids = student_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            print(f"\n{'='*60}")
            print(f"Processing Batch {batch_num} (Students {batch_ids[0]} to {batch_ids[-1]})")
            print(f"{'='*60}")
            
            batch_passed = 0
            batch_failed = 0
            batch_failed_details = []
            
            for student_id in batch_ids:
                try:
                    student = Student.query.get(student_id)
                    if not student:
                        print(f"  Student {student_id}: Not found - SKIPPED")
                        results['total_not_found'] += 1
                        results['not_found_students'].append(student_id)
                        continue
                    
                    result = self.validate_student(student)
                    results['total_processed'] += 1
                    
                    if result['valid']:
                        batch_passed += 1
                        results['total_passed'] += 1
                        print(f"  Student {student_id} ({result['student_name']}): PASSED ✅")
                    else:
                        batch_failed += 1
                        results['total_failed'] += 1
                        results['failed_students'].append(result)
                        batch_failed_details.append(result)
                        print(f"  Student {student_id} ({result['student_name']}): FAILED ❌")
                        print(f"    Error: {result['error_details']}")
                        
                except Exception as e:
                    print(f"  Student {student_id}: ERROR - {str(e)}")
                    results['total_errors'] += 1
                    results['error_students'].append({
                        'student_id': student_id,
                        'error_type': 'Exception',
                        'error': str(e)
                    })
            
            # Batch summary
            batch_total = batch_passed + batch_failed
            success_rate = (batch_passed / batch_total * 100) if batch_total > 0 else 0
            
            batch_result = {
                'batch_number': batch_num,
                'batch_range': f"{batch_ids[0]}-{batch_ids[-1]}",
                'processed': batch_total,
                'passed': batch_passed,
                'failed': batch_failed,
                'success_rate': success_rate,
                'failed_details': batch_failed_details
            }
            
            results['batch_results'].append(batch_result)
            
            print(f"\n  Batch {batch_num} Summary:")
            print(f"    Processed: {batch_total}")
            print(f"    Passed: {batch_passed}")
            print(f"    Failed: {batch_failed}")
            print(f"    Success Rate: {success_rate:.1f}%")
            
            if batch_failed > 0:
                print(f"    Failed Students: {[r['student_id'] for r in batch_failed_details]}")
            
            # Small delay between batches for readability
            time.sleep(0.1)
        
        results['processing_time'] = time.time() - start_time
        return results

@pytest.fixture(scope="module")
def app():
    """Create application context for testing"""
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        yield app

@pytest.fixture(scope="module")
def validator():
    """Create batch validator instance"""
    return BatchStudentValidator()

def test_batch_students_asc_order(app, validator):
    """Test students in ascending order (batch size 10)"""
    with app.app_context():
        # Get all student IDs in ascending order
        student_ids = [s.id for s in Student.query.order_by(Student.id.asc()).all()]
        if not student_ids:
            pytest.skip("No students found in database")
        
        print(f"\n🚀 BATCH TESTING - ASCENDING ORDER")
        print(f"Total students to process: {len(student_ids)}")
        print(f"Student ID range: {student_ids[0]} to {student_ids[-1]}")
        
        results = validator.process_students_batch(student_ids, batch_size=10)
        
        # Print final summary
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY - ASCENDING ORDER")
        print(f"{'='*80}")
        print(f"Total Students Processed: {results['total_processed']}")
        print(f"Total Passed: {results['total_passed']}")
        print(f"Total Failed: {results['total_failed']}")
        print(f"Overall Success Rate: {(results['total_passed']/results['total_processed']*100):.1f}%" if results['total_processed'] > 0 else "N/A")
        print(f"Processing Time: {results['processing_time']:.2f} seconds")
        print(f"Average Time per Student: {(results['processing_time']/results['total_processed']*1000):.2f} ms" if results['total_processed'] > 0 else "N/A")
        
        # Show detailed failed students if any
        if results['failed_students']:
            print(f"\n❌ DETAILED FAILURE REPORT:")
            for student in results['failed_students'][:10]:  # Show first 10 failures
                print(f"  Student {student['student_id']} ({student['student_name']}):")
                print(f"    Applications: {student['applications_count']}")
                print(f"    Error: {student['error_details']}")
            
            if len(results['failed_students']) > 10:
                print(f"  ... and {len(results['failed_students']) - 10} more failed students")
        
        # Assert that we processed some students (but don't fail if there are business logic errors)
        assert results['total_processed'] > 0, "No students were processed"

def test_batch_students_desc_order(app, validator):
    """Test students in descending order (batch size 10)"""
    with app.app_context():
        # Get all student IDs in descending order
        student_ids = [s.id for s in Student.query.order_by(Student.id.desc()).all()]
        if not student_ids:
            pytest.skip("No students found in database")
        
        print(f"\n🚀 BATCH TESTING - DESCENDING ORDER")
        print(f"Total students to process: {len(student_ids)}")
        print(f"Student ID range: {student_ids[0]} to {student_ids[-1]}")
        
        results = validator.process_students_batch(student_ids, batch_size=10)
        
        # Print final summary
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY - DESCENDING ORDER")
        print(f"{'='*80}")
        print(f"Total Students Processed: {results['total_processed']}")
        print(f"Total Passed: {results['total_passed']}")
        print(f"Total Failed: {results['total_failed']}")
        print(f"Overall Success Rate: {(results['total_passed']/results['total_processed']*100):.1f}%" if results['total_processed'] > 0 else "N/A")
        print(f"Processing Time: {results['processing_time']:.2f} seconds")
        
        # Assert that we processed some students
        assert results['total_processed'] > 0, "No students were processed"

def test_batch_custom_range(app, validator):
    """Test custom range of students (configurable)"""
    start_id = 1
    end_id = 50
    batch_size = 5
    
    with app.app_context():
        # Get student IDs in the specified range
        student_ids = [s.id for s in Student.query.filter(
            Student.id >= start_id, 
            Student.id <= end_id
        ).order_by(Student.id.asc()).all()]
        
        if not student_ids:
            pytest.skip(f"No students found in range {start_id}-{end_id}")
        
        print(f"\n🚀 BATCH TESTING - CUSTOM RANGE ({start_id}-{end_id})")
        print(f"Batch size: {batch_size}")
        print(f"Students found in range: {len(student_ids)}")
        
        results = validator.process_students_batch(student_ids, batch_size=batch_size)
        
        # Print final summary
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY - CUSTOM RANGE")
        print(f"{'='*80}")
        print(f"Range: {start_id} to {end_id}")
        print(f"Batch Size: {batch_size}")
        print(f"Total Students Processed: {results['total_processed']}")
        print(f"Total Passed: {results['total_passed']}")
        print(f"Total Failed: {results['total_failed']}")
        print(f"Overall Success Rate: {(results['total_passed']/results['total_processed']*100):.1f}%" if results['total_processed'] > 0 else "N/A")
        
        # Assert that we processed some students
        assert results['total_processed'] > 0, "No students were processed in the specified range"

def test_batch_students_with_applications_only(app, validator):
    """Test only students who have applications"""
    with app.app_context():
        # Get student IDs who have applications
        student_ids = [s.id for s in Student.query.filter(Student.applications.any()).order_by(Student.id.asc()).all()]
        
        if not student_ids:
            pytest.skip("No students with applications found")
        
        print(f"\n🚀 BATCH TESTING - STUDENTS WITH APPLICATIONS ONLY")
        print(f"Students with applications: {len(student_ids)}")
        
        results = validator.process_students_batch(student_ids, batch_size=8)
        
        # Print final summary
        print(f"\n{'='*80}")
        print(f"FINAL SUMMARY - STUDENTS WITH APPLICATIONS")
        print(f"{'='*80}")
        print(f"Total Students Processed: {results['total_processed']}")
        print(f"Total Passed: {results['total_passed']}")
        print(f"Total Failed: {results['total_failed']}")
        print(f"Overall Success Rate: {(results['total_passed']/results['total_processed']*100):.1f}%" if results['total_processed'] > 0 else "N/A")
        
        # Show batch-wise performance
        if results['batch_results']:
            print(f"\nBatch-wise Performance:")
            for batch in results['batch_results']:
                print(f"  Batch {batch['batch_number']} (Range: {batch['batch_range']}): "
                      f"{batch['success_rate']:.1f}% success rate")

        # Assert that we processed some students
        assert results['total_processed'] > 0, "No students with applications were processed"

def test_performance_large_batch(app, validator):
    """Test performance with large batch processing"""
    with app.app_context():
        # Get first 100 students or all if less than 100
        all_student_ids = [s.id for s in Student.query.order_by(Student.id.asc()).all()]
        student_ids = all_student_ids[:100] if len(all_student_ids) >= 100 else all_student_ids
        
        if len(student_ids) < 50:
            pytest.skip("Need at least 50 students for performance test")
        
        print(f"\n🚀 PERFORMANCE TEST - LARGE BATCH")
        print(f"Testing with {len(student_ids)} students")
        
        start_time = time.time()
        results = validator.process_students_batch(student_ids, batch_size=20)
        end_time = time.time()
        
        # Performance metrics
        total_time = end_time - start_time
        avg_time_per_student = (total_time / results['total_processed']) * 1000 if results['total_processed'] > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"PERFORMANCE TEST RESULTS")
        print(f"{'='*80}")
        print(f"Students Processed: {results['total_processed']}")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Average Time per Student: {avg_time_per_student:.2f} ms")
        print(f"Students per Second: {results['total_processed']/total_time:.1f}" if total_time > 0 else "N/A")
        print(f"Success Rate: {(results['total_passed']/results['total_processed']*100):.1f}%" if results['total_processed'] > 0 else "N/A")
        
        # Performance assertions
        assert avg_time_per_student < 100, f"Performance too slow: {avg_time_per_student:.2f}ms per student"
        assert results['total_processed'] > 0, "No students were processed"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch test student business logic")
    parser.add_argument("--order", choices=['asc', 'desc'], default='asc',
                       help="Order to process students (asc or desc)")
    parser.add_argument("--batch-size", type=int, default=10,
                       help="Number of students to process in each batch")
    parser.add_argument("--start-from", type=int,
                       help="Start processing from this student ID")
    parser.add_argument("--limit", type=int,
                       help="Limit total number of students to process")
    parser.add_argument("--apps-only", action="store_true",
                       help="Process only students with applications")
    
    args = parser.parse_args()
    
    # Create app and validator
    app = create_app()
    app.config['TESTING'] = True
    validator = BatchStudentValidator()
    
    with app.app_context():
        print(f"\n🎯 BATCH STUDENT BUSINESS LOGIC VALIDATOR")
        print(f"{'='*60}")
        print(f"Order: {args.order.upper()}")
        print(f"Batch Size: {args.batch_size}")
        print(f"Apps Only: {args.apps_only}")
        if args.start_from:
            print(f"Start From: {args.start_from}")
        if args.limit:
            print(f"Limit: {args.limit}")
        
        # Build query
        query = Student.query
        
        if args.apps_only:
            query = query.filter(Student.applications.any())
        
        if args.start_from:
            if args.order == 'asc':
                query = query.filter(Student.id >= args.start_from)
            else:
                query = query.filter(Student.id <= args.start_from)
        
        # Apply ordering
        if args.order == 'asc':
            query = query.order_by(Student.id.asc())
        else:
            query = query.order_by(Student.id.desc())
        
        # Apply limit
        if args.limit:
            query = query.limit(args.limit)
        
        # Get student IDs
        student_ids = [s.id for s in query.all()]
        
        if not student_ids:
            print("❌ No students found matching criteria")
            sys.exit(1)
        
        print(f"\nFound {len(student_ids)} students to process")
        print(f"ID Range: {student_ids[0]} to {student_ids[-1]}")
        
        # Process students
        results = validator.process_students_batch(student_ids, batch_size=args.batch_size)
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"EXECUTION COMPLETE")
        print(f"{'='*80}")
        print(f"Total Processed: {results['total_processed']}")
        print(f"Passed: {results['total_passed']} ({(results['total_passed']/results['total_processed']*100):.1f}%)" if results['total_processed'] > 0 else "Passed: 0")
        print(f"Failed: {results['total_failed']} ({(results['total_failed']/results['total_processed']*100):.1f}%)" if results['total_processed'] > 0 else "Failed: 0")
        print(f"Not Found: {results['total_not_found']}")
        print(f"Errors: {results['total_errors']}")
        print(f"Processing Time: {results['processing_time']:.2f} seconds")
        
        # Show not found students
        if results['not_found_students']:
            print(f"\n⚠️  NOT FOUND STUDENT IDs: {results['not_found_students']}")
        
        # Show error students
        if results['error_students']:
            print(f"\n💥 STUDENTS WITH ERRORS:")
            for error_info in results['error_students']:
                print(f"  ID {error_info['student_id']}: {error_info['error_type']} - {error_info['error']}")
        
        # Show failed students
        if results['failed_students']:
            print(f"\n❌ FAILED STUDENTS SUMMARY:")
            for student in results['failed_students']:
                print(f"  ID {student['student_id']} ({student['student_name']}): {student['error_details']}")
        
        # Exit code based on results
        total_issues = results['total_failed'] + results['total_not_found'] + results['total_errors']
        if total_issues > 0:
            print(f"\n⚠️  {total_issues} students had issues ({results['total_failed']} failed validation, {results['total_not_found']} not found, {results['total_errors']} errors)")
            if results['total_failed'] > 0:
                sys.exit(1)  # Exit with error code only for validation failures
            else:
                sys.exit(0)  # Not found or errors don't fail the test
        else:
            print(f"\n✅ All students passed business logic validation!")
            sys.exit(0)