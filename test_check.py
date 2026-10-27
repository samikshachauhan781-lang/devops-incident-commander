from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("🔍 Testing DevOps Incident Commander API")
print("=" * 50)

# Test 1: Root endpoint
print("\n1. Testing root endpoint (GET /)")
response = client.get("/")
print(f"   Status Code: {response.status_code}")
print(f"   Response: {response.json()}")
print(f"   Success: {response.status_code == 200}")

# Test 2: Health endpoint
print("\n2. Testing health endpoint (GET /health)")
response = client.get("/health")
print(f"   Status Code: {response.status_code}")
print(f"   Response: {response.json()}")
print(f"   Success: {response.status_code == 200}")

# Test 3: Check if response has correct fields
print("\n3. Validating response structure")
root_data = client.get("/").json()
health_data = client.get("/health").json()

required_root_fields = ["project_name", "status", "welcome_message"]
required_health_fields = ["status", "timestamp"]

print(f"   Root fields: {list(root_data.keys())}")
print(f"   Required root fields present: {all(field in root_data for field in required_root_fields)}")

print(f"   Health fields: {list(health_data.keys())}")
print(f"   Required health fields present: {all(field in health_data for field in required_health_fields)}")

print("\n" + "=" * 50)
print("✅ Application checks complete!")
