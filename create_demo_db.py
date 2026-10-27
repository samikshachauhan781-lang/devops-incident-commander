#!/usr/bin/env python3
"""
Create a separate demo database with synthetic incidents for public demo.
Run this once to generate incidents_demo.db
"""
import os
import sqlite3

DEMO_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "incidents_demo.db")

# Demo incident dates: Jul–Aug 2026 (~2–3 months before Oct 2026), not legacy 2024 data.

# Synthetic demo incidents - fictional services, realistic but fake data
DEMO_INCIDENTS = [
    {
        "id": "demo-001-payment-gateway-timeout",
        "title": "Payment Gateway Timeout on Checkout",
        "description": "Customers report checkout failures on the e-commerce platform. Payment provider API returning 504 Gateway Timeout after 30s. Affecting ~15% of transactions. Investigating provider status page and network connectivity.",
        "severity": "high",
        "status": "investigating",
        "service": "payment-gateway",
        "created_at": "2026-08-15T14:30:00.000Z",
        "updated_at": "2026-08-15T14:45:00.000Z",
        "resolved_at": None
    },
    {
        "id": "demo-002-api-latency-spike",
        "title": "API Latency Spike - User Service",
        "description": "P99 latency for /api/users endpoint increased from 200ms to 2.5s over past hour. Database connection pool near exhaustion. Suspected slow query on user_sessions table. Scaling read replicas and investigating query plan.",
        "severity": "medium",
        "status": "open",
        "service": "user-service",
        "created_at": "2026-08-14T09:15:00.000Z",
        "updated_at": "2026-08-14T10:00:00.000Z",
        "resolved_at": None
    },
    {
        "id": "demo-003-cdn-cache-invalidation",
        "title": "CDN Cache Invalidation Failure",
        "description": "New deployment assets not propagating to edge nodes. Users seeing stale JavaScript bundles causing UI errors. Cache purge API returning success but assets not refreshed. Escalated to CDN vendor support.",
        "severity": "medium",
        "status": "open",
        "service": "cdn",
        "created_at": "2026-08-13T16:20:00.000Z",
        "updated_at": "2026-08-13T17:00:00.000Z",
        "resolved_at": None
    },
    {
        "id": "demo-004-database-deadlock",
        "title": "Database Deadlock on Order Processing",
        "description": "Deadlock detected in PostgreSQL during high-volume order processing. Transaction serialization failures causing order creation retries. Reviewing isolation levels and lock ordering in inventory reservation logic.",
        "severity": "critical",
        "status": "investigating",
        "service": "order-service",
        "created_at": "2026-08-12T22:10:00.000Z",
        "updated_at": "2026-08-12T22:30:00.000Z",
        "resolved_at": None
    },
    {
        "id": "demo-005-auth-token-expiry",
        "title": "Auth Token Expiry Clock Skew",
        "description": "Intermittent 401 Unauthorized errors for valid sessions. NTP drift detected on auth service nodes causing JWT exp claim validation failures. Chrony sync restored, monitoring for recurrence.",
        "severity": "low",
        "status": "resolved",
        "service": "auth-service",
        "created_at": "2026-08-10T08:00:00.000Z",
        "updated_at": "2026-08-10T09:30:00.000Z",
        "resolved_at": "2026-08-10T09:30:00.000Z"
    },
    {
        "id": "demo-006-queue-backlog",
        "title": "Message Queue Backlog - Notification Worker",
        "description": "Notification delivery queue depth exceeded 50k messages. Worker pool autoscaling maxed out. Email provider rate limiting compounding backlog. Implemented priority queue for critical alerts.",
        "severity": "high",
        "status": "resolved",
        "service": "notification-service",
        "created_at": "2026-08-09T13:45:00.000Z",
        "updated_at": "2026-08-09T16:20:00.000Z",
        "resolved_at": "2026-08-09T16:20:00.000Z"
    },
    {
        "id": "demo-007-search-index-corruption",
        "title": "Search Index Corruption - Product Catalog",
        "description": "Elasticsearch cluster reporting corrupted shards on product-catalog index. Search returning incomplete results. Restoring from snapshot taken 2026-08-08T06:00:00Z. Estimated recovery 2 hours.",
        "severity": "critical",
        "status": "investigating",
        "service": "search-service",
        "created_at": "2026-08-08T11:00:00.000Z",
        "updated_at": "2026-08-08T11:15:00.000Z",
        "resolved_at": None
    },
    {
        "id": "demo-008-ssl-cert-expiry",
        "title": "SSL Certificate Near Expiry - Partner API",
        "description": "Monitoring alert: Partner integration TLS certificate expires in 7 days. Certificate auto-renewal failed due to DNS validation challenge. Manual renewal initiated via Let's Encrypt. No user impact yet.",
        "severity": "low",
        "status": "open",
        "service": "partner-api",
        "created_at": "2026-08-07T10:00:00.000Z",
        "updated_at": "2026-08-07T10:00:00.000Z",
        "resolved_at": None
    },
    {
        "id": "demo-009-memory-leak",
        "title": "Memory Leak in Real-time Analytics Worker",
        "description": "Analytics ingestion worker RSS growing 50MB/hour. Heap dump shows accumulating WebSocket connection objects not being released. Hotfix deployed with connection cleanup. Monitoring memory stability.",
        "severity": "medium",
        "status": "resolved",
        "service": "analytics-worker",
        "created_at": "2026-07-30T18:30:00.000Z",
        "updated_at": "2026-07-30T20:00:00.000Z",
        "resolved_at": "2026-07-30T20:00:00.000Z"
    },
    {
        "id": "demo-010-config-drift",
        "title": "Config Drift - Feature Flag Service",
        "description": "Feature flag evaluation returning stale values in us-east-1 region. Config sync from control plane delayed by 15min due to network partition. Forced config refresh resolved inconsistency. Adding health check for sync lag.",
        "severity": "medium",
        "status": "resolved",
        "service": "feature-flags",
        "created_at": "2026-07-28T12:00:00.000Z",
        "updated_at": "2026-07-28T12:45:00.000Z",
        "resolved_at": "2026-07-28T12:45:00.000Z"
    }
]

DEMO_EVENTS = [
    # Events for demo-001
    {
        "id": "evt-demo-001-01",
        "incident_id": "demo-001-payment-gateway-timeout",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Payment Gateway Timeout on Checkout", "severity": "high", "status": "investigating", "service": "payment-gateway", "description": "Customers report checkout failures..."}',
        "created_at": "2026-08-15T14:30:00.000Z"
    },
    {
        "id": "evt-demo-001-02",
        "incident_id": "demo-001-payment-gateway-timeout",
        "event_type": "incident_updated",
        "description": "Incident details updated",
        "old_values": '{"status": "open"}',
        "new_values": '{"status": "investigating"}',
        "created_at": "2026-08-15T14:45:00.000Z"
    },
    # Events for demo-002
    {
        "id": "evt-demo-002-01",
        "incident_id": "demo-002-api-latency-spike",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "API Latency Spike - User Service", "severity": "medium", "status": "open", "service": "user-service", "description": "P99 latency for /api/users endpoint increased..."}',
        "created_at": "2026-08-14T09:15:00.000Z"
    },
    # Events for demo-004
    {
        "id": "evt-demo-004-01",
        "incident_id": "demo-004-database-deadlock",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Database Deadlock on Order Processing", "severity": "critical", "status": "investigating", "service": "order-service", "description": "Deadlock detected in PostgreSQL..."}',
        "created_at": "2026-08-12T22:10:00.000Z"
    },
    # Events for demo-005 (resolved)
    {
        "id": "evt-demo-005-01",
        "incident_id": "demo-005-auth-token-expiry",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Auth Token Expiry Clock Skew", "severity": "low", "status": "open", "service": "auth-service", "description": "Intermittent 401 Unauthorized errors..."}',
        "created_at": "2026-08-10T08:00:00.000Z"
    },
    {
        "id": "evt-demo-005-02",
        "incident_id": "demo-005-auth-token-expiry",
        "event_type": "incident_status_changed",
        "description": "Incident status changed",
        "old_values": '{"status": "investigating"}',
        "new_values": '{"status": "resolved"}',
        "created_at": "2026-08-10T09:30:00.000Z"
    },
    {
        "id": "evt-demo-005-03",
        "incident_id": "demo-005-auth-token-expiry",
        "event_type": "incident_resolved",
        "description": "Incident resolved",
        "old_values": '{"status": "investigating"}',
        "new_values": '{"status": "resolved", "resolved_at": "2026-08-10T09:30:00.000Z"}',
        "created_at": "2026-08-10T09:30:00.000Z"
    },
    # Events for demo-006
    {
        "id": "evt-demo-006-01",
        "incident_id": "demo-006-queue-backlog",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Message Queue Backlog - Notification Worker", "severity": "high", "status": "open", "service": "notification-service", "description": "Notification delivery queue depth exceeded 50k messages..."}',
        "created_at": "2026-08-09T13:45:00.000Z"
    },
    {
        "id": "evt-demo-006-02",
        "incident_id": "demo-006-queue-backlog",
        "event_type": "incident_status_changed",
        "description": "Incident status changed",
        "old_values": '{"status": "investigating"}',
        "new_values": '{"status": "resolved"}',
        "created_at": "2026-08-09T16:20:00.000Z"
    },
    # Events for demo-007
    {
        "id": "evt-demo-007-01",
        "incident_id": "demo-007-search-index-corruption",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Search Index Corruption - Product Catalog", "severity": "critical", "status": "investigating", "service": "search-service", "description": "Elasticsearch cluster reporting corrupted shards..."}',
        "created_at": "2026-08-08T11:00:00.000Z"
    },
    # Events for demo-009
    {
        "id": "evt-demo-009-01",
        "incident_id": "demo-009-memory-leak",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Memory Leak in Real-time Analytics Worker", "severity": "medium", "status": "open", "service": "analytics-worker", "description": "Analytics ingestion worker RSS growing 50MB/hour..."}',
        "created_at": "2026-07-30T18:30:00.000Z"
    },
    {
        "id": "evt-demo-009-02",
        "incident_id": "demo-009-memory-leak",
        "event_type": "incident_status_changed",
        "description": "Incident status changed",
        "old_values": '{"status": "investigating"}',
        "new_values": '{"status": "resolved"}',
        "created_at": "2026-07-30T20:00:00.000Z"
    },
    # Events for demo-010
    {
        "id": "evt-demo-010-01",
        "incident_id": "demo-010-config-drift",
        "event_type": "incident_created",
        "description": "Incident created",
        "old_values": None,
        "new_values": '{"title": "Config Drift - Feature Flag Service", "severity": "medium", "status": "open", "service": "feature-flags", "description": "Feature flag evaluation returning stale values..."}',
        "created_at": "2026-07-28T12:00:00.000Z"
    },
    {
        "id": "evt-demo-010-02",
        "incident_id": "demo-010-config-drift",
        "event_type": "incident_status_changed",
        "description": "Incident status changed",
        "old_values": '{"status": "investigating"}',
        "new_values": '{"status": "resolved"}',
        "created_at": "2026-07-28T12:45:00.000Z"
    }
]

def create_demo_database():
    """Create demo database with synthetic data"""
    conn = sqlite3.connect(DEMO_DB_PATH)
    cursor = conn.cursor()

    # Create tables (same schema as production)
    cursor.execute("""
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
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_events (
            id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            old_values TEXT,
            new_values TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_incident_events_incident_id ON incident_events(incident_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_incident_events_created_at ON incident_events(created_at)
    """)

    cursor.execute("DELETE FROM incident_events")
    cursor.execute("DELETE FROM incidents")

    # Insert demo incidents
    for inc in DEMO_INCIDENTS:
        cursor.execute("""
            INSERT INTO incidents (id, title, description, severity, status, service, created_at, updated_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inc["id"], inc["title"], inc["description"], inc["severity"],
            inc["status"], inc["service"], inc["created_at"], inc["updated_at"], inc["resolved_at"]
        ))

    # Insert demo events
    for evt in DEMO_EVENTS:
        cursor.execute("""
            INSERT INTO incident_events (id, incident_id, event_type, description, old_values, new_values, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            evt["id"], evt["incident_id"], evt["event_type"], evt["description"],
            evt["old_values"], evt["new_values"], evt["created_at"]
        ))

    conn.commit()
    conn.close()

    # Verify
    conn = sqlite3.connect(DEMO_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM incidents")
    inc_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM incident_events")
    evt_count = cursor.fetchone()[0]
    cursor.execute("SELECT id, title, severity, status, service FROM incidents")
    for row in cursor.fetchall():
        print(f"  {row}")
    conn.close()

    print(f"\n✅ Demo database created: {DEMO_DB_PATH}")
    print(f"   Incidents: {inc_count}")
    print(f"   Events: {evt_count}")

if __name__ == "__main__":
    create_demo_database()
