#!/usr/bin/env python3
"""
Test Runner for Student Logic Tests

This script provides a convenient way to run different types of tests
for the student highest status and highest intake logic.

Usage:
    python tests/test_runner.py --help
    python tests/test_runner.py --individual --student-id 1
    python tests/test_runner.py --range --start 1 --end 20
    python tests/test_runner.py --all
    python tests/test_runner.py --examples
"""

import subprocess
import sys
import argparse
import os

def run_command(command, description):
    """Run a command and handle the output"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    print(f"Command: {' '.join(command)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully")
        else:
            print(f"\n❌ {description} failed with return code {result.returncode}")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"\n❌ Error running {description}: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Runner for Student Logic Tests")
    parser.add_argument("--individual", action="store_true",
                       help="Run individual student tests")
    parser.add_argument("--student-id", type=int,
                       help="Test specific student ID")
    parser.add_argument("--range", action="store_true",
                       help="Run student range tests")
    parser.add_argument("--start", type=int, default=1,
                       help="Start student ID for range test")
    parser.add_argument("--end", type=int, default=20,
                       help="End student ID for range test")
    parser.add_argument("--all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--examples", action="store_true",
                       help="Run logic examples test")
    parser.add_argument("--verbose", action="store_true",
                       help="Run tests with verbose output")
    parser.add_argument("--slow", action="store_true",
                       help="Include slow tests")
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-vv")
    
    if not args.slow:
        base_cmd.extend(["-m", "not slow"])
    
    success = True
    
    # Run individual student test
    if args.individual:
        if args.student_id:
            cmd = base_cmd + [f"tests/test_individual_student_logic.py::test_student_{args.student_id}"]
            success &= run_command(cmd, f"Individual Student Test (ID: {args.student_id})")
        else:
            cmd = base_cmd + ["tests/test_individual_student_logic.py", "-k", "individual"]
            success &= run_command(cmd, "Individual Student Tests")
    
    # Run range tests
    if args.range:
        if args.start == 1 and args.end == 20:
            cmd = base_cmd + ["tests/test_student_range_logic.py::test_students_1_to_20"]
            success &= run_command(cmd, f"Student Range Test ({args.start}-{args.end})")
        elif args.start == 1 and args.end == 10:
            cmd = base_cmd + ["tests/test_student_range_logic.py::test_students_1_to_10"]
            success &= run_command(cmd, f"Student Range Test ({args.start}-{args.end})")
        else:
            # Run all range tests
            cmd = base_cmd + ["tests/test_student_range_logic.py", "-k", "range"]
            success &= run_command(cmd, f"Student Range Tests")
    
    # Run logic examples
    if args.examples:
        cmd = ["python", "script/api/logic_test_examples.py"]
        success &= run_command(cmd, "Logic Examples Test")
    
    # Run all tests
    if args.all:
        cmd = base_cmd + ["tests/"]
        success &= run_command(cmd, "All Tests")
    
    # If no specific test was requested, show help
    if not any([args.individual, args.range, args.all, args.examples]):
        print("🎯 Student Logic Test Runner")
        print("=" * 40)
        print("Available test options:")
        print("  --individual --student-id 1    Test specific student")
        print("  --range --start 1 --end 20     Test student range")
        print("  --all                          Run all tests")
        print("  --examples                     Run logic examples")
        print("  --verbose                      Verbose output")
        print("  --slow                         Include slow tests")
        print("\nExamples:")
        print("  python tests/test_runner.py --individual --student-id 1")
        print("  python tests/test_runner.py --range --start 1 --end 10")
        print("  python tests/test_runner.py --all --verbose")
        return
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RUNNER SUMMARY")
    print("=" * 60)
    
    if success:
        print("🎉 All requested tests completed successfully!")
    else:
        print("❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
