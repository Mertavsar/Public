// Kare yakalayıcı. player.html'i açar, zaman çizelgesini yükler, her kare için
// seek(t) + ekran görüntüsü alır ve JPEG akışını ffmpeg'e borular.
//
//   node capture.mjs --timeline tl.json --out parca.mp4 --from 0 --to 450 --fps 30
//   node capture.mjs --timeline tl.json --still 3.2 --out kare.png [--cover]
import { spawn, execSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
let pw;
try { pw = require("playwright"); }
catch { pw = require(path.join(execSync("npm root -g").toString().trim(), "playwright")); }

const args = Object.fromEntries(process.argv.slice(2).reduce((a, x, i, arr) => {
  if (x.startsWith("--")) a.push([x.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]);
  return a;
}, []));
const HERE = path.dirname(fileURLToPath(import.meta.url));
const player = "file://" + path.resolve(HERE, "../engine/player.html");
const tl = JSON.parse(fs.readFileSync(args.timeline, "utf8"));
const fps = +(args.fps || 30);


const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
page.on("pageerror", e => { console.error("SAYFA HATASI:", e.message); process.exit(2); });
await page.goto(player);
await page.evaluate(([t, c]) => window.load(t, { cover: c }), [tl, !!args.cover]);

if (args.still !== undefined) {
  await page.evaluate(t => window.seek(t), +args.still);
  await page.screenshot({ path: args.out, type: args.out.endsWith(".jpg") ? "jpeg" : "png" });
  await browser.close();
  process.exit(0);
}

const f0 = +(args.from || 0), f1 = +(args.to ?? Math.ceil(tl.dur * fps));
const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg",
  "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", String(fps), args.out],
  { stdio: ["pipe", "inherit", "inherit"] });
for (let f = f0; f < f1; f++) {
  await page.evaluate(t => window.seek(t), f / fps);
  const buf = await page.screenshot({ type: "jpeg", quality: 93 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
}
ff.stdin.end();
await new Promise(r => ff.on("close", r));
await browser.close();
