import pytest
import json
from app import db
from models import Student, Application

class TestApplicationRoutes:
    """Test cases for application routes"""
    
    def test_create_application_success(self, client, created_student, sample_application_data):
        """Test successful application creation"""
        application_data = {**sample_application_data, 'student_id': created_student['id']}
        response = client.post('/api/applications/', json=application_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'application' in data
        assert data['application']['university_name'] == sample_application_data['university_name']
        assert data['application']['program_name'] == sample_application_data['program_name']
        assert data['application']['intake'] == sample_application_data['intake']
        assert data['application']['status'] == sample_application_data['status']
        assert data['application']['student_id'] == created_student['id']
    
    def test_create_application_missing_data(self, client, created_student):
        """Test application creation with missing required fields"""
        response = client.post('/api/applications/', json={'student_id': created_student['id']})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
    
    def test_create_application_invalid_status(self, client, created_student, sample_application_data):
        """Test application creation with invalid status"""
        sample_application_data['status'] = 'Invalid Status'
        application_data = {**sample_application_data, 'student_id': created_student['id']}
        response = client.post('/api/applications/', json=application_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert any('status' in error.lower() for error in data['errors'])
    
    def test_create_application_invalid_intake(self, client, created_student, sample_application_data):
        """Test application creation with invalid intake format"""
        sample_application_data['intake'] = 'Invalid Intake'
        application_data = {**sample_application_data, 'student_id': created_student['id']}
        response = client.post('/api/applications/', json=application_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert any('intake' in error.lower() for error in data['errors'])
    
    def test_create_application_nonexistent_student(self, client, sample_application_data):
        """Test application creation for non-existent student"""
        application_data = {**sample_application_data, 'student_id': 999}
        response = client.post('/api/applications/', json=application_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert any('not found' in error.lower() for error in data['errors'])
    
    def test_get_application_success(self, client, created_application):
        """Test successful application retrieval"""
        response = client.get(f"/api/applications/{created_application['id']}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'application' in data
        assert data['application']['id'] == created_application['id']
    
    def test_get_application_not_found(self, client):
        """Test application retrieval for non-existent application"""
        response = client.get('/api/applications/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_all_applications(self, client, created_application):
        """Test getting all applications with pagination"""
        response = client.get('/api/applications/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data
        assert 'pagination' in data
        assert len(data['applications']) == 1
        assert data['pagination']['total'] == 1
    
    def test_update_application_success(self, client, created_application):
        """Test successful application update"""
        update_data = {
            'status': 'Offer Received',
            'university_name': 'Updated University'
        }
        
        response = client.put(f"/api/applications/{created_application['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['application']['status'] == update_data['status']
        assert data['application']['university_name'] == update_data['university_name']
    
    def test_update_application_not_found(self, client):
        """Test updating non-existent application"""
        update_data = {'status': 'Offer Received'}
        response = client.put('/api/applications/999', json=update_data)
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_delete_application_success(self, client, created_application):
        """Test successful application deletion"""
        response = client.delete(f"/api/applications/{created_application['id']}")
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Verify application is deleted
        response = client.get(f"/api/applications/{created_application['id']}")
        assert response.status_code == 404
    
    def test_delete_application_not_found(self, client):
        """Test deleting non-existent application"""
        response = client.delete('/api/applications/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_get_status_hierarchy(self, client):
        """Test getting status hierarchy"""
        response = client.get('/api/applications/status-hierarchy')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'status_hierarchy' in data
        assert 'valid_statuses' in data
        assert len(data['valid_statuses']) == 6
        assert 'Visa Approved' in data['valid_statuses']
        assert 'Building Application' in data['valid_statuses']
