// Tıkla Bakalım — seri kapak şablonu (1080×1920), "Denizin Sırları" gibi seriler için.
// Instagram ızgarası 3:4 kırpar (y 240–1680). Sağ üst (video ikonu) ve sol alt (izlenme sayısı)
// boş bırakılır. Sabit öğeler: seri rozeti (sol üst), dev başlık, en çok 3 kelimelik alt satır,
// "sırrın" üstünde tıklayan imleç (kanal imzası), sağ altta logo.
//
//   node seri_kapak.mjs kapak.json
// kapak.json: { "cikti": "klasor", "kapaklar": [ { "ad": "cokertme", "gorsel": "/yol/foto.jpg",
//   "odak": "50% 50%", "seri": "DENİZİN SIRLARI", "no": 5, "ust": "ÇÖKERTME", "vurgu": "DALYANI",
//   "alt": "Balık nasıl hapsoluyor?", "baslikY": 330, "imlec": [520, 1010] } ] }
import { execSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
let pw;
try { pw = require("playwright"); }
catch { pw = require(path.join(execSync("npm root -g").toString().trim(), "playwright")); }

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FONTS = "file://" + path.resolve(HERE, "../engine/fonts");
const LOGO = "file://" + path.resolve(HERE, "../../../../tikla-bakalim/markalama/logo.jpg");
const cfgPath = path.resolve(process.argv[2]);
const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
const base = path.dirname(cfgPath);
const abs = p => "file://" + path.resolve(base, p);
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

const css = `
@font-face { font-family: M; font-weight: 900; src: url(${FONTS}/montserrat-latin-900-normal.woff2); unicode-range: U+0000-00FF, U+0131, U+2000-206F; }
@font-face { font-family: M; font-weight: 900; src: url(${FONTS}/montserrat-latin-ext-900-normal.woff2); unicode-range: U+0100-02BA, U+02BD-02C5, U+1E00-1E9F; }
@font-face { font-family: M; font-weight: 800; src: url(${FONTS}/montserrat-latin-800-normal.woff2); unicode-range: U+0000-00FF, U+0131, U+2000-206F; }
@font-face { font-family: M; font-weight: 800; src: url(${FONTS}/montserrat-latin-ext-800-normal.woff2); unicode-range: U+0100-02BA, U+02BD-02C5, U+1E00-1E9F; }
* { margin:0; padding:0; box-sizing:border-box; }
html,body { width:1080px; height:1920px; overflow:hidden; background:#000; font-family:M,sans-serif; }
#k { position:relative; width:1080px; height:1920px; overflow:hidden; }
.bg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.shade { position:absolute; inset:0; background:
  linear-gradient(180deg, rgba(0,0,0,.38) 0%, rgba(0,0,0,.10) 34%, rgba(0,0,0,0) 48%, rgba(0,0,0,0) 78%, rgba(0,0,0,.45) 100%); }
.seri { position:absolute; left:64px; top:270px; display:flex; align-items:center; gap:0;
  font-weight:900; font-size:34px; letter-spacing:3px; color:#fff; transform:skewX(-8deg); }
.seri .a { background:#e3141b; padding:12px 20px; }
.seri .n { background:#111; padding:12px 18px; }
.bas { position:absolute; left:0; right:0; text-align:center; transform:skewX(-8deg); }
.ust { display:block; font-weight:900; color:#fff; line-height:.95; letter-spacing:-2px;
  -webkit-text-stroke:6px #111; paint-order:stroke fill; text-shadow:0 10px 0 #111, 0 18px 30px rgba(0,0,0,.5); }
.vur { display:inline-block; margin-top:14px; background:#e3141b; color:#fff; font-weight:900; line-height:1;
  padding:12px 34px 18px; border-radius:22px; border:6px solid #fff; box-shadow:0 12px 0 #8d0b10, 0 20px 34px rgba(0,0,0,.45); }
.alt { display:inline-block; margin-top:34px; background:#111; color:#ffd400; font-weight:800; font-size:46px;
  padding:12px 26px; border-radius:12px; }
.imlec { position:absolute; width:190px; height:190px; }
.logo { position:absolute; right:56px; top:1470px; width:150px; height:150px; border-radius:50%;
  box-shadow:0 8px 24px rgba(0,0,0,.45); }
`;

const imlecSvg = `<svg viewBox="0 0 190 190" xmlns="http://www.w3.org/2000/svg">
 <g stroke="#e3141b" stroke-width="11" stroke-linecap="round">
  <line x1="34" y1="6" x2="40" y2="34"/><line x1="6" y1="40" x2="32" y2="50"/><line x1="72" y1="10" x2="62" y2="36"/></g>
 <path d="M58 58 L58 168 L84 142 L104 182 L124 172 L104 133 L142 133 Z" fill="#fff" stroke="#111" stroke-width="9" stroke-linejoin="round"/>
</svg>`;

const html = k => {
  const n = k.ust.length, fs1 = k.ustBoy || Math.min(158, Math.round(1400 / Math.max(n, 6)));
  const fs2 = k.vurguBoy || Math.min(150, Math.round(1350 / Math.max(k.vurgu.length, 6)));
  const [ix, iy] = k.imlec || [450, 1000];
  return `<!doctype html><meta charset="utf-8"><style>${css}</style><div id="k">
 <img class="bg" src="${abs(k.gorsel)}" style="object-position:${k.odak || "50% 50%"}">
 <div class="shade"></div>
 <div class="seri"><span class="a">${esc(k.seri)}</span><span class="n">#${k.no}</span></div>
 <div class="bas" style="top:${k.baslikY || 360}px">
  <span class="ust" style="font-size:${fs1}px">${esc(k.ust)}</span>
  <span class="vur" style="font-size:${fs2}px">${esc(k.vurgu)}</span><br>
  <span class="alt">${esc(k.alt)}</span>
 </div>
 <div class="imlec" style="left:${ix - 58}px;top:${iy - 58}px">${imlecSvg}</div>
 <img class="logo" src="${LOGO}">
</div>`;
};

const out = path.resolve(base, cfg.cikti || "kapaklar");
fs.mkdirSync(out, { recursive: true });
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
for (const k of cfg.kapaklar) {
  const tmp = path.join(out, "." + k.ad + ".html");
  fs.writeFileSync(tmp, html(k));
  await page.goto("file://" + tmp, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const f = path.join(out, k.ad + ".jpg");
  await page.screenshot({ path: f, type: "jpeg", quality: 92 });
  fs.unlinkSync(tmp);
  console.log(f);
}
await browser.close();
