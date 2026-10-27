// Incident list component for DevOps Incident Commander
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { useIncidentContext } from '../../contexts/IncidentContext';
import { IncidentFilters } from '../../types/api';
import { usePageTitle } from '../../layouts/MainLayout';
import { useToast } from '../../hooks/useToast';
import { AlertTriangle, Plus, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { capitalizeLabel, formatIncidentDate, severityBadgeClass, statusBadgeClass } from '../../lib/incidentUi';

export default function IncidentList() {
  const { state, loadIncidents, selectIncident } = useIncidentContext();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<IncidentFilters>({ page: 1, page_size: 10 });
  const { setPageTitle } = usePageTitle();
  const { toast } = useToast();

  useEffect(() => {
    setPageTitle('Incidents', 'Manage and track all incidents', [
      { label: 'Incidents', href: '/incidents' },
    ]);
  }, [setPageTitle]);

  useEffect(() => {
    loadIncidents(filters);
  }, [filters]);

  const handleFiltersChange = (newFilters: Partial<IncidentFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }));
  };

  const totalPages = Math.ceil(state.total / (filters.page_size || 10));

  return (
    <div className="page-stack">
      <PageHeader
        title="Incidents"
        description="Search, filter, and triage active issues across services"
        actions={
          <Button onClick={() => toast({ title: "Read-only demo", description: "Incident creation is disabled in the read-only demo." })}>
            <Plus className="h-4 w-4 mr-2" />
            Create incident
          </Button>
        }
      />

      <Card className="filters-panel">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter incidents by various criteria</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="filters-row">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-app-muted opacity-70" aria-hidden="true" />
              <label htmlFor="incident-filter-service" className="text-sm text-app-muted">Service:</label>
              <Select value={filters.service || 'all'} onValueChange={(value) => handleFiltersChange({ service: value === 'all' ? undefined : value })}>
                <SelectTrigger id="incident-filter-service" className="w-[160px]">
                  <SelectValue placeholder="All Services" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Services</SelectItem>
                  <SelectItem value="payment-api">Payment API</SelectItem>
                  <SelectItem value="database-service">Database Service</SelectItem>
                  <SelectItem value="api-service">API Service</SelectItem>
                  <SelectItem value="test-service">Test Service</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <label htmlFor="incident-filter-severity" className="text-sm text-app-muted">Severity:</label>
              <Select value={filters.severity || 'all'} onValueChange={(value) => handleFiltersChange({ severity: value === 'all' ? undefined : value as any })}>
                <SelectTrigger id="incident-filter-severity" className="w-[140px]">
                  <SelectValue placeholder="All Severities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severities</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <label htmlFor="incident-filter-status" className="text-sm text-app-muted">Status:</label>
              <Select value={filters.status || 'all'} onValueChange={(value) => handleFiltersChange({ status: value === 'all' ? undefined : value as any })}>
                <SelectTrigger id="incident-filter-status" className="w-[140px]">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="investigating">Investigating</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2 ml-auto">
              <label htmlFor="incident-filter-search" className="sr-only">Search incidents</label>
              <Search className="h-4 w-4 text-app-muted opacity-70" aria-hidden="true" />
              <Input
                id="incident-filter-search"
                type="search"
                placeholder="Search incidents..."
                value={filters.search || ''}
                onChange={(e) => handleFiltersChange({ search: e.target.value || undefined })}
                className="w-64"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Incident Count & Pagination */}
      <div className="pagination-bar">
        <p className="text-sm text-app-muted">
          Showing {state.incidents.length} of {state.total} incidents
        </p>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleFiltersChange({ page: Math.max(1, (filters.page || 1) - 1) })}
            disabled={state.loading || state.page === 1}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <span className="text-sm text-app-muted px-2">
            Page {state.page} of {totalPages || 1}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleFiltersChange({ page: (filters.page || 1) + 1 })}
            disabled={state.loading || !state.hasMore}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>

      {/* Incidents Grid */}
      {state.loading ? (
        <div className="loading-container">
          <div className="loading-spinner h-12 w-12"></div>
        </div>
      ) : state.error ? (
        <Card className="error-state">
          <CardContent className="error-state-content">
            <AlertTriangle className="error-state-icon" />
            <div>
              <h3 className="error-state-title">Error loading incidents</h3>
              <p className="error-state-text">{state.error}</p>
              <Button onClick={() => loadIncidents(filters)} variant="outline" className="mt-3">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : state.incidents.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="empty-state">
              <AlertTriangle className="empty-state-icon" />
              <h3 className="empty-state-title">No incidents found</h3>
              <p className="empty-state-text">
                {Object.keys(filters).length > 0
                  ? 'Try adjusting your filters to see more results'
                  : 'Get started by creating your first incident'}
              </p>
              <Button onClick={() => toast({ title: "Read-only demo", description: "Incident creation is disabled in the read-only demo." })}>
                <Plus className="h-4 w-4 mr-2" />
                Create Incident
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {state.incidents.map((incident) => (
            <Card
              key={incident.id}
              className="incident-tile cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]"
              onClick={() => { selectIncident(incident); navigate(`/incidents/${incident.id}`); }}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  selectIncident(incident);
                  navigate(`/incidents/${incident.id}`);
                }
              }}
              role="link"
              tabIndex={0}
              aria-label={`View incident: ${incident.title}`}
            >
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg line-clamp-1">{incident.title}</CardTitle>
                  <Badge className={severityBadgeClass(incident.severity)} variant="outline">
                    {capitalizeLabel(incident.severity)}
                  </Badge>
                </div>
                <CardDescription className="line-clamp-2">
                  {incident.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <Badge className={statusBadgeClass(incident.status)} variant="outline">
                      {capitalizeLabel(incident.status)}
                    </Badge>
                    <span className="text-sm text-app-muted">{incident.service}</span>
                  </div>
                  <div className="text-xs text-app-muted opacity-75">
                    {formatIncidentDate(incident.created_at)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
