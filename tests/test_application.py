import pytest
from app import create_app
from app.extensions import db
from app.student.models import Student
from app.application.models import Application

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def sample_student_data():
    """Sample student data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890'
    }

@pytest.fixture
def sample_application_data():
    """Sample application data for testing."""
    return {
        'student_id': 1,
        'university_name': 'Harvard University',
        'program_name': 'Computer Science',
        'intake': 'Jan 2026',
        'status': 'Building Application'
    }

class TestApplicationAPI:
    """Test cases for Application API endpoints."""
    
    def test_create_application_success(self, client, app, sample_student_data, sample_application_data):
        """Test successful application creation."""
        with app.app_context():
            # Create a student first
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
        
        application_data = sample_application_data.copy()
        application_data['student_id'] = student_id
        
        response = client.post('/api/applications/', json=application_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['university_name'] == application_data['university_name']
        assert data['data']['program_name'] == application_data['program_name']
        assert data['data']['status'] == application_data['status']
    
    def test_create_application_validation_error(self, client):
        """Test application creation with validation errors."""
        invalid_data = {
            'student_id': 1,
            'university_name': '',  # Empty university name
            'program_name': '',  # Empty program name
            'intake': 'invalid-intake',  # Invalid intake format
            'status': 'Invalid Status'  # Invalid status
        }
        
        response = client.post('/api/applications/', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert 'errors' in data
    
    def test_create_application_student_not_found(self, client, sample_application_data):
        """Test creating application for non-existent student."""
        application_data = sample_application_data.copy()
        application_data['student_id'] = 999  # Non-existent student
        
        response = client.post('/api/applications/', json=application_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert 'Student not found' in data['errors'][0]
    
    def test_get_applications_pagination(self, client, app, sample_student_data, sample_application_data):
        """Test getting applications with pagination."""
        with app.app_context():
            # Create a student
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create test applications
            for i in range(15):
                app_data = sample_application_data.copy()
                app_data['student_id'] = student_id
                app_data['university_name'] = f'University {i}'
                application = Application(**app_data)
                db.session.add(application)
            db.session.commit()
        
        # Test first page
        response = client.get('/api/applications/?page=1&per_page=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10
        assert data['pagination']['total'] == 15
    
    def test_get_application_by_id(self, client, app, sample_student_data, sample_application_data):
        """Test getting a specific application by ID."""
        with app.app_context():
            # Create a student
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create an application
            app_data = sample_application_data.copy()
            app_data['student_id'] = student_id
            application = Application(**app_data)
            db.session.add(application)
            db.session.commit()
            application_id = application.id
        
        response = client.get(f'/api/applications/{application_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == application_id
        assert data['data']['university_name'] == sample_application_data['university_name']
    
    def test_get_application_not_found(self, client):
        """Test getting a non-existent application."""
        response = client.get('/api/applications/999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_application(self, client, app, sample_student_data, sample_application_data):
        """Test updating an application."""
        with app.app_context():
            # Create a student
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create an application
            app_data = sample_application_data.copy()
            app_data['student_id'] = student_id
            application = Application(**app_data)
            db.session.add(application)
            db.session.commit()
            application_id = application.id
        
        update_data = {
            'university_name': 'MIT',
            'status': 'Offer Received'
        }
        
        response = client.put(f'/api/applications/{application_id}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['university_name'] == update_data['university_name']
        assert data['data']['status'] == update_data['status']
    
    def test_delete_application(self, client, app, sample_student_data, sample_application_data):
        """Test deleting an application."""
        with app.app_context():
            # Create a student
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create an application
            app_data = sample_application_data.copy()
            app_data['student_id'] = student_id
            application = Application(**app_data)
            db.session.add(application)
            db.session.commit()
            application_id = application.id
        
        response = client.delete(f'/api/applications/{application_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        
        # Verify application is deleted
        response = client.get(f'/api/applications/{application_id}')
        assert response.status_code == 404
    
    def test_get_status_hierarchy(self, client):
        """Test getting status hierarchy information."""
        response = client.get('/api/applications/status-hierarchy')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'status_hierarchy' in data['data']
        assert 'valid_statuses' in data['data']
        
        # Check that all expected statuses are present
        expected_statuses = [
            'Building Application',
            'Application Submitted to University',
            'Offer Received',
            'Offer Accepted by Student',
            'Visa Approved',
            'Dropped'
        ]
        
        for status in expected_statuses:
            assert status in data['data']['valid_statuses']
            assert status in data['data']['status_hierarchy']
    
    def test_application_status_hierarchy_weights(self, client, app, sample_student_data, sample_application_data):
        """Test that application status hierarchy weights are correct."""
        with app.app_context():
            # Create a student
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create applications with different statuses
            statuses = [
                'Building Application',
                'Application Submitted to University',
                'Offer Received',
                'Offer Accepted by Student',
                'Visa Approved',
                'Dropped'
            ]
            
            for i, status in enumerate(statuses):
                app_data = sample_application_data.copy()
                app_data['student_id'] = student_id
                app_data['university_name'] = f'University {i}'
                app_data['status'] = status
                application = Application(**app_data)
                db.session.add(application)
            db.session.commit()
        
        # Test that Visa Approved has the highest weight
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['highest_status'] == 'Visa Approved'
