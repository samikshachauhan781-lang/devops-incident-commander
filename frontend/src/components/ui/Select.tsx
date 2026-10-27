// Select component for DevOps Incident Commander
import React from 'react';
import * as SelectPrimitives from '@radix-ui/react-select';
import { cn } from '@utils/cn';

const Select = SelectPrimitives.Root;

const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitives.Trigger>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitives.Trigger>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitives.Trigger
    ref={ref}
    className={cn(
      'flex h-10 w-full items-center justify-between rounded-md border border-[var(--app-line)] bg-[var(--app-surface)] text-[var(--app-ink)] px-3 py-2 text-sm ring-offset-[var(--app-bg)] placeholder:text-[var(--app-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      '[&>span]:line-clamp-1',
      className
    )}
    {...props}
  >
    {children}
    <SelectPrimitives.Icon className="h-4 w-4 opacity-50" />
  </SelectPrimitives.Trigger>
));
SelectTrigger.displayName = SelectPrimitives.Trigger.displayName;

const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitives.Content>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitives.Content>
>(({ className, children, position = 'popper', ...props }, ref) => (
  <SelectPrimitives.Portal>
    <SelectPrimitives.Content
      ref={ref}
      className={cn(
        'relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border border-[var(--app-line)] bg-[var(--app-surface-elevated)] text-[var(--app-ink)] shadow-card data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-top-1/2 data-[state=open]:slide-in-from-top-1/2',
        position === 'popper' &&
          'data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1',
        className
      )}
      position={position}
      {...props}
    >
      <SelectPrimitives.Viewport className={cn('p-1', position === 'popper' && 'h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]')}
      >
        {children}
      </SelectPrimitives.Viewport>
      <SelectPrimitives.ScrollDownButton className="flex cursor-default items-center justify-center py-1" />
      <SelectPrimitives.ScrollUpButton className="flex cursor-default items-center justify-center py-1" />
      <SelectPrimitives.Arrow className="border-gray-200" />
    </SelectPrimitives.Content>
  </SelectPrimitives.Portal>
));
SelectContent.displayName = SelectPrimitives.Content.displayName;

const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitives.Item>,
  React.ComponentPropsWithoutRef<typeof SelectPrimitives.Item>
>(({ className, children, ...props }, ref) => (
  <SelectPrimitives.Item
    ref={ref}
    className={cn(
      'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none text-[var(--app-ink)] data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      'data-[highlighted]:bg-[color-mix(in_srgb,var(--color-accent)_12%,transparent)] data-[highlighted]:text-[var(--app-ink)]',
      'data-[state=selected]:bg-[var(--color-accent-soft)] data-[state=selected]:text-[var(--app-ink)]',
      className
    )}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <SelectPrimitives.ItemIndicator>
        <span className="h-2 w-2 rounded-full bg-[var(--color-accent)]" />
      </SelectPrimitives.ItemIndicator>
    </span>
    <SelectPrimitives.ItemText>{children}</SelectPrimitives.ItemText>
  </SelectPrimitives.Item>
));
SelectItem.displayName = SelectPrimitives.Item.displayName;

const SelectValue = SelectPrimitives.Value;

export { Select, SelectTrigger, SelectContent, SelectItem, SelectValue };