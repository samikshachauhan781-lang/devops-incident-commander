// Incident context for state management
import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { Incident, IncidentCreateRequest, IncidentUpdateRequest, IncidentResponse, IncidentListResponse, AnalyticsResponse } from '../types/api';
import { incidentService } from '../services/incidentService';

// Context types
interface IncidentState {
  incidents: IncidentResponse[];
  selectedIncident: IncidentResponse | null;
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

interface IncidentFilters {
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

interface IncidentContextType {
  state: IncidentState;
  loadIncidents: (filters?: IncidentFilters) => Promise<IncidentListResponse>;
  loadIncident: (id: string) => Promise<IncidentResponse>;
  createIncident: (data: IncidentCreateRequest) => Promise<IncidentResponse>;
  updateIncident: (id: string, data: IncidentUpdateRequest) => Promise<IncidentResponse>;
  deleteIncident: (id: string) => Promise<void>;
  selectIncident: (incident: IncidentResponse | null) => void;
  clearError: () => void;
  setFilters: (filters: IncidentFilters) => void;
  getAnalytics: () => Promise<AnalyticsResponse>;
}

// Initial state
const initialState: IncidentState = {
  incidents: [],
  selectedIncident: null,
  loading: false,
  error: null,
  total: 0,
  page: 1,
  pageSize: 10,
  hasMore: false,
};

// Action types
type IncidentAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_INCIDENTS'; payload: { incidents: IncidentResponse[]; total: number; page: number; pageSize: number; hasMore: boolean } }
  | { type: 'SET_SELECTED_INCIDENT'; payload: IncidentResponse | null }
  | { type: 'ADD_INCIDENT'; payload: IncidentResponse }
  | { type: 'UPDATE_INCIDENT'; payload: IncidentResponse }
  | { type: 'REMOVE_INCIDENT'; payload: string }
  | { type: 'SET_FILTERS'; payload: Partial<IncidentFilters> };

// Reducer function
function incidentReducer(state: IncidentState, action: IncidentAction): IncidentState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };

    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };

    case 'SET_INCIDENTS':
      return {
        ...state,
        incidents: action.payload.page === 1 ? action.payload.incidents : [...state.incidents, ...action.payload.incidents],
        total: action.payload.total,
        page: action.payload.page,
        pageSize: action.payload.pageSize,
        hasMore: action.payload.hasMore,
        loading: false,
        error: null,
      };

    case 'SET_SELECTED_INCIDENT':
      return { ...state, selectedIncident: action.payload };

    case 'ADD_INCIDENT':
      return {
        ...state,
        incidents: [action.payload, ...state.incidents],
        total: state.total + 1,
      };

    case 'UPDATE_INCIDENT':
      return {
        ...state,
        incidents: state.incidents.map(incident =>
          incident.id === action.payload.id ? action.payload : incident
        ),
        selectedIncident: state.selectedIncident?.id === action.payload.id ? action.payload : state.selectedIncident,
      };

    case 'REMOVE_INCIDENT':
      return {
        ...state,
        incidents: state.incidents.filter(incident => incident.id !== action.payload),
        total: Math.max(0, state.total - 1),
        selectedIncident: state.selectedIncident?.id === action.payload ? null : state.selectedIncident,
      };

    default:
      return state;
  }
}

// Create context
const IncidentContext = createContext<IncidentContextType | undefined>(undefined);

// Export the context for direct access
export { IncidentContext };
export type { IncidentFilters }; // Export IncidentFilters type

// Provider component
export function IncidentProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(incidentReducer, initialState);

  const loadIncidents = useCallback(async (filters: IncidentFilters = {}): Promise<IncidentListResponse> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      // Use actual API service instead of mock data
      const response = await incidentService.getIncidents(filters);

      dispatch({
        type: 'SET_INCIDENTS',
        payload: {
          incidents: response.incidents,
          total: response.total,
          page: response.page,
          pageSize: response.page_size,
          hasMore: response.has_more,
        },
      });

      return response;

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to load incidents' });
      throw error;
    }
  }, []);

  const loadIncident = useCallback(async (id: string): Promise<IncidentResponse> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // Use actual API service
      const incident = await incidentService.getIncident(id);

      dispatch({ type: 'SET_SELECTED_INCIDENT', payload: incident });
      dispatch({ type: 'SET_LOADING', payload: false });

      return incident;

    } catch (error) {
      dispatch({ type: 'SET_SELECTED_INCIDENT', payload: null });
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to load incident' });
      throw error;
    }
  }, []);

  const createIncident = useCallback(async (data: IncidentCreateRequest): Promise<IncidentResponse> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // Use actual API service
      const newIncident = await incidentService.createIncident(data);

      dispatch({ type: 'ADD_INCIDENT', payload: newIncident });
      dispatch({ type: 'SET_LOADING', payload: false });
      return newIncident;

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to create incident' });
      throw error;
    }
  }, []);

  const updateIncident = useCallback(async (id: string, data: IncidentUpdateRequest): Promise<IncidentResponse> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // Use actual API service
      const updatedIncident = await incidentService.updateIncident(id, data);

      dispatch({ type: 'UPDATE_INCIDENT', payload: updatedIncident });
      dispatch({ type: 'SET_LOADING', payload: false });
      return updatedIncident;

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to update incident' });
      throw error;
    }
  }, []);

  const deleteIncident = useCallback(async (id: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });

      // Use actual API service
      await incidentService.deleteIncident(id);

      dispatch({ type: 'REMOVE_INCIDENT', payload: id });
      dispatch({ type: 'SET_LOADING', payload: false });

    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Failed to delete incident' });
      throw error;
    }
  }, []);

  const selectIncident = useCallback((incident: IncidentResponse | null) => {
    dispatch({ type: 'SET_SELECTED_INCIDENT', payload: incident });
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: 'SET_ERROR', payload: null });
  }, []);

  const setFilters = useCallback((filters: Partial<IncidentFilters>) => {
    // This would typically update the URL and reload data
    console.log('Filters updated:', filters);
  }, []);

  const getAnalytics = useCallback(async () => {
    try {
      // Use actual API service
      return await incidentService.getAnalytics();
    } catch (error) {
      console.error('Failed to load analytics:', error);
      throw error;
    }
  }, []);

  const contextValue: IncidentContextType = {
    state,
    loadIncidents,
    loadIncident,
    createIncident,
    updateIncident,
    deleteIncident,
    selectIncident,
    clearError,
    setFilters,
    getAnalytics,
  };

  return (
    <IncidentContext.Provider value={contextValue}>
      {children}
    </IncidentContext.Provider>
  );
}

// Custom hook to use incident context
export function useIncidentContext() {
  const context = useContext(IncidentContext);
  if (context === undefined) {
    throw new Error('useIncidentContext must be used within an IncidentProvider');
  }
  return context;
}

// Convenience hook for common operations
export function useIncidentService() {
  const { loadIncidents, loadIncident, createIncident, updateIncident, deleteIncident } = useIncidentContext();
  return {
    getIncidents: loadIncidents,
    getIncident: loadIncident,
    createIncident,
    updateIncident,
    deleteIncident,
  };
}
