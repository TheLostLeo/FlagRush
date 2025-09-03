"""
Simple test script to verify API functionality
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health Check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = requests.post(f'{BASE_URL}/auth/register', json=data)
        print(f"Registration: {response.status_code} - {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Registration failed: {e}")
        return False

def test_user_login():
    """Test user login and return token"""
    try:
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"Login: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            return response.json()['data']['access_token']
        return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_admin_login():
    """Test admin login"""
    try:
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"Admin Login: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            return response.json()['data']['access_token']
        return None
    except Exception as e:
        print(f"Admin login failed: {e}")
        return None

def test_get_challenges(token):
    """Test getting challenges"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{BASE_URL}/challenges/', headers=headers)
        print(f"Get Challenges: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Get challenges failed: {e}")
        return False

def test_create_team(token):
    """Test team creation"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'name': 'Test Team',
            'description': 'A test team for API testing'
        }
        response = requests.post(f'{BASE_URL}/teams/', json=data, headers=headers)
        print(f"Create Team: {response.status_code} - {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Create team failed: {e}")
        return False

def test_submit_flag(token):
    """Test flag submission"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'challenge_id': 1,
            'flag': 'CTF{welcome_to_the_competition}'
        }
        response = requests.post(f'{BASE_URL}/submissions/', json=data, headers=headers)
        print(f"Submit Flag: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Submit flag failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("=== CTF Backend API Tests ===\n")
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    print("✅ Health check passed\n")
    
    # Test user registration
    if test_user_registration():
        print("✅ User registration passed")
    else:
        print("❌ User registration failed")
    
    # Test user login
    token = test_user_login()
    if token:
        print("✅ User login passed")
    else:
        print("❌ User login failed")
        return
    
    # Test admin login
    admin_token = test_admin_login()
    if admin_token:
        print("✅ Admin login passed")
    else:
        print("❌ Admin login failed")
    
    # Test getting challenges
    if test_get_challenges(token):
        print("✅ Get challenges passed")
    else:
        print("❌ Get challenges failed")
    
    # Test team creation
    if test_create_team(token):
        print("✅ Team creation passed")
    else:
        print("❌ Team creation failed")
    
    # Test flag submission
    if test_submit_flag(token):
        print("✅ Flag submission passed")
    else:
        print("❌ Flag submission failed")
    
    print("\n=== Tests completed ===")

if __name__ == '__main__':
    run_tests()
