/** Shared incident presentation helpers for consistent UI across pages. */

export function severityBadgeClass(severity: string): string {
  switch (severity) {
    case 'critical':
      return 'badge-severity-critical';
    case 'high':
      return 'badge-severity-high';
    case 'medium':
      return 'badge-severity-medium';
    case 'low':
      return 'badge-severity-low';
    default:
      return 'badge-muted';
  }
}

export function statusBadgeClass(status: string): string {
  switch (status) {
    case 'open':
      return 'badge-status-open';
    case 'investigating':
      return 'badge-status-investigating';
    case 'resolved':
      return 'badge-status-resolved';
    case 'closed':
      return 'badge-status-closed';
    default:
      return 'badge-muted';
  }
}

export function formatIncidentDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

export function capitalizeLabel(value: string): string {
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1);
}
