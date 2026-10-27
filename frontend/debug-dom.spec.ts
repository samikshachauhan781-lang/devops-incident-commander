import { test } from '@playwright/test';

const BASE_URL = 'http://localhost:4173';

test('Debug DOM structure', async ({ page }) => {
  await page.goto(`${BASE_URL}/incidents`);
  await page.waitForTimeout(2000);

  // Print all visible text
  const bodyText = await page.locator('body').textContent();
  console.log('=== BODY TEXT ===');
  console.log(bodyText?.substring(0, 3000));

  // Find all select elements
  const selects = await page.locator('select').all();
  console.log(`\n=== SELECT ELEMENTS (${selects.length}) ===`);
  for (let i = 0; i < selects.length; i++) {
    const options = await selects[i].locator('option').all();
    const optionTexts = [];
    for (const opt of options) {
      optionTexts.push(await opt.textContent());
    }
    console.log(`Select ${i}: ${optionTexts.join(', ')}`);
  }

  // Find all labels
  const labels = await page.locator('label').all();
  console.log(`\n=== LABELS (${labels.length}) ===`);
  for (const label of labels) {
    console.log(await label.textContent());
  }

  // Find page-title
  const pageTitles = await page.locator('.page-title').all();
  console.log(`\n=== PAGE TITLES (${pageTitles.length}) ===`);
  for (const title of pageTitles) {
    console.log(await title.textContent());
  }

  // Find all buttons with "Create"
  const createButtons = await page.locator('button:has-text("Create")').all();
  console.log(`\n=== CREATE BUTTONS (${createButtons.length}) ===`);
  for (const btn of createButtons) {
    console.log(await btn.textContent());
  }
});