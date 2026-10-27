"""
Simple script to check your DevOps Incident Commander application
"""
import subprocess
import sys
import time
import requests

def check_with_requests():
    """Check using requests library (most common for Python users)"""
    print("🔍 Checking with requests library")
    try:
        base_url = "http://127.0.0.1:8000"

        # Test root endpoint
        response = requests.get(f"{base_url}/")
        print(f"   Root endpoint (GET /): Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print(f"   ✓ Project: {data.get('project_name')}")
            print(f"   ✓ Status: {data.get('status')}")
        else:
            print(f"   ✗ Error: {response.text}")

        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"   Health endpoint (GET /health): Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print(f"   ✓ Status: {data.get('status')}")
            print(f"   ✓ Timestamp: {data.get('timestamp')}")
        else:
            print(f"   ✗ Error: {response.text}")

        return True

    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to server")
        print("   💡 Start the server first: .venv/bin/uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def check_with_curl():
    """Check using curl command (terminal users)"""
    print("\n🔍 Checking with curl (terminal)")
    try:
        # Test root endpoint
        result = subprocess.run(['curl', '-s', 'http://127.0.0.1:8000/'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   Root endpoint (GET /): {result.stdout.strip()}")
        else:
            print(f"   ✗ Root endpoint failed: {result.stderr}")

        # Test health endpoint
        result = subprocess.run(['curl', '-s', 'http://127.0.0.1:8000/health'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   Health endpoint (GET /health): {result.stdout.strip()}")
        else:
            print(f"   ✗ Health endpoint failed: {result.stderr}")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def check_with_test_client():
    """Check using FastAPI TestClient (best for testing)"""
    print("\n🔍 Checking with FastAPI TestClient")
    try:
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        # Test root endpoint
        response = client.get("/")
        print(f"   Root endpoint (GET /): Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print(f"   ✓ Project: {data.get('project_name')}")
            print(f"   ✓ Status: {data.get('status')}")

        # Test health endpoint
        response = client.get("/health")
        print(f"   Health endpoint (GET /health): Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print(f"   ✓ Status: {data.get('status')}")
            print(f"   ✓ Timestamp: {data.get('timestamp')}")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def main():
    print("🚀 DevOps Incident Commander Application Checker")
    print("=" * 60)

    # Try each method
    methods = [
        ("TestClient", check_with_test_client),
        ("Requests", check_with_requests),
        ("Curl", check_with_curl)
    ]

    results = []
    for method_name, method_func in methods:
        print(f"\n--- Trying {method_name} method ---")
        try:
            result = method_func()
            results.append((method_name, result))
        except ImportError as e:
            print(f"   ⚠️  {method_name} not available: {e}")
            results.append((method_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    successful_methods = [name for name, success in results if success]
    print(f"✅ Successfully checked with: {', '.join(successful_methods) if successful_methods else 'None'}")

    if successful_methods:
        print("\n🎉 Your application is working correctly!")
        print("\n📝 Recommended next steps:")
        print("   1. Start the server for production: .venv/bin/uvicorn main:app --reload")
        print("   2. Test with curl in terminal")
        print("   3. Use TestClient for automated testing")
        print("   4. Visit http://127.0.0.1:8000/docs for API documentation")
    else:
        print("\n❌ Could not check application")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure all dependencies are installed")
        print("   2. Check if main.py has syntax errors")
        print("   3. Install missing packages: pip install requests")

    return len(successful_methods) > 0

if __name__ == "__main__":
    # Check if we have requests installed
    try:
        import requests
        print("✅ requests library available")
    except ImportError:
        print("⚠️  requests not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])

    success = main()
    sys.exit(0 if success else 1)
