// node gpu-test.cjs  → tarayıcının hangi çiziciyi kullandığını yazar
const { chromium } = require("playwright");
(async () => { const br = await chromium.launch({ args: ["--ignore-gpu-blocklist", "--enable-gpu", "--enable-gpu-rasterization"] });
  const pg = await br.newPage();
  const r = await pg.evaluate(() => { const gl = document.createElement("canvas").getContext("webgl2"); if (!gl) return "WebGL YOK";
    const e = gl.getExtension("WEBGL_debug_renderer_info"); return e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); });
  console.log("Çizici:", r);
  console.log(/swiftshader|llvmpipe|software|basic render/i.test(r) ? "→ EKRAN KARTI KULLANILMIYOR (yazılımsal, yavaş)" : "→ EKRAN KARTI KULLANILIYOR ✓");
  await br.close(); })();
