/**
 * API base URL for axios. Local dev uses Vite `/api` proxy; production uses VITE_API_BASE_URL.
 */
export function getApiBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL?.trim();
  if (fromEnv) {
    return fromEnv.replace(/\/+$/, '');
  }
  if (import.meta.env.DEV) {
    return '/api';
  }
  if (import.meta.env.PROD) {
    console.warn(
      '[api] VITE_API_BASE_URL is not set. Set it in Render (static site env) and redeploy.',
    );
  }
  return '';
}
