import requests
import json
import time
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_get_karma_profile():
    """Test the GET /karma/{user_id} endpoint"""
    print("Testing GET /karma/{user_id} endpoint...")
    
    # Test with a sample user ID
    user_id = "test_user_001"
    url = f"{BASE_URL}/karma/{user_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_log_action():
    """Test the POST /log-action/ endpoint"""
    print("\nTesting POST /log-action/ endpoint...")
    
    url = f"{BASE_URL}/log-action/"
    
    # Test data
    payload = {
        "user_id": "test_user_001",
        "action": "completing_lessons",
        "role": "learner",
        "intensity": 1.5,
        "context": "Completed Python programming lesson",
        "metadata": {
            "lesson_id": "py101",
            "duration_minutes": 45
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_submit_atonement():
    """Test the POST /submit-atonement/ endpoint"""
    print("\nTesting POST /submit-atonement/ endpoint...")
    
    url = f"{BASE_URL}/submit-atonement/"
    
    # Test data (this would need a real plan_id to work)
    payload = {
        "user_id": "test_user_001",
        "plan_id": "plan_001",
        "atonement_type": "Jap",
        "amount": 108,
        "proof_text": "Completed 108 repetitions of Om Mani Padme Hum"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_invalid_user():
    """Test error handling for invalid user"""
    print("\nTesting error handling for invalid user...")
    
    user_id = "invalid_user_999"
    url = f"{BASE_URL}/karma/{user_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print("Correctly handled invalid user with 404 error")
            print(f"Error message: {response.text}")
            return True
        else:
            print(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_rnanubandhan_network():
    """Test the GET /rnanubandhan/{user_id} endpoint"""
    print("\nTesting GET /rnanubandhan/{user_id} endpoint...")
    
    # Test with a sample user ID
    user_id = "test_user_001"
    url = f"{BASE_URL}/rnanubandhan/{user_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_create_rnanubandhan_debt():
    """Test the POST /rnanubandhan/create-debt endpoint"""
    print("\nTesting POST /rnanubandhan/create-debt endpoint...")
    
    url = f"{BASE_URL}/rnanubandhan/create-debt"
    
    # Test data
    payload = {
        "debtor_id": "test_user_001",
        "receiver_id": "test_user_002",
        "action_type": "help_action",
        "severity": "minor",
        "amount": 10.0,
        "description": "Provided assistance with project"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_agami_prediction():
    """Test the POST /agami/predict endpoint"""
    print("\nTesting POST /agami/predict endpoint...")
    
    url = f"{BASE_URL}/agami/predict"
    
    # Test data
    payload = {
        "user_id": "test_user_001",
        "scenario": {
            "context": {
                "environment": "gurukul",
                "role": "student",
                "goal": "learning"
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_get_agami_prediction():
    """Test the GET /agami/user/{user_id} endpoint"""
    print("\nTesting GET /agami/user/{user_id} endpoint...")
    
    # Test with a sample user ID
    user_id = "test_user_001"
    url = f"{BASE_URL}/agami/user/{user_id}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    print("Running Karma Tracker API Tests")
    print("=" * 40)
    
    # Note: These tests require the server to be running
    print("Make sure the KarmaChain server is running at http://localhost:8000")
    print("Press Ctrl+C to skip and continue with other tests\n")
    
    try:
        # Test each endpoint
        tests = [
            test_get_karma_profile,
            test_log_action,
            test_submit_atonement,
            test_invalid_user,
            test_rnanubandhan_network,
            test_create_rnanubandhan_debt,
            test_agami_prediction,
            test_get_agami_prediction
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                time.sleep(1)  # Small delay between tests
            except KeyboardInterrupt:
                print("Skipping test due to user interruption...")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 40)
        print("TEST SUMMARY")
        print("=" * 40)
        passed = sum(results)
        total = len(results)
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed or were skipped.")
            
    except Exception as e:
        print(f"Error running tests: {e}")