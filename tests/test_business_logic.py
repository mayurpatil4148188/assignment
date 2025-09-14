import pytest
import json
from app import db
from models import Student, Application
from services.student_service import StudentService
from services.application_service import ApplicationService

class TestBusinessLogic:
    """Test cases for business logic (status hierarchy and intake calculations)"""
    
    def test_status_hierarchy_calculation(self, client, created_student):
        """Test that highest status is calculated correctly based on hierarchy"""
        student_id = created_student['id']
        
        # Create applications with different statuses
        applications_data = [
            {
                'student_id': student_id,
                'university_name': 'University A',
                'program_name': 'Program A',
                'intake': 'Jan 2026',
                'status': 'Building Application'
            },
            {
                'student_id': student_id,
                'university_name': 'University B',
                'program_name': 'Program B',
                'intake': 'Feb 2026',
                'status': 'Offer Received'
            },
            {
                'student_id': student_id,
                'university_name': 'University C',
                'program_name': 'Program C',
                'intake': 'Mar 2026',
                'status': 'Visa Approved'
            }
        ]
        
        # Create all applications
        for app_data in applications_data:
            response = client.post('/api/applications/', json=app_data)
            assert response.status_code == 201
        
        # Check highest status
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should be 'Visa Approved' (highest weight)
        assert data['highest_status'] == 'Visa Approved'
        assert data['highest_intake'] == 'Mar 2026'
    
    def test_same_status_closest_intake(self, client, created_student):
        """Test that when statuses are equal, closest intake is chosen"""
        student_id = created_student['id']
        
        # Create applications with same status but different intakes
        applications_data = [
            {
                'student_id': student_id,
                'university_name': 'University A',
                'program_name': 'Program A',
                'intake': 'Sep 2026',
                'status': 'Offer Received'
            },
            {
                'student_id': student_id,
                'university_name': 'University B',
                'program_name': 'Program B',
                'intake': 'Jan 2026',
                'status': 'Offer Received'
            }
        ]
        
        # Create all applications
        for app_data in applications_data:
            response = client.post('/api/applications/', json=app_data)
            assert response.status_code == 201
        
        # Check highest status
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should be 'Offer Received' with 'Jan 2026' (closest intake)
        assert data['highest_status'] == 'Offer Received'
        assert data['highest_intake'] == 'Jan 2026'
    
    def test_status_update_recalculation(self, client, created_student, created_application):
        """Test that updating application status recalculates student's highest status"""
        student_id = created_student['id']
        application_id = created_application['id']
        
        # Initially should have the created application's status
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        initial_data = response.get_json()
        assert initial_data['highest_status'] == created_application['status']
        
        # Update application to higher status
        update_data = {'status': 'Visa Approved'}
        response = client.put(f'/api/applications/{application_id}', json=update_data)
        assert response.status_code == 200
        
        # Check that highest status is updated
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        updated_data = response.get_json()
        assert updated_data['highest_status'] == 'Visa Approved'
        assert updated_data['highest_intake'] == created_application['intake']
    
    def test_application_deletion_recalculation(self, client, created_student):
        """Test that deleting application recalculates student's highest status"""
        student_id = created_student['id']
        
        # Create multiple applications
        applications_data = [
            {
                'student_id': student_id,
                'university_name': 'University A',
                'program_name': 'Program A',
                'intake': 'Jan 2026',
                'status': 'Building Application'
            },
            {
                'student_id': student_id,
                'university_name': 'University B',
                'program_name': 'Program B',
                'intake': 'Feb 2026',
                'status': 'Visa Approved'
            }
        ]
        
        application_ids = []
        for app_data in applications_data:
            response = client.post('/api/applications/', json=app_data)
            assert response.status_code == 201
            application_ids.append(response.get_json()['application']['id'])
        
        # Check highest status
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['highest_status'] == 'Visa Approved'
        
        # Delete the application with highest status
        response = client.delete(f'/api/applications/{application_ids[1]}')
        assert response.status_code == 200
        
        # Check that highest status is recalculated
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        updated_data = response.get_json()
        assert updated_data['highest_status'] == 'Building Application'
        assert updated_data['highest_intake'] == 'Jan 2026'
    
    def test_no_applications_highest_status_none(self, client, created_student):
        """Test that student with no applications has None highest status"""
        student_id = created_student['id']
        
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['highest_status'] is None
        assert data['highest_intake'] is None
    
    def test_dropped_status_lowest_priority(self, client, created_student):
        """Test that 'Dropped' status has lowest priority"""
        student_id = created_student['id']
        
        # Create applications with different statuses including 'Dropped'
        applications_data = [
            {
                'student_id': student_id,
                'university_name': 'University A',
                'program_name': 'Program A',
                'intake': 'Jan 2026',
                'status': 'Dropped'
            },
            {
                'student_id': student_id,
                'university_name': 'University B',
                'program_name': 'Program B',
                'intake': 'Feb 2026',
                'status': 'Building Application'
            }
        ]
        
        # Create all applications
        for app_data in applications_data:
            response = client.post('/api/applications/', json=app_data)
            assert response.status_code == 201
        
        # Check highest status
        response = client.get(f'/api/students/{student_id}/highest-status')
        assert response.status_code == 200
        data = response.get_json()
        
        # Should be 'Building Application' (not 'Dropped')
        assert data['highest_status'] == 'Building Application'
        assert data['highest_intake'] == 'Feb 2026'
    
    def test_all_status_hierarchy_weights(self, client, created_student):
        """Test all status hierarchy weights are correct"""
        student_id = created_student['id']
        
        # Test each status in order of hierarchy
        statuses = [
            'Building Application',
            'Application Submitted to University',
            'Offer Received',
            'Offer Accepted by Student',
            'Visa Approved'
        ]
        
        for i, status in enumerate(statuses):
            # Create application with current status
            app_data = {
                'student_id': student_id,
                'university_name': f'University {i}',
                'program_name': f'Program {i}',
                'intake': f'Jan 2026',
                'status': status
            }
            
            response = client.post('/api/applications/', json=app_data)
            assert response.status_code == 201
            
            # Check highest status
            response = client.get(f'/api/students/{student_id}/highest-status')
            assert response.status_code == 200
            data = response.get_json()
            
            # Should be the current status (highest so far)
            assert data['highest_status'] == status
            assert data['highest_intake'] == 'Jan 2026'
