import React from 'react';
import { cn } from '@utils/cn';
import type { LucideIcon } from 'lucide-react';

type MetricCardProps = {
  label: string;
  value: number | string;
  hint?: string;
  icon: LucideIcon;
  tone?: 'default' | 'critical' | 'info' | 'success' | 'warning';
  className?: string;
};

const toneIconClass = {
  default: 'metric-card-icon-default',
  critical: 'metric-card-icon-critical',
  info: 'metric-card-icon-info',
  success: 'metric-card-icon-success',
  warning: 'metric-card-icon-warning',
};

const toneValueClass = {
  default: 'metric-card-value-default',
  critical: 'metric-card-value-critical',
  info: 'metric-card-value-info',
  success: 'metric-card-value-success',
  warning: 'metric-card-value-warning',
};

export function MetricCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = 'default',
  className,
}: MetricCardProps) {
  return (
    <div className={cn('metric-card', className)}>
      <div className="metric-card-top">
        <p className="metric-card-label">{label}</p>
        <div className={cn('metric-card-icon', toneIconClass[tone])} aria-hidden="true">
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className={cn('metric-card-value', toneValueClass[tone])}>{value}</p>
      {hint ? <p className="metric-card-hint">{hint}</p> : null}
    </div>
  );
}
