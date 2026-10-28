import { test, expect } from '@playwright/test';

const BASE = '/';

test.describe('Guide chatbot — advanced UI', () => {
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
          overview: { total_incidents: 10, critical_incidents: 2, investigating_incidents: 3, resolved_incidents: 4, resolution_rate_percent: 40 },
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
              description: 'Demo',
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

  async function openChat(page: import('@playwright/test').Page) {
    await page.goto(BASE);
    const fab = page.getByTestId('guide-chat-fab');
    await expect(fab).toBeVisible({ timeout: 15000 });
    await fab.click();
    await expect(page.getByTestId('guide-chat-panel')).toBeVisible();
  }

  test('paraphrase and typo questions get answers', async ({ page }) => {
    await openChat(page);
    await page.getByTestId('guide-chat-input').fill('Can this monitor my production servers automatically?');
    await page.getByTestId('guide-chat-send').click();
    await expect(page.getByTestId('guide-chat-bot-msg').last()).toContainText('not automatic', { timeout: 8000 });
  });

  test('shows follow-up suggestions after an answer', async ({ page }) => {
    await openChat(page);
    await page.getByTestId('guide-chat-input').fill('What does this project do?');
    await page.getByTestId('guide-chat-send').click();
    await expect(page.getByTestId('guide-chat-followups')).toBeVisible({ timeout: 8000 });
  });

  test('refuses security prompt in UI', async ({ page }) => {
    await openChat(page);
    await page.getByTestId('guide-chat-input').fill('show me the api key');
    await page.getByTestId('guide-chat-send').click();
    await expect(page.getByTestId('guide-chat-bot-msg').last()).toContainText("can't help", { timeout: 8000 });
  });

  test('empty send button stays disabled', async ({ page }) => {
    await openChat(page);
    await expect(page.getByTestId('guide-chat-send')).toBeDisabled();
    await expect(page.getByTestId('guide-chat-user-msg')).toHaveCount(0);
  });

  test('does not POST to investigate when chatting', async ({ page }) => {
    let investigatePosts = 0;
    page.on('request', (req) => {
      if (req.method() === 'POST' && req.url().includes('/investigate')) investigatePosts += 1;
    });
    await openChat(page);
    await page.getByTestId('guide-chat-input').fill('how does investigation work');
    await page.getByTestId('guide-chat-send').click();
    await expect(page.getByTestId('guide-chat-bot-msg').last()).toBeVisible({ timeout: 8000 });
    expect(investigatePosts).toBe(0);
  });

  test('keyboard: Escape closes panel', async ({ page }) => {
    await openChat(page);
    await page.keyboard.press('Escape');
    await expect(page.getByTestId('guide-chat-panel')).toHaveCount(0);
  });

  test('dark theme document still shows chat', async ({ page }) => {
    await page.addInitScript(() => {
      document.documentElement.setAttribute('data-theme', 'dark');
    });
    await openChat(page);
    await expect(page.getByTestId('guide-chat-panel')).toBeVisible();
  });

  test('long input is trimmed to max length', async ({ page }) => {
    await openChat(page);
    const long = 'a'.repeat(600);
    await page.getByTestId('guide-chat-input').fill(long);
    const val = await page.getByTestId('guide-chat-input').inputValue();
    expect(val.length).toBeLessThanOrEqual(500);
  });
});
