#!/usr/bin/env python3
"""
API Test Script for Student Platform API

This script reads students.json file and creates students and applications
using the API endpoints. It includes error handling and logging.

Usage:
    python api_test.py                    # Use default settings
    python api_test.py --base-url http://localhost:5005  # Custom base URL
    python api_test.py --limit 10         # Limit number of students to create
    python api_test.py --dry-run          # Show what would be created without making API calls
"""

import json
import requests
import time
import logging
import argparse
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class StudentPlatformAPIClient:
    """Client for Student Platform API"""
    
    def __init__(self, base_url: str = "http://localhost:5005", debug: bool = False):
        self.base_url = base_url.rstrip('/')
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Setup logging
        self.setup_logging()
        
        # Track created resources
        self.created_students = {}
        self.created_applications = []
        self.errors = []
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = f"api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(os.path.dirname(__file__), log_filename)
        
        log_level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging to: {log_path}")
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = self.session.get(f"{self.base_url}/api/health/")
            if response.status_code == 200:
                self.logger.info("✅ API connection successful")
                return True
            else:
                self.logger.error(f"❌ API health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ API connection failed: {str(e)}")
            return False
    
    def create_student(self, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a student via API"""
        try:
            # Prepare student data for API (remove timestamps)
            api_data = {
                "name": student_data["name"],
                "email": student_data["email"],
                "phone": student_data["phone"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/students/",
                json=api_data,
                timeout=30
            )
            
            if response.status_code == 201:
                try:
                    created_student = response.json()
                    self.logger.debug(f"Student response: {created_student}")
                    student_id = created_student.get('id') or created_student.get('student_id')
                    self.logger.info(f"✅ Created student: {student_data['name']} (ID: {student_id})")
                    return created_student
                except Exception as e:
                    error_msg = f"Failed to parse student response: {str(e)} - Response: {response.text}"
                    self.logger.error(f"❌ {error_msg}")
                    self.errors.append(error_msg)
                    return None
            else:
                error_msg = f"Failed to create student {student_data['name']}: {response.status_code} - {response.text}"
                self.logger.error(f"❌ {error_msg}")
                self.errors.append(error_msg)
                return None
                
        except Exception as e:
            error_msg = f"Exception creating student {student_data['name']}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return None
    
    def create_application(self, application_data: Dict[str, Any], student_id: int) -> Optional[Dict[str, Any]]:
        """Create an application via API"""
        try:
            # Prepare application data for API
            api_data = {
                "student_id": student_id,
                "university_name": application_data["university_name"],
                "program_name": application_data["program_name"],
                "intake": application_data["intake"],
                "status": application_data["status"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/applications/",
                json=api_data,
                timeout=30
            )
            
            if response.status_code == 201:
                created_application = response.json()
                app_id = created_application.get('id') or created_application.get('application_id')
                self.logger.info(f"✅ Created application: {application_data['university_name']} - {application_data['program_name']} (ID: {app_id})")
                return created_application
            else:
                error_msg = f"Failed to create application for student {student_id}: {response.status_code} - {response.text}"
                self.logger.error(f"❌ {error_msg}")
                self.errors.append(error_msg)
                return None
                
        except Exception as e:
            error_msg = f"Exception creating application for student {student_id}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return None
    
    def load_students_data(self, json_file: str = "students.json") -> Dict[str, Any]:
        """Load students data from JSON file"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), json_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"📁 Loaded data from: {file_path}")
            self.logger.info(f"   Students: {len(data.get('students', []))}")
            self.logger.info(f"   Applications: {len(data.get('applications', []))}")
            
            return data
        except Exception as e:
            self.logger.error(f"❌ Failed to load JSON file: {str(e)}")
            raise
    
    def process_students_and_applications(self, data: Dict[str, Any], limit: Optional[int] = None, dry_run: bool = False):
        """Process students and applications from JSON data"""
        students = data.get("students", [])
        applications = data.get("applications", [])
        
        if limit:
            students = students[:limit]
            self.logger.info(f"🔢 Limited to {limit} students")
        
        if dry_run:
            self.logger.info("🔍 DRY RUN MODE - No API calls will be made")
            self.logger.info(f"   Would create {len(students)} students")
            self.logger.info(f"   Would create {len(applications)} applications")
            return
        
        # Create students first
        self.logger.info(f"👥 Creating {len(students)} students...")
        for i, student_data in enumerate(students, 1):
            self.logger.info(f"   Processing student {i}/{len(students)}: {student_data['name']}")
            
            created_student = self.create_student(student_data)
            if created_student:
                # Map original student index to new student ID
                student_id = created_student.get('id') or created_student.get('student_id')
                if student_id:
                    self.created_students[i] = student_id
                else:
                    self.logger.error(f"❌ No ID found in student response: {created_student}")
                    self.errors.append(f"No ID found in student response for {student_data['name']}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        # Create applications
        self.logger.info(f"📝 Creating applications...")
        application_count = 0
        for application_data in applications:
            original_student_id = application_data["student_id"]
            new_student_id = self.created_students.get(original_student_id)
            
            if new_student_id:
                created_application = self.create_application(application_data, new_student_id)
                if created_application:
                    self.created_applications.append(created_application)
                    application_count += 1
            else:
                error_msg = f"Student ID {original_student_id} not found in created students"
                self.logger.warning(f"⚠️  {error_msg}")
                self.errors.append(error_msg)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        self.logger.info(f"✅ Created {application_count} applications")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API statistics"""
        try:
            # Get students count
            students_response = self.session.get(f"{self.base_url}/api/students/?page=1&per_page=1")
            students_count = 0
            if students_response.status_code == 200:
                students_data = students_response.json()
                students_count = students_data.get("total", 0)
            
            # Get applications count
            applications_response = self.session.get(f"{self.base_url}/api/applications/?page=1&per_page=1")
            applications_count = 0
            if applications_response.status_code == 200:
                applications_data = applications_response.json()
                applications_count = applications_data.get("total", 0)
            
            return {
                "students": students_count,
                "applications": applications_count
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get statistics: {str(e)}")
            return {"students": 0, "applications": 0}
    
    def print_summary(self):
        """Print summary of operations"""
        print("\n" + "="*60)
        print("📊 API TEST SUMMARY")
        print("="*60)
        
        print(f"✅ Created Students: {len(self.created_students)}")
        print(f"✅ Created Applications: {len(self.created_applications)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ Error Details:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")
        
        # Get current API statistics
        stats = self.get_statistics()
        print(f"\n📈 Current API Statistics:")
        print(f"   Total Students in API: {stats['students']}")
        print(f"   Total Applications in API: {stats['applications']}")
        
        print("="*60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Student Platform API with JSON data")
    parser.add_argument("--base-url", default="http://localhost:5005", 
                       help="Base URL for the API (default: http://localhost:5005)")
    parser.add_argument("--json-file", default="students.json", 
                       help="JSON file to read (default: students.json)")
    parser.add_argument("--limit", type=int, 
                       help="Limit number of students to create")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be created without making API calls")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    try:
        # Create API client
        client = StudentPlatformAPIClient(args.base_url, debug=args.debug)
        
        # Test connection
        if not client.test_connection():
            print("❌ Cannot connect to API. Please check if the server is running.")
            sys.exit(1)
        
        # Load data
        data = client.load_students_data(args.json_file)
        
        # Process students and applications
        client.process_students_and_applications(
            data, 
            limit=args.limit, 
            dry_run=args.dry_run
        )
        
        # Print summary
        client.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
