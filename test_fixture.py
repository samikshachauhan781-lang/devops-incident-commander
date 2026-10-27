"""Test to verify fixture activation"""
from fastapi.testclient import TestClient
from main import app

def test_simple():
    print('\n🔍 Testing fixture activation')
    client = TestClient(app)
    response = client.get('/health')
    print('   Status:', response.status_code)
    print('   Response:', response.json())
    assert response.status_code == 200
    print('   ✅ Health check passed')

if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '-s'])