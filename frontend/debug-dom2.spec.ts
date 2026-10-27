import { test } from '@playwright/test';

const BASE_URL = 'http://localhost:4173';

test('Debug DOM structure - filters', async ({ page }) => {
  await page.goto(`${BASE_URL}/incidents`);
  await page.waitForTimeout(2000);

  // Find all elements with "Service" text
  const serviceElements = await page.locator('*:has-text("Service:")').all();
  console.log(`\n=== ELEMENTS WITH "Service:" (${serviceElements.length}) ===`);
  for (const el of serviceElements) {
    const tag = await el.evaluate(e => e.tagName);
    const className = await el.getAttribute('class');
    console.log(`  <${tag} class="${className}">`);
  }

  // Find all elements with "Severity" text
  const severityElements = await page.locator('*:has-text("Severity:")').all();
  console.log(`\n=== ELEMENTS WITH "Severity:" (${severityElements.length}) ===`);
  for (const el of severityElements) {
    const tag = await el.evaluate(e => e.tagName);
    const className = await el.getAttribute('class');
    console.log(`  <${tag} class="${className}">`);
  }

  // Find all elements with "Status" text
  const statusElements = await page.locator('*:has-text("Status:")').all();
  console.log(`\n=== ELEMENTS WITH "Status:" (${statusElements.length}) ===`);
  for (const el of statusElements) {
    const tag = await el.evaluate(e => e.tagName);
    const className = await el.getAttribute('class');
    console.log(`  <${tag} class="${className}">`);
  }

  // Find all buttons
  const buttons = await page.locator('button').all();
  console.log(`\n=== ALL BUTTONS (${buttons.length}) ===`);
  for (const btn of buttons) {
    const text = await btn.textContent();
    const className = await btn.getAttribute('class');
    console.log(`  <button class="${className}">${text?.trim()}</button>`);
  }

  // Find all elements with role="combobox" (Radix Select)
  const comboboxes = await page.locator('[role="combobox"]').all();
  console.log(`\n=== COMBOBOXES (${comboboxes.length}) ===`);
  for (const cb of comboboxes) {
    const className = await cb.getAttribute('class');
    console.log(`  [role="combobox"] class="${className}"`);
  }

  // Check IncidentDetail page
  console.log('\n=== CHECKING INCIDENT DETAIL PAGE ===');
  await page.goto(`${BASE_URL}/incidents/demo-001-payment-gateway-timeout`);
  await page.waitForTimeout(2000);

  const detailTitles = await page.locator('.page-title').all();
  console.log(`\n=== DETAIL PAGE TITLES (${detailTitles.length}) ===`);
  for (const title of detailTitles) {
    console.log(await title.textContent());
  }

  const detailBodyText = await page.locator('body').textContent();
  console.log('\n=== DETAIL BODY (first 2000 chars) ===');
  console.log(detailBodyText?.substring(0, 2000));
});