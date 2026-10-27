import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:4173';

async function resetAppearanceStorage(page: import('@playwright/test').Page) {
  await page.goto(`${BASE}/`);
  await page.evaluate(() => {
    const light = { darkMode: false, primaryColor: '#4f46e5' };
    localStorage.setItem('dic-appearance', JSON.stringify(light));
    localStorage.setItem('app-settings', JSON.stringify({ appearance: light }));
  });
  await page.reload();
}

async function openAppearance(page: import('@playwright/test').Page) {
  await page.goto(`${BASE}/settings`);
  await expect(page.locator('.page-title')).toContainText('Settings', { timeout: 15000 });
  await page.getByRole('button', { name: 'Appearance settings' }).click();
  await expect(page.getByText('Switch between light and dark color schemes')).toBeVisible();
}

test.describe('Theme — dark mode and accent', () => {
  test.beforeEach(async ({ page }) => {
    await resetAppearanceStorage(page);
  });

  test('dark mode toggles document theme immediately (desktop)', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openAppearance(page);

    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');

    const darkSwitch = page.locator('#darkMode');
    await darkSwitch.click();

    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    await expect(page.locator('html')).toHaveClass(/dark/);

    const bodyBg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    expect(bodyBg).not.toBe('rgb(244, 246, 251)');
  });

  test('theme persists after reload', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openAppearance(page);
    await page.locator('#darkMode').click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark', { timeout: 15000 });
  });

  test('accent color updates CSS variable immediately', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openAppearance(page);

    await page.getByRole('button', { name: 'Red' }).click();
    const accent = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim()
    );
    expect(accent.toLowerCase()).toBe('#ef4444');
  });

  test('theme survives navigation across routes', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openAppearance(page);
    await page.locator('#darkMode').click();

    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page.locator('.page-title')).toContainText('Dashboard');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

    await page.getByRole('link', { name: 'Analytics' }).click();
    await expect(page.locator('.page-title')).toContainText('Analytics');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  });

  test('dark mode on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await openAppearance(page);
    await page.locator('#darkMode').click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    await page.getByRole('button', { name: 'Open navigation menu' }).click();
    await page.getByRole('link', { name: 'Incidents' }).click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  });
});
