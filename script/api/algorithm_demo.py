#!/usr/bin/env python3
"""
Algorithm Demonstration and Benchmarking Script

This script demonstrates the different algorithms for calculating highest status and intake,
and provides benchmarking capabilities to compare their performance.
"""

import sys
import os
import time
import random
from datetime import datetime

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app
from models.student import Student
from models.application import Application
from database import db
from services.optimized_student_service import OptimizedStudentService, get_optimal_algorithm

class AlgorithmDemo:
    """Demonstration class for different algorithms"""
    
    def __init__(self):
        self.app = create_app()
        self.app.app_context().push()
        
        # Status hierarchy for reference
        self.status_hierarchy = {
            'Building Application': 1,
            'Application Submitted to University': 2,
            'Offer Received': 3,
            'Offer Accepted by Student': 4,
            'Visa Approved': 5,
            'Dropped': 0
        }
        
        # Sample intakes for testing
        self.sample_intakes = [
            'Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025',
            'Jun 2025', 'Jul 2025', 'Aug 2025', 'Sep 2025', 'Oct 2025',
            'Nov 2025', 'Dec 2025', 'Jan 2026', 'Feb 2026', 'Mar 2026'
        ]
    
    def create_test_data(self, student_count=5, apps_per_student=10):
        """Create test data for algorithm demonstration"""
        print(f"🧪 Creating test data: {student_count} students, {apps_per_student} apps each")
        
        students = []
        for i in range(student_count):
            student = Student(
                name=f"Test Student {i+1}",
                email=f"test{i+1}@example.com",
                phone=f"123456789{i}"
            )
            db.session.add(student)
            db.session.flush()  # Get the ID
            
            # Create applications for this student
            for j in range(apps_per_student):
                app = Application(
                    student_id=student.id,
                    university_name=f"University {j+1}",
                    program_name=f"Program {j+1}",
                    intake=random.choice(self.sample_intakes),
                    status=random.choice(list(self.status_hierarchy.keys()))
                )
                db.session.add(app)
            
            students.append(student)
        
        db.session.commit()
        print(f"✅ Created {student_count} students with {apps_per_student} applications each")
        return students
    
    def demonstrate_algorithm(self, student_id, algorithm_name, algorithm_func):
        """Demonstrate a specific algorithm"""
        print(f"\n🔍 Demonstrating {algorithm_name}")
        print("=" * 50)
        
        # Get student and applications
        student = Student.query.get(student_id)
        applications = Application.query.filter_by(student_id=student_id).all()
        
        print(f"Student: {student.name}")
        print(f"Applications: {len(applications)}")
        
        # Show applications
        print("\n📋 Applications:")
        for i, app in enumerate(applications, 1):
            weight = self.status_hierarchy.get(app.status, 0)
            print(f"  {i}. {app.university_name} | {app.intake} | {app.status} (weight: {weight})")
        
        # Run algorithm
        start_time = time.time()
        result, errors = algorithm_func(student_id)
        end_time = time.time()
        
        if errors:
            print(f"❌ Error: {errors}")
            return
        
        print(f"\n📊 Result:")
        print(f"  Highest Status: {result['highest_status']}")
        print(f"  Highest Intake: {result['highest_intake']}")
        print(f"  Execution Time: {(end_time - start_time)*1000:.2f} ms")
    
    def benchmark_algorithms(self, student_id, iterations=100):
        """Benchmark different algorithms"""
        print(f"\n⚡ Benchmarking algorithms ({iterations} iterations)")
        print("=" * 60)
        
        algorithms = {
            'V1_Optimized': OptimizedStudentService.calculate_highest_status_and_intake_v1,
            'V2_Database': OptimizedStudentService.calculate_highest_status_and_intake_v2,
            'V3_Cached': OptimizedStudentService.calculate_highest_status_and_intake_v3
        }
        
        results = {}
        
        for name, algorithm in algorithms.items():
            print(f"\n🔄 Testing {name}...")
            times = []
            
            for i in range(iterations):
                start_time = time.time()
                result, errors = algorithm(student_id)
                end_time = time.time()
                
                if errors:
                    print(f"❌ Error in {name}: {errors}")
                    continue
                
                times.append(end_time - start_time)
                
                if (i + 1) % 20 == 0:
                    print(f"  Completed {i + 1}/{iterations} iterations")
            
            if times:
                results[name] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_time': sum(times),
                    'iterations': len(times)
                }
        
        # Display results
        print(f"\n📈 Benchmark Results:")
        print("=" * 60)
        print(f"{'Algorithm':<15} {'Avg (ms)':<10} {'Min (ms)':<10} {'Max (ms)':<10} {'Total (s)':<10}")
        print("-" * 60)
        
        for name, stats in results.items():
            print(f"{name:<15} {stats['avg_time']*1000:<10.2f} {stats['min_time']*1000:<10.2f} "
                  f"{stats['max_time']*1000:<10.2f} {stats['total_time']:<10.2f}")
        
        return results
    
    def test_edge_cases(self):
        """Test edge cases for algorithm correctness"""
        print(f"\n🧪 Testing Edge Cases")
        print("=" * 40)
        
        # Test case 1: Student with no applications
        student1 = Student(
            name="No Apps Student",
            email="noapps@example.com",
            phone="1234567890"
        )
        db.session.add(student1)
        db.session.flush()
        
        result, errors = OptimizedStudentService.calculate_highest_status_and_intake_v1(student1.id)
        print(f"✅ No applications: {result}")
        
        # Test case 2: Student with all same status
        student2 = Student(
            name="Same Status Student",
            email="samestatus@example.com",
            phone="1234567891"
        )
        db.session.add(student2)
        db.session.flush()
        
        for i in range(3):
            app = Application(
                student_id=student2.id,
                university_name=f"University {i+1}",
                program_name=f"Program {i+1}",
                intake=self.sample_intakes[i],
                status="Offer Received"  # Same status
            )
            db.session.add(app)
        
        db.session.commit()
        
        result, errors = OptimizedStudentService.calculate_highest_status_and_intake_v1(student2.id)
        print(f"✅ Same status (closest intake): {result}")
        
        # Test case 3: Student with highest status
        student3 = Student(
            name="Highest Status Student",
            email="highest@example.com",
            phone="1234567892"
        )
        db.session.add(student3)
        db.session.flush()
        
        for i in range(3):
            app = Application(
                student_id=student3.id,
                university_name=f"University {i+1}",
                program_name=f"Program {i+1}",
                intake=self.sample_intakes[i],
                status="Visa Approved" if i == 0 else "Offer Received"
            )
            db.session.add(app)
        
        db.session.commit()
        
        result, errors = OptimizedStudentService.calculate_highest_status_and_intake_v1(student3.id)
        print(f"✅ Highest status: {result}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print(f"\n🧹 Cleaning up test data...")
        
        # Delete test students and their applications
        test_students = Student.query.filter(Student.name.like("Test Student %")).all()
        for student in test_students:
            db.session.delete(student)
        
        # Delete edge case students
        edge_students = Student.query.filter(
            Student.name.in_(["No Apps Student", "Same Status Student", "Highest Status Student"])
        ).all()
        for student in edge_students:
            db.session.delete(student)
        
        db.session.commit()
        print("✅ Test data cleaned up")
    
    def run_demo(self):
        """Run the complete demonstration"""
        print("🎯 Algorithm Demonstration and Benchmarking")
        print("=" * 60)
        
        try:
            # Create test data
            students = self.create_test_data(student_count=3, apps_per_student=5)
            
            # Demonstrate algorithms
            for student in students[:2]:  # Demo first 2 students
                self.demonstrate_algorithm(
                    student.id, 
                    "V1_Optimized", 
                    OptimizedStudentService.calculate_highest_status_and_intake_v1
                )
            
            # Benchmark algorithms
            if students:
                self.benchmark_algorithms(students[0].id, iterations=50)
            
            # Test edge cases
            self.test_edge_cases()
            
            # Show algorithm selection
            print(f"\n🎯 Algorithm Selection Guide:")
            print("=" * 40)
            print("• Default use case: V1_Optimized")
            print("• Large datasets (>1000 apps): V2_Database")
            print("• High frequency updates: V3_Cached")
            print("• Batch processing: Batch algorithm")
            
        except Exception as e:
            print(f"❌ Error during demonstration: {str(e)}")
        finally:
            # Clean up
            self.cleanup_test_data()

def main():
    """Main function"""
    demo = AlgorithmDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
