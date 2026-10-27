import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:4173';
const API = 'http://127.0.0.1:8000';

test.describe('Final QA — pages and layout', () => {
  test('Dashboard loads with metrics and demo incidents', async ({ page }) => {
    await page.goto(BASE);
    await expect(page.locator('.page-title')).toContainText('Dashboard', { timeout: 15000 });
    await expect(page.locator('.metric-card')).toHaveCount(4);
    await expect(page.getByRole('heading', { name: 'Recent incidents' })).toBeVisible();
    await expect(page.locator('.incident-feed-title').first()).toContainText('Payment Gateway');
  });

  test('Incidents page — filters and list', async ({ page }) => {
    await page.goto(`${BASE}/incidents`);
    await expect(page.locator('.page-title')).toContainText('Incidents');
    await expect(page.getByRole('heading', { name: 'Filters' })).toBeVisible();
    await expect(page.locator('#incident-filter-search')).toBeVisible();
    await page.locator('#incident-filter-search').fill('Payment');
    await expect(page.getByText('Payment Gateway Timeout on Checkout')).toBeVisible({ timeout: 10000 });
  });

  test('Timeline page loads', async ({ page }) => {
    await page.goto(`${BASE}/timeline`);
    await expect(page.locator('.page-title')).toContainText('Timeline');
    await expect(page.getByRole('heading', { name: 'Filters' })).toBeVisible();
  });

  test('Analytics page loads with charts', async ({ page }) => {
    await page.goto(`${BASE}/analytics`);
    await expect(page.locator('.page-title')).toContainText('Analytics');
    await expect(page.locator('.metric-card').first()).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole('heading', { name: 'Severity Breakdown' })).toBeVisible();
  });

  test('Settings page loads and section nav works', async ({ page }) => {
    await page.goto(`${BASE}/settings`);
    await expect(page.locator('.page-title')).toContainText('Settings');
    await page.getByRole('button', { name: 'Notifications settings' }).click();
    await expect(page.getByText('Configure how you receive alerts')).toBeVisible();
  });

  test('Sidebar fixed — no internal scroll (desktop)', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(BASE);
    const sidebar = page.locator('.app-sidebar');
    await expect(sidebar).toBeVisible();
    const metrics = await sidebar.evaluate((el) => ({
      scrollHeight: el.scrollHeight,
      clientHeight: el.clientHeight,
      overflowY: getComputedStyle(el).overflowY,
    }));
    expect(metrics.overflowY).toBe('hidden');
    expect(metrics.scrollHeight).toBeLessThanOrEqual(metrics.clientHeight + 1);
    const mainScroll = await page.locator('.app-main-scroll').evaluate((el) => getComputedStyle(el).overflowY);
    expect(mainScroll).toBe('auto');
  });

  test('Mobile drawer opens and navigates', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(BASE);
    await page.getByRole('button', { name: 'Open navigation menu' }).click();
    await page.getByRole('link', { name: 'Incidents' }).click();
    await expect(page.locator('.page-title')).toContainText('Incidents');
  });

  test('Invalid incident deep link shows not found', async ({ page }) => {
    await page.goto(`${BASE}/incidents/not-a-real-id-00000000`);
    await expect(page.getByText('Incident not found')).toBeVisible({ timeout: 15000 });
  });

  test('Investigation action from incident detail', async ({ page }) => {
    const res = await fetch(`${API}/incidents?page_size=1`);
    const data = await res.json();
    const id = data.incidents[0].id;
    await page.goto(`${BASE}/incidents/${id}`);
    await expect(page.locator('.page-title')).not.toContainText('Dashboard', { timeout: 15000 });
    await page.getByRole('button', { name: 'Start Investigation' }).click();
    await expect(page.getByText('Investigation started', { exact: true })).toBeVisible({ timeout: 15000 });
  });

  test('Main nav links all routes', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(BASE);
    const routes = [
      { link: 'Incidents', title: 'Incidents' },
      { link: 'Timeline', title: 'Timeline' },
      { link: 'Analytics', title: 'Analytics' },
      { link: 'Settings', title: 'Settings' },
      { link: 'Dashboard', title: 'Dashboard' },
    ];
    for (const r of routes) {
      await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: r.link }).click();
      await expect(page.locator('.page-title')).toContainText(r.title);
    }
  });
});
