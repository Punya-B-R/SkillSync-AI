"""
Simple test script for API endpoints.
Run this after starting the Flask server.
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test root health check endpoint."""
    print("\n1. Testing GET / (Health Check)...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"   Error: Cannot connect to server. Is Flask running on {BASE_URL}?")
        print(f"   Make sure to run: python app.py in the backend folder")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_api_health():
    """Test API health endpoint."""
    print("\n2. Testing GET /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 503]  # 503 is OK if API key not set
    except requests.exceptions.ConnectionError:
        print(f"   Error: Cannot connect to server. Is Flask running on {BASE_URL}?")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_analyze_resume():
    """Test analyze resume endpoint."""
    print("\n3. Testing POST /api/analyze-resume...")
    try:
        test_resume = """
        John Doe
        Software Engineer
        5 years of experience
        
        Skills: Python, JavaScript, React, Node.js, AWS
        Experience: Senior Developer at Tech Corp (2020-2024)
        Education: BS Computer Science
        """
        
        payload = {
            "resume_text": test_resume
        }
        
        response = requests.post(
            f"{BASE_URL}/api/analyze-resume",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # AI calls can take time
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            profile = result.get('profile', {})
            print(f"   Skills found: {len(profile.get('skills', []))}")
            print(f"   Experience level: {profile.get('experience_level', 'N/A')}")
        else:
            print(f"   Error: {result.get('message', 'Unknown error')}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"   Error: Cannot connect to server. Is Flask running?")
        return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_recommend_domains():
    """Test recommend domains endpoint."""
    print("\n4. Testing POST /api/recommend-domains...")
    try:
        payload = {
            "profile": {
                "skills": ["Python", "JavaScript", "React"],
                "experience_level": "Mid-Level",
                "years_of_experience": 3,
                "domains": ["Web Development"]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/recommend-domains",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            recommendations = result.get('recommendations', [])
            print(f"   Recommendations: {len(recommendations)}")
        else:
            print(f"   Error: {result.get('message', 'Unknown error')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_chat():
    """Test chat endpoint."""
    print("\n5. Testing POST /api/chat...")
    try:
        payload = {
            "message": "What is the best way to learn React?",
            "context": {
                "profile": {
                    "skills": ["JavaScript"],
                    "experience_level": "Junior"
                }
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Success: {result.get('success', False)}")
        if result.get('success'):
            response_text = result.get('response', '')
            print(f"   Response length: {len(response_text)} characters")
            print(f"   Response preview: {response_text[:100]}...")
        else:
            print(f"   Error: {result.get('message', 'Unknown error')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   Error: {e}")
        return False

def check_server_running():
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return True
    except:
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("API Endpoint Tests")
    print("=" * 60)
    
    # Check if server is running first
    print("\nChecking if server is running...")
    if not check_server_running():
        print("\n❌ ERROR: Flask server is not running!")
        print(f"   Please start the server first:")
        print(f"   1. Open a terminal")
        print(f"   2. cd backend")
        print(f"   3. python app.py")
        print(f"\n   Then run this test script again.")
        return
    
    print("✓ Server is running!")
    print("\nStarting tests...")
    time.sleep(1)  # Small delay
    
    results = []
    results.append(("Health Check (/)", test_health_check()))
    results.append(("API Health", test_api_health()))
    results.append(("Analyze Resume", test_analyze_resume()))
    results.append(("Recommend Domains", test_recommend_domains()))
    results.append(("Chat", test_chat()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {passed_count}/{len(results)} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    main()

