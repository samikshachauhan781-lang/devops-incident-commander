// Incident detail component for DevOps Incident Commander
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { useIncidentContext } from '../../contexts/IncidentContext';
import { IncidentUpdateRequest } from '../../types/api';
import { usePageTitle } from '../../layouts/MainLayout';
import { useIncidentService } from '../../hooks/useIncidentService';
import { useToast } from '../../hooks/useToast';
import { AlertTriangle, Calendar, Clock, Edit, Save, X, User, Activity, AlertCircle, ArrowLeft } from 'lucide-react';
import { capitalizeLabel, severityBadgeClass, statusBadgeClass } from '../../lib/incidentUi';

export default function IncidentDetail() {
  const { state, loadIncident, updateIncident, selectIncident, clearError } = useIncidentContext();
  const { investigateIncident } = useIncidentService();
  const { toast } = useToast();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<IncidentUpdateRequest>>({});
  const [detailStatus, setDetailStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const { setPageTitle } = usePageTitle();

  const incident =
    state.selectedIncident?.id === id ? state.selectedIncident : null;

  useEffect(() => {
    if (!id) {
      setDetailStatus('idle');
      return;
    }

    if (incident?.id === id) {
      setDetailStatus('ready');
      return;
    }

    let cancelled = false;
    setDetailStatus('loading');
    clearError();

    loadIncident(id)
      .then(() => {
        if (!cancelled) setDetailStatus('ready');
      })
      .catch(() => {
        if (!cancelled) setDetailStatus('error');
      });

    return () => {
      cancelled = true;
    };
  }, [id, loadIncident, clearError, incident?.id]);

  useEffect(() => {
    if (incident) {
      setFormData(incident);
      setPageTitle(incident.title, `Incident ID: ${incident.id}`, [
        { label: 'Incidents', href: '/incidents' },
        { label: incident.title },
      ]);
    } else if (id && detailStatus === 'error') {
      setPageTitle('Incident not found', `No incident matches ID ${id}`, [
        { label: 'Incidents', href: '/incidents' },
        { label: 'Not found' },
      ]);
    }
  }, [incident, id, detailStatus, setPageTitle]);

  const handleSave = async () => {
    if (!incident) return;

    try {
      await updateIncident(incident.id, formData);
      setIsEditing(false);
      toast({ title: 'Incident updated', description: 'Your changes have been saved.' });
    } catch (error) {
      toast({ title: 'Could not save incident', description: error instanceof Error ? error.message : 'Please try again.', variant: 'destructive' });
    }
  };

  const goToIncidents = () => {
    selectIncident(null);
    navigate('/incidents');
  };

  const handleInvestigation = async () => {
    if (!incident) return;
    try {
      const result = await investigateIncident(incident.id, {
        incident_id: incident.id,
        investigation_type: 'root_cause_analysis',
        priority: incident.severity,
      });
      toast({ title: 'Investigation started', description: result.findings || 'The investigation workflow is now running.' });
    } catch (error) {
      toast({ title: 'Could not start investigation', description: error instanceof Error ? error.message : 'Please try again.', variant: 'destructive' });
    }
  };

  const handleCancel = () => {
    setFormData(incident || {});
    setIsEditing(false);
    clearError();
  };

  if (!incident) {
    const isLoading = detailStatus === 'loading' || (Boolean(id) && detailStatus === 'idle');
    const isNotFound = Boolean(id) && detailStatus === 'error';

    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={goToIncidents}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Incidents
          </Button>
        </div>
        {isLoading ? (
          <div className="loading-container" role="status" aria-live="polite">
            <div className="loading-spinner h-10 w-10" />
            <p className="text-sm text-app-muted mt-4">Loading incident details…</p>
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <div className="empty-state">
                <AlertTriangle className="empty-state-icon" />
                <h3 className="empty-state-title">
                  {isNotFound ? 'Incident not found' : 'No incident selected'}
                </h3>
                <p className="empty-state-text">
                  {isNotFound
                    ? `We could not find an incident with ID "${id}". It may have been removed or the link is incorrect.`
                    : 'Select an incident from the list to view its details.'}
                </p>
                {isNotFound && (
                  <Button className="mt-2" variant="outline" onClick={goToIncidents}>
                    Browse incidents
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  const severityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ];

  const statusOptions = [
    { value: 'open', label: 'Open' },
    { value: 'investigating', label: 'Investigating' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' },
  ];

  return (
    <div className="page-stack">
      <div className="page-header">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={goToIncidents}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back to Incidents
          </Button>
          <div>
            <h1 className="page-title">{incident.title}</h1>
            <p className="page-description">Incident ID: {incident.id}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          {isEditing ? (
            <>
              <Button onClick={handleSave} disabled={state.loading}>
                <Save className="h-4 w-4 mr-2" />
                Save
              </Button>
              <Button onClick={handleCancel} variant="outline" >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)} variant="outline" >
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </div>

      {/* Error Message */}
      {state.error && (
        <Card className="error-state">
          <CardContent className="error-state-content">
            <AlertCircle className="error-state-icon" />
            <div>
              <h3 className="error-state-title">Error</h3>
              <p className="error-state-text">{state.error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {state.loading && (
        <div className="loading-container">
          <div className="loading-spinner h-8 w-8"></div>
        </div>
      )}

      {/* Incident Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="panel-card">
            <CardHeader className="panel-card-header">
              <CardTitle>Incident details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {isEditing ? (
                <div className="space-y-5">
                  <Field label="Title" required>
                    <Input
                      value={formData.title || ''}
                      onChange={(e) => setFormData((prev: Partial<IncidentUpdateRequest>) => ({ ...prev, title: e.target.value }))}
                      placeholder="Incident title"
                    />
                  </Field>

                  <Field label="Description" required>
                    <textarea
                      value={formData.description || ''}
                      onChange={(e) => setFormData((prev: Partial<IncidentUpdateRequest>) => ({ ...prev, description: e.target.value }))}
                      className="field-textarea"
                    />
                  </Field>
                </div>
              ) : (
                <div className="space-y-5">
                  <Field label="Description">
                    <p className="text-sm text-app-muted whitespace-pre-wrap">{incident.description}</p>
                  </Field>
                </div>
              )}

              <div className="grid grid-cols-2 gap-5">
                <Field label="Severity">
                  {isEditing ? (
                    <Select value={formData.severity || 'medium'} onValueChange={(v) => setFormData((prev: Partial<IncidentUpdateRequest>) => ({ ...prev, severity: v as any }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select severity" />
                      </SelectTrigger>
                      <SelectContent>
                        {severityOptions.map(opt => (
                          <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge className={severityBadgeClass(incident.severity)} variant="outline">
                      {capitalizeLabel(incident.severity)}
                    </Badge>
                  )}
                </Field>
                <Field label="Status">
                  {isEditing ? (
                    <Select value={formData.status || 'open'} onValueChange={(v) => setFormData((prev: Partial<IncidentUpdateRequest>) => ({ ...prev, status: v as any }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        {statusOptions.map(opt => (
                          <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Badge className={statusBadgeClass(incident.status)} variant="outline">
                      {capitalizeLabel(incident.status)}
                    </Badge>
                  )}
                </Field>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <Field label="Service">
                  {isEditing ? (
                    <Input
                      value={formData.service || ''}
                      onChange={(e) => setFormData((prev: Partial<IncidentUpdateRequest>) => ({ ...prev, service: e.target.value }))}
                      placeholder="Service name"
                    />
                  ) : (
                    <p className="text-sm text-app-muted">{incident.service}</p>
                  )}
                </Field>
                <Field label="Resolved At">
                  {isEditing ? (
                    <Input
                      type="datetime-local"
                      value={formData.resolved_at ? new Date(formData.resolved_at).toISOString().slice(0, 16) : ''}
                      onChange={(e) => setFormData((prev: Partial<IncidentUpdateRequest>) => ({ ...prev, resolved_at: e.target.value }))}
                    />
                  ) : (
                    <p className="text-sm text-app-muted">
                      {incident.resolved_at
                        ? new Date(incident.resolved_at).toLocaleString()
                        : 'Not resolved'
                      }
                    </p>
                  )}
                </Field>
              </div>
            </CardContent>
          </Card>

          {/* Timeline Section */}
          <Card className="panel-card">
            <CardHeader className="panel-card-header">
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" aria-hidden="true" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-app-ink">Incident created</p>
                    <p className="text-xs text-app-muted">
                      {new Date(incident.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-app-ink">Last updated</p>
                    <p className="text-xs text-app-muted">
                      {new Date(incident.updated_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                {incident.resolved_at && (
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-app-ink">Incident resolved</p>
                      <p className="text-xs text-app-muted">
                        {new Date(incident.resolved_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card className="panel-card">
            <CardHeader className="panel-card-header compact">
              <CardTitle>Quick actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start" variant="outline" onClick={handleInvestigation}>
                <Activity className="h-4 w-4 mr-2" />
                Start Investigation
              </Button>
              <Button className="w-full justify-start" variant="outline" onClick={() => toast({ title: 'Maintenance scheduling', description: 'Scheduling is not configured in this demo environment.' })}>
                <Calendar className="h-4 w-4 mr-2" />
                Schedule Maintenance
              </Button>
              <Button className="w-full justify-start" variant="outline" onClick={() => toast({ title: 'Assignment', description: 'Team assignment is not configured in this demo environment.' })}>
                <User className="h-4 w-4 mr-2" />
                Assign to Team
              </Button>
            </CardContent>
          </Card>

          {/* Incident Metadata */}
          <Card className="panel-card">
            <CardHeader className="panel-card-header compact">
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-app-muted">Created by:</span>
                <span className="font-medium">System</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-app-muted">Last updated by:</span>
                <span className="font-medium">System</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-app-muted">Category:</span>
                <span className="font-medium">Technical</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-app-muted">Priority:</span>
                <Badge className={severityBadgeClass(incident.severity)} >
                  {capitalizeLabel(incident.severity)}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Helper Field component for consistent form layout
function Field({ label, children, required = false }: { label: string; children: React.ReactNode; required?: boolean }) {
  return (
    <div className="field">
      <label className="field-label">
        {label}
        {required && <span className="field-required" aria-hidden="true">*</span>}
      </label>
      {children}
    </div>
  );
}
