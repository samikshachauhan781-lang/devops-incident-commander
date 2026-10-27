// API TypeScript type definitions for DevOps Incident Commander

// Base API response type
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
  timestamp: string;
}

// Incident-related types
export interface Incident {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  service: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
}

export interface IncidentCreateRequest {
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  service: string;
}

export interface IncidentUpdateRequest {
  title?: string;
  description?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  status?: 'open' | 'investigating' | 'resolved' | 'closed';
  service?: string;
  resolved_at?: string | null;
}

export interface IncidentResponse {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  service: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
}

export interface IncidentListResponse {
  incidents: IncidentResponse[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface IncidentEvent {
  id: string;
  incident_id: string;
  event_type: string;
  description: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  created_at: string;
}

export interface TimelineResponse {
  incident_id: string;
  events: IncidentEvent[];
}

// Analytics types
export interface AnalyticsOverview {
  total_incidents: number;
  open_incidents: number;
  investigating_incidents: number;
  resolved_incidents: number;
  closed_incidents: number;
  critical_incidents: number;
  resolution_rate_percent: number;
  // recent_incidents is not provided by the backend and not used by the component
  recent_incidents?: number;
}

export interface SeverityBreakdown {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

export interface StatusBreakdown {
  open: number;
  investigating: number;
  resolved: number;
  closed: number;
}

export interface AnalyticsResponse {
  overview: AnalyticsOverview;
  severity_breakdown: SeverityBreakdown;
  status_breakdown: StatusBreakdown;
}

// Raw backend response types for transformation
export interface SeverityBreakdownRaw {
  severity_breakdown: Array<{
    severity: string;
    count: number;
    percentage: number;
  }>;
}

export interface StatusBreakdownRaw {
  status_breakdown: Array<{
    status: string;
    count: number;
    percentage: number;
  }>;
}

// Investigation types
export interface InvestigationEvidence {
  id: string;
  incident_id: string;
  evidence_type: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface InvestigationResult {
  incident_id: string;
  investigation_id: string;
  status: 'in_progress' | 'completed' | 'failed';
  findings: string;
  root_cause?: string;
  recommendations: string[];
  evidence?: InvestigationEvidence[];
  completed_at?: string;
}

export interface InvestigationRequest {
  incident_id: string;
  investigation_type: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  deadline?: string;
  required_expertise?: string[];
}

// Filter types
export interface IncidentFilters {
  page?: number;
  page_size?: number;
  service?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical' | 'all';
  status?: 'open' | 'investigating' | 'resolved' | 'closed' | 'all';
  search?: string;
  created_after?: string;
  created_before?: string;
  sort_by?: 'created_at' | 'updated_at' | 'severity' | 'status';
  order?: 'asc' | 'desc';
}

// API endpoint types
export type ApiEndpoints = {
  incidents: {
    list: (filters?: IncidentFilters) => `/incidents${string}`;
    create: () => '/incidents';
    get: (id: string) => `/incidents/${string}`;
    update: (id: string) => `/incidents/${string}`;
    delete: (id: string) => `/incidents/${string}`;
    timeline: (id: string) => `/incidents/${string}/timeline`;
    investigate: (id: string) => `/incidents/${string}/investigate`;
  };
  analytics: {
    overview: () => '/analytics/overview';
    severity: () => '/analytics/severity';
    status: () => '/analytics/status';
  };
};

// Utility functions for API endpoints
export const endpoints: ApiEndpoints = {
  incidents: {
    list: (filters?: IncidentFilters) => {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== 'all') {
            params.append(key, value.toString());
          }
        });
      }
      const queryString = params.toString();
      return `/incidents${queryString ? `?${queryString}` : ''}`;
    },
    create: () => '/incidents',
    get: (id: string) => `/incidents/${id}`,
    update: (id: string) => `/incidents/${id}`,
    delete: (id: string) => `/incidents/${id}`,
    timeline: (id: string) => `/incidents/${id}/timeline`,
    investigate: (id: string) => `/incidents/${id}/investigate`,
  },
  analytics: {
    overview: () => '/analytics/overview',
    severity: () => '/analytics/severity',
    status: () => '/analytics/status',
  },
};