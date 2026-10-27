#!/usr/bin/env python3
"""
Test suite for DEMO_MODE protections.
Run with: DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db python3 test_demo_mode.py

NOTE: This test file is designed to run as a standalone script, NOT under pytest.
The conftest.py fixture overrides the database path, which breaks demo mode tests.
To run: DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db python3 test_demo_mode.py
"""
import os
os.environ['DEMO_MODE'] = 'true'
os.environ['DEMO_DB_PATH'] = 'incidents_demo.db'

# Skip this module when running under pytest
import pytest
pytestmark = pytest.mark.skip(reason="Demo mode tests must run as standalone script: DEMO_MODE=true DEMO_DB_PATH=incidents_demo.db python3 test_demo_mode.py")

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_demo_mode_enabled():
    """Verify demo mode is active"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['demo_mode'] == True, "Demo mode should be enabled"
    assert data['database'] == 'incidents_demo.db', "Should use demo database"
    print("✅ Demo mode enabled and using demo database")

def test_original_database_untouched():
    """Verify original database has 1137+ incidents, demo has 10"""
    import sqlite3

    # Check original
    conn = sqlite3.connect('incidents.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM incidents')
    orig_count = cursor.fetchone()[0]
    conn.close()

    # Check demo
    conn = sqlite3.connect('incidents_demo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM incidents')
    demo_count = cursor.fetchone()[0]
    conn.close()

    assert demo_count == 10, f"Demo DB should have 10 incidents, has {demo_count}"
    assert orig_count >= 1137, f"Original DB should have 1137+ incidents, has {orig_count}"
    print(f"✅ Original DB preserved ({orig_count} incidents), Demo DB has {demo_count} synthetic incidents")

def test_get_incidents_works():
    """GET /incidents should return demo data"""
    response = client.get('/incidents')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 10, f"Should have 10 demo incidents, got {data['total']}"
    print("✅ GET /incidents returns demo data")

def test_get_single_incident_works():
    """GET /incidents/{id} should work for demo incidents"""
    response = client.get('/incidents/demo-001-payment-gateway-timeout')
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Payment Gateway Timeout on Checkout'
    print("✅ GET /incidents/{id} works for demo incidents")

def test_post_incidents_blocked():
    """POST /incidents should be blocked with 403"""
    response = client.post('/incidents', json={
        'title': 'Test', 'description': 'Test description',
        'severity': 'low', 'status': 'open', 'service': 'test'
    })
    assert response.status_code == 403
    assert 'read-only' in response.json()['detail'].lower()
    print("✅ POST /incidents blocked with 403")

def test_patch_incident_blocked():
    """PATCH /incidents/{id} should be blocked with 403"""
    response = client.patch('/incidents/demo-001-payment-gateway-timeout', json={'status': 'resolved'})
    assert response.status_code == 403
    assert 'read-only' in response.json()['detail'].lower()
    print("✅ PATCH /incidents/{id} blocked with 403")

def test_delete_incident_blocked():
    """DELETE /incidents/{id} should be blocked with 403"""
    response = client.delete('/incidents/demo-001-payment-gateway-timeout')
    assert response.status_code == 403
    assert 'read-only' in response.json()['detail'].lower()
    print("✅ DELETE /incidents/{id} blocked with 403")

def test_docs_disabled():
    """GET /docs should be blocked with 403"""
    response = client.get('/docs')
    assert response.status_code == 403
    assert 'documentation' in response.json()['detail'].lower()
    print("✅ /docs disabled with 403")

def test_redoc_disabled():
    """GET /redoc should be blocked with 403"""
    response = client.get('/redoc')
    assert response.status_code == 403
    assert 'documentation' in response.json()['detail'].lower()
    print("✅ /redoc disabled with 403")

def test_openapi_json_disabled():
    """GET /openapi.json should be blocked with 403"""
    response = client.get('/openapi.json')
    assert response.status_code == 403
    assert 'documentation' in response.json()['detail'].lower()
    print("✅ /openapi.json disabled with 403")

def test_investigation_returns_mock():
    """POST /incidents/{id}/investigate should return mock data, not call AI"""
    response = client.post('/incidents/demo-001-payment-gateway-timeout/investigate', json={})
    assert response.status_code == 200
    data = response.json()
    assert data.get('demo_mode') == True
    assert data.get('ai_analysis', {}).get('metadata', {}).get('provider') == 'mock'
    assert 'mock' in data.get('ai_analysis', {}).get('reasoning', '').lower()
    assert len(data.get('ai_analysis', {}).get('hypotheses', [])) > 0
    print("✅ Investigation returns mock data (no external AI calls)")

def test_analytics_works():
    """Analytics endpoints should work with demo data"""
    response = client.get('/analytics/overview')
    assert response.status_code == 200
    data = response.json()
    assert data['total_incidents'] == 10
    print("✅ Analytics overview works with demo data")

def test_severity_breakdown_works():
    """Severity breakdown should work with demo data"""
    response = client.get('/analytics/severity')
    assert response.status_code == 200
    data = response.json()
    breakdown = data['severity_breakdown']
    total = sum(item['count'] for item in breakdown)
    assert total == 10
    print("✅ Severity breakdown works with demo data")

def test_status_breakdown_works():
    """Status breakdown should work with demo data"""
    response = client.get('/analytics/status')
    assert response.status_code == 200
    data = response.json()
    breakdown = data['status_breakdown']
    total = sum(item['count'] for item in breakdown)
    assert total == 10
    print("✅ Status breakdown works with demo data")

def test_timeline_works():
    """Timeline endpoint should work for demo incidents"""
    response = client.get('/incidents/demo-001-payment-gateway-timeout/timeline')
    assert response.status_code == 200
    data = response.json()
    assert data['incident_id'] == 'demo-001-payment-gateway-timeout'
    assert len(data['events']) >= 1
    print("✅ Timeline works with demo data")

def test_filtering_works():
    """Filtering should work on demo data"""
    # Filter by service
    response = client.get('/incidents?service=payment-gateway')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 1
    assert data['incidents'][0]['service'] == 'payment-gateway'

    # Filter by severity
    response = client.get('/incidents?severity=critical')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 2
    for inc in data['incidents']:
        assert inc['severity'] == 'critical'

    # Filter by status
    response = client.get('/incidents?status=resolved')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 4
    for inc in data['incidents']:
        assert inc['status'] == 'resolved'

    print("✅ Filtering works on demo data")

def test_search_works():
    """Search should work on demo data"""
    response = client.get('/incidents?search=payment')
    assert response.status_code == 200
    data = response.json()
    assert data['total'] >= 1
    print("✅ Search works on demo data")

def test_pagination_works():
    """Pagination should work on demo data"""
    response = client.get('/incidents?page=1&page_size=5')
    assert response.status_code == 200
    data = response.json()
    assert len(data['incidents']) == 5
    assert data['page'] == 1
    assert data['page_size'] == 5
    assert data['has_more'] == True

    response = client.get('/incidents?page=2&page_size=5')
    assert response.status_code == 200
    data = response.json()
    assert len(data['incidents']) == 5
    assert data['has_more'] == False
    print("✅ Pagination works on demo data")

def test_sorting_works():
    """Sorting should work on demo data"""
    response = client.get('/incidents?sort_by=title&order=asc')
    assert response.status_code == 200
    data = response.json()
    titles = [inc['title'] for inc in data['incidents']]
    assert titles == sorted(titles)
    print("✅ Sorting works on demo data")

if __name__ == '__main__':
    print("=" * 60)
    print("DEMO MODE PROTECTION TESTS")
    print("=" * 60)

    test_demo_mode_enabled()
    test_original_database_untouched()
    test_get_incidents_works()
    test_get_single_incident_works()
    test_post_incidents_blocked()
    test_patch_incident_blocked()
    test_delete_incident_blocked()
    test_docs_disabled()
    test_redoc_disabled()
    test_openapi_json_disabled()
    test_investigation_returns_mock()
    test_analytics_works()
    test_severity_breakdown_works()
    test_status_breakdown_works()
    test_timeline_works()
    test_filtering_works()
    test_search_works()
    test_pagination_works()
    test_sorting_works()

    print("=" * 60)
    print("✅ ALL DEMO MODE TESTS PASSED")
    print("=" * 60)