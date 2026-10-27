import { defineConfig } from '@playwright/test';

const previewPort = process.env.PLAYWRIGHT_PREVIEW_PORT || '4188';
const baseURL = process.env.PLAYWRIGHT_BASE_URL || `http://127.0.0.1:${previewPort}`;

export default defineConfig({
  testDir: '.',
  testMatch: ['qa-*.spec.ts', 'browser-test.spec.ts'],
  timeout: 60_000,
  use: {
    baseURL,
  },
  webServer: {
    command: `npm run preview -- --host 127.0.0.1 --port ${previewPort}`,
    url: baseURL,
    reuseExistingServer: !process.env.PLAYWRIGHT_FORCE_NEW_SERVER,
    timeout: 120_000,
  },
});
