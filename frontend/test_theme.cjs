const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Listen for console logs
  page.on('console', msg => {
    console.log(`[BROWSER LOG] [${msg.type()}] ${msg.text()}`);
  });

  try {
    console.log('Navigating to login page...');
    await page.goto('http://localhost:5177/login');
    await page.waitForTimeout(1000);

    console.log('Clicking Sign In with GitHub...');
    await page.click('button:has-text("Sign In with GitHub")');
    await page.waitForTimeout(2000);

    console.log('Current URL:', page.url());

    // Print initial classList of html
    let htmlClass = await page.evaluate(() => document.documentElement.className);
    console.log('Initial HTML class:', htmlClass);

    // Look for theme switcher button
    console.log('Locating theme switcher button...');
    const buttonTitle = await page.evaluate(() => {
      const btn = document.querySelector('button[title*="Switch to"]');
      return btn ? btn.getAttribute('title') : 'NOT FOUND';
    });
    console.log('Found button with title:', buttonTitle);

    console.log('Clicking theme switcher button...');
    await page.click('button[title*="Switch to"]');
    await page.waitForTimeout(1000);

    htmlClass = await page.evaluate(() => document.documentElement.className);
    console.log('HTML class after click:', htmlClass);

    const bgValue = await page.evaluate(() => {
      return getComputedStyle(document.body).backgroundColor;
    });
    console.log('Body background color after click:', bgValue);

  } catch (err) {
    console.error('Test failed:', err);
  } finally {
    await browser.close();
  }
})();
