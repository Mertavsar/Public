// Tıkla Bakalım — kapak şablonu "B / belgesel" (kullanıcı seçimi, Kasım 2026). 1080×1920.
// Dev dar başlık (Anton) sola yaslı, altında 1–2 satır GERÇEK bilgi cümlesi (Poppins SemiBold),
// vurgu kelimesi kırmızı alt çizgiyle. Seri rozeti, kutu, logo, imleç YOK (kullanıcı: "berbat").
// Instagram ızgarası 3:4 kırpar (y 240–1680): başlık ve cümle bu alanın üst kısmında.
//   node seri_kapak.mjs kapak.json
// "ust": küçük kırmızı etiket (ne olduğunu ilk bakışta söyler), "baslik" <br> ile iki satır olabilir.
// { "cikti": "out", "kapaklar": [ { "ad": "paraketa", "gorsel": "foto.jpg", "odak": "50% 50%",
//   "baslik": "PARAKETA", "cumle": "Tek bir ipe <b>yüzlerce iğne</b><br>diziliyor..." } ] }
// Cümle kaynaklı bir gerçek olmalı (bölümün analiz.md'si); uydurma yok.
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
const F = "file://" + path.resolve(HERE, "../engine/fonts") + "/";
const cfgPath = path.resolve(process.argv[2]);
const cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
const base = path.dirname(cfgPath);
const out = path.resolve(base, cfg.cikti || "kapaklar");
fs.mkdirSync(out, { recursive: true });
const css0 = `@font-face{font-family:AN;src:url(${F}Anton-Regular.ttf)}@font-face{font-family:PS;src:url(${F}Poppins-SemiBold.ttf)}
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1080px;height:1920px;overflow:hidden;background:#000}
#k{position:relative;width:1080px;height:1920px;overflow:hidden}.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.sh{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.72) 0%,rgba(0,0,0,.45) 30%,rgba(0,0,0,.25) 40%,rgba(0,0,0,0) 52%)}
.col{position:absolute;left:84px;top:${"${"}TOP}px;width:910px}
.u{display:inline-block;background:#e3141b;color:#fff;font-family:PS;font-size:36px;letter-spacing:3px;padding:8px 18px 6px;margin:0 0 18px 6px}
.t{display:inline-block;white-space:nowrap;font-family:AN;color:#fff;font-size:250px;line-height:.98;letter-spacing:2px;text-shadow:0 6px 30px rgba(0,0,0,.45)}
.c{margin:22px 0 0 6px;width:880px;font-family:PS;font-size:50px;line-height:1.25;color:#fff;text-shadow:0 3px 16px rgba(0,0,0,.75)}
.c b{font-weight:inherit;box-shadow:inset 0 -12px 0 #e3141b}`;
const br = await pw.chromium.launch();
const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } });
for (const k of cfg.kapaklar) {
  const img = "file://" + path.resolve(base, k.gorsel);
  const tmp = path.join(out, "." + k.ad + ".html");
  const css = css0.replace("${TOP}", k.top || 330);
  fs.writeFileSync(tmp, `<!doctype html><meta charset=utf-8><style>${css}</style><div id="k">
<img class="bg" src="${img}" style="object-position:${k.odak || "50% 50%"}"><div class="sh"></div>
<div class="col">${k.ust ? `<div class="u">${k.ust}</div><br>` : ""}<div class="t">${k.baslik}</div><div class="c">${k.cumle}</div></div></div>`);
  await pg.goto("file://" + tmp);
  await pg.evaluate(() => document.fonts.ready);
  await pg.waitForTimeout(300);
  await pg.evaluate(() => { const t = document.querySelector(".t"); let f = 250;
    while (t.getBoundingClientRect().width > 900 && f > 80) { f -= 4; t.style.fontSize = f + "px"; } });
  const f = path.join(out, k.ad + ".jpg");
  await pg.screenshot({ path: f, type: "jpeg", quality: 92 });
  fs.unlinkSync(tmp);
  console.log(f);
}
await br.close();
