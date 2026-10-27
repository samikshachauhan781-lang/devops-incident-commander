// Button component for DevOps Incident Commander
import React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '@utils/cn';

const buttonVariants = {
  variant: {
    default:
      'text-white border shadow-sm bg-[var(--color-accent)] border-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] hover:border-[var(--color-accent-hover)]',
    destructive: 'bg-rose-600 text-white border border-rose-600 hover:bg-rose-700',
    outline:
      'bg-[var(--app-surface)] text-[var(--app-ink)] border border-[var(--app-line)] hover:bg-[color-mix(in_srgb,var(--app-ink)_5%,transparent)]',
    secondary:
      'bg-[color-mix(in_srgb,var(--app-ink)_6%,transparent)] text-[var(--app-ink)] border border-[var(--app-line)] hover:bg-[color-mix(in_srgb,var(--app-ink)_10%,transparent)]',
    ghost:
      'text-[var(--app-muted)] hover:bg-[color-mix(in_srgb,var(--app-ink)_6%,transparent)] hover:text-[var(--app-ink)] border-transparent',
    link: 'text-[var(--color-accent)] underline-offset-4 hover:underline p-0 h-auto border-transparent',
  },
  size: {
    default: 'h-10 px-4 py-2 text-sm',
    sm: 'h-8 px-3 text-xs',
    lg: 'h-11 px-5 text-sm',
    icon: 'h-10 w-10',
  },
};

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof buttonVariants.variant;
  size?: keyof typeof buttonVariants.size;
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    const variantClass = buttonVariants.variant[variant] || buttonVariants.variant.default;
    const sizeClass = buttonVariants.size[size] || buttonVariants.size.default;

    return (
      <Comp
        className={cn(
          'inline-flex items-center justify-center whitespace-nowrap rounded-lg font-medium ring-offset-[var(--app-bg)] transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
          variantClass,
          sizeClass,
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = 'Button';

export { Button };
