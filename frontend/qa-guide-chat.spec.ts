import { test, expect } from '@playwright/test';
import { findGuideAnswer } from './src/lib/guideChatEngine';

const BASE = '/';

test.describe('Guide engine (unit)', () => {
  test('matches known topics and fallback', () => {
    expect(findGuideAnswer('What is DevOps Incident Commander?').topicId).toBe('what-is');
    expect(findGuideAnswer('is this a demo or real monitoring').topicId).toBe('demo');
    expect(findGuideAnswer('xyzzy unknown qwerty').topicId).toBe('fallback');
  });
});

test.describe('Guide chatbot (homepage)', () => {
  test.setTimeout(60_000);

  test.beforeEach(async ({ page }) => {
    await page.route('**/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy', demo_mode: true, database: 'incidents_demo.db' }),
      });
    });
    await page.route('**/analytics/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          overview: {
            total_incidents: 10,
            critical_incidents: 2,
            investigating_incidents: 3,
            resolved_incidents: 4,
            resolution_rate_percent: 40,
          },
          severity: [],
          status: [],
        }),
      });
    });
    await page.route('**/incidents?**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          incidents: [
            {
              id: 'demo-001',
              title: 'Sample incident',
              description: 'Demo incident for UI tests',
              severity: 'high',
              status: 'open',
              service: 'api',
              created_at: '2026-08-15T12:00:00+00:00',
              updated_at: '2026-08-15T12:00:00+00:00',
            },
          ],
          page: 1,
          page_size: 8,
          total: 1,
        }),
      });
    });
  });

  test('FAB visible only on dashboard', async ({ page }) => {
    await page.goto(BASE);
    await expect(page.getByTestId('guide-chat-fab')).toBeVisible({ timeout: 15000 });
    await page.goto('/incidents');
    await expect(page.getByTestId('guide-chat-fab')).not.toBeVisible();
  });

  test('opens panel, shows welcome and suggestion', async ({ page }) => {
    await page.goto(BASE);
    const fab = page.getByTestId('guide-chat-fab');
    await expect(fab).toBeVisible({ timeout: 5000 });
    await fab.evaluate((el) => (el as HTMLButtonElement).click());
    await expect(page.getByTestId('guide-chat-panel')).toBeVisible();
    await expect(page.getByTestId('guide-chat-messages')).toContainText('documentation-based');
    await expect(page.getByTestId('guide-chat-suggestions')).toBeVisible();
  });

  test('sends a question and receives an answer', async ({ page }) => {
    await page.goto(BASE);
    const fab = page.getByTestId('guide-chat-fab');
    await expect(fab).toBeVisible({ timeout: 20000 });
    await fab.evaluate((el) => (el as HTMLButtonElement).click());
    await page.getByTestId('guide-chat-input').fill('What is DevOps Incident Commander?');
    await page.getByTestId('guide-chat-send').click();
    await expect(page.getByTestId('guide-chat-user-msg')).toContainText('DevOps Incident Commander');
    await expect(page.getByTestId('guide-chat-bot-msg').last()).toContainText('web app', {
      timeout: 5000,
    });
  });

  test('closes and reopens', async ({ page }) => {
    await page.goto(BASE);
    const fab = page.getByTestId('guide-chat-fab');
    await expect(fab).toBeVisible({ timeout: 20000 });
    await fab.evaluate((el) => (el as HTMLButtonElement).click());
    await expect(page.getByTestId('guide-chat-panel')).toBeVisible();
    await page.getByTestId('guide-chat-header-close').click();
    await expect(page.getByTestId('guide-chat-panel')).toHaveCount(0);
    await page.getByTestId('guide-chat-fab').evaluate((el) => (el as HTMLButtonElement).click());
    await expect(page.getByTestId('guide-chat-panel')).toBeVisible();
  });

  test('mobile viewport layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE);
    const fab = page.getByTestId('guide-chat-fab');
    await expect(fab).toBeVisible({ timeout: 20000 });
    await fab.evaluate((el) => (el as HTMLButtonElement).click());
    const panel = page.getByTestId('guide-chat-panel');
    await expect(panel).toBeVisible();
    const box = await panel.boundingBox();
    expect(box).toBeTruthy();
    if (box) {
      expect(box.width).toBeLessThanOrEqual(375);
    }
  });
});
