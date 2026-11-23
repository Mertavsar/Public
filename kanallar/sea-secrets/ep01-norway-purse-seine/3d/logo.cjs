const { chromium } = require("playwright");
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 600, height: 600 } });
  await p.setContent(`<html><body style="margin:0"><style>@font-face{font-family:AN;src:url(file://${__dirname}/fonts/Anton-Regular.ttf)}</style>
  <div style="width:600px;height:600px;background:radial-gradient(circle at 50% 35%,#1f6fa8,#0a2a4a);display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:AN;color:#fff">
  <svg width="300" height="110" viewBox="0 0 300 110"><path d="M10 70 Q50 30 90 70 T170 70 T250 70 T330 70" stroke="#7fe0ff" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M110 45 q40 -30 80 0 q-40 30 -80 0z M190 45 l22 -16 v32z" fill="#fff"/></svg>
  <div style="font-size:118px;line-height:1;letter-spacing:2px">SEA</div><div style="font-size:84px;line-height:1.05;color:#ffd54a;letter-spacing:3px">SECRETS</div></div></body></html>`);
  await p.waitForTimeout(300); await p.screenshot({ path: __dirname + "/logo.jpg", type: "jpeg", quality: 92 }); await b.close(); })();
