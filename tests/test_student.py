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

class TestStudentAPI:
    """Test cases for Student API endpoints."""
    
    def test_create_student_success(self, client, sample_student_data):
        """Test successful student creation."""
        response = client.post('/api/students/', json=sample_student_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == sample_student_data['name']
        assert data['data']['email'] == sample_student_data['email']
        assert data['data']['phone'] == sample_student_data['phone']
    
    def test_create_student_validation_error(self, client):
        """Test student creation with validation errors."""
        invalid_data = {
            'name': '',  # Empty name
            'email': 'invalid-email',  # Invalid email
            'phone': '123'  # Invalid phone
        }
        
        response = client.post('/api/students/', json=invalid_data)
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert 'errors' in data
    
    def test_get_students_pagination(self, client, app, sample_student_data):
        """Test getting students with pagination."""
        with app.app_context():
            # Create test students
            for i in range(15):
                student_data = sample_student_data.copy()
                student_data['email'] = f'student{i}@example.com'
                student = Student(**student_data)
                db.session.add(student)
            db.session.commit()
        
        # Test first page
        response = client.get('/api/students/?page=1&per_page=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['per_page'] == 10
        assert data['pagination']['total'] == 15
    
    def test_get_student_by_id(self, client, app, sample_student_data):
        """Test getting a specific student by ID."""
        with app.app_context():
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
        
        response = client.get(f'/api/students/{student_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == student_id
        assert data['data']['name'] == sample_student_data['name']
    
    def test_get_student_not_found(self, client):
        """Test getting a non-existent student."""
        response = client.get('/api/students/999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_student(self, client, app, sample_student_data):
        """Test updating a student."""
        with app.app_context():
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
        
        update_data = {
            'name': 'Jane Doe',
            'email': 'jane.doe@example.com'
        }
        
        response = client.put(f'/api/students/{student_id}', json=update_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['name'] == update_data['name']
        assert data['data']['email'] == update_data['email']
    
    def test_delete_student(self, client, app, sample_student_data):
        """Test deleting a student."""
        with app.app_context():
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
        
        response = client.delete(f'/api/students/{student_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        
        # Verify student is deleted
        response = client.get(f'/api/students/{student_id}')
        assert response.status_code == 404
    
    def test_get_student_applications(self, client, app, sample_student_data, sample_application_data):
        """Test getting applications for a student."""
        with app.app_context():
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create applications
            for i in range(3):
                app_data = sample_application_data.copy()
                app_data['student_id'] = student_id
                app_data['university_name'] = f'University {i}'
                application = Application(**app_data)
                db.session.add(application)
            db.session.commit()
        
        response = client.get(f'/api/students/{student_id}/applications')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
    
    def test_get_student_highest_status(self, client, app, sample_student_data, sample_application_data):
        """Test getting student's highest status and intake."""
        with app.app_context():
            student = Student(**sample_student_data)
            db.session.add(student)
            db.session.commit()
            student_id = student.id
            
            # Create applications with different statuses
            applications_data = [
                {**sample_application_data, 'student_id': student_id, 'status': 'Building Application', 'intake': 'Jan 2026'},
                {**sample_application_data, 'student_id': student_id, 'status': 'Offer Received', 'intake': 'Feb 2026'},
                {**sample_application_data, 'student_id': student_id, 'status': 'Visa Approved', 'intake': 'Mar 2026'}
            ]
            
            for app_data in applications_data:
                application = Application(**app_data)
                db.session.add(application)
            db.session.commit()
        
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['highest_status'] == 'Visa Approved'
        assert data['data']['highest_intake'] == 'Mar 2026'
