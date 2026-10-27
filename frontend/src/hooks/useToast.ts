// Toast hook for DevOps Incident Commander
import React from 'react';
import { ToastAction, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport, ToastContext, ToasterToast } from '../components/ui/Toast';
import { cn } from '@utils/cn';

const TOAST_LIMIT = 1;
const TOAST_REMOVE_DELAY = 1000000;

const actionTypes = {
  ADD_TOAST: 'ADD_TOAST',
  UPDATE_TOAST: 'UPDATE_TOAST',
  DISMISS_TOAST: 'DISMISS_TOAST',
  REMOVE_TOAST: 'REMOVE_TOAST',
} as const;

type ActionType = typeof actionTypes;

export type Toast = Omit<ToasterToast, 'id'>;

let count = 0;
function genId() {
  count = (count + 1) % Number.MAX_VALUE;
  return count.toString();
}

// Use shared ToastContext from Toast.tsx
function useToastContext() {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error('useToastContext must be used within a ToastProvider');
  }
  return context;
}

function useToast() {
  const context = useToastContext();

  // Toast function that has access to the current dispatch
  const toastFn = ({ ...props }: Toast) => {
    const toastId = genId();
    const update = (props: ToasterToast) => context.dispatch({ type: actionTypes.UPDATE_TOAST, toast: { ...props, id: toastId } });
    const dismiss = () => context.dispatch({ type: actionTypes.DISMISS_TOAST, toastId });

    context.dispatch({
      type: actionTypes.ADD_TOAST,
      toast: {
        ...props,
        id: toastId,
        open: true,
        onOpenChange: (open: boolean) => {
          if (!open) dismiss();
        },
      },
    });

    return { id: toastId, dismiss, update };
  };

  const addToRemoveQueue = (toastId: string) => {
    if (context.toastTimeouts.has(toastId)) return;
    const timeout = setTimeout(() => {
      context.setToastTimeouts(prev => {
        const newTimeouts = new Map(prev);
        newTimeouts.delete(toastId);
        return newTimeouts;
      });
      context.dispatch({ type: actionTypes.REMOVE_TOAST, toastId });
    }, TOAST_REMOVE_DELAY);
    context.setToastTimeouts(prev => {
      const newTimeouts = new Map(prev);
      newTimeouts.set(toastId, timeout);
      return newTimeouts;
    });
  };

  React.useEffect(() => {
    return () => {
      context.toastTimeouts.forEach((timeout) => clearTimeout(timeout));
    };
  }, [context.toastTimeouts]);

  return {
    toast: toastFn,
    dismiss: (toastId?: string) => context.dispatch({ type: actionTypes.DISMISS_TOAST, toastId }),
    state: context.state,
  };
}

export { useToast };