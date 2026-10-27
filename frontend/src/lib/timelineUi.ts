/** Timeline event presentation tokens */

export type TimelineEventMeta = {
  label: string;
  badgeClass: string;
  signalTone: string;
};

export const TIMELINE_EVENT_META: Record<string, TimelineEventMeta> = {
  incident_created: {
    label: 'Incident created',
    badgeClass: 'timeline-badge timeline-badge-created',
    signalTone: 'signal-tone-created',
  },
  incident_updated: {
    label: 'Incident updated',
    badgeClass: 'timeline-badge timeline-badge-updated',
    signalTone: 'signal-tone-updated',
  },
  incident_resolved: {
    label: 'Incident resolved',
    badgeClass: 'timeline-badge timeline-badge-resolved',
    signalTone: 'signal-tone-resolved',
  },
  investigation_started: {
    label: 'Investigation started',
    badgeClass: 'timeline-badge timeline-badge-investigation',
    signalTone: 'signal-tone-investigation',
  },
  investigation_completed: {
    label: 'Investigation completed',
    badgeClass: 'timeline-badge timeline-badge-investigation-done',
    signalTone: 'signal-tone-investigation-done',
  },
  alert_triggered: {
    label: 'Alert triggered',
    badgeClass: 'timeline-badge timeline-badge-alert',
    signalTone: 'signal-tone-alert',
  },
  alert_acknowledged: {
    label: 'Alert acknowledged',
    badgeClass: 'timeline-badge timeline-badge-ack',
    signalTone: 'signal-tone-ack',
  },
};

export function getTimelineEventMeta(eventType: string): TimelineEventMeta {
  return (
    TIMELINE_EVENT_META[eventType] ?? {
      label: eventType.replace(/_/g, ' '),
      badgeClass: 'timeline-badge timeline-badge-default',
      signalTone: 'signal-tone-default',
    }
  );
}

function parseEventDate(dateString: string): Date {
  const d = new Date(dateString);
  return Number.isNaN(d.getTime()) ? new Date(0) : d;
}

function isSameCalendarDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

function formatClockTime(date: Date): string {
  return date.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  });
}

/** Full timestamp for tooltips and screen readers */
export function formatAbsoluteTime(dateString: string): string {
  const date = parseEventDate(dateString);
  const now = new Date();
  const includeYear = date.getFullYear() !== now.getFullYear();

  return date.toLocaleString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: includeYear ? 'numeric' : undefined,
    hour: 'numeric',
    minute: '2-digit',
  });
}

/**
 * Primary label on timeline cards: precise for recent events, absolute date for older ones.
 */
export function formatTimelineEventTime(dateString: string): string {
  const date = parseEventDate(dateString);
  if (Number.isNaN(date.getTime()) || date.getTime() === 0) {
    return 'Unknown time';
  }

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();

  if (diffMs < 0) {
    return formatAbsoluteTime(dateString);
  }

  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);

  if (diffMin < 1) {
    return 'Just now';
  }

  if (isSameCalendarDay(date, now)) {
    if (diffMin < 60) {
      return diffMin === 1 ? '1 min ago' : `${diffMin} min ago`;
    }
    if (diffHour < 24) {
      return diffHour === 1 ? '1 hour ago' : `${diffHour} hours ago`;
    }
    return `Today, ${formatClockTime(date)}`;
  }

  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (isSameCalendarDay(date, yesterday)) {
    return `Yesterday, ${formatClockTime(date)}`;
  }

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays < 7) {
    return date.toLocaleString(undefined, {
      weekday: 'short',
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  const includeYear = date.getFullYear() !== now.getFullYear();
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: includeYear ? 'numeric' : undefined,
    hour: 'numeric',
    minute: '2-digit',
  });
}

/** @deprecated Use formatTimelineEventTime */
export function formatRelativeTime(dateString: string): string {
  return formatTimelineEventTime(dateString);
}

export function groupEventsByDay<T extends { created_at: string }>(
  events: T[]
): { key: string; label: string; events: T[] }[] {
  const groups = new Map<string, T[]>();
  const now = new Date();

  for (const event of events) {
    const d = parseEventDate(event.created_at);
    const key = d.toDateString();
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(event);
  }

  return Array.from(groups.entries()).map(([key, list]) => {
    const d = new Date(key);
    let label: string;
    if (isSameCalendarDay(d, now)) label = 'Today';
    else if (isSameCalendarDay(d, new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1))) {
      label = 'Yesterday';
    } else {
      label = d.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });
    }
    return { key, label, events: list };
  });
}
