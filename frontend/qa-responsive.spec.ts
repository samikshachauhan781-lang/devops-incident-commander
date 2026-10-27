import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:4173';

const VIEWPORTS = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'large-desktop', width: 1920, height: 1080 },
] as const;

const ROUTES = ['/', '/incidents', '/timeline', '/analytics', '/settings'] as const;

async function assertNoHorizontalOverflow(page: import('@playwright/test').Page) {
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    const main = document.querySelector('.app-main-scroll');
    return {
      document: doc.scrollWidth - doc.clientWidth,
      main: main ? (main as HTMLElement).scrollWidth - (main as HTMLElement).clientWidth : 0,
    };
  });
  expect(overflow.document).toBeLessThanOrEqual(2);
  expect(overflow.main).toBeLessThanOrEqual(2);
}

for (const vp of VIEWPORTS) {
  test.describe(`Responsive ${vp.name} (${vp.width}px)`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
    });

    for (const route of ROUTES) {
      test(`${route} renders without horizontal overflow`, async ({ page }) => {
        await page.goto(`${BASE}${route === '/' ? '' : route}`);
        await page.waitForSelector('.page-title, .loading-container', { timeout: 15000 });
        await assertNoHorizontalOverflow(page);
      });
    }

    if (vp.width >= 1280) {
      test('sidebar fixed without internal scroll', async ({ page }) => {
        await page.goto(BASE);
        const sidebar = page.locator('.app-sidebar');
        await expect(sidebar).toBeVisible();
        const metrics = await sidebar.evaluate((el) => ({
          overflowY: getComputedStyle(el).overflowY,
          scrollHeight: el.scrollHeight,
          clientHeight: el.clientHeight,
        }));
        expect(metrics.overflowY).toBe('hidden');
        expect(metrics.scrollHeight).toBeLessThanOrEqual(metrics.clientHeight + 1);
      });
    }

    if (vp.width < 1024) {
      test('mobile menu navigates to incidents', async ({ page }) => {
        await page.goto(BASE);
        await page.getByRole('button', { name: 'Open navigation menu' }).click();
        await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Analytics' }).click();
        await expect(page.locator('.page-title')).toContainText('Analytics');
      });
    }
  });
}
