#!/usr/bin/env python3
"""
Logic Test Examples for Student Platform API

This script demonstrates the highest status and highest intake logic
with concrete examples to validate the implementation.
"""

from datetime import datetime
from dateutil import parser

class MockApplication:
    """Mock application class for testing"""
    def __init__(self, university, program, intake, status):
        self.university_name = university
        self.program_name = program
        self.intake = intake
        self.status = status

class LogicTester:
    """Test the highest status and intake logic"""
    
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
    
    def calculate_highest_status(self, applications):
        """Calculate highest status based on applications"""
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
    
    def calculate_highest_intake(self, applications, highest_status):
        """Calculate highest intake based on highest status applications"""
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
    
    def test_example(self, name, applications, expected_status, expected_intake):
        """Test a specific example"""
        print(f"\n🧪 Testing: {name}")
        print("=" * 50)
        
        # Show applications
        print("Applications:")
        for i, app in enumerate(applications, 1):
            weight = self.status_hierarchy.get(app.status, 0)
            print(f"  {i}. {app.university_name} | {app.program_name} | {app.intake} | {app.status} (weight: {weight})")
        
        # Calculate results
        actual_status, max_weight = self.calculate_highest_status(applications)
        actual_intake = self.calculate_highest_intake(applications, actual_status)
        
        # Show results
        print(f"\nResults:")
        print(f"  Expected Highest Status: {expected_status}")
        print(f"  Actual Highest Status: {actual_status}")
        print(f"  Expected Highest Intake: {expected_intake}")
        print(f"  Actual Highest Intake: {actual_intake}")
        
        # Check if correct
        status_correct = actual_status == expected_status
        intake_correct = actual_intake == expected_intake
        
        print(f"\nValidation:")
        print(f"  Status: {'✅ CORRECT' if status_correct else '❌ INCORRECT'}")
        print(f"  Intake: {'✅ CORRECT' if intake_correct else '❌ INCORRECT'}")
        
        return status_correct and intake_correct

def main():
    """Run test examples"""
    tester = LogicTester()
    
    print("🎯 STUDENT LOGIC TEST EXAMPLES")
    print("=" * 60)
    
    # Example 1: Single application
    apps1 = [
        MockApplication("Harvard", "Computer Science", "Jan 2026", "Offer Received")
    ]
    result1 = tester.test_example(
        "Single Application",
        apps1,
        "Offer Received",
        "Jan 2026"
    )
    
    # Example 2: Multiple applications with different statuses
    apps2 = [
        MockApplication("MIT", "Data Science", "Sep 2025", "Building Application"),
        MockApplication("Stanford", "AI", "Jan 2026", "Offer Received"),
        MockApplication("Berkeley", "ML", "Sep 2026", "Offer Accepted by Student")
    ]
    result2 = tester.test_example(
        "Multiple Applications - Different Statuses",
        apps2,
        "Offer Accepted by Student",
        "Sep 2026"
    )
    
    # Example 3: Same highest status, different intakes (closest should win)
    apps3 = [
        MockApplication("Harvard", "CS", "Jan 2026", "Offer Received"),
        MockApplication("MIT", "AI", "Sep 2026", "Offer Received"),
        MockApplication("Stanford", "ML", "Jan 2027", "Building Application")
    ]
    result3 = tester.test_example(
        "Same Highest Status - Closest Intake",
        apps3,
        "Offer Received",
        "Jan 2026"  # Closest intake among "Offer Received" applications
    )
    
    # Example 4: Complex scenario
    apps4 = [
        MockApplication("Harvard", "CS", "Jan 2026", "Visa Approved"),
        MockApplication("MIT", "AI", "Sep 2025", "Offer Accepted by Student"),
        MockApplication("Stanford", "ML", "Jan 2027", "Offer Received"),
        MockApplication("Berkeley", "DS", "Sep 2026", "Building Application")
    ]
    result4 = tester.test_example(
        "Complex Scenario - Multiple Statuses",
        apps4,
        "Visa Approved",
        "Jan 2026"
    )
    
    # Example 5: Dropped applications
    apps5 = [
        MockApplication("Harvard", "CS", "Jan 2026", "Dropped"),
        MockApplication("MIT", "AI", "Sep 2025", "Offer Received"),
        MockApplication("Stanford", "ML", "Jan 2027", "Dropped")
    ]
    result5 = tester.test_example(
        "With Dropped Applications",
        apps5,
        "Offer Received",
        "Sep 2025"
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    results = [result1, result2, result3, result4, result5]
    passed = sum(results)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n🎉 All logic tests passed! The implementation is correct.")
    else:
        print("\n❌ Some tests failed. Please check the logic implementation.")

if __name__ == "__main__":
    main()
