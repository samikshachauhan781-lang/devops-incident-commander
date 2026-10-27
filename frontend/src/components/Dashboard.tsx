// Dashboard — command center overview
import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useIncidentContext } from '../contexts/IncidentContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { MetricCard } from './ui/MetricCard';
import { PageHeader } from './ui/PageHeader';
import { useIncidentService } from '../hooks/useIncidentService';
import { AnalyticsResponse, Incident } from '../types/api';
import { usePageTitle } from '../layouts/MainLayout';
import { useToast } from '../hooks/useToast';
import { apiGet } from '../api/client';
import {
  AlertTriangle,
  TrendingUp,
  Clock,
  CheckCircle,
  Activity,
  RefreshCw,
  ArrowRight,
  Sparkles,
  Database,
  Server,
} from 'lucide-react';
import { capitalizeLabel, formatIncidentDate, severityBadgeClass, statusBadgeClass } from '../lib/incidentUi';

type HealthResponse = {
  status: string;
  demo_mode?: boolean;
  database?: string;
};

export default function Dashboard() {
  const [recentIncidents, setRecentIncidents] = useState<Incident[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getIncidents, getAnalytics } = useIncidentService();
  const { setPageTitle } = usePageTitle();
  const { toast } = useToast();
  const navigate = useNavigate();
  const { selectIncident } = useIncidentContext();

  useEffect(() => {
    setPageTitle('Dashboard', 'Operational overview and incident posture', [
      { label: 'Dashboard', href: '/' },
    ]);
  }, [setPageTitle]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [analyticsData, incidentsResponse, healthData] = await Promise.all([
        getAnalytics(),
        getIncidents({ page_size: 8, sort_by: 'created_at', order: 'desc' }),
        apiGet<HealthResponse>('/health'),
      ]);

      setAnalytics(analyticsData);
      setRecentIncidents(incidentsResponse.incidents);
      setHealth(healthData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const overview = analytics?.overview;

  const activityFeed = useMemo(
    () =>
      recentIncidents.slice(0, 5).map((incident) => ({
        id: incident.id,
        title: incident.title,
        meta: `${incident.service} · ${capitalizeLabel(incident.status)}`,
        time: formatIncidentDate(incident.updated_at || incident.created_at),
        severity: incident.severity,
      })),
    [recentIncidents]
  );

  let content: React.ReactNode;

  if (loading) {
    content = (
      <div className="loading-container">
        <div className="loading-spinner h-12 w-12" role="status" aria-label="Loading dashboard" />
      </div>
    );
  } else if (error) {
    content = (
      <Card className="error-state">
        <CardContent className="error-state-content">
          <AlertTriangle className="error-state-icon" />
          <div>
            <h3 className="error-state-title">Error loading dashboard</h3>
            <p className="error-state-text">{error}</p>
            <Button onClick={loadDashboardData} variant="outline" size="sm" className="mt-3">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  } else {
    content = (
    <div className="page-stack">
      <PageHeader
        title="Dashboard"
        description="Real-time incident posture across your services"
        actions={
          <Button onClick={loadDashboardData} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        }
      />

      {overview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 lg:gap-5">
          <MetricCard
            label="Total incidents"
            value={overview.total_incidents}
            hint="All records in the current dataset"
            icon={AlertTriangle}
          />
          <MetricCard
            label="Critical"
            value={overview.critical_incidents}
            hint="Requires immediate attention"
            icon={TrendingUp}
            tone="critical"
          />
          <MetricCard
            label="Investigating"
            value={overview.investigating_incidents}
            hint="Active investigations in progress"
            icon={Clock}
            tone="info"
          />
          <MetricCard
            label="Resolved"
            value={overview.resolved_incidents}
            hint={`${overview.resolution_rate_percent}% resolution rate`}
            icon={CheckCircle}
            tone="success"
          />
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 lg:gap-6">
        <div className="xl:col-span-8">
          <Card className="panel-card h-full">
            <CardHeader className="panel-card-header">
              <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
                <div>
                  <CardTitle>Recent incidents</CardTitle>
                  <CardDescription>Newest reports sorted by creation time</CardDescription>
                </div>
                <Button variant="ghost" size="sm" className="text-indigo-600" onClick={() => navigate('/incidents')}>
                  View all
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="panel-card-body pt-0">
              {recentIncidents.length === 0 ? (
                <div className="empty-state">
                  <AlertTriangle className="empty-state-icon" />
                  <h3 className="empty-state-title">No incidents yet</h3>
                  <p className="empty-state-text">Incidents from the API will appear here automatically.</p>
                </div>
              ) : (
                <ul className="incident-feed" role="list">
                  {recentIncidents.map((incident) => (
                    <li key={incident.id}>
                      <button
                        type="button"
                        className="incident-feed-item"
                        onClick={() => {
                          selectIncident(incident);
                          navigate(`/incidents/${incident.id}`);
                        }}
                      >
                        <div className="incident-feed-main">
                          <p className="incident-feed-title">{incident.title}</p>
                          <p className="incident-feed-desc">{incident.description}</p>
                          <div className="incident-feed-badges">
                            <Badge className={severityBadgeClass(incident.severity)} variant="outline">
                              {capitalizeLabel(incident.severity)}
                            </Badge>
                            <Badge className={statusBadgeClass(incident.status)} variant="outline">
                              {capitalizeLabel(incident.status)}
                            </Badge>
                          </div>
                        </div>
                        <div className="incident-feed-meta">
                          <span className="incident-feed-service">{incident.service}</span>
                          <time className="incident-feed-time" dateTime={incident.created_at}>
                            {formatIncidentDate(incident.created_at)}
                          </time>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="xl:col-span-4 space-y-5">
          <Card className="panel-card">
            <CardHeader className="panel-card-header compact">
              <CardTitle className="text-base">Quick actions</CardTitle>
            </CardHeader>
            <CardContent className="panel-card-body space-y-2">
              <Button
                className="w-full justify-start action-tile"
                variant="outline"
                onClick={() =>
                  toast({
                    title: 'Read-only demo',
                    description: 'Incident creation is disabled in the read-only demo.',
                  })
                }
              >
                <Activity className="h-4 w-4 mr-2 text-indigo-600" />
                Create incident
              </Button>
              <Button className="w-full justify-start action-tile" variant="outline" onClick={() => navigate('/analytics')}>
                <TrendingUp className="h-4 w-4 mr-2 text-indigo-600" />
                View analytics
              </Button>
              <Button
                className="w-full justify-start action-tile"
                variant="outline"
                onClick={() => navigate('/timeline')}
              >
                <Clock className="h-4 w-4 mr-2 text-indigo-600" />
                Open timeline
              </Button>
            </CardContent>
          </Card>

          <Card className="panel-card">
            <CardHeader className="panel-card-header compact">
              <CardTitle className="text-base">Platform health</CardTitle>
            </CardHeader>
            <CardContent className="panel-card-body space-y-3">
              <div className="health-row">
                <div className="health-row-label">
                  <Server className="h-4 w-4" />
                  <span>API</span>
                </div>
                <Badge variant="success">{health?.status === 'healthy' ? 'Healthy' : health?.status || 'Unknown'}</Badge>
              </div>
              <div className="health-row">
                <div className="health-row-label">
                  <Database className="h-4 w-4" />
                  <span>Database</span>
                </div>
                <Badge variant="success">Connected</Badge>
              </div>
              {health?.demo_mode && (
                <div className="health-row">
                  <div className="health-row-label">
                    <Sparkles className="h-4 w-4" />
                    <span>Mode</span>
                  </div>
                  <Badge variant="secondary">Read-only demo</Badge>
                </div>
              )}
              {health?.database && (
                <p className="text-xs text-slate-500 pt-1 border-t border-slate-100">
                  Source: <span className="font-mono text-slate-600">{health.database}</span>
                </p>
              )}
            </CardContent>
          </Card>

          <Card className="panel-card">
            <CardHeader className="panel-card-header compact">
              <CardTitle className="text-base">Latest activity</CardTitle>
              <CardDescription>From your most recent incidents</CardDescription>
            </CardHeader>
            <CardContent className="panel-card-body">
              {activityFeed.length === 0 ? (
                <p className="text-sm text-slate-500">No recent activity.</p>
              ) : (
                <ul className="activity-feed" role="list">
                  {activityFeed.map((item) => (
                    <li key={item.id} className="activity-feed-item">
                      <span
                        className={`activity-dot ${
                          item.severity === 'critical'
                            ? 'activity-dot-critical'
                            : item.severity === 'high'
                              ? 'activity-dot-high'
                              : 'activity-dot-default'
                        }`}
                        aria-hidden="true"
                      />
                      <div className="min-w-0">
                        <p className="activity-feed-title">{item.title}</p>
                        <p className="activity-feed-meta">{item.meta}</p>
                        <p className="activity-feed-time">{item.time}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
    );
  }

  return content;
}
