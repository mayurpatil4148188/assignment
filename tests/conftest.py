import pytest
import os
import sys
from app import create_app, db
from models import Student, Application

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def sample_student_data():
    """Sample student data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890'
    }

@pytest.fixture(scope='function')
def sample_application_data():
    """Sample application data for testing."""
    return {
        'university_name': 'Harvard University',
        'program_name': 'Computer Science',
        'intake': 'Jan 2026',
        'status': 'Building Application'
    }

@pytest.fixture(scope='function')
def created_student(client, sample_student_data):
    """Create a student for testing."""
    response = client.post('/api/students/', json=sample_student_data)
    assert response.status_code == 201
    return response.get_json()['student']

@pytest.fixture(scope='function')
def created_application(client, created_student, sample_application_data):
    """Create an application for testing."""
    application_data = {**sample_application_data, 'student_id': created_student['id']}
    response = client.post('/api/applications/', json=application_data)
    assert response.status_code == 201
    return response.get_json()['application']
