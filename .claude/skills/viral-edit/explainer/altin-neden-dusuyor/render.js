// node render.js <worker> <nworkers> [fps] [maxframes]  -> chunks/c<worker>.mp4
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
(async () => {
  const [wi, nw] = [+process.argv[2], +process.argv[3]];
  const fps = +(process.argv[4] || 30);
  const b = await chromium.launch({ args: ['--disable-gpu-vsync', '--disable-frame-rate-limit'] });
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  pg.on('pageerror', e => console.log('PAGEERROR', e.message));
  await pg.goto('file://' + __dirname + '/index.html');
  await pg.evaluate(() => window.READY);
  const dur = await pg.evaluate(() => window.DUR);
  const N = Math.min(Math.ceil(dur * fps), +(process.argv[5] || 1e9));
  const per = Math.ceil(N / nw), f0 = wi * per, f1 = Math.min(N, f0 + per);
  fs.mkdirSync('chunks', { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps), `chunks/c${wi}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = f0; f < f1; f++) {
    const url = await pg.evaluate(t => { window.render(t); return document.getElementById('c').toDataURL('image/jpeg', 0.94); }, f / fps);
    const buf = Buffer.from(url.slice(url.indexOf(',') + 1), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((f - f0) % 300 === 0) console.log(`w${wi} ${f - f0}/${f1 - f0} ${((Date.now() - t0) / Math.max(1, f - f0)).toFixed(0)}ms/kare`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log(`w${wi} bitti ${f1 - f0} kare ${((Date.now() - t0) / 1000).toFixed(0)}s`);
})();
