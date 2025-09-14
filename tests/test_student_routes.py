import pytest
import json
from app import db
from models import Student, Application

class TestStudentRoutes:
    """Test cases for student routes"""
    
    def test_create_student_success(self, client, sample_student_data):
        """Test successful student creation"""
        response = client.post('/api/students/', json=sample_student_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'student' in data
        assert data['student']['name'] == sample_student_data['name']
        assert data['student']['email'] == sample_student_data['email']
        assert data['student']['phone'] == sample_student_data['phone']
        assert data['student']['highest_status'] is None
        assert data['student']['highest_intake'] is None
    
    def test_create_student_missing_data(self, client):
        """Test student creation with missing required fields"""
        response = client.post('/api/students/', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data or 'error' in data
    
    def test_create_student_invalid_email(self, client, sample_student_data):
        """Test student creation with invalid email"""
        sample_student_data['email'] = 'invalid-email'
        response = client.post('/api/students/', json=sample_student_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert any('email' in error.lower() for error in data['errors'])
    
    def test_create_student_duplicate_email(self, client, sample_student_data):
        """Test student creation with duplicate email"""
        # Create first student
        client.post('/api/students/', json=sample_student_data)
        
        # Try to create second student with same email
        response = client.post('/api/students/', json=sample_student_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert any('email' in error.lower() for error in data['errors'])
    
    def test_get_student_success(self, client, created_student):
        """Test successful student retrieval"""
        response = client.get(f"/api/students/{created_student['id']}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'student' in data
        assert data['student']['id'] == created_student['id']
    
    def test_get_student_not_found(self, client):
        """Test student retrieval for non-existent student"""
        response = client.get('/api/students/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_all_students(self, client, created_student):
        """Test getting all students with pagination"""
        response = client.get('/api/students/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'students' in data
        assert 'pagination' in data
        assert len(data['students']) == 1
        assert data['pagination']['total'] == 1
    
    def test_get_all_students_pagination(self, client):
        """Test pagination for students"""
        # Create multiple students
        for i in range(15):
            student_data = {
                'name': f'Student {i}',
                'email': f'student{i}@example.com',
                'phone': f'+123456789{i:02d}'
            }
            client.post('/api/students/', json=student_data)
        
        # Test first page
        response = client.get('/api/students/?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['students']) == 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['has_next'] is True
        
        # Test second page
        response = client.get('/api/students/?page=2&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['students']) == 5
        assert data['pagination']['page'] == 2
        assert data['pagination']['has_next'] is False
    
    def test_update_student_success(self, client, created_student):
        """Test successful student update"""
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com'
        }
        
        response = client.put(f"/api/students/{created_student['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['student']['name'] == update_data['name']
        assert data['student']['email'] == update_data['email']
        assert data['student']['phone'] == created_student['phone']  # Unchanged
    
    def test_update_student_not_found(self, client):
        """Test updating non-existent student"""
        update_data = {'name': 'Updated Name'}
        response = client.put('/api/students/999', json=update_data)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_delete_student_success(self, client, created_student):
        """Test successful student deletion"""
        response = client.delete(f"/api/students/{created_student['id']}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Verify student is deleted
        response = client.get(f"/api/students/{created_student['id']}")
        assert response.status_code == 404
    
    def test_delete_student_not_found(self, client):
        """Test deleting non-existent student"""
        response = client.delete('/api/students/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_student_applications(self, client, created_student, created_application):
        """Test getting applications for a student"""
        response = client.get(f"/api/students/{created_student['id']}/applications")
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data
        assert len(data['applications']) == 1
        assert data['applications'][0]['id'] == created_application['id']
    
    def test_get_student_highest_status(self, client, created_student, created_application):
        """Test getting highest status and intake for a student"""
        response = client.get(f"/api/students/{created_student['id']}/highest-status")
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'highest_status' in data
        assert 'highest_intake' in data
        assert data['highest_status'] == created_application['status']
        assert data['highest_intake'] == created_application['intake']
