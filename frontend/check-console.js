const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });

  page.on('pageerror', error => {
    errors.push(error.message);
  });

  try {
    await page.goto('http://localhost:3000/', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000); // Wait for React to render

    const title = await page.title();
    const content = await page.content();

    console.log('Page title:', title);
    console.log('Errors captured:', errors.length);
    errors.forEach((err, i) => console.log(`Error ${i+1}:`, err));

    // Check if root has content
    const rootContent = await page.$eval('#root', el => el.innerHTML).catch(() => 'NOT FOUND');
    console.log('Root content:', rootContent.substring(0, 500));

  } catch (err) {
    console.error('Navigation error:', err.message);
  }

  await browser.close();
})();