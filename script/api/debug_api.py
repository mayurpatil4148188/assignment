#!/usr/bin/env python3
"""
Debug script to check API response format
"""

import requests
import json

def test_api_response():
    """Test what the API actually returns"""
    base_url = "http://localhost:5005"
    
    # Test student creation
    student_data = {
        "name": "Test Student",
        "email": "test@example.com",
        "phone": "+1234567890"
    }
    
    print("🧪 Testing API response format...")
    print(f"📤 Sending student data: {student_data}")
    
    try:
        response = requests.post(
            f"{base_url}/api/students/",
            json=student_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 201:
            try:
                response_json = response.json()
                print(f"✅ Parsed JSON: {json.dumps(response_json, indent=2)}")
                print(f"🔑 Available keys: {list(response_json.keys())}")
                
                # Check for the expected response structure
                if response_json.get('success') and 'data' in response_json:
                    student_data = response_json['data']
                    print(f"📊 Student data: {json.dumps(student_data, indent=2)}")
                    print(f"🆔 Student ID: {student_data.get('id')}")
                else:
                    print("⚠️  Response doesn't match expected format (success + data)")
                    
            except Exception as e:
                print(f"❌ Failed to parse JSON: {e}")
        else:
            print(f"❌ API returned error status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_response()
