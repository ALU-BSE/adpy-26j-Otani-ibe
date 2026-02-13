import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_session_login_throttle():
    print("=" * 60)
    print("TESTING SESSION LOGIN THROTTLE (5 attempts/minute)")
    print("=" * 60)
    
    for i in range(1, 8):  # Try 7 times
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login/session/",
            json={"username": "wrong", "password": "wrong"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n[{timestamp}] Attempt {i}:")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        if response.status_code == 429:
            print(f"\n SUCCESS! Throttle triggered on attempt {i}")
            print(f"  Retry-After: {response.headers.get('Retry-After', 'Not provided')} seconds")
            print(f"  X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit', 'Not provided')}")
            break
        elif i >= 6:
            print(f"\n FAILED! Should have been throttled by attempt 6")
            break
        
        time.sleep(0.5)  # Small delay between attempts
    
    print("\n" + "=" * 60)

def test_jwt_token_throttle():
    """Test JWT token endpoint throttling"""
    print("\nTESTING JWT TOKEN THROTTLE (5 attempts/minute)")
    print("=" * 60)
    
    for i in range(1, 8):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        response = requests.post(
            f"{BASE_URL}/api/auth/token/obtain/",
            json={"username": "wrong", "password": "wrong"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n[{timestamp}] Attempt {i}:")
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 429:
            print(f" Throttled! Response: {response.json()}")
            break
        elif response.status_code == 401:
            print(f"  Response: {response.json()}")
        
        time.sleep(0.5)
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_session_login_throttle()
    print("\n\nWaiting 65 seconds to let throttle reset...")
    time.sleep(65)
    test_jwt_token_throttle()