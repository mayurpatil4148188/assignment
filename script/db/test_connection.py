#!/usr/bin/env python3
"""
Test script to verify DATABASE_URL connection works
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_url():
    """Test DATABASE_URL connection"""
    print("🧪 Testing DATABASE_URL connection...")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Please set: DATABASE_URL=postgresql://postgres:1234@localhost:5432/student_platform_db")
        return False
    
    print(f"✅ DATABASE_URL found: {database_url}")
    
    # Test connection
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        print("✅ Database connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database version: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_reset_script():
    """Test the reset script with DATABASE_URL"""
    print("\n🧪 Testing reset script with DATABASE_URL...")
    
    try:
        from reset_db import get_db_connection
        
        conn = get_db_connection()
        if conn:
            print("✅ Reset script connection successful!")
            conn.close()
            return True
        else:
            print("❌ Reset script connection failed!")
            return False
    except Exception as e:
        print(f"❌ Reset script test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing DATABASE_URL connection...\n")
    
    tests = [
        test_database_url,
        test_reset_script
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DATABASE_URL connection is working correctly.")
        print("\n💡 You can now use:")
        print("   python reset_db.py           # Interactive reset")
        print("   python reset_db.py --force   # Force reset")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
