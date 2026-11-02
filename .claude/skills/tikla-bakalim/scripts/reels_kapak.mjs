// Tıkla Bakalım — Instagram Reels / Shorts kapak şablonu (1080×1920).
// Tüm kapaklar aynı marka dili: logo, kırmızı çerçeve, kategori etiketi, siyah-beyaz dev yazı,
// vurgulu satır logodaki gibi kırmızı kutu içinde beyaz. Instagram ızgarası 3:4 kırpar
// (y 240–1680) — logo, etiket ve başlık bu alanın içinde.
//
//   node reels_kapak.mjs kapaklar.json
// kapaklar.json: { "logo": "logo.jpg", "cikti": "klasor", "kapaklar": [
//   { "ad": "baraj", "gorsel": "foto/x.jpg" | null, "ikon": "⛽", "etiket": "NASIL ÇALIŞIR?",
//     "satirlar": ["SU NASIL", "[ELEKTRİĞE]", "DÖNÜŞÜR?"], "odak": "50% 40%", "kredi": "Foto: ..." } ] }
// Köşeli parantezli satır = kırmızı kutulu vurgu satırı.
import { execSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
let pw;
try { pw = require("playwright"); }
catch { pw = require(path.join(execSync("npm root -g").toString().trim(), "playwright")); }
const { chromium } = pw;

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FONTS = "file://" + path.resolve(HERE, "../engine/fonts");
const cfgPath = path.resolve(process.argv[2]);
const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
const base = path.dirname(cfgPath);
const url = p => "file://" + path.resolve(base, p);
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

const css = `
@font-face { font-family: M; font-weight: 900; src: url(${FONTS}/montserrat-latin-900-normal.woff2); unicode-range: U+0000-00FF, U+0131, U+2000-206F; }
@font-face { font-family: M; font-weight: 900; src: url(${FONTS}/montserrat-latin-ext-900-normal.woff2); unicode-range: U+0100-02BA, U+02BD-02C5, U+1E00-1E9F; }
@font-face { font-family: M; font-weight: 800; src: url(${FONTS}/montserrat-latin-800-normal.woff2); unicode-range: U+0000-00FF, U+0131, U+2000-206F; }
@font-face { font-family: M; font-weight: 800; src: url(${FONTS}/montserrat-latin-ext-800-normal.woff2); unicode-range: U+0100-02BA, U+02BD-02C5, U+1E00-1E9F; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #0d0d10; font-family: M, sans-serif; }
#k { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
.bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.grid { position: absolute; inset: 0; background: radial-gradient(90% 60% at 50% 42%, #2a1215 0%, #0d0d10 75%);
  }
.grid::after { content: ""; position: absolute; inset: 0; opacity: .12;
  background-image: linear-gradient(#fff 2px, transparent 2px), linear-gradient(90deg, #fff 2px, transparent 2px); background-size: 120px 120px; }
.ikon { position: absolute; left: 0; right: 0; top: 520px; text-align: center; font-size: 470px; line-height: 1;
  font-family: "Noto Color Emoji"; filter: drop-shadow(0 30px 40px rgba(0,0,0,.6)); }
.nesne { position: absolute; left: 50%; border-radius: 10px; box-shadow: 0 0 0 6px #fff, 0 40px 80px rgba(0,0,0,.75); z-index: 2; }
.shade { position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 42%, rgba(0,0,0,.78) 64%, rgba(0,0,0,.92) 100%); }
.frame { position: absolute; inset: 0; border: 16px solid #e3141b; }
.logo { position: absolute; left: 50%; top: 262px; width: 210px; height: 210px; margin-left: -105px; border-radius: 50%;
  overflow: hidden; box-shadow: 0 0 0 8px #fff, 0 14px 40px rgba(0,0,0,.55); background: #fff; }
.logo img { width: 112%; height: 112%; margin: -6%; }
.blok { position: absolute; left: 60px; right: 60px; top: 1010px; display: flex; flex-direction: column; align-items: center; text-align: center; }
.etiket { background: #e3141b; color: #fff; font-weight: 900; font-size: 44px; letter-spacing: 3px; padding: 12px 34px;
  border-radius: 14px; margin-bottom: 30px; box-shadow: 0 8px 22px rgba(0,0,0,.45); }
.s { color: #fff; font-weight: 900; font-size: var(--b); line-height: 1.02; letter-spacing: -1px; white-space: nowrap;
  text-shadow: 0 6px 0 #000, 0 0 30px rgba(0,0,0,.7); -webkit-text-stroke: 3px #000; paint-order: stroke fill; }
.v { display: inline-block; background: #e3141b; border-radius: 22px; padding: 4px 30px 12px; margin: 14px 0; transform: rotate(-2deg);
  box-shadow: 0 10px 0 #8d0b10, 0 18px 30px rgba(0,0,0,.5); }
.v .s { text-shadow: none; -webkit-text-stroke: 0; }
.cizgi { margin-top: 34px; display: flex; flex-direction: column; align-items: center; gap: 14px; }
.cizgi i { display: block; height: 12px; border-radius: 6px; background: #e3141b; }
.kredi { position: absolute; right: 34px; bottom: 34px; color: rgba(255,255,255,.55); font-weight: 800; font-size: 18px; }
`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
fs.mkdirSync(path.resolve(base, cfg.cikti), { recursive: true });
for (const k of cfg.kapaklar) {
  const lines = k.satirlar.map(t => {
    const v = /^\[(.*)\]$/.exec(t);
    return v ? `<div class="v"><div class="s">${esc(v[1])}</div></div>` : `<div class="s">${esc(t)}</div>`;
  }).join("");
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body><div id="k">
    ${k.gorsel ? `<img class="bg" src="${url(k.gorsel)}" style="object-position:${k.odak || "50% 50%"}">` : `<div class="grid"></div>`}
    ${k.ikon ? `<div class="ikon" style="${k.ikonTop ? "top:" + k.ikonTop + "px;" : ""}${k.ikonBoy ? "font-size:" + k.ikonBoy + "px;" : ""}">${k.ikon}</div>` : ""}
    ${k.nesne ? `<img class="nesne" src="${url(k.nesne)}" style="width:${k.nesneBoy || 760}px;top:${k.nesneY || 560}px;transform:translateX(-50%) rotate(${k.nesneAci ?? -7}deg)">` : ""}
    <div class="shade"></div>
    <div class="logo"><img src="${url(cfg.logo)}"></div>
    <div class="blok" style="--b:${k.boy || 132}px">
      <div class="etiket">${esc(k.etiket)}</div>${lines}
      <div class="cizgi"><i style="width:420px"></i><i style="width:220px"></i></div>
    </div>
    ${k.kredi ? `<div class="kredi">${esc(k.kredi)}</div>` : ""}
    <div class="frame"></div></div></body></html>`;
  // file:// görseller ve fontlar about:blank'ten yüklenmez — sayfayı dosyadan aç
  const tmp = path.resolve(base, cfg.cikti, ".kapak.html");
  fs.writeFileSync(tmp, html);
  await page.goto("file://" + tmp, { waitUntil: "load" });
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode().catch(() => {}))); });
  // satırlar taşarsa küçült
  await page.evaluate(() => document.querySelectorAll(".s").forEach(e => {
    const max = 940; if (e.scrollWidth > max) e.style.fontSize = (parseFloat(getComputedStyle(e).fontSize) * max / e.scrollWidth) + "px"; }));
  const out = path.resolve(base, cfg.cikti, k.ad + ".jpg");
  await page.screenshot({ path: out, type: "jpeg", quality: 92 });
  console.log(out);
  fs.unlinkSync(tmp);
}
await browser.close();
