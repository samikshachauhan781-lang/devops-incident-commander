"""
Pytest configuration for DevOps Incident Commander test suite.

This file provides fixtures for test database isolation and FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from models import set_test_database_path, clear_test_database_path
import os
import sqlite3
import json
from datetime import datetime, timezone

@pytest.fixture
def test_client():
    """Provide a FastAPI TestClient for testing."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def function_test_isolation(request):
    """
    Fixture that runs before and after each test function.

    Ensures complete test database isolation by:
    1. Setting up a fresh test database path
    2. Creating database tables
    3. Cleaning up after test completion

    This is critical because models.py has a global _db_path pointing to
    the real incidents.db. We need to override this for tests.
    """
    # Setup: Create fresh test database path
    # Use test name from request fixture for unique database files
    test_name = request.node.originalname or request.node.name
    test_db_path = f"/tmp/test_incidents_{hash(test_name)}.db"

    set_test_database_path(test_db_path)

    # Initialize with empty database
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create tables matching the actual database schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            service TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            resolved_at TEXT
        )
    ''')

    # Create incident_events table (matching actual schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incident_events (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            old_values TEXT,
            new_values TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE NO ACTION
        )
    ''')

    # Create indexes for efficient querying
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_incident_events_incident_id ON incident_events(incident_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_incident_events_created_at ON incident_events(created_at)
    ''')

    # Clear existing data (ensures test isolation)
    cursor.execute('DELETE FROM incidents')
    cursor.execute('DELETE FROM incident_events')

    conn.commit()
    conn.close()

    # Yield control to the actual test
    yield

    # Teardown: Clean up test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Reset test database override
    clear_test_database_path()

# Session fixture for tests that need session-level setup
@pytest.fixture(autouse=False)
def session_test_database():
    """
    Session-scoped fixture for tests that need shared database state.

    This fixture runs once per test session and can be used by multiple tests
    that want to share database state. Most tests should use function_test_isolation
    for complete isolation.
    """
    # We don't use session fixtures for now to maintain isolation
    yield
    # Cleanup handled by function_test_isolation for most tests

# Sample incidents data fixture for tests that need it
def sample_incidents_data():
    """Return sample incident data for tests that need it."""
    return [
        {'title': 'Test Incident 1', 'description': 'Description for incident 1', 'severity': 'critical', 'status': 'open', 'service': 'api'},
        {'title': 'Test Incident 2', 'description': 'Description for incident 2', 'severity': 'high', 'status': 'investigating', 'service': 'auth'},
        {'title': 'Test Incident 3', 'description': 'Description for incident 3', 'severity': 'medium', 'status': 'resolved', 'service': 'payments'},
        {'title': 'Test Incident 4', 'description': 'Description for incident 4', 'severity': 'low', 'status': 'closed', 'service': 'api'},
        {'title': 'API Rate Limit Exceeded', 'description': 'Service Unavailable due to rate limits', 'severity': 'critical', 'status': 'open', 'service': 'api'}
    ]

# Make sample_incidents_data available as a fixture for compatibility
def sample_incidents_data_fixture():
    """Fixture version of sample_incidents_data."""
    return sample_incidents_data()