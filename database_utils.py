#!/usr/bin/env python3
"""
Database utility script for managing the Student Platform database
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models import Student, Application

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",  # Connect to default postgres database first
            user="postgres",
            password="1234"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def drop_database():
    """Drop the student_platform_db database if it exists"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Terminate existing connections to the database
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'student_platform_db' AND pid <> pg_backend_pid()
        """)
        
        # Drop the database
        cursor.execute("DROP DATABASE IF EXISTS student_platform_db")
        print("✅ Dropped existing student_platform_db database")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error dropping database: {e}")
        cursor.close()
        conn.close()
        return False

def create_database():
    """Create the student_platform_db database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE student_platform_db")
        print("✅ Created student_platform_db database")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        cursor.close()
        conn.close()
        return False

def create_tables():
    """Create all tables using Flask-SQLAlchemy"""
    try:
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Created all tables successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def reset_database():
    """Reset the entire database (drop, create, and create tables)"""
    print("🔄 Resetting database...")
    
    # Drop existing database
    if not drop_database():
        return False
    
    # Create new database
    if not create_database():
        return False
    
    # Create tables
    if not create_tables():
        return False
    
    print("✅ Database reset completed successfully!")
    return True

def show_tables():
    """Show all tables in the database"""
    try:
        app = create_app()
        with app.app_context():
            # Get table names
            result = db.engine.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in result]
            
            if tables:
                print("📋 Tables in student_platform_db:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("📋 No tables found in student_platform_db")
                
    except Exception as e:
        print(f"❌ Error showing tables: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python database_utils.py <command>")
        print("Commands:")
        print("  reset     - Drop, create database and create tables")
        print("  drop      - Drop the database")
        print("  create    - Create the database")
        print("  tables    - Create tables")
        print("  show      - Show existing tables")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "reset":
        reset_database()
    elif command == "drop":
        drop_database()
    elif command == "create":
        create_database()
    elif command == "tables":
        create_tables()
    elif command == "show":
        show_tables()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
