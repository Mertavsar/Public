// Sunumu kare kare yakalayıp MP4'e döker.
//   node build/render.mjs                      -> out/video-silent.mp4
//   node build/render.mjs --stills 1,8,20      -> out/still-<t>.png (kontrol için)
import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.join(ROOT, 'out');
const FPS = 30;
const args = process.argv.slice(2);
const PAGE = args.includes('--page') ? args[args.indexOf('--page') + 1] : 'index.html';
const stills = args.includes('--stills') ? args[args.indexOf('--stills') + 1].split(',').map(Number) : null;
fs.mkdirSync(OUT, { recursive: true });

const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.woff2': 'font/woff2', '.m4a': 'audio/mp4' };
const server = http.createServer((req, res) => {
  const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]).replace(/^\/$/, '/index.html'));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(0);
const port = server.address().port;

const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(`http://127.0.0.1:${port}/${PAGE}?capture=1`);
await page.waitForFunction(() => window.__ready === true || (window.__ready && window.__ready.then), null, { timeout: 60000 });
await page.evaluate(() => window.__ready);
const DUR = await page.evaluate(() => window.__DUR || 86);

if (stills) {
  for (const t of stills) {
    await page.evaluate(t => window.__render(t), t);
    await page.screenshot({ path: path.join(OUT, `${PAGE === 'index.html' ? '' : PAGE.replace(/\.html$/, '') + '-'}still-${t}.png`) });
  }
} else {
  const silent = path.join(OUT, PAGE === 'index.html' ? 'video-silent.mp4' : PAGE.replace(/\.html$/, '') + '-silent.mp4');
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(DUR * FPS);
  for (let i = 0; i < N; i++) {
    await page.evaluate(t => window.__render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`kare ${i}/${N}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log('yazıldı:', silent);
}
await browser.close();
server.close();
