#!/usr/bin/env python3
"""
Script to create .env file from template
"""

import os
import shutil

def create_env_file():
    """Create .env file from template"""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted. .env file not created.")
            return
    
    # Copy template to .env
    if os.path.exists('env_template.txt'):
        shutil.copy('env_template.txt', '.env')
        print("✅ .env file created successfully!")
        print("📝 Please review and update the values in .env file as needed.")
        print("🔧 Key settings to check:")
        print("   - DATABASE_URL: postgresql://postgres:1234@localhost:5432/student_platform_db")
        print("   - SECRET_KEY: Change to a secure random string")
        print("   - PORT: 5005 (or your preferred port)")
    else:
        print("❌ env_template.txt not found!")
        print("Creating basic .env file...")
        
        # Create basic .env file
        env_content = """# Flask Application Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Application Settings
APP_NAME=Student Platform API
APP_VERSION=1.0.0
SECRET_KEY=your-secret-key-change-in-production-12345

# Database Configuration
DATABASE_URL=postgresql://postgres:1234@localhost:5432/student_platform_db

# Server Configuration
HOST=0.0.0.0
PORT=5005

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# CORS Configuration
CORS_ORIGINS=*

# Pagination Defaults
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Basic .env file created successfully!")

if __name__ == "__main__":
    create_env_file()
