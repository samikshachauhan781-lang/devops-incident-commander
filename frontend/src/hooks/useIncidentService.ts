// Incident service hook for DevOps Incident Commander
import { useContext } from 'react';
import { IncidentContext } from '../contexts/IncidentContext';
import { IncidentFilters } from '../types/api';
import { incidentService } from '../services/incidentService';

export function useIncidentService() {
  const context = useContext(IncidentContext);
  if (context === undefined) {
    throw new Error('useIncidentService must be used within an IncidentProvider');
  }
  return {
    getIncidents: context.loadIncidents,
    getIncident: context.loadIncident,
    getAnalytics: context.getAnalytics,
    createIncident: context.createIncident,
    updateIncident: context.updateIncident,
    deleteIncident: context.deleteIncident,
    investigateIncident: incidentService.investigateIncident.bind(incidentService),
  };
}
