"""
Database Reset Script for Student Platform API

This script connects to PostgreSQL database and deletes all records from tables.
It safely handles foreign key constraints by deleting applications first, then students.

Usage:
    python reset_db.py
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection using DATABASE_URL or individual environment variables"""
    try:
        # Try to use DATABASE_URL first (standard approach)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print(f"🔗 Connecting using DATABASE_URL...")
            conn = psycopg2.connect(database_url)
        else:
            # Fallback to individual environment variables
            print(f"🔗 Connecting using individual environment variables...")
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'student_platform_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '1234')
            )
        
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print(f"   Make sure DATABASE_URL is set or individual DB variables are configured")
        return None

def get_table_counts(cursor):
    """Get current record counts from tables"""
    try:
        cursor.execute("SELECT COUNT(*) FROM applications")
        app_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        return student_count, app_count
    except Exception as e:
        print(f"❌ Error getting table counts: {e}")
        return 0, 0

def reset_db(force=False):
    """
    Reset database by deleting all records from tables
    
    Args:
        force (bool): If True, skip confirmation prompt
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    print("🗄️  Student Platform API - Database Reset")
    print("=" * 40)
    
    # Get database connection
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get current statistics
        student_count, app_count = get_table_counts(cursor)
        total_records = student_count + app_count
        
        print(f"📊 Current Database Statistics:")
        print(f"   Students: {student_count}")
        print(f"   Applications: {app_count}")
        print(f"   Total Records: {total_records}")
        
        if total_records == 0:
            print("\n✅ Database is already empty. No action needed.")
            return True
        
        # Confirmation prompt (unless forced)
        if not force:
            print(f"\n⚠️  WARNING: This will permanently delete ALL data!")
            print(f"   - {app_count} applications will be deleted")
            print(f"   - {student_count} students will be deleted")
            print(f"   - This action cannot be undone")
            
            while True:
                response = input("\nAre you sure you want to proceed? (yes/no): ").lower().strip()
                if response in ['yes', 'y']:
                    break
                elif response in ['no', 'n']:
                    print("❌ Database reset cancelled by user")
                    return False
                else:
                    print("Please enter 'yes' or 'no'")
        
        print(f"\n🗑️  Resetting database...")
        
        # Delete applications first (due to foreign key constraints)
        print(f"   Deleting {app_count} applications...")
        cursor.execute("DELETE FROM applications")
        deleted_apps = cursor.rowcount
        print(f"   ✅ Deleted {deleted_apps} applications")
        
        # Delete students
        print(f"   Deleting {student_count} students...")
        cursor.execute("DELETE FROM students")
        deleted_students = cursor.rowcount
        print(f"   ✅ Deleted {deleted_students} students")
        
        # Commit transaction
        conn.commit()
        
        print(f"\n🎉 Database reset completed successfully!")
        print(f"   - Deleted {deleted_apps} applications")
        print(f"   - Deleted {deleted_students} students")
        print(f"   - Total records deleted: {deleted_apps + deleted_students}")
        
        # Verify reset
        final_student_count, final_app_count = get_table_counts(cursor)
        if final_student_count == 0 and final_app_count == 0:
            print("   ✅ Database is now empty")
        else:
            print(f"   ⚠️  Warning: {final_student_count + final_app_count} records still remain")
        
        return True
        
    except Exception as e:
        # Rollback on error
        conn.rollback()
        print(f"\n❌ Error resetting database: {e}")
        print("   Transaction rolled back - no changes made")
        return False
        
    finally:
        # Always close connections
        if 'cursor' in locals():
            cursor.close()
        if conn:
            conn.close()

def main():
    """Main function for command line usage"""
    import sys
    
    # Check for force flag
    force = '--force' in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("🗄️  Database Reset Script")
        print("=" * 25)
        print()
        print("Usage:")
        print("  python reset_db.py           # Interactive reset with confirmation")
        print("  python reset_db.py --force   # Force reset without confirmation")
        print("  python reset_db.py --help    # Show this help")
        print()
        print("Database Connection:")
        print("  Uses DATABASE_URL environment variable:")
        print("  DATABASE_URL=postgresql://postgres:1234@localhost:5432/student_platform_db")
        print()
        print("  Or individual environment variables:")
        print("  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        print()
        print("This script safely deletes all records from:")
        print("  - applications table")
        print("  - students table")
        print()
        print("Safety features:")
        print("  - Confirmation prompt (unless --force)")
        print("  - Proper foreign key handling")
        print("  - Transaction rollback on errors")
        print("  - Statistics before and after reset")
        return
    
    # Run reset
    success = reset_db(force=force)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()