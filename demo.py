#!/usr/bin/env python3
"""
Demo script to showcase the Student Platform API functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5005"

def make_request(method, endpoint, data=None):
    """Make HTTP request and return response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {url}")
        print("Make sure the Flask server is running: python app.py")
        return None

def demo_api():
    """Demonstrate the Student Platform API"""
    print("🚀 Student Platform API Demo")
    print("=" * 50)
    
    # 1. Health Check
    print("\n1. Health Check")
    response = make_request("GET", "/api/health/")
    if response and response.status_code == 200:
        data = response.json()
        print("✅ API is healthy")
        print(f"   Status: {data.get('data', {}).get('status', 'unknown')}")
        print(f"   Database: {data.get('data', {}).get('database', 'unknown')}")
    else:
        print("❌ API health check failed")
        return
    
    # 2. Create a Student
    print("\n2. Creating a Student")
    student_data = {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+1234567890"
    }
    response = make_request("POST", "/api/students/", student_data)
    if response and response.status_code == 201:
        data = response.json()
        student = data["data"]
        student_id = student["id"]
        print(f"✅ Student created: {student['name']} (ID: {student_id})")
    else:
        print("❌ Failed to create student")
        return
    
    # 3. Create Applications
    print("\n3. Creating Applications")
    applications_data = [
        {
            "student_id": student_id,
            "university_name": "MIT",
            "program_name": "Computer Science",
            "intake": "Sep 2026",
            "status": "Building Application"
        },
        {
            "student_id": student_id,
            "university_name": "Stanford University",
            "program_name": "Data Science",
            "intake": "Jan 2026",
            "status": "Offer Received"
        },
        {
            "student_id": student_id,
            "university_name": "Harvard University",
            "program_name": "Artificial Intelligence",
            "intake": "Mar 2026",
            "status": "Visa Approved"
        }
    ]
    
    application_ids = []
    for i, app_data in enumerate(applications_data, 1):
        response = make_request("POST", "/api/applications/", app_data)
        if response and response.status_code == 201:
            data = response.json()
            application = data["data"]
            application_ids.append(application["id"])
            print(f"✅ Application {i} created: {app_data['university_name']} - {app_data['status']}")
        else:
            print(f"❌ Failed to create application {i}")
    
    # 4. Check Highest Status
    print("\n4. Checking Highest Status")
    response = make_request("GET", f"/api/students/{student_id}/highest-status")
    if response and response.status_code == 200:
        data = response.json()
        highest_status = data["data"]
        print(f"✅ Highest Status: {highest_status['highest_status']}")
        print(f"   Highest Intake: {highest_status['highest_intake']}")
    else:
        print("❌ Failed to get highest status")
    
    # 5. Update Application Status
    print("\n5. Updating Application Status")
    if application_ids:
        update_data = {"status": "Offer Accepted by Student"}
        response = make_request("PUT", f"/api/applications/{application_ids[0]}", update_data)
        if response and response.status_code == 200:
            print(f"✅ Application {application_ids[0]} updated to: Offer Accepted by Student")
        else:
            print("❌ Failed to update application")
    
    # 6. Check Updated Highest Status
    print("\n6. Checking Updated Highest Status")
    response = make_request("GET", f"/api/students/{student_id}/highest-status")
    if response and response.status_code == 200:
        highest_status = response.json()
        print(f"✅ Updated Highest Status: {highest_status['highest_status']}")
        print(f"   Updated Highest Intake: {highest_status['highest_intake']}")
    else:
        print("❌ Failed to get updated highest status")
    
    # 7. Get Student Applications
    print("\n7. Getting Student Applications")
    response = make_request("GET", f"/api/students/{student_id}/applications")
    if response and response.status_code == 200:
        applications = response.json()["applications"]
        print(f"✅ Found {len(applications)} applications:")
        for app in applications:
            print(f"   - {app['university_name']}: {app['status']} ({app['intake']})")
    else:
        print("❌ Failed to get student applications")
    
    # 8. Get Status Hierarchy
    print("\n8. Getting Status Hierarchy")
    response = make_request("GET", "/api/applications/status-hierarchy")
    if response and response.status_code == 200:
        hierarchy = response.json()["status_hierarchy"]
        print("✅ Status Hierarchy (weight: status):")
        for status, weight in sorted(hierarchy.items(), key=lambda x: x[1], reverse=True):
            print(f"   {weight}: {status}")
    else:
        print("❌ Failed to get status hierarchy")
    
    print("\n🎉 Demo completed successfully!")
    print("\nTo test more endpoints, use the Postman collection:")
    print("   Student_Platform_API.postman_collection.json")

if __name__ == "__main__":
    demo_api()
