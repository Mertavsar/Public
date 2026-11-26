// node cap.cjs frames <from> <to> <outdir>   |   node cap.cjs at t1,t2,... <outdir>
const { chromium } = require("playwright"); const fs = require("fs"); const path = require("path");
const W = __dirname; const MIME = { html: "text/html", js: "text/javascript", json: "application/json", ttf: "font/ttf", jpg: "image/jpeg", png: "image/png" };
(async () => {
  const [mode, a, b, out] = process.argv.slice(2);
  const args = process.env.CPU ? ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] : ["--ignore-gpu-blocklist", "--enable-gpu", "--enable-gpu-rasterization"];
  const br = await chromium.launch({ args, headless: !process.env.SHOW });
  const pg = await br.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on("pageerror", e => console.error("PAGEERR", e.message)); pg.on("console", m => { if (m.type() === "error") console.error("CONSOLE", m.text()); });
  await pg.route("http://istakoz.local/**", r => { const p = path.join(W, decodeURIComponent(new URL(r.request().url()).pathname));
    if (!fs.existsSync(p)) return r.fulfill({ status: 404, body: "" }); r.fulfill({ status: 200, body: fs.readFileSync(p), contentType: MIME[p.split(".").pop()] || "application/octet-stream" }); });
  await pg.goto("http://istakoz.local/film.html" + "?x=1" + (process.env.NOCAP ? "&nocap=1" : "") + (process.env.EN === "0" ? "" : "&en=1")); await pg.waitForFunction(() => window.ready === true, null, { timeout: 120000 });
  await pg.evaluate(() => document.fonts.ready);
  const dir = mode === "at" ? b : out; fs.mkdirSync(dir, { recursive: true });
  const times = mode === "at" ? a.split(",").map(Number) : Array.from({ length: +b - +a }, (_, i) => (+a + i) / 30);
  let n = mode === "at" ? 0 : +a;
  for (const t of times) { const id = await pg.evaluate(t => window.seek(t), t);
    await pg.screenshot({ path: path.join(dir, mode === "at" ? `k_${String(n).padStart(2, "0")}_${id}.jpg` : `f_${String(n).padStart(5, "0")}.jpg`), type: "jpeg", quality: 90 }); n++; }
  await br.close();
})();
