const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  pg.on('pageerror', e => console.log('PAGEERROR', e.message));
  await pg.goto('file://' + __dirname + '/index.html');
  await pg.evaluate(() => window.READY);
  const t0 = Date.now();
  const r = await pg.evaluate(() => window.collect());
  console.log('collect ms', Date.now() - t0, 'pops', r.pops.length, 'missing', r.missing, 'dur', r.dur);
  require('fs').writeFileSync('events.json', JSON.stringify(r));
  await b.close();
})();
