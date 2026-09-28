// kullanım: node shot.js t1 t2 ... -> frames/shot_<t>.png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  pg.on('console', m => console.log('console:', m.text()));
  pg.on('pageerror', e => console.log('PAGEERROR', e.message));
  await pg.goto('file://' + __dirname + '/index.html');
  await pg.evaluate(() => window.READY);
  require('fs').mkdirSync('frames', { recursive: true });
  for (const t of process.argv.slice(2)) {
    await pg.evaluate(t => window.render(t), +t);
    await pg.locator('canvas').screenshot({ path: `frames/shot_${t}.png` });
  }
  await b.close();
})();
