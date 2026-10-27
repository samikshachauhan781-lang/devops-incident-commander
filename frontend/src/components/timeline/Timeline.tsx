// Timeline — vertical center rail with alternating event cards
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { useIncidentContext } from '../../contexts/IncidentContext';
import { incidentService } from '../../services/incidentService';
import { IncidentEvent, TimelineResponse } from '../../types/api';
import { usePageTitle } from '../../layouts/MainLayout';
import {
  Clock,
  Filter,
  Search,
  AlertTriangle,
  Plus,
  Activity,
  Sparkles,
} from 'lucide-react';
import { PageHeader } from '../ui/PageHeader';
import { Badge } from '../ui/Badge';
import { cn } from '@utils/cn';
import { severityBadgeClass, statusBadgeClass } from '../../lib/incidentUi';
import {
  formatAbsoluteTime,
  formatTimelineEventTime,
  getTimelineEventMeta,
} from '../../lib/timelineUi';

export default function Timeline() {
  const { state, loadIncidents } = useIncidentContext();
  const [eventFilter, setEventFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const { setPageTitle } = usePageTitle();

  useEffect(() => {
    setPageTitle('Timeline', 'Chronological view of all incidents and events', [
      { label: 'Timeline', href: '/timeline' },
    ]);
  }, [setPageTitle]);

  useEffect(() => {
    loadIncidents({ page_size: 100 });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const [allEvents, setAllEvents] = useState<IncidentEvent[]>([]);
  const [loadingEvents, setLoadingEvents] = useState(true);

  useEffect(() => {
    const loadAllEvents = async () => {
      try {
        setLoadingEvents(true);
        const eventsPromises = state.incidents.map(async (incident) => {
          try {
            const timeline: TimelineResponse = await incidentService.getIncidentTimeline(incident.id);
            return timeline.events.map((event) => ({ ...event, incident_id: incident.id }));
          } catch {
            return [];
          }
        });
        const eventsArrays = await Promise.all(eventsPromises);
        setAllEvents(eventsArrays.flat());
      } finally {
        setLoadingEvents(false);
      }
    };

    if (state.incidents.length > 0) loadAllEvents();
    else setLoadingEvents(false);
  }, [state.incidents]);

  const filteredEvents = allEvents
    .filter((event) => {
      if (eventFilter !== 'all' && event.event_type !== eventFilter) return false;
      if (searchTerm && !event.description.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'incident_created':
        return <Plus className="h-3.5 w-3.5" aria-hidden="true" />;
      case 'incident_updated':
        return <Activity className="h-3.5 w-3.5" aria-hidden="true" />;
      case 'incident_resolved':
        return <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />;
      case 'investigation_started':
      case 'investigation_completed':
        return <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />;
      case 'alert_triggered':
      case 'alert_acknowledged':
        return <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />;
      default:
        return <Clock className="h-3.5 w-3.5" aria-hidden="true" />;
    }
  };

  const eventTypeOptions = [
    { value: 'all', label: 'All Events' },
    { value: 'incident_created', label: 'Incident Created' },
    { value: 'incident_updated', label: 'Incident Updated' },
    { value: 'incident_resolved', label: 'Incident Resolved' },
    { value: 'investigation_started', label: 'Investigation Started' },
    { value: 'investigation_completed', label: 'Investigation Completed' },
    { value: 'alert_triggered', label: 'Alert Triggered' },
    { value: 'alert_acknowledged', label: 'Alert Acknowledged' },
  ];

  return (
    <div className="page-stack">
      <PageHeader
        title="Timeline"
        description="Chronological view of incidents and operational events"
      />

      <Card className="filters-panel">
        <CardHeader className="panel-card-header compact">
          <CardTitle>Filters</CardTitle>
          <CardDescription>Filter events by type and search</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="filters-row">
            <div className="flex items-center gap-2 min-w-0">
              <Filter className="h-4 w-4 text-app-muted shrink-0" aria-hidden="true" />
              <span className="text-sm text-app-muted whitespace-nowrap">Event type</span>
              <Select value={eventFilter} onValueChange={setEventFilter}>
                <SelectTrigger className="w-[11rem] sm:w-[12.5rem]" aria-label="Event type filter">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {eventTypeOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2 min-w-0 flex-1 sm:max-w-xs sm:ml-auto">
              <Search className="h-4 w-4 text-app-muted shrink-0" aria-hidden="true" />
              <Input
                type="search"
                placeholder="Search events…"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
                aria-label="Search events"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="timeline-stream-card panel-card">
        <CardHeader>
          <CardTitle>Event timeline</CardTitle>
          <CardDescription>
            {filteredEvents.length === 0
              ? 'No events match your filters'
              : `${filteredEvents.length} event${filteredEvents.length === 1 ? '' : 's'} · newest first`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingEvents ? (
            <div className="loading-container py-14">
              <div className="loading-spinner h-12 w-12" />
            </div>
          ) : filteredEvents.length === 0 ? (
            <div className="empty-state py-12">
              <Clock className="empty-state-icon" />
              <h3 className="empty-state-title">No events found</h3>
              <p className="empty-state-text">Try clearing filters or adjusting your search.</p>
              <Button
                variant="outline"
                onClick={() => {
                  setEventFilter('all');
                  setSearchTerm('');
                }}
              >
                Clear filters
              </Button>
            </div>
          ) : (
            <div className="vtimeline-stage">
              <div className="vtimeline">
                <div className="vtimeline-rail" aria-hidden="true" />
                <ol className="vtimeline-list">
                  {filteredEvents.map((event, index) => {
                    const incident = state.incidents.find((i) => i.id === event.incident_id);
                    const meta = getTimelineEventMeta(event.event_type);
                    const headline = incident?.title ?? meta.label;
                    const side = index % 2 === 0 ? 'left' : 'right';
                    const cardMod = `vtimeline-card--${event.event_type.replace(/_/g, '-')}`;

                    return (
                      <li
                        key={event.id}
                        className={cn(
                          'vtimeline-item',
                          side === 'left' ? 'vtimeline-item--left' : 'vtimeline-item--right',
                          index === 0 && 'vtimeline-item--hot'
                        )}
                        style={{ animationDelay: `${Math.min(index * 0.05, 0.6)}s` }}
                      >
                        <span className="vtimeline-connector" aria-hidden="true" />
                        <span className="vtimeline-node" aria-hidden="true" />
                        <div className="vtimeline-card-col">
                          <article className={cn('vtimeline-card', cardMod)}>
                            <div className="vtimeline-card-head">
                              <span className={meta.badgeClass}>
                                {getEventTypeIcon(event.event_type)}
                                {meta.label}
                              </span>
                              <time
                                className="text-xs font-medium text-app-muted whitespace-nowrap tabular-nums"
                                dateTime={event.created_at}
                                title={formatAbsoluteTime(event.created_at)}
                              >
                                {formatTimelineEventTime(event.created_at)}
                              </time>
                            </div>
                            <div className="vtimeline-card-title-row">
                              <h3 className="vtimeline-card-title">{headline}</h3>
                              {incident && (
                                <>
                                  <Badge className={severityBadgeClass(incident.severity)}>
                                    {incident.severity}
                                  </Badge>
                                  <Badge className={statusBadgeClass(incident.status)}>
                                    {incident.status}
                                  </Badge>
                                </>
                              )}
                            </div>
                            {event.description && (
                              <p className="vtimeline-card-desc">{event.description}</p>
                            )}
                            {event.old_values && Object.keys(event.old_values).length > 0 && (
                              <pre className="vtimeline-payload">
                                {JSON.stringify(event.old_values, null, 2)}
                              </pre>
                            )}
                            <footer className="vtimeline-card-foot">
                              <span>
                                {incident?.service ? (
                                  <>
                                    Service:{' '}
                                    <strong className="text-app-ink font-medium">{incident.service}</strong>
                                  </>
                                ) : (
                                  <span className="font-mono text-[0.65rem]">{event.incident_id}</span>
                                )}
                              </span>
                              <Link to={`/incidents/${event.incident_id}`} className="vtimeline-cta">
                                View incident →
                              </Link>
                            </footer>
                          </article>
                        </div>
                      </li>
                    );
                  })}
                </ol>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
