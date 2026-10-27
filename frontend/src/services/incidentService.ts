// Incident management service for DevOps Incident Commander
import {
  apiGet,
  apiPost,
  apiPatch,
  apiDelete
} from '../api/client';
import {
  Incident,
  IncidentCreateRequest,
  IncidentUpdateRequest,
  IncidentResponse,
  IncidentListResponse,
  TimelineResponse,
  AnalyticsResponse,
  InvestigationResult,
  InvestigationRequest,
  IncidentFilters,
  AnalyticsOverview,
  SeverityBreakdown,
  StatusBreakdown,
  SeverityBreakdownRaw,
  StatusBreakdownRaw,
  endpoints
} from '../types/api';

// Incident service class
class IncidentService {
  private readonly baseUrl = '';

  constructor() {
    // Base URL is handled by the API client
  }

  // Incident management methods
  async getIncidents(filters?: IncidentFilters): Promise<IncidentListResponse> {
    try {
      const response = await apiGet<IncidentListResponse>(endpoints.incidents.list(filters));
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch incidents');
    }
  }

  async getIncident(id: string): Promise<IncidentResponse> {
    try {
      const response = await apiGet<IncidentResponse>(endpoints.incidents.get(id));
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch incident');
    }
  }

  async createIncident(data: IncidentCreateRequest): Promise<IncidentResponse> {
    try {
      const response = await apiPost<IncidentResponse>(endpoints.incidents.create(), data);
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to create incident');
    }
  }

  async updateIncident(id: string, data: IncidentUpdateRequest): Promise<IncidentResponse> {
    try {
      const response = await apiPatch<IncidentResponse>(endpoints.incidents.update(id), data);
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to update incident');
    }
  }

  async deleteIncident(id: string): Promise<void> {
    try {
      await apiDelete<void>(endpoints.incidents.delete(id));
    } catch (error: any) {
      throw new Error(error.message || 'Failed to delete incident');
    }
  }

  // Analytics methods
  async getAnalytics(): Promise<AnalyticsResponse> {
    try {
      // Fetch all three analytics endpoints in parallel
      const [overview, severityRaw, statusRaw] = await Promise.all([
        apiGet<AnalyticsOverview>(endpoints.analytics.overview()),
        apiGet<SeverityBreakdownRaw>(endpoints.analytics.severity()),
        apiGet<StatusBreakdownRaw>(endpoints.analytics.status()),
      ]);

      // Transform severity breakdown from array to object format
      const severity_breakdown: SeverityBreakdown = {
        low: 0,
        medium: 0,
        high: 0,
        critical: 0,
      };
      for (const item of severityRaw.severity_breakdown) {
        if (item.severity in severity_breakdown) {
          severity_breakdown[item.severity as keyof SeverityBreakdown] = item.count;
        }
      }

      // Transform status breakdown from array to object format
      const status_breakdown: StatusBreakdown = {
        open: 0,
        investigating: 0,
        resolved: 0,
        closed: 0,
      };
      for (const item of statusRaw.status_breakdown) {
        if (item.status in status_breakdown) {
          status_breakdown[item.status as keyof StatusBreakdown] = item.count;
        }
      }

      return {
        overview,
        severity_breakdown,
        status_breakdown,
      };
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch analytics');
    }
  }

  async getSeverityBreakdown(): Promise<{ breakdown: any }> {
    try {
      const response = await apiGet<{ breakdown: any }>(endpoints.analytics.severity());
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch severity breakdown');
    }
  }

  async getStatusBreakdown(): Promise<{ breakdown: any }> {
    try {
      const response = await apiGet<{ breakdown: any }>(endpoints.analytics.status());
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch status breakdown');
    }
  }

  // Timeline methods
  async getIncidentTimeline(incidentId: string): Promise<TimelineResponse> {
    try {
      const response = await apiGet<TimelineResponse>(endpoints.incidents.timeline(incidentId));
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to fetch incident timeline');
    }
  }

  // Investigation methods
  async investigateIncident(incidentId: string, data?: InvestigationRequest): Promise<InvestigationResult> {
    try {
      const response = await apiPost<InvestigationResult>(endpoints.incidents.investigate(incidentId), data);
      return response;
    } catch (error: any) {
      throw new Error(error.message || 'Failed to start investigation');
    }
  }

  // Utility methods
  async getIncidentsByService(service: string): Promise<IncidentListResponse> {
    return this.getIncidents({ service, page_size: 100 });
  }

  async getIncidentsBySeverity(severity: 'low' | 'medium' | 'high' | 'critical'): Promise<IncidentListResponse> {
    return this.getIncidents({ severity, page_size: 100 });
  }

  async getIncidentsByStatus(status: 'open' | 'investigating' | 'resolved' | 'closed'): Promise<IncidentListResponse> {
    return this.getIncidents({ status, page_size: 100 });
  }

  // Search and filtering
  async searchIncidents(searchTerm: string): Promise<IncidentListResponse> {
    return this.getIncidents({ search: searchTerm, page_size: 50 });
  }

  // Date-based filtering
  async getIncidentsCreatedAfter(date: string): Promise<IncidentListResponse> {
    return this.getIncidents({ created_after: date, page_size: 100 });
  }

  // Bulk operations
  async getAllIncidents(): Promise<IncidentResponse[]> {
    let allIncidents: IncidentResponse[] = [];
    let page = 1;
    let hasMore = true;

    while (hasMore) {
      const response = await this.getIncidents({ page, page_size: 100 });
      allIncidents.push(...response.incidents);
      hasMore = response.has_more;
      page++;
    }

    return allIncidents;
  }

  // Statistics helpers
  async getIncidentStats() {
    const [analytics, allIncidents] = await Promise.all([
      this.getAnalytics(),
      this.getAllIncidents()
    ]);

    return {
      total: allIncidents.length,
      bySeverity: allIncidents.reduce((acc, incident) => {
        acc[incident.severity] = (acc[incident.severity] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      byStatus: allIncidents.reduce((acc, incident) => {
        acc[incident.status] = (acc[incident.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      byService: allIncidents.reduce((acc, incident) => {
        acc[incident.service] = (acc[incident.service] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      analytics,
    };
  }

  // Error handling wrapper
  private handleError(error: any): never {
    const message = error.response?.data?.message || error.message || 'An unexpected error occurred';
    throw new Error(message);
  }
}

// Export singleton instance
export const incidentService = new IncidentService();

// Convenience exports for backward compatibility
export default incidentService;

// Export types for use in components
export type {
  Incident,
  IncidentCreateRequest,
  IncidentUpdateRequest,
  IncidentResponse,
  IncidentListResponse,
  TimelineResponse,
  AnalyticsResponse,
  InvestigationResult,
  InvestigationRequest,
  IncidentFilters,
};