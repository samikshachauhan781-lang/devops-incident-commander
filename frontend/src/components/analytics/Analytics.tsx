// Analytics component for DevOps Incident Commander
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { useIncidentService } from '../../hooks/useIncidentService';
import { AnalyticsResponse, IncidentResponse } from '../../types/api';
import { usePageTitle } from '../../layouts/MainLayout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import { TrendingUp, Users, AlertTriangle, Activity, Clock } from 'lucide-react';
import { MetricCard } from '../ui/MetricCard';
import { PageHeader } from '../ui/PageHeader';
import { useChartTheme } from '../../hooks/useChartTheme';

export default function Analytics() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [recentIncidents, setRecentIncidents] = useState<IncidentResponse[]>([]);
  const [timeRange, setTimeRange] = useState('7d');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { getAnalytics, getIncidents } = useIncidentService();
  const { setPageTitle } = usePageTitle();
  const chartTheme = useChartTheme();

  useEffect(() => {
    setPageTitle('Analytics', 'Incident analytics and trends', [
      { label: 'Analytics', href: '/analytics' },
    ]);
  }, [setPageTitle]);

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const rangeDays = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365;
      const createdAfter = new Date(Date.now() - rangeDays * 24 * 60 * 60 * 1000).toISOString();
      const [data, incidents] = await Promise.all([
        getAnalytics(),
        getIncidents({ page: 1, page_size: 100, created_after: createdAfter, sort_by: 'created_at', order: 'desc' }),
      ]);
      setAnalytics(data);
      setRecentIncidents(incidents.incidents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for charts
  const severityData = analytics ? [
    { name: 'Critical', value: analytics.severity_breakdown.critical, color: '#dc2626' },
    { name: 'High', value: analytics.severity_breakdown.high, color: '#ea580c' },
    { name: 'Medium', value: analytics.severity_breakdown.medium, color: '#ca8a04' },
    { name: 'Low', value: analytics.severity_breakdown.low, color: '#16a34a' },
  ] : [];

  const statusData = analytics ? [
    { name: 'Open', value: analytics.status_breakdown.open, color: '#dc2626' },
    { name: 'Investigating', value: analytics.status_breakdown.investigating, color: '#2563eb' },
    { name: 'Resolved', value: analytics.status_breakdown.resolved, color: '#16a34a' },
    { name: 'Closed', value: analytics.status_breakdown.closed, color: '#6b7280' },
  ] : [];

  const trendData = useMemo(() => {
    const rangeDays = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365;
    const bucketCount = rangeDays <= 7 ? 7 : rangeDays <= 30 ? 10 : 12;
    const bucketSize = Math.ceil(rangeDays / bucketCount);
    const now = new Date();
    const buckets = Array.from({ length: bucketCount }, (_, index) => {
      const start = new Date(now.getTime() - (bucketCount - index) * bucketSize * 86400000);
      return { day: rangeDays <= 7 ? start.toLocaleDateString(undefined, { weekday: 'short' }) : start.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }), incidents: 0, resolved: 0 };
    });
    recentIncidents.forEach((incident) => {
      const ageInDays = (now.getTime() - new Date(incident.created_at).getTime()) / 86400000;
      const index = Math.min(bucketCount - 1, Math.max(0, bucketCount - 1 - Math.floor(ageInDays / bucketSize)));
      buckets[index].incidents += 1;
      if (incident.status === 'resolved' || incident.status === 'closed') buckets[index].resolved += 1;
    });
    return buckets;
  }, [recentIncidents, timeRange]);

  const serviceData = useMemo(() => Object.entries(recentIncidents.reduce<Record<string, number>>((totals, incident) => {
    totals[incident.service] = (totals[incident.service] || 0) + 1;
    return totals;
  }, {})).sort(([, a], [, b]) => b - a).slice(0, 5), [recentIncidents]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner h-12 w-12"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="error-state">
        <CardContent className="error-state-content">
          <AlertTriangle className="error-state-icon" />
          <div>
            <h3 className="error-state-title">Error loading analytics</h3>
            <p className="error-state-text">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="page-stack">
      <PageHeader
        title="Analytics"
        description="Severity, status, and service-level incident insights"
        actions={
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
        }
      />

      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 lg:gap-5">
          <MetricCard
            label="Total incidents"
            value={analytics.overview.total_incidents}
            hint="Across the selected time window"
            icon={AlertTriangle}
          />
          <MetricCard
            label="Open"
            value={analytics.overview.open_incidents}
            hint="Awaiting triage or action"
            icon={Users}
            tone="critical"
          />
          <MetricCard
            label="Resolved"
            value={analytics.overview.resolved_incidents}
            hint={`${analytics.overview.resolution_rate_percent}% resolution rate`}
            icon={Activity}
            tone="success"
          />
          <MetricCard
            label="Critical"
            value={analytics.overview.critical_incidents}
            hint="Highest severity in dataset"
            icon={Clock}
            tone="warning"
          />
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Severity Breakdown</CardTitle>
            <CardDescription>Incident distribution by severity level</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: chartTheme.axis }}
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={chartTheme.tooltip} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Status Breakdown</CardTitle>
            <CardDescription>Incident distribution by current status</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={{ stroke: chartTheme.axis }}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={chartTheme.tooltip} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Trend Analysis */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Trend Analysis</CardTitle>
            <CardDescription>Incidents over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartTheme.grid} />
                <XAxis dataKey="day" stroke={chartTheme.axis} fontSize={12} tick={{ fill: chartTheme.axis }} />
                <YAxis stroke={chartTheme.axis} fontSize={12} tick={{ fill: chartTheme.axis }} />
                <Tooltip contentStyle={chartTheme.tooltip} />
                <Legend wrapperStyle={{ color: chartTheme.legend }} />
                <Line type="monotone" dataKey="incidents" stroke="#dc2626" strokeWidth={2} dot={{ r: 4 }} name="Incidents" />
                <Line type="monotone" dataKey="resolved" stroke="#16a34a" strokeWidth={2} dot={{ r: 4 }} name="Resolved" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Additional Analytics Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Service Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Service Performance</CardTitle>
            <CardDescription>Incidents by affected service</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {serviceData.length ? serviceData.map(([service, count], index) => (
                <div className="flex items-center justify-between" key={service}>
                  <div className="flex items-center space-x-2 min-w-0">
                    <div className={`w-3 h-3 rounded-full flex-shrink-0 ${['bg-red-500', 'bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-violet-500'][index]}`} />
                    <span className="text-sm font-medium truncate">{service}</span>
                  </div>
                  <span className="text-sm text-app-muted ml-3">{count} {count === 1 ? 'incident' : 'incidents'}</span>
                </div>
              )) : <p className="text-sm text-app-muted">No service activity in this period.</p>}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest incident-related activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentIncidents.slice(0, 4).map((incident) => (
                <div className="flex items-start space-x-3" key={incident.id}>
                  <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${incident.severity === 'critical' ? 'bg-red-500' : incident.severity === 'high' ? 'bg-orange-500' : 'bg-blue-500'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-app-ink truncate">{incident.title}</p>
                    <p className="text-xs text-app-muted mt-0.5 truncate">{incident.service} · {incident.status}</p>
                    <p className="text-xs text-app-muted mt-1 opacity-80">{new Date(incident.created_at).toLocaleString()}</p>
                  </div>
                </div>
              ))}
              {!recentIncidents.length && <p className="text-sm text-app-muted">No activity in this period.</p>}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
