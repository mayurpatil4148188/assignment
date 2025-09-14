#!/usr/bin/env python3
"""
Dummy Data Generator for Student Platform API

This script generates realistic dummy data for students and applications
and saves it to a JSON file for easy import into the database.

Usage:
    python faker_data.py                    # Generate default data (50 students)
    python faker_data.py --count 100        # Generate 100 students
    python faker_data.py --output my_data.json  # Custom output file
    python faker_data.py --show-help        # Show detailed help
"""

import json
import random
import argparse
import sys
import os
from datetime import datetime, timedelta
from faker import Faker
from typing import List, Dict, Any

# Initialize Faker for generating realistic data
fake = Faker()

class StudentDataGenerator:
    """Generate realistic dummy data for students and applications"""
    
    def __init__(self):
        # Realistic university names
        self.universities = [
            "Harvard University", "Stanford University", "Massachusetts Institute of Technology",
            "University of California, Berkeley", "Yale University", "Princeton University",
            "Columbia University", "University of Chicago", "University of Pennsylvania",
            "California Institute of Technology", "Duke University", "Northwestern University",
            "Johns Hopkins University", "Cornell University", "Brown University",
            "University of Michigan", "Carnegie Mellon University", "University of Virginia",
            "Georgia Institute of Technology", "University of North Carolina at Chapel Hill",
            "New York University", "University of Southern California", "University of Texas at Austin",
            "University of Wisconsin-Madison", "University of Illinois at Urbana-Champaign",
            "University of Washington", "University of California, Los Angeles",
            "University of California, San Diego", "Boston University", "Northeastern University",
            "University of Florida", "Ohio State University", "Pennsylvania State University",
            "University of Minnesota", "Purdue University", "University of Maryland",
            "University of Pittsburgh", "Rutgers University", "University of Connecticut",
            "University of Delaware", "University of Vermont", "University of New Hampshire",
            "University of Maine", "University of Rhode Island", "University of Massachusetts",
            "University of Iowa", "University of Kansas", "University of Missouri",
            "University of Nebraska", "University of Oklahoma", "University of Arkansas",
            "Louisiana State University", "University of Mississippi", "University of Alabama",
            "University of Tennessee", "University of Kentucky", "University of West Virginia"
        ]
        
        # Realistic program names
        self.programs = [
            "Computer Science", "Data Science", "Artificial Intelligence", "Machine Learning",
            "Software Engineering", "Information Technology", "Cybersecurity", "Computer Engineering",
            "Business Administration", "Finance", "Marketing", "Economics", "Accounting",
            "International Business", "Management Information Systems", "Operations Research",
            "Mechanical Engineering", "Electrical Engineering", "Civil Engineering",
            "Chemical Engineering", "Biomedical Engineering", "Aerospace Engineering",
            "Environmental Engineering", "Industrial Engineering", "Materials Science",
            "Physics", "Mathematics", "Statistics", "Chemistry", "Biology", "Biochemistry",
            "Psychology", "Sociology", "Political Science", "International Relations",
            "Public Policy", "Public Health", "Nursing", "Medicine", "Dentistry",
            "Law", "Journalism", "Communications", "English Literature", "History",
            "Art History", "Fine Arts", "Graphic Design", "Architecture", "Urban Planning",
            "Education", "Social Work", "Criminal Justice", "Anthropology", "Geography"
        ]
        
        # Valid intake months and years
        self.intake_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.intake_years = ["2024", "2025", "2026", "2027"]
        
        # Application statuses
        self.statuses = [
            "Building Application", "Application Submitted to University", "Offer Received",
            "Offer Accepted by Student", "Visa Approved", "Dropped"
        ]
        
        # Status weights for realistic progression
        self.status_weights = {
            "Building Application": 0.3,
            "Application Submitted to University": 0.25,
            "Offer Received": 0.2,
            "Offer Accepted by Student": 0.15,
            "Visa Approved": 0.08,
            "Dropped": 0.02
        }
    
    def generate_student_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate realistic student data"""
        students = []
        
        for i in range(count):
            # Generate unique email
            email = fake.unique.email()
            
            # Generate realistic phone number
            phone = fake.phone_number()
            # Clean phone number to match validation
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) < 10:
                phone = f"+1{phone_digits[:10]}"
            else:
                phone = f"+1{phone_digits[:10]}"
            
            student = {
                "name": fake.name(),
                "email": email,
                "phone": phone,
                "created_at": fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
                "updated_at": fake.date_time_between(start_date='-1y', end_date='now').isoformat()
            }
            students.append(student)
        
        return students
    
    def generate_application_data(self, student_ids: List[int], applications_per_student: int = 3) -> List[Dict[str, Any]]:
        """Generate realistic application data for students"""
        applications = []
        
        for student_id in student_ids:
            # Each student applies to 1-5 universities
            num_applications = random.randint(1, applications_per_student)
            
            for _ in range(num_applications):
                # Generate realistic intake date (mostly future dates)
                intake_month = random.choice(self.intake_months)
                intake_year = random.choice(self.intake_years)
                intake = f"{intake_month} {intake_year}"
                
                # Generate status based on realistic progression
                status = random.choices(
                    list(self.status_weights.keys()),
                    weights=list(self.status_weights.values())
                )[0]
                
                application = {
                    "student_id": student_id,
                    "university_name": random.choice(self.universities),
                    "program_name": random.choice(self.programs),
                    "intake": intake,
                    "status": status,
                    "created_at": fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                    "updated_at": fake.date_time_between(start_date='-6m', end_date='now').isoformat()
                }
                applications.append(application)
        
        return applications
    
    def generate_complete_dataset(self, student_count: int = 50) -> Dict[str, Any]:
        """Generate complete dataset with students and applications"""
        print(f"🎲 Generating {student_count} students with applications...")
        
        # Generate students
        students = self.generate_student_data(student_count)
        student_ids = list(range(1, len(students) + 1))
        
        # Generate applications
        applications = self.generate_application_data(student_ids, applications_per_student=3)
        
        # Create complete dataset
        dataset = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_students": len(students),
                "total_applications": len(applications),
                "description": "Realistic dummy data for Student Platform API"
            },
            "students": students,
            "applications": applications
        }
        
        return dataset
    
    def save_to_json(self, data: Dict[str, Any], filename: str = "students.json") -> str:
        """Save data to JSON file"""
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to: {filepath}")
        return filepath
    
    def show_data_summary(self, data: Dict[str, Any]):
        """Show summary of generated data"""
        students = data.get("students", [])
        applications = data.get("applications", [])
        
        print(f"\n📊 Generated Data Summary:")
        print(f"   Students: {len(students)}")
        print(f"   Applications: {len(applications)}")
        
        # Show status distribution
        status_counts = {}
        for app in applications:
            status = app["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 Application Status Distribution:")
        for status, count in status_counts.items():
            percentage = (count / len(applications)) * 100
            print(f"   {status}: {count} ({percentage:.1f}%)")
        
        # Show university distribution (top 10)
        university_counts = {}
        for app in applications:
            uni = app["university_name"]
            university_counts[uni] = university_counts.get(uni, 0) + 1
        
        top_universities = sorted(university_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"\n🏫 Top 10 Universities by Applications:")
        for uni, count in top_universities:
            print(f"   {uni}: {count} applications")
        
        # Show program distribution (top 10)
        program_counts = {}
        for app in applications:
            program = app["program_name"]
            program_counts[program] = program_counts.get(program, 0) + 1
        
        top_programs = sorted(program_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"\n🎓 Top 10 Programs by Applications:")
        for program, count in top_programs:
            print(f"   {program}: {count} applications")


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="Generate dummy data for Student Platform API")
    parser.add_argument("--count", type=int, default=50, help="Number of students to generate (default: 50)")
    parser.add_argument("--output", default="students.json", help="Output JSON filename (default: students.json)")
    parser.add_argument("--show-help", action="store_true", help="Show detailed help message")
    
    args = parser.parse_args()
    
    if args.show_help:
        print("🎲 Dummy Data Generator for Student Platform API")
        print("=" * 50)
        print()
        print("This script generates realistic dummy data for students and applications")
        print("and saves it to a JSON file for easy import into the database.")
        print()
        print("Usage:")
        print("  python faker_data.py                    # Generate 50 students")
        print("  python faker_data.py --count 100        # Generate 100 students")
        print("  python faker_data.py --output my_data.json  # Custom output file")
        print("  python faker_data.py --show-help         # Show this help")
        print()
        print("Generated Data Includes:")
        print("  - Realistic student names, emails, and phone numbers")
        print("  - University applications to 50+ real universities")
        print("  - 50+ realistic academic programs")
        print("  - Valid application statuses and intake dates")
        print("  - Proper relationships between students and applications")
        print()
        print("Output:")
        print("  - JSON file with students and applications data")
        print("  - Metadata with generation timestamp and statistics")
        print("  - Data ready for import into PostgreSQL database")
        return
    
    try:
        # Create generator
        generator = StudentDataGenerator()
        
        # Generate data
        data = generator.generate_complete_dataset(args.count)
        
        # Save to JSON
        filepath = generator.save_to_json(data, args.output)
        
        # Show summary
        generator.show_data_summary(data)
        
        print(f"\n✅ Successfully generated dummy data!")
        print(f"   File: {filepath}")
        print(f"   Students: {len(data['students'])}")
        print(f"   Applications: {len(data['applications'])}")
        
    except Exception as e:
        print(f"❌ Error generating data: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
