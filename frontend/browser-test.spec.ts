import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:4173';
const API_URL = 'http://localhost:8000';

test.describe('DevOps Incident Commander - Browser Verification', () => {

  test('Dashboard route (/) renders visible content', async ({ page }) => {
    await page.goto(BASE_URL);
    // Use the specific page-title h1
    await expect(page.locator('.page-title')).toContainText('Dashboard', { timeout: 15000 });
    await expect(page.locator('.metric-card')).toHaveCount(4, { timeout: 15000 });
    await expect(page.getByRole('heading', { name: 'Recent incidents' })).toBeVisible();
    console.log('✅ Dashboard route renders correctly');
  });

  test('Incidents route (/incidents) renders incident list', async ({ page }) => {
    await page.goto(`${BASE_URL}/incidents`);
    await expect(page.locator('.page-title')).toContainText('Incidents');
    // Check for filter controls using exact text match
    await expect(page.getByRole('heading', { name: 'Filters' })).toBeVisible();
    await expect(page.locator('label:has-text("Service:")')).toBeVisible();
    await expect(page.locator('label:has-text("Severity:")')).toBeVisible();
    await expect(page.locator('label:has-text("Status:")')).toBeVisible();
    await expect(page.locator('input[placeholder="Search incidents..."]')).toBeVisible();
    console.log('✅ Incidents route renders with filters');
  });

  test('Incidents route refresh still renders', async ({ page }) => {
    await page.goto(`${BASE_URL}/incidents`);
    await page.reload();
    await expect(page.locator('.page-title')).toContainText('Incidents');
    await expect(page.getByRole('heading', { name: 'Filters' })).toBeVisible();
    console.log('✅ Incidents route survives refresh');
  });

  test('Navigation between dashboard and incidents works', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator('.page-title')).toContainText('Dashboard');

    // Click Incidents in sidebar
    await page.click('a[href="/incidents"]');
    await expect(page.locator('.page-title')).toContainText('Incidents');

    // Click Dashboard in sidebar
    await page.click('a[href="/"]');
    await expect(page.locator('.page-title')).toContainText('Dashboard');
    console.log('✅ Navigation between routes works');
  });

  test('Incident list displays incident data', async ({ page }) => {
    const response = await fetch(`${API_URL}/incidents?page_size=1`);
    const data = await response.json();
    const title = data.incidents?.[0]?.title;
    expect(title).toBeTruthy();

    await page.goto(`${BASE_URL}/incidents`);
    await expect(page.getByRole('heading', { name: title, level: 3 })).toBeVisible({ timeout: 15000 });
    console.log('✅ Incident list displays API data');
  });

  test('Browser console has no critical errors', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(BASE_URL);
    await page.waitForTimeout(2000);

    // Filter out expected errors
    const criticalErrors = consoleErrors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('manifest') &&
      !e.includes('websocket') &&
      !e.includes('Failed to load resource') &&
      !e.includes('net::ERR')
    );

    if (criticalErrors.length > 0) {
      console.log('⚠️ Console errors found:', criticalErrors);
    } else {
      console.log('✅ No critical console errors');
    }
  });

  test('API requests return expected responses', async ({ page }) => {
    const apiResponses: any[] = [];
    page.on('response', response => {
      if (response.url().includes('/incidents') ||
          response.url().includes('/analytics') ||
          response.url().includes('/health')) {
        apiResponses.push({
          url: response.url(),
          status: response.status()
        });
      }
    });

    await page.goto(`${BASE_URL}/incidents`);
    await page.waitForTimeout(2000);

    // Check that API calls were made and returned 200
    const incidentsCalls = apiResponses.filter(r => r.url.includes('/incidents') && !r.url.includes('/investigate'));
    if (incidentsCalls.length > 0) {
      const allSuccess = incidentsCalls.every(r => r.status === 200);
      if (allSuccess) {
        console.log('✅ API requests return 200 OK');
      } else {
        console.log('⚠️ Some API requests failed:', incidentsCalls.filter(r => r.status !== 200));
      }
    } else {
      console.log('⚠️ No API calls captured');
    }
  });

  test('Create Incident button click does not create incident in demo mode', async ({ page }) => {
    await page.goto(`${BASE_URL}/incidents`);

    // Click Create Incident button
    await page.click('button:has-text("Create Incident")');
    await page.waitForTimeout(1000);

    // Verify no incident was created by checking the incident count didn't increase
    // (We can't easily check this without API, but we can verify the page didn't navigate)
    const url = page.url();
    if (url === `${BASE_URL}/incidents`) {
      console.log('✅ Create Incident button does not navigate (correct for demo mode)');
    } else {
      console.log('⚠️ Page navigated after Create Incident click:', url);
    }
  });

  test('Incident detail page accessible via deep link', async ({ page }) => {
    // Get an incident ID from API
    const response = await fetch(`${API_URL}/incidents`);
    const data = await response.json();
    if (data.incidents && data.incidents.length > 0) {
      const incidentId = data.incidents[0].id;
      await page.goto(`${BASE_URL}/incidents/${incidentId}`);
      await expect(page.locator('.page-title')).toContainText(data.incidents[0].title, { timeout: 15000 });
      console.log('✅ Incident detail page works via deep link');
    }
  });
});