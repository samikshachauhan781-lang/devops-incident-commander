// Badge component for DevOps Incident Commander
import React from 'react';
import { cn } from '@utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'secondary' | 'outline';
}

const variantClasses = {
  default: 'badge-token badge-token-default',
  primary: 'badge-token badge-token-primary',
  success: 'badge-token badge-token-success',
  warning: 'badge-token badge-token-warning',
  danger: 'badge-token badge-token-danger',
  secondary: 'badge-token badge-token-secondary',
  outline: 'badge-token badge-token-outline',
};

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide',
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
