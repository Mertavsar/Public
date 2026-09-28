const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  pg.on('pageerror', e => console.log('PAGEERROR', e.message));
  await pg.goto('file://' + __dirname + '/index.html');
  await pg.evaluate(() => window.READY);
  await pg.evaluate(() => window.thumb());
  await pg.locator('canvas').screenshot({ path: 'kapak_full.png' });
  await b.close();
})();
