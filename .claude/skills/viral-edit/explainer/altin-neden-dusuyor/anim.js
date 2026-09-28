'use strict';
// "Altın neden düşüyor?" — 1920x1080 animasyonlu anlatım.
// render(t) tamamen deterministik: aynı t her zaman aynı kareyi çizer.
// Tüm zamanlamalar seslendirmedeki kelimelerden (words.js) okunur: cue(p, 'kelime').

const W = 1920, H = 1080;
const cv = document.getElementById('c'), g = cv.getContext('2d');
const F = 'Montserrat', MONO = 'JetBrains Mono';
const C = {
  gold: '#FFC83D', gold2: '#F2A516', goldD: '#A8690C', goldL: '#FFE9A3',
  red: '#FF4D5E', green: '#2FE39A', blue: '#4DA3FF', teal: '#2DD4BF', purple: '#A78BFA',
  orange: '#FF9F43', white: '#F4F6FB', mute: '#8FA0C2', ink: '#0A1128',
  card: 'rgba(20,32,64,0.94)',
};

const WORDS = window.WORDS;
const NP = Math.max(...WORDS.map(w => w.p)) + 1;
const PS = [], PE = [];
for (let p = 0; p < NP; p++) {
  const ws = WORDS.filter(w => w.p === p);
  PS[p] = ws[0].s; PE[p] = ws[ws.length - 1].e;
}
const DUR = PE[NP - 1] + 0.7;
const SW = PS.map((s, p) => (p === 0 ? 0 : s - 0.12));   // sahne değişim anları

// ---------------------------------------------------------------- yardımcılar
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const eo = t => 1 - Math.pow(1 - t, 3);
const eio = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const eback = t => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const hash = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

let T = 0, COLLECT = false;
const EV = [], EVSEEN = new Set(), MISSING = new Set();
const P = (t0, d = 0.5) => clamp((T - t0) / d);
function pop(t0, d = 0.5) {
  if (COLLECT && !EVSEEN.has(t0)) { EVSEEN.add(t0); EV.push(t0); }
  return clamp((T - t0) / d);
}

const norm = s => s.toLocaleLowerCase('tr').replace(/[’'`]/g, '').replace(/[^a-zçğıöşü0-9%,]/g, '');
const CUE = new Map();
function cue(p, key, n = 0) {
  const id = p + '|' + key + '|' + n;
  if (CUE.has(id)) return CUE.get(id);
  const k0 = norm(key); let k = 0, r = null;
  for (const w of WORDS) {
    if (w.p !== p) continue;
    if (norm(w.w).startsWith(k0)) { if (k === n) { r = w.s; break; } k++; }
  }
  if (r === null) { MISSING.add(id); r = PS[p]; }
  CUE.set(id, r); return r;
}

// A: bir öğeyi t0 anında sahneye sokar (pop/kayma), `out` anında çıkarır.
function A(t0, x, y, fn, o = {}) {
  const d = o.d || 0.5;
  const p = o.sfx === false ? P(t0, d) : pop(t0, d);
  if (p <= 0) return;
  const out = o.out != null ? P(o.out, 0.35) : 0;
  if (out >= 1) return;
  g.save(); g.translate(x, y);
  let s = 1;
  const m = o.m || 'pop';
  if (m === 'pop') s = eback(p);
  else if (m === 'up') g.translate(0, (1 - eo(p)) * 70);
  else if (m === 'down') g.translate(0, -(1 - eo(p)) * 70);
  else if (m === 'left') g.translate(-(1 - eo(p)) * 140, 0);
  else if (m === 'right') g.translate((1 - eo(p)) * 140, 0);
  if (out > 0) s *= 1 - 0.2 * eo(out);
  g.scale(s, s);
  g.globalAlpha *= clamp(p * 2.2) * (1 - eo(out));
  fn(p);
  g.restore();
}

function font(size, w = 800, fam = F) { g.font = `${w} ${size}px ${fam}`; }
function tx(s, x, y, size, o = {}) {
  g.save();
  font(size, o.w || 800, o.fam || F);
  if (o.ls) g.letterSpacing = o.ls + 'px';
  if (o.max) { const m = g.measureText(s).width; if (m > o.max) font(size * o.max / m, o.w || 800, o.fam || F); }
  g.textAlign = o.a || 'center'; g.textBaseline = 'middle';
  if (o.glow) { g.shadowColor = o.gc || o.c || C.gold; g.shadowBlur = o.glow; }
  if (o.stroke) { g.lineJoin = 'round'; g.lineWidth = o.stroke; g.strokeStyle = o.sc || 'rgba(0,0,0,0.55)'; g.strokeText(s, x, y); }
  g.fillStyle = o.c || C.white; g.fillText(s, x, y);
  g.restore();
}
function tw(s, size, w = 800) { g.save(); font(size, w); const m = g.measureText(s).width; g.restore(); return m; }
function rr(x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }

function card(w, h, o = {}) {           // (0,0) merkezli kart
  g.save();
  rr(-w / 2, -h / 2, w, h, o.r ?? 28);
  g.shadowColor = 'rgba(0,0,0,0.5)'; g.shadowBlur = 40; g.shadowOffsetY = 16;
  g.fillStyle = o.fill || C.card; g.fill();
  g.shadowColor = 'transparent';
  g.lineWidth = o.lw || 2; g.strokeStyle = o.stroke || 'rgba(255,255,255,0.10)'; g.stroke();
  if (o.accent) { g.save(); g.clip(); g.fillStyle = o.accent; g.fillRect(-w / 2, -h / 2, w, 8); g.restore(); }
  g.restore();
}
function chip(s, size, o = {}) {        // (0,0) merkezli hap etiket
  const w = tw(s, size, o.w || 800) + size * 1.3, h = size * 1.9;
  g.save();
  rr(-w / 2, -h / 2, w, h, h / 2);
  if (o.glow) { g.shadowColor = o.bg || C.gold; g.shadowBlur = o.glow; }
  g.fillStyle = o.bg || C.gold; g.fill();
  if (o.line) { g.lineWidth = 3; g.strokeStyle = o.line; g.stroke(); }
  g.restore();
  tx(s, 0, size * 0.04, size, { c: o.c || C.ink, w: o.w || 800 });
  return w;
}

function barrow(s, dir, col, glow = 30) {    // blok ok; dir=1 aşağı, -1 yukarı
  g.save(); g.scale(1, dir);
  g.beginPath();
  g.moveTo(-s * 0.2, -s * 0.5); g.lineTo(s * 0.2, -s * 0.5); g.lineTo(s * 0.2, s * 0.02);
  g.lineTo(s * 0.44, s * 0.02); g.lineTo(0, s * 0.5); g.lineTo(-s * 0.44, s * 0.02); g.lineTo(-s * 0.2, s * 0.02);
  g.closePath();
  g.shadowColor = col; g.shadowBlur = glow; g.fillStyle = col; g.fill();
  g.restore();
}
function arr(x1, y1, x2, y2, p = 1, o = {}) {
  if (p <= 0) return;
  const x = lerp(x1, x2, p), y = lerp(y1, y2, p);
  g.save();
  g.strokeStyle = g.fillStyle = o.c || C.white; g.lineWidth = o.w || 7; g.lineCap = 'round';
  if (o.glow) { g.shadowColor = o.c || C.white; g.shadowBlur = o.glow; }
  if (o.dash) { g.setLineDash(o.dash); g.lineDashOffset = -T * 60; }
  const a = Math.atan2(y2 - y1, x2 - x1), hs = o.hs || 26;
  g.beginPath(); g.moveTo(x1, y1); g.lineTo(x - Math.cos(a) * hs * 0.6, y - Math.sin(a) * hs * 0.6); g.stroke();
  g.setLineDash([]);
  g.beginPath(); g.moveTo(x, y);
  g.lineTo(x - Math.cos(a - 0.45) * hs, y - Math.sin(a - 0.45) * hs);
  g.lineTo(x - Math.cos(a + 0.45) * hs, y - Math.sin(a + 0.45) * hs);
  g.closePath(); g.fill();
  g.restore();
}
function strike(x1, y1, x2, y2, p, col = C.red, w = 10) {
  if (p <= 0) return;
  g.save(); g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.shadowColor = col; g.shadowBlur = 18;
  g.beginPath(); g.moveTo(x1, y1); g.lineTo(lerp(x1, x2, eo(p)), lerp(y1, y2, eo(p))); g.stroke(); g.restore();
}
function check(s, p, col = C.green) {
  if (p <= 0) return;
  g.save(); g.strokeStyle = col; g.lineWidth = s * 0.16; g.lineCap = g.lineJoin = 'round';
  g.beginPath();
  const pts = [[-s * 0.35, 0], [-s * 0.08, s * 0.28], [s * 0.4, -s * 0.3]];
  const q = eo(p) * 2;
  g.moveTo(...pts[0]);
  if (q < 1) g.lineTo(lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q));
  else { g.lineTo(...pts[1]); g.lineTo(lerp(pts[1][0], pts[2][0], q - 1), lerp(pts[1][1], pts[2][1], q - 1)); }
  g.stroke(); g.restore();
}
function cross(s, p, col = C.red) {
  if (p <= 0) return;
  const q = eo(p) * 2;
  g.save(); g.strokeStyle = col; g.lineWidth = s * 0.16; g.lineCap = 'round'; g.shadowColor = col; g.shadowBlur = 20;
  g.beginPath(); g.moveTo(-s / 2, -s / 2); const a = Math.min(1, q); g.lineTo(lerp(-s / 2, s / 2, a), lerp(-s / 2, s / 2, a)); g.stroke();
  if (q > 1) { g.beginPath(); g.moveTo(s / 2, -s / 2); g.lineTo(lerp(s / 2, -s / 2, q - 1), lerp(-s / 2, s / 2, q - 1)); g.stroke(); }
  g.restore();
}
function stamp(s, size, col, rot = -0.12) {
  g.save(); g.rotate(rot);
  const w = tw(s, size, 900) + size * 1.1, h = size * 1.7;
  rr(-w / 2, -h / 2, w, h, 12); g.lineWidth = 6; g.strokeStyle = col; g.shadowColor = col; g.shadowBlur = 16; g.stroke();
  g.shadowBlur = 0; g.fillStyle = 'rgba(8,12,28,0.75)'; g.fill();
  tx(s, 0, size * 0.05, size, { c: col, w: 900, ls: 2 });
  g.restore();
}

// ---------------------------------------------------------------- ikonlar
function goldBar(w, o = {}) {           // (0,0) merkezli külçe
  const h = w * 0.30, ins = w * 0.11, top = w * 0.17, ti = ins * 2.1;
  const fb = h / 2, ft = -h / 2 + top * 0.35, tt = ft - top;
  g.save();
  if (o.rot) g.rotate(o.rot);
  g.save(); g.translate(0, fb + 14); g.scale(1, 0.3);
  const sg0 = g.createRadialGradient(0, 0, 0, 0, 0, w * 0.6);
  sg0.addColorStop(0, 'rgba(0,0,0,0.45)'); sg0.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = sg0; g.beginPath(); g.arc(0, 0, w * 0.6, 0, 7); g.fill(); g.restore();
  const shape = new Path2D();
  shape.moveTo(-w / 2, fb); shape.lineTo(w / 2, fb); shape.lineTo(w / 2 - ins, ft);
  shape.lineTo(w / 2 - ti, tt); shape.lineTo(-w / 2 + ti, tt); shape.lineTo(-w / 2 + ins, ft); shape.closePath();
  if (o.glow) { g.save(); g.shadowColor = C.gold; g.shadowBlur = o.glow; g.fillStyle = C.gold; g.fill(shape); g.restore(); }
  let gr = g.createLinearGradient(0, ft, 0, fb);
  gr.addColorStop(0, '#FFD65A'); gr.addColorStop(0.55, '#EFA11A'); gr.addColorStop(1, '#B0700C');
  g.beginPath(); g.moveTo(-w / 2, fb); g.lineTo(w / 2, fb); g.lineTo(w / 2 - ins, ft); g.lineTo(-w / 2 + ins, ft); g.closePath();
  g.fillStyle = gr; g.fill();
  gr = g.createLinearGradient(0, tt, 0, ft);
  gr.addColorStop(0, '#FFF4C4'); gr.addColorStop(1, '#FFCF45');
  g.beginPath(); g.moveTo(-w / 2 + ins, ft); g.lineTo(w / 2 - ins, ft); g.lineTo(w / 2 - ti, tt); g.lineTo(-w / 2 + ti, tt); g.closePath();
  g.fillStyle = gr; g.fill();
  g.lineWidth = Math.max(1.5, w * 0.008); g.strokeStyle = '#8A560A'; g.lineJoin = 'round'; g.stroke(shape);
  g.beginPath(); g.moveTo(-w / 2 + ins, ft); g.lineTo(w / 2 - ins, ft); g.strokeStyle = 'rgba(138,86,10,0.55)'; g.stroke();
  if (w > 120) {
    tx(o.label || '999,9', 0, (ft + fb) / 2 + 2, (fb - ft) * 0.36, { c: 'rgba(110,62,0,0.55)', w: 900, ls: 2 });
    tx('ALTIN', 0, (tt + ft) / 2 + 1, (ft - tt) * 0.42, { c: 'rgba(150,95,10,0.5)', w: 900, ls: 4 });
  }
  const sh = o.shine ?? ((T * 0.35) % 1.6);
  if (sh < 1) {
    g.save(); g.clip(shape);
    const sx = lerp(-w, w, sh);
    const sg = g.createLinearGradient(sx - w * 0.2, 0, sx + w * 0.2, 0);
    sg.addColorStop(0, 'rgba(255,255,255,0)'); sg.addColorStop(0.5, 'rgba(255,255,255,0.55)'); sg.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = sg; g.transform(1, 0, -0.5, 1, 0, 0); g.fillRect(-w * 2, tt - 10, w * 4, h * 2);
    g.restore();
  }
  g.restore();
}
function coin(r, sym, o = {}) {
  const c1 = o.c1 || '#FFE38F', c2 = o.c2 || '#D6961C';
  g.save();
  const gr = g.createRadialGradient(-r * 0.35, -r * 0.35, r * 0.1, 0, 0, r * 1.05);
  gr.addColorStop(0, c1); gr.addColorStop(1, c2);
  g.shadowColor = 'rgba(0,0,0,0.45)'; g.shadowBlur = r * 0.5; g.shadowOffsetY = r * 0.12;
  g.beginPath(); g.arc(0, 0, r, 0, 7); g.fillStyle = gr; g.fill();
  g.shadowColor = 'transparent';
  g.lineWidth = r * 0.08; g.strokeStyle = 'rgba(255,255,255,0.35)'; g.beginPath(); g.arc(0, 0, r * 0.8, 0, 7); g.stroke();
  tx(sym, 0, r * 0.05, r * (sym.length > 1 ? 0.62 : 0.95), { c: o.tc || 'rgba(80,45,0,0.85)', w: 900 });
  g.restore();
}
function globe(r, o = {}) {
  g.save();
  const gr = g.createRadialGradient(-r * 0.3, -r * 0.35, r * 0.1, 0, 0, r);
  gr.addColorStop(0, '#6FB8FF'); gr.addColorStop(1, '#1D4E9E');
  g.shadowColor = 'rgba(77,163,255,0.5)'; g.shadowBlur = 30;
  g.beginPath(); g.arc(0, 0, r, 0, 7); g.fillStyle = gr; g.fill(); g.shadowBlur = 0;
  g.save(); g.clip();
  g.strokeStyle = 'rgba(255,255,255,0.35)'; g.lineWidth = r * 0.04;
  const rot = (T * 0.25) % 1;
  for (let i = 0; i < 4; i++) {
    const k = Math.cos(((i / 4 + rot) % 1) * Math.PI);
    g.beginPath(); g.ellipse(0, 0, Math.abs(k) * r, r, 0, 0, 7); g.stroke();
  }
  for (const yy of [-0.5, 0, 0.5]) { g.beginPath(); g.ellipse(0, yy * r, Math.sqrt(1 - yy * yy) * r, r * 0.12, 0, 0, 7); g.stroke(); }
  g.fillStyle = 'rgba(47,227,154,0.55)';
  const dx = ((T * 0.25) % 1) * 2 * r;
  for (const [bx, by, bw, bh] of [[-0.5, -0.3, 0.45, 0.35], [0.3, 0.1, 0.35, 0.5], [-0.2, 0.35, 0.3, 0.25]]) {
    for (const off of [0, -2 * r]) {
      g.beginPath(); g.ellipse(bx * r + dx + off, by * r, bw * r, bh * r, 0.4, 0, 7); g.fill();
    }
  }
  g.restore();
  g.restore();
}
function thermo(s, level, col = C.red) {
  const tw_ = s * 0.24, bulb = s * 0.2;
  g.save();
  rr(-tw_ / 2, -s / 2, tw_, s * 0.85, tw_ / 2); g.fillStyle = 'rgba(255,255,255,0.14)'; g.fill();
  g.lineWidth = 4; g.strokeStyle = 'rgba(255,255,255,0.55)'; g.stroke();
  g.beginPath(); g.arc(0, s * 0.38, bulb, 0, 7); g.fillStyle = col; g.shadowColor = col; g.shadowBlur = 24; g.fill();
  const lh = (s * 0.72) * level;
  rr(-tw_ * 0.27, s * 0.33 - lh, tw_ * 0.54, lh + 4, tw_ * 0.27); g.fill();
  g.shadowBlur = 0; g.strokeStyle = 'rgba(255,255,255,0.5)'; g.lineWidth = 3;
  for (let i = 0; i < 5; i++) { const y = -s * 0.38 + i * s * 0.14; g.beginPath(); g.moveTo(tw_ / 2 + 6, y); g.lineTo(tw_ / 2 + 22, y); g.stroke(); }
  g.restore();
}
function bolt(s, col = C.gold) {
  g.save(); g.beginPath();
  g.moveTo(s * 0.1, -s / 2); g.lineTo(-s * 0.3, s * 0.08); g.lineTo(-s * 0.02, s * 0.08);
  g.lineTo(-s * 0.12, s / 2); g.lineTo(s * 0.3, -s * 0.1); g.lineTo(s * 0.02, -s * 0.1); g.closePath();
  g.fillStyle = col; g.shadowColor = col; g.shadowBlur = 25; g.fill(); g.restore();
}
function shield(s, col = C.teal) {
  g.save(); g.beginPath();
  g.moveTo(0, -s / 2); g.quadraticCurveTo(s * 0.3, -s * 0.38, s * 0.45, -s * 0.38);
  g.quadraticCurveTo(s * 0.48, s * 0.25, 0, s / 2); g.quadraticCurveTo(-s * 0.48, s * 0.25, -s * 0.45, -s * 0.38);
  g.quadraticCurveTo(-s * 0.3, -s * 0.38, 0, -s / 2); g.closePath();
  const gr = g.createLinearGradient(0, -s / 2, 0, s / 2); gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(20,60,80,0.9)');
  g.fillStyle = gr; g.shadowColor = col; g.shadowBlur = 30; g.fill();
  g.lineWidth = 5; g.strokeStyle = 'rgba(255,255,255,0.6)'; g.stroke();
  g.restore();
}
function bank(s, label, col = C.white) {
  g.save(); g.fillStyle = col; g.strokeStyle = col;
  g.beginPath(); g.moveTo(-s * 0.55, -s * 0.2); g.lineTo(0, -s * 0.5); g.lineTo(s * 0.55, -s * 0.2); g.closePath(); g.fill();
  g.fillRect(-s * 0.5, -s * 0.17, s, s * 0.06);
  for (let i = 0; i < 4; i++) { const x = -s * 0.38 + i * s * 0.253; rr(x - s * 0.05, -s * 0.08, s * 0.1, s * 0.46, 4); g.fill(); }
  g.fillRect(-s * 0.55, s * 0.4, s * 1.1, s * 0.08);
  g.restore();
  if (label) tx(label, 0, -s * 0.28, s * 0.1, { c: C.ink, w: 900 });
}
function barrel(s) {
  g.save();
  const gr = g.createLinearGradient(-s * 0.35, 0, s * 0.35, 0);
  gr.addColorStop(0, '#1b2238'); gr.addColorStop(0.45, '#3b4668'); gr.addColorStop(1, '#141a2c');
  rr(-s * 0.35, -s * 0.5, s * 0.7, s, s * 0.12); g.fillStyle = gr; g.fill();
  g.strokeStyle = C.orange; g.lineWidth = s * 0.05;
  for (const y of [-0.28, 0.28]) { g.beginPath(); g.moveTo(-s * 0.35, y * s); g.lineTo(s * 0.35, y * s); g.stroke(); }
  g.beginPath(); g.moveTo(0, -s * 0.14); g.bezierCurveTo(s * 0.14, s * 0.02, s * 0.12, s * 0.16, 0, s * 0.16);
  g.bezierCurveTo(-s * 0.12, s * 0.16, -s * 0.14, s * 0.02, 0, -s * 0.14); g.fillStyle = C.orange; g.fill();
  g.restore();
}
function calendar(s, month, day, o = {}) {
  g.save();
  card(s, s * 1.05, { r: 18, fill: '#F4F6FB' });
  rr(-s / 2, -s * 0.525, s, s * 0.3, [18, 18, 0, 0]); g.fillStyle = o.hc || C.red; g.fill();
  tx(month, 0, -s * 0.375, s * 0.14, { c: '#fff', w: 900, ls: 2, max: s * 0.9 });
  tx(day, 0, s * 0.17, s * 0.42, { c: C.ink, w: 900, max: s * 0.84 });
  for (const x of [-0.25, 0.25]) { rr(x * s - 6, -s * 0.6, 12, s * 0.16, 6); g.fillStyle = '#c9d2e6'; g.fill(); }
  g.restore();
}
function person(s, col) {
  g.save(); g.fillStyle = col;
  g.beginPath(); g.arc(0, -s * 0.28, s * 0.2, 0, 7); g.fill();
  g.beginPath(); g.moveTo(-s * 0.34, s * 0.45); g.quadraticCurveTo(-s * 0.34, -s * 0.02, 0, -s * 0.02);
  g.quadraticCurveTo(s * 0.34, -s * 0.02, s * 0.34, s * 0.45); g.closePath(); g.fill();
  g.restore();
}
function phone(w, h) {
  g.save();
  rr(-w / 2, -h / 2, w, h, w * 0.14); g.fillStyle = '#10162a'; g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = 40; g.fill();
  g.shadowBlur = 0; g.lineWidth = 6; g.strokeStyle = '#3a4566'; g.stroke();
  rr(-w / 2 + 14, -h / 2 + 14, w - 28, h - 28, w * 0.1); g.fillStyle = '#18213d'; g.fill();
  rr(-w * 0.14, -h / 2 + 22, w * 0.28, 16, 8); g.fillStyle = '#0a0f1f'; g.fill();
  g.restore();
}
function shop(s, label, col) {
  g.save();
  rr(-s / 2, -s * 0.2, s, s * 0.72, 10); g.fillStyle = '#1c2a52'; g.fill();
  g.lineWidth = 3; g.strokeStyle = 'rgba(255,255,255,0.15)'; g.stroke();
  const n = 6, sw = s * 1.08 / n;
  for (let i = 0; i < n; i++) {
    g.beginPath(); const x = -s * 0.54 + i * sw;
    g.moveTo(x, -s * 0.36); g.lineTo(x + sw, -s * 0.36); g.lineTo(x + sw, -s * 0.2);
    g.arc(x + sw / 2, -s * 0.2, sw / 2, 0, Math.PI); g.closePath();
    g.fillStyle = i % 2 ? '#F4F6FB' : col; g.fill();
  }
  rr(-s * 0.4, -s * 0.54, s * 0.8, s * 0.17, 10); g.fillStyle = col; g.fill();
  tx(label, 0, -s * 0.455, s * 0.09, { c: C.ink, w: 900, ls: 2 });
  rr(-s * 0.36, -s * 0.02, s * 0.3, s * 0.5, 6); g.fillStyle = '#0e1630'; g.fill();
  rr(s * 0.02, -s * 0.02, s * 0.34, s * 0.26, 6); g.fillStyle = 'rgba(255,200,61,0.25)'; g.fill();
  g.restore();
}
function gauge(r, v, label) {          // v: 0 (düşük) .. 1 (yüksek)
  g.save();
  g.lineWidth = r * 0.2; g.lineCap = 'round';
  const gr = g.createLinearGradient(-r, 0, r, 0);
  gr.addColorStop(0, C.red); gr.addColorStop(0.5, C.gold); gr.addColorStop(1, C.green);
  g.strokeStyle = 'rgba(255,255,255,0.08)'; g.beginPath(); g.arc(0, 0, r, Math.PI, 0); g.stroke();
  g.strokeStyle = gr; g.beginPath(); g.arc(0, 0, r, Math.PI, 0); g.stroke();
  const a = Math.PI + v * Math.PI;
  g.strokeStyle = C.white; g.lineWidth = r * 0.07; g.shadowColor = 'rgba(0,0,0,.6)'; g.shadowBlur = 10;
  g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * r * 0.85, Math.sin(a) * r * 0.85); g.stroke();
  g.beginPath(); g.arc(0, 0, r * 0.1, 0, 7); g.fillStyle = C.white; g.fill();
  g.restore();
  if (label) tx(label, 0, r * 0.38, r * 0.17, { c: C.mute, w: 800, ls: 2 });
}
// Çizgi grafik: pts [0..1] değerleri; p çizim ilerlemesi; uç noktayı döner
function lineChart(x, y, w, h, pts, p, o = {}) {
  const n = pts.length, k = (n - 1) * clamp(p);
  const X = i => x + (i / (n - 1)) * w, Y = v => y + h - v * h;
  const i0 = Math.floor(k), fr = k - i0;
  const ex = X(k), ey = Y(i0 + 1 < n ? lerp(pts[i0], pts[i0 + 1], fr) : pts[n - 1]);
  g.save();
  if (o.fill !== false) {
    g.beginPath(); g.moveTo(X(0), y + h);
    for (let i = 0; i <= i0; i++) g.lineTo(X(i), Y(pts[i]));
    g.lineTo(ex, ey); g.lineTo(ex, y + h); g.closePath();
    const gr = g.createLinearGradient(0, y, 0, y + h);
    gr.addColorStop(0, (o.fc || 'rgba(255,200,61,') + '0.35)'); gr.addColorStop(1, (o.fc || 'rgba(255,200,61,') + '0)');
    g.fillStyle = gr; g.fill();
  }
  g.beginPath(); g.moveTo(X(0), Y(pts[0]));
  for (let i = 1; i <= i0; i++) g.lineTo(X(i), Y(pts[i]));
  g.lineTo(ex, ey);
  g.strokeStyle = o.c || C.gold; g.lineWidth = o.w || 6; g.lineJoin = 'round'; g.lineCap = 'round';
  if (o.dash) g.setLineDash(o.dash);
  g.shadowColor = o.c || C.gold; g.shadowBlur = 18; g.stroke();
  g.setLineDash([]);
  if (o.dot !== false && p > 0) { g.beginPath(); g.arc(ex, ey, (o.w || 6) * 1.6, 0, 7); g.fillStyle = C.white; g.fill(); }
  g.restore();
  return [ex, ey];
}
function axes(x, y, w, h) {
  g.save(); g.strokeStyle = 'rgba(255,255,255,0.08)'; g.lineWidth = 2;
  for (let i = 0; i <= 4; i++) { const yy = y + (i / 4) * h; g.beginPath(); g.moveTo(x, yy); g.lineTo(x + w, yy); g.stroke(); }
  g.restore();
}
const seq = (n, f) => Array.from({ length: n }, (_, i) => f(i / (n - 1), i));
const noise = (i, s = 1) => (hash(i * 3.1 + s) - 0.5);
function badge(n, label, col = C.gold) {   // bölüm rozeti "1  FAİZ"
  g.save();
  g.beginPath(); g.arc(0, 0, 70, 0, 7); g.fillStyle = col; g.shadowColor = col; g.shadowBlur = 40; g.fill();
  g.restore();
  tx(String(n), 0, 4, 84, { c: C.ink, w: 900 });
  if (label) tx(label, 100, 2, 64, { a: 'left', w: 900, c: C.white });
}
function note(s, x, y) { tx(s, x, y, 20, { c: 'rgba(143,160,194,0.8)', w: 600, ls: 2 }); }

// ---------------------------------------------------------------- arka plan
function background() {
  const gr = g.createRadialGradient(W * 0.5, H * 0.42, 60, W * 0.5, H * 0.5, W * 0.78);
  gr.addColorStop(0, '#172757'); gr.addColorStop(0.55, '#0b1431'); gr.addColorStop(1, '#03060e');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
  g.save(); g.strokeStyle = 'rgba(120,150,230,0.055)'; g.lineWidth = 1.5;
  const off = (T * 14) % 90;
  for (let x = -90 + off; x < W + 90; x += 90) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
  for (let y = -90 + off * 0.5; y < H + 90; y += 90) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
  g.restore();
  g.save();
  for (let i = 0; i < 70; i++) {
    const sp = 8 + hash(i + 7) * 26;
    const x = (hash(i) * W + T * sp * 0.6) % W;
    const y = (hash(i + 99) * H - T * sp + H * 10) % H;
    const r = 1 + hash(i + 3) * 2.6;
    const a = 0.12 + 0.3 * (0.5 + 0.5 * Math.sin(T * (1 + hash(i + 5) * 2) + i));
    g.beginPath(); g.arc(x, y, r, 0, 7); g.fillStyle = `rgba(255,205,90,${a})`; g.fill();
  }
  g.restore();
}
function vignette() {
  const gr = g.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.72);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.55)');
  g.fillStyle = gr; g.fillRect(0, 0, W, H);
}

// ---------------------------------------------------------------- sahneler
const TAGS = ['', 'SPOT ALTIN', 'ONS ≠ GRAM', 'GRAM HESABI', 'İKİ KUVVET', 'TEMSİLİ HESAP', 'ASIL SORU',
  '1 · FAİZ', '1 · FAİZ', '1 · FAİZ', '2 · GÜÇLÜ DOLAR', '2 · GÜÇLÜ DOLAR', '3 · PETROL', 'TERS KÖŞE',
  'GÜVENLİ LİMAN', 'TÜRKİYE', 'TÜRKİYE · FAİZ', 'TÜRKİYE · ENFLASYON', 'PARANIN YOLU', 'BANKA ≠ KUYUMCU',
  'DOĞRU KIYAS', 'ZAMAN ÖLÇEĞİ', '3 PARÇA', 'SON SÖZ'];

const S = [];

// 0 — Açılış
S[0] = (p) => {
  const tDus = cue(p, 'düşüyor'), tKorku = cue(p, 'korku'), tGuv = cue(p, 'güvenli');
  const fall = eo(P(tDus, 0.55));
  const bob = Math.sin(T * 2) * 8 * (1 - fall);
  // başlık
  A(tDus - 0.05, W / 2, 170, (q) => {
    tx('ALTIN NEDEN', 0, -70, 76, { w: 900, c: C.white, ls: 3 });
    tx('DÜŞÜYOR?', 0, 40, 124, { w: 900, c: C.gold, glow: 30, ls: 4 });
  }, { m: 'down' });
  // sol: enflasyon
  A(-0.2, 400, 470, () => {
    card(360, 330, { accent: C.red });
    g.save(); g.translate(-80, 10); thermo(170, 0.35 + 0.55 * eo(P(0.1, 1.4))); g.restore();
    g.save(); g.translate(90, -10); barrow(110, -1, C.red); g.restore();
    tx('ENFLASYON', 0, 120, 38, { w: 900 });
  }, { m: 'left', out: tDus - 0.1 < 0 ? null : null });
  // sağ: gerilim
  A(cue(p, 'dünyada') - 0.1, 1520, 470, () => {
    card(360, 330, { accent: C.gold });
    g.save(); g.translate(-10, -10); globe(95); g.restore();
    const fl = 0.6 + 0.4 * Math.sin(T * 18);
    g.save(); g.translate(80, -60); g.globalAlpha *= fl; bolt(90, C.gold); g.restore();
    tx('GERİLİM', 0, 120, 38, { w: 900 });
  }, { m: 'right' });
  // orta: külçe + kalkan
  A(tGuv - 0.1, W / 2, 470, () => { g.save(); g.globalAlpha *= 0.9 * (1 - fall * 0.6); shield(330, C.teal); g.restore(); }, { d: 0.6 });
  g.save(); g.translate(W / 2, 520 + bob + fall * 70); g.rotate(fall * 0.12);
  const s0 = eback(P(-0.3, 0.6));
  g.scale(s0, s0); goldBar(330, { glow: 20 }); g.restore();
  A(tGuv + 0.2, W / 2, 690, () => chip('GÜVENLİ LİMAN?', 32, { bg: C.teal, c: C.ink }), { out: tDus - 0.05 });
  A(tDus, W / 2 + 250, 560, () => barrow(170, 1, C.red, 50), { m: 'down' });
  // korku yetmez
  A(tKorku - 0.25, W / 2, 790, () => {
    tx('Fiyatı yalnızca', -150, 0, 44, { w: 700, c: C.white });
    tx('KORKU', 150, 0, 56, { w: 900, c: C.red, glow: 20 });
    tx('belirlemiyor', 0, 62, 44, { w: 700, c: C.white });
  }, { m: 'up' });
};

// 1 — Reuters, spot altın
S[1] = (p) => {
  const t0 = PS[p], tSpot = cue(p, 'spot'), tPct = cue(p, '%3,8'), tAnl = cue(p, 'anlık'), tKap = cue(p, 'kapanışı');
  A(t0, W / 2, 150, () => chip('REUTERS  ·  28 EYLÜL', 30, { bg: 'rgba(255,255,255,0.12)', c: C.white, line: 'rgba(255,255,255,0.25)' }), { m: 'down' });
  A(t0 + 0.2, 690, 540, () => {
    card(1120, 560, {});
    tx('SPOT ALTIN · GÜN İÇİ', -510, -235, 26, { a: 'left', c: C.mute, ls: 2 });
    axes(-500, -190, 1000, 380);
    const pts = seq(60, (u, i) => {
      const base = u < 0.35 ? 0.82 + 0.05 * Math.sin(u * 30) : 0.82 - (u - 0.35) / 0.65 * 0.7;
      return clamp(base + noise(i, 4) * 0.08, 0.05, 0.98);
    });
    const pr = eio(clamp((T - tSpot) / (tPct + 1.2 - tSpot)));
    lineChart(-500, -190, 1000, 380, pts, pr, { c: pr > 0.4 ? C.red : C.gold, fc: pr > 0.4 ? 'rgba(255,77,94,' : 'rgba(255,200,61,' });
    note('TEMSİLİ GÖRÜNÜM', 420, 245);
  }, { m: 'up', sfx: false });
  // fiyat kutusu
  A(tSpot, 1540, 420, () => {
    card(460, 300, { accent: C.gold });
    tx('SPOT ALTIN (ONS)', 0, -95, 26, { c: C.mute, ls: 2 });
    const pr = eio(clamp((T - tSpot) / (cue(p, '4.122') + 0.4 - tSpot)));
    const v = Math.round(lerp(4285, 4122, pr));
    tx('≈ $' + v.toLocaleString('tr-TR'), 0, -10, 76, { w: 900, fam: F, c: C.white });
    A(tPct, 0, 90, () => chip('▼ %3,8', 40, { bg: C.red, c: '#fff', glow: 25 }));
  }, { m: 'right' });
  A(tAnl - 0.1, 1540, 680, () => stamp('ANLIK FİYAT', 40, C.gold, -0.08));
  A(tKap - 0.2, 1540, 800, () => {
    tx('GÜN SONU KAPANIŞI', 0, 0, 32, { c: C.mute, w: 800 });
    strike(-190, 0, 190, 0, P(tKap + 0.3, 0.4), C.red, 7);
  }, { m: 'up' });
};

// 2 — Ons ≠ gram
S[2] = (p) => {
  const tGram = cue(p, 'gram'), tOns = cue(p, 'ons'), tAyni = cue(p, 'aynı'), tYan = cue(p, 'yanlış');
  A(tGram - 0.3, 560, 470, () => {
    card(560, 520, { accent: C.gold });
    tx('GRAM', 0, -180, 64, { w: 900, c: C.gold });
    tx('Türkiye · ₺', 0, -115, 32, { w: 700, c: C.mute });
    g.save(); g.translate(0, 20); goldBar(150); g.restore();
    tx('1 gram', 0, 120, 38, { w: 800 });
    tx('TL ile fiyatlanır', 0, 180, 28, { w: 600, c: C.mute });
  }, { m: 'left' });
  A(tOns - 0.2, 1360, 470, () => {
    card(560, 520, { accent: C.blue });
    tx('ONS', 0, -180, 64, { w: 900, c: C.blue });
    tx('Dünya · $', 0, -115, 32, { w: 700, c: C.mute });
    g.save(); g.translate(0, 20); goldBar(300); g.restore();
    tx('≈ 31,1 gram', 0, 120, 38, { w: 800 });
    tx('Dolar ile fiyatlanır', 0, 180, 28, { w: 600, c: C.mute });
  }, { m: 'right' });
  A(tAyni, W / 2, 470, () => tx('≠', 0, 0, 200, { w: 900, c: C.red, glow: 40 }));
  A(tYan - 0.3, W / 2, 830, () => {
    chip('⚠  FARKI BİLMEDEN YANLIŞ OKURSUN', 34, { bg: C.gold, c: C.ink });
  }, { m: 'up' });
};

// 3 — Formül
S[3] = (p) => {
  const t0 = PS[p];
  const tiles = [
    [cue(p, 'ons'), 'ONS', '$', C.gold, 'ons fiyatı'],
    [cue(p, 'dolar'), 'USD/TRY', '₺', C.blue, 'dolar kuru'],
    [cue(p, '31,1'), '31,1', 'g', '#9AA7C7', 'ons → gram'],
  ];
  A(t0, W / 2, 190, () => tx('GRAM ALTININ TEORİK TL DEĞERİ', 0, 0, 48, { w: 900, c: C.white, ls: 2 }), { m: 'down' });
  const xs = [330, 760, 1190, 1600], ops = ['×', '÷', '='];
  tiles.forEach(([tt, a, b, col, lab], i) => {
    A(tt - 0.1, xs[i], 480, () => {
      card(300, 230, { accent: col });
      tx(a, 0, -20, a.length > 5 ? 54 : 70, { w: 900, c: col });
      tx(lab, 0, 62, 26, { w: 600, c: C.mute });
    });
    A(tt + 0.25, (xs[i] + xs[i + 1]) / 2, 480, () => tx(ops[i], 0, 0, 90, { w: 900, c: C.white }), { sfx: false });
  });
  A(cue(p, 'bulunur') - 0.15, xs[3], 480, () => {
    card(320, 260, { fill: 'rgba(60,44,8,0.95)', stroke: C.gold, lw: 4 });
    g.save(); g.translate(0, -30); goldBar(170); g.restore();
    tx('GRAM ₺', 0, 70, 48, { w: 900, c: C.gold, glow: 20 });
  });
  A(cue(p, 'yerel') - 0.1, W / 2 + 200, 770, () => {
    chip('+ YEREL FİYAT FARKLARI', 38, { bg: 'rgba(255,255,255,0.1)', c: C.gold, line: C.gold });
  }, { m: 'up' });
  arr(W / 2 + 420, 740, xs[3] - 30, 640, eo(P(cue(p, 'bunun'), 0.5)), { c: C.gold, w: 6, dash: [14, 12] });
};

// 4 — İki kuvvet: tahterevalli
S[4] = (p) => {
  const tOns = cue(p, 'ons'), tDol = cue(p, 'dolar'), tDen = cue(p, 'kısmen'), tMut = cue(p, 'mutlaka');
  const a1 = eback(P(tOns + 0.2, 0.7)), a2 = eback(P(tDol + 0.2, 0.8));
  const ang = -0.2 * a1 + 0.15 * a2 + Math.sin(T * 3) * 0.008;
  const cx = W / 2, cy = 560, L = 520;
  // pivot
  g.save(); g.translate(cx, cy);
  g.beginPath(); g.moveTo(0, 0); g.lineTo(-70, 190); g.lineTo(70, 190); g.closePath();
  g.fillStyle = '#2b3a66'; g.fill(); g.lineWidth = 3; g.strokeStyle = 'rgba(255,255,255,0.2)'; g.stroke();
  g.rotate(ang);
  rr(-L, -14, 2 * L, 28, 14); g.fillStyle = '#c9d2e6'; g.fill();
  g.beginPath(); g.arc(0, 0, 22, 0, 7); g.fillStyle = C.gold; g.fill();
  // gram göstergesi (ortada)
  tx('GRAM ₺', 0, -60, 34, { w: 900, c: C.gold });
  // sol ağırlık: ONS
  A(tOns - 0.1, -L + 130, -95, () => {
    card(230, 150, { fill: 'rgba(255,77,94,0.18)', stroke: C.red, lw: 4 });
    tx('ONS', 0, -22, 50, { w: 900, c: C.white });
    tx('▼ düşüyor', 0, 34, 28, { w: 800, c: C.red });
  }, { m: 'down' });
  // sağ: DOLAR
  A(tDol - 0.1, L - 130, -95, () => {
    card(230, 150, { fill: 'rgba(47,227,154,0.16)', stroke: C.green, lw: 4 });
    tx('DOLAR/TL', 0, -22, 42, { w: 900, c: C.white });
    tx('▲ yükseliyor', 0, 34, 28, { w: 800, c: C.green });
  }, { m: 'down' });
  g.restore();
  A(tOns, cx - L + 130, 290, () => barrow(90, 1, C.red, 30), { m: 'down', sfx: false });
  A(tDol, cx + L - 130, 270, () => barrow(90, -1, C.green, 30), { m: 'up', sfx: false });
  A(tDen - 0.2, cx, 200, () => chip('İKİ KUVVET KISMEN DENGELENİR', 36, { bg: C.gold }), { m: 'down', out: tMut - 0.9 });
  A(tMut - 0.6, cx, 190, () => {
    tx('DOLAR ▲', -330, 0, 58, { w: 900, c: C.green });
    tx('≠', 0, 0, 80, { w: 900, c: C.red, glow: 20 });
    tx('GRAM MUTLAKA ▲', 380, 0, 58, { w: 900, c: C.white });
  }, { m: 'down' });
};

// 5 — Temsili hesap
S[5] = (p) => {
  const t0 = PS[p], t4 = cue(p, '%4'), t3 = cue(p, '%3y'), tR = cue(p, '%1,12'), tG = cue(p, 'gramın');
  A(t0, W / 2, 150, () => stamp('TEMSİLİ HESAP', 40, C.gold, 0), { m: 'down' });
  A(t4 - 0.4, 560, 330, () => {
    card(760, 150, { accent: C.red });
    tx('ONS', -300, 0, 50, { w: 900, a: 'left' });
    tx('−%4', 80, 0, 64, { w: 900, c: C.red });
    tx('× 0,96', 260, 0, 44, { w: 800, c: C.mute, fam: MONO });
  }, { m: 'left' });
  A(t3 - 0.6, 560, 510, () => {
    card(760, 150, { accent: C.green });
    tx('DOLAR KURU', -300, 0, 46, { w: 900, a: 'left' });
    tx('+%3', 120, 0, 64, { w: 900, c: C.green });
    tx('× 1,03', 280, 0, 44, { w: 800, c: C.mute, fam: MONO });
  }, { m: 'left' });
  A(tG - 0.2, 560, 720, () => {
    card(760, 200, { fill: 'rgba(60,20,28,0.95)', stroke: C.red, lw: 4 });
    tx('GRAM (TEORİK)', -300, -45, 40, { w: 900, a: 'left', c: C.gold });
    tx('0,96 × 1,03 = 0,9888', -300, 25, 30, { w: 700, a: 'left', c: C.white, fam: MONO });
    A(tR - 0.1, 245, 0, () => tx('≈ −%1,12', 0, 0, 62, { w: 900, c: C.red, glow: 25 }));
  }, { m: 'up' });
  // sağ: yatay çubuklar
  const bx = 1440, sc = 90;
  A(t4, bx, 330, () => {}, { sfx: false });
  g.save();
  g.strokeStyle = 'rgba(255,255,255,0.3)'; g.lineWidth = 3; g.beginPath(); g.moveTo(bx, 250); g.lineTo(bx, 800); g.stroke();
  const bars = [[t4, -4, C.red, 'ONS', 330], [t3, 3, C.green, 'KUR', 510], [tR, -1.12, C.red, 'GRAM', 720]];
  for (const [tt, v, col, lab, y] of bars) {
    const q = eo(P(tt, 0.7)); if (q <= 0) continue;
    const w = v * sc * q;
    rr(Math.min(bx, bx + w), y - 34, Math.abs(w), 68, 10); g.fillStyle = col; g.shadowColor = col; g.shadowBlur = 20; g.fill(); g.shadowBlur = 0;
    tx(lab, v < 0 ? bx + 30 : bx - 30, y, 30, { w: 900, a: v < 0 ? 'left' : 'right', c: C.mute });
  }
  g.restore();
};

// 6 — Çelişki yok + asıl soru
S[6] = (p) => {
  const tC = cue(p, 'çelişki'), tK = cue(p, 'kayıp'), tKur = cue(p, 'kur'), tB = cue(p, 'büyük'), tS = cue(p, 'şimdi'), tQ = cue(p, 'ons', 1);
  const out = tS + 0.3;
  A(tC - 0.1, W / 2, 200, () => {
    g.save(); g.translate(-300, 0); check(70, P(tC, 0.5)); g.restore();
    tx('ÇELİŞKİ YOK', 40, 0, 72, { w: 900, c: C.green, glow: 20 });
  }, { out });
  A(tK - 0.5, 620, 560, () => {
    const h = 360 * eo(P(tK - 0.3, 0.8));
    rr(-110, 180 - h, 220, h, 14); g.fillStyle = C.red; g.shadowColor = C.red; g.shadowBlur = 30; g.fill();
    tx('ONS KAYBI', 0, 230, 36, { w: 900 });
    tx('%4', 0, 150 - h, 50, { w: 900, c: C.red });
  }, { out, m: 'up' });
  A(tKur - 0.2, 1300, 560, () => {
    const h = 270 * eo(P(tKur, 0.8));
    rr(-110, 180 - h, 220, h, 14); g.fillStyle = C.green; g.shadowColor = C.green; g.shadowBlur = 30; g.fill();
    tx('KUR ARTIŞI', 0, 230, 36, { w: 900 });
    tx('%3', 0, 150 - h, 50, { w: 900, c: C.green });
  }, { out, m: 'up' });
  A(tB - 0.1, W / 2, 560, () => tx('>', 0, 0, 200, { w: 900, c: C.gold, glow: 30 }), { out });
  // asıl soru
  A(tS + 0.35, W / 2, 330, () => {
    tx('ONS ALTINI', 0, -60, 80, { w: 900 });
    tx('AŞAĞI ÇEKEN NE?', 0, 40, 96, { w: 900, c: C.gold, glow: 25 });
  }, { m: 'down' });
  const cards = [['1', 'FAİZ'], ['2', 'DOLAR'], ['3', 'PETROL']];
  cards.forEach(([n], i) => {
    A(tQ + 0.3 + i * 0.25, W / 2 + (i - 1) * 330, 690, () => {
      card(260, 230, { fill: 'rgba(255,200,61,0.12)', stroke: C.gold, lw: 3 });
      tx(n, 0, -40, 90, { w: 900, c: C.gold });
      tx('?', 0, 60, 60, { w: 900, c: C.white });
    });
  });
};

// 7 — Külçe faiz ödemez
S[7] = (p) => {
  const t0 = PS[p], tF = cue(p, 'faiz'), tK = cue(p, 'kupon'), tF2 = cue(p, 'faiz', 1), tCaz = cue(p, 'cazipleştiğinde'), tM = cue(p, 'maliyeti');
  A(t0 - 0.1, 240, 150, () => badge(1, 'FAİZ'), { m: 'left' });
  A(t0, 560, 520, () => {
    card(620, 560, { accent: C.gold });
    g.save(); g.translate(0, -90); goldBar(320, { glow: 12 }); g.restore();
    A(tF - 0.1, 0, 90, () => { tx('FAİZ', -90, 0, 44, { w: 900, a: 'right' }); tx('0', 20, 0, 60, { w: 900, c: C.red, a: 'left' }); });
    A(tK - 0.1, 0, 170, () => { tx('KUPON', -90, 0, 44, { w: 900, a: 'right' }); tx('0', 20, 0, 60, { w: 900, c: C.red, a: 'left' }); });
  }, { m: 'left' });
  A(tF2 - 0.2, 1360, 520, () => {
    card(620, 560, { accent: C.green });
    tx('FAİZ GETİRİLİ', 0, -220, 44, { w: 900, c: C.green });
    tx('mevduat · tahvil', 0, -170, 28, { w: 600, c: C.mute });
    // kumbara kutusu
    rr(-150, 20, 300, 170, 20); g.fillStyle = '#1d3a36'; g.fill(); g.lineWidth = 4; g.strokeStyle = C.green; g.stroke();
    rr(-60, 12, 120, 16, 8); g.fillStyle = C.ink; g.fill();
    const rate = T > tCaz ? 2.6 : 1.3;
    for (let i = 0; i < 4; i++) {
      const ph = ((T - tF2) * rate / 1.2 + i / 4) % 1;
      if (T - tF2 < i * 0.3) continue;
      g.save(); g.translate(0, lerp(-95, 30, eio(ph))); g.globalAlpha *= 1 - clamp((ph - 0.85) / 0.15); coin(38, '%', { c1: '#b8ffd9', c2: '#23b47a', tc: '#0b3b27' }); g.restore();
    }
    const glow = eo(P(tCaz, 0.6));
    if (glow > 0) { g.save(); g.globalAlpha *= glow; tx('CAZİP', 0, 250, 40, { w: 900, c: C.green, glow: 25 }); g.restore(); }
  }, { m: 'right' });
  A(tM - 0.4, 560, 880, () => chip('VAZGEÇİLEN GELİR = FIRSAT MALİYETİ ▲', 30, { bg: C.red, c: '#fff' }), { m: 'up' });
};

// 8 — Fed
S[8] = (p) => {
  const tA = cue(p, 'amerikan'), tD = cue(p, '16'), tC = cue(p, 'çeyrek'), tR = cue(p, '%3,75'), tArt = cue(p, 'artırarak');
  A(PS[p] - 0.1, 240, 150, () => badge(1, 'FAİZ'), { sfx: false });
  A(tA - 0.2, 380, 520, () => {
    card(460, 470, { accent: C.blue });
    g.save(); g.translate(0, -40); bank(250, 'FED', C.white); g.restore();
    tx('ABD MERKEZ BANKASI', 0, 170, 30, { w: 900 });
  }, { m: 'left' });
  A(tD - 0.2, 380, 910, () => chip('16 EYLÜL', 34, { bg: C.red, c: '#fff' }), { m: 'up' });
  // basamak grafik
  A(tA, 1180, 540, () => {
    card(900, 560, {});
    tx('POLİTİKA FAİZ ARALIĞI', -400, -230, 26, { a: 'left', c: C.mute, ls: 2 });
    const x0 = -380, x1 = 380, yb = 200, sc = 300; // %3,25..%4,25 ölçek
    const Y = v => yb - (v - 3.25) * sc;
    const step = eo(P(tArt, 0.8)), xm = 40;
    g.save();
    g.fillStyle = 'rgba(77,163,255,0.25)'; g.fillRect(x0, Y(3.75), xm - x0, Y(3.5) - Y(3.75));
    g.strokeStyle = C.blue; g.lineWidth = 5; g.strokeRect(x0, Y(3.75), xm - x0, Y(3.5) - Y(3.75));
    if (step > 0) {
      const top = lerp(Y(3.75), Y(4.0), step), bot = lerp(Y(3.5), Y(3.75), step);
      g.fillStyle = 'rgba(255,200,61,0.3)'; g.fillRect(xm, top, (x1 - xm) * clamp(step * 1.3), bot - top);
      g.strokeStyle = C.gold; g.shadowColor = C.gold; g.shadowBlur = 20; g.strokeRect(xm, top, (x1 - xm) * clamp(step * 1.3), bot - top);
    }
    g.restore();
    for (const v of [3.5, 3.75, 4.0]) tx('%' + v.toFixed(2).replace('.', ','), x0 - 20, Y(v), 22, { a: 'right', c: C.mute, w: 700, fam: MONO });
    tx('ÖNCE', (x0 + xm) / 2, yb + 40, 24, { c: C.mute });
    tx('16 EYLÜL SONRASI', (xm + x1) / 2, yb + 40, 24, { c: C.gold });
    A(tC - 0.1, (xm + x1) / 2, Y(4.0) - 60, () => chip('+0,25 PUAN', 30, { bg: C.gold }));
  }, { m: 'right', sfx: false });
  A(tR - 0.1, 1180, 150, () => tx('%3,75 – %4,00', 0, 0, 80, { w: 900, c: C.gold, glow: 25 }), { m: 'down' });
};

// 9 — Beklenti, reel getiri
S[9] = (p) => {
  const t0 = PS[p], tU = cue(p, 'uzun'), tE = cue(p, 'enflasyondan'), tC = cue(p, 'cazibesini');
  A(t0 - 0.1, 240, 150, () => badge(1, 'FAİZ'), { sfx: false });
  A(t0, 560, 540, () => {
    card(820, 520, {});
    tx('FAİZ BEKLENTİSİ', -370, -210, 26, { a: 'left', c: C.mute, ls: 2 });
    axes(-360, -150, 720, 320);
    const q = clamp((T - t0) / 1.2);
    // bugün noktası
    const xb = -200;
    g.save(); g.strokeStyle = 'rgba(255,255,255,0.35)'; g.setLineDash([8, 8]); g.lineWidth = 3;
    g.beginPath(); g.moveTo(xb, -170); g.lineTo(xb, 190); g.stroke(); g.restore();
    tx('BUGÜN', xb, 210, 24, { c: C.white });
    lineChart(-360, -150, 160, 320, [0.3, 0.45, 0.62, 0.75], eo(q), { c: C.gold, dot: false });
    const q2 = eio(P(tU - 0.2, 1.4));
    if (q2 > 0) lineChart(xb, -150, 560, 320, [0.75, 0.78, 0.77, 0.79, 0.78, 0.8], q2, { c: C.gold, dash: [18, 12], fill: false });
    A(tU + 0.3, 180, -190, () => chip('DAHA UZUN SÜRE YÜKSEK', 26, { bg: C.gold }));
  }, { m: 'left', sfx: false });
  A(tE - 0.3, 1400, 330, () => {
    card(720, 200, { accent: C.teal });
    tx('REEL GETİRİ', 0, -45, 46, { w: 900, c: C.teal });
    tx('= faiz − enflasyon', 0, 30, 40, { w: 700, fam: MONO });
  }, { m: 'right' });
  A(tC - 0.4, 1400, 700, () => {
    card(720, 380, {});
    const v = lerp(0.7, 0.22, eio(P(tC, 1.0)));
    g.save(); g.translate(0, 60); gauge(170, v, ''); g.restore();
    tx('ALTININ CAZİBESİ', 0, -140, 36, { w: 900 });
  }, { m: 'up' });
};

// 10 — Güçlü dolar
S[10] = (p) => {
  const t0 = PS[p], tG = cue(p, 'güçlü'), tF = cue(p, 'fiyatlanır'), tB = cue(p, 'başka'), tM = cue(p, 'maliyeti'), tT = cue(p, 'talebi');
  A(t0 - 0.1, 240, 150, () => badge(2, 'GÜÇLÜ DOLAR', C.blue));
  const pulse = 1 + 0.06 * Math.sin(T * 6) * P(tG, 0.4);
  A(tG - 0.2, 560, 520, () => {
    g.save(); g.scale(pulse, pulse); coin(190, '$', { c1: '#b9ddff', c2: '#2f78d6', tc: '#07234a' }); g.restore();
    const q = P(tG, 0.6);
    for (let i = 0; i < 12; i++) {
      const a = i / 12 * Math.PI * 2 + T * 0.4;
      g.save(); g.globalAlpha *= 0.5 * q; g.strokeStyle = C.blue; g.lineWidth = 5; g.lineCap = 'round';
      g.beginPath(); g.moveTo(Math.cos(a) * 230, Math.sin(a) * 230); g.lineTo(Math.cos(a) * (250 + 30 * q), Math.sin(a) * (250 + 30 * q)); g.stroke(); g.restore();
    }
  });
  A(tF - 0.5, 560, 860, () => {
    g.save(); g.translate(-120, 0); goldBar(180); g.restore();
    tx('= $ ile fiyatlanır', 100, 0, 36, { w: 800, a: 'left' });
  }, { m: 'up' });
  const cur = [['€', '#c7a6ff', '#6d45c9'], ['£', '#ffd1a6', '#c96f2b'], ['¥', '#ffb3be', '#c9344a'], ['₺', '#b8ffd9', '#23b47a']];
  cur.forEach(([s, a, b], i) => {
    A(tB - 0.1 + i * 0.18, 1150 + i * 190, 430, () => {
      coin(70, s, { c1: a, c2: b, tc: '#111' });
      A(tM - 0.1 + i * 0.1, 0, -120, () => chip('+ MALİYET', 22, { bg: C.red, c: '#fff' }), { sfx: i === 0 });
    }, { sfx: i === 0 });
  });
  A(tB + 0.3, 1435, 560, () => tx('başka para birimiyle altın alanlar', 0, 0, 30, { w: 700, c: C.mute }), { sfx: false });
  A(tT - 0.3, 1435, 760, () => {
    card(560, 200, { fill: 'rgba(255,77,94,0.16)', stroke: C.red, lw: 4 });
    tx('TALEP', -80, 0, 70, { w: 900 });
    g.save(); g.translate(150, 0); barrow(120, 1, C.red); g.restore();
  }, { m: 'up' });
};

// 11 — İki farklı gösterge
S[11] = (p) => {
  const tK = cue(p, 'küresel'), tT = cue(p, 'türk'), tA = cue(p, 'aynı'), tG = cue(p, 'tek');
  A(PS[p] - 0.1, 240, 150, () => badge(2, 'GÜÇLÜ DOLAR', C.blue), { sfx: false });
  const out = tG - 0.2;
  const dxy = seq(40, (u, i) => 0.5 + 0.18 * Math.sin(u * 7) + noise(i, 9) * 0.12);
  const tl = seq(40, (u, i) => 0.12 + 0.75 * u + noise(i, 2) * 0.05);
  A(tK - 0.3, 520, 530, () => {
    card(700, 460, { accent: C.blue });
    tx('DOLARIN KÜRESEL GÜCÜ', 0, -180, 36, { w: 900, c: C.blue });
    tx('diğer büyük paralara karşı', 0, -135, 24, { w: 600, c: C.mute });
    lineChart(-300, -90, 600, 260, dxy, eio(P(tK, 1.3)), { c: C.blue, fc: 'rgba(77,163,255,' });
    note('TEMSİLİ', 260, 200);
  }, { m: 'left', out });
  A(tT - 0.3, 1400, 530, () => {
    card(700, 460, { accent: C.orange });
    tx('DOLAR / TÜRK LİRASI', 0, -180, 36, { w: 900, c: C.orange });
    tx('USD/TRY kuru', 0, -135, 24, { w: 600, c: C.mute });
    lineChart(-300, -90, 600, 260, tl, eio(P(tT, 1.3)), { c: C.orange, fc: 'rgba(255,159,67,' });
    note('TEMSİLİ', 260, 200);
  }, { m: 'right', out });
  A(tA, W / 2, 530, () => tx('≠', 0, 0, 180, { w: 900, c: C.red, glow: 40 }), { out });
  A(tG - 0.1, W / 2, 520, () => {
    card(900, 480, {});
    tx('TEK GRAFİK?', 0, -170, 44, { w: 900 });
    lineChart(-360, -110, 720, 280, dxy, 1, { c: C.blue, fill: false, dot: false });
    lineChart(-360, -110, 720, 280, tl, 1, { c: C.orange, fill: false, dot: false });
    g.save(); g.translate(0, 30); cross(300, P(tG + 0.4, 0.5)); g.restore();
  });
};

// 12 — Petrol zinciri
S[12] = (p) => {
  const t0 = PS[p];
  A(t0 - 0.1, 240, 150, () => badge(3, 'PETROL', C.orange));
  const nodes = [
    [cue(p, 'petrol'), 'ENERJİ ▲', C.orange, () => barrel(170)],
    [cue(p, 'enflasyon'), 'ENFLASYON ENDİŞESİ ▲', C.red, () => thermo(170, 0.5 + 0.35 * eo(P(cue(p, 'endişesi'), 1)))],
    [cue(p, 'merkez'), 'FAİZ YÜKSEK KALIR', C.blue, () => bank(170, '%', C.white)],
    [cue(p, 'güçlendirebilir'), 'ALTIN BASKI ALTINDA', C.gold, () => { goldBar(190); g.save(); g.translate(110, 30); barrow(70, 1, C.red); g.restore(); }],
  ];
  const xs = [270, 730, 1190, 1650], y = 540;
  nodes.forEach(([tt, lab, col, icon], i) => {
    A(tt - 0.2, xs[i], y, () => {
      card(380, 400, { accent: col });
      g.save(); g.translate(0, -40); icon(); g.restore();
      tx(lab, 0, 140, 28, { w: 900, c: col, max: 340 });
    }, { m: 'up' });
    if (i < 3) arr(xs[i] + 200, y, xs[i + 1] - 200, y, eo(P(nodes[i + 1][0] - 0.4, 0.4)), { c: C.white, w: 6, hs: 22 });
  });
  A(cue(p, 'şaşırtıcı'), W / 2, 870, () => tx('ŞAŞIRTICI 3. BAĞLANTI', 0, 0, 34, { w: 900, c: C.mute, ls: 4 }), { sfx: false });
};

// 13 — Ters köşe: iki yol
S[13] = (p) => {
  const tT = cue(p, 'ters'), tE = cue(p, 'enflasyon'), tB1 = cue(p, 'bazen'), tB2 = cue(p, 'bazen', 1), tG = cue(p, 'güçlü'), tH = cue(p, 'haber');
  A(tT - 0.2, W / 2, 150, () => stamp('TERS KÖŞE', 52, C.gold, -0.05), { m: 'down' });
  const rx = 420, ry = 560;
  A(tE - 0.2, rx, ry, () => {
    card(460, 220, { accent: C.red });
    tx('ENFLASYON', 0, -30, 50, { w: 900 });
    tx('KORKUSU', 0, 34, 50, { w: 900, c: C.red });
  }, { m: 'left' });
  // yollar
  const hl = T > tH ? (Math.floor((T - tH) / 0.8) % 2) : -1;
  const up = eo(P(tB1, 0.5)), dn = eo(P(tB2, 0.5));
  const thick = 1 + 0.8 * eo(P(tG, 0.5));
  arr(rx + 240, ry - 40, 1150, 330, up, { c: hl === 1 ? 'rgba(47,227,154,0.35)' : C.green, w: 8, glow: 20 });
  arr(rx + 240, ry + 40, 1150, 790, dn, { c: hl === 0 ? 'rgba(255,77,94,0.35)' : C.red, w: 8 * thick, glow: 20 });
  A(tB1 + 0.2, 1440, 330, () => {
    card(560, 190, { fill: 'rgba(47,227,154,0.14)', stroke: C.green, lw: 4 });
    tx('ALTINA TALEP ▲', 0, -20, 44, { w: 900, c: C.green });
    tx('güvenli liman etkisi', 0, 38, 26, { w: 600, c: C.mute });
  }, { m: 'right' });
  A(tB2 + 0.2, 1440, 790, () => {
    card(560, 190, { fill: 'rgba(255,77,94,0.14)', stroke: C.red, lw: 4 });
    tx('FAİZ + DOLAR KANALI', 0, -28, 40, { w: 900, c: C.red });
    tx('→ ALTIN ▼', 0, 34, 40, { w: 900, c: C.white });
  }, { m: 'right' });
  A(tG - 0.1, 1440, 640, () => chip('bazen DAHA GÜÇLÜ', 26, { bg: C.red, c: '#fff' }));
  A(tH - 0.4, rx, 820, () => chip('AYNI HABER → FARKLI SONUÇ', 28, { bg: 'rgba(255,255,255,0.12)', c: C.white, line: 'rgba(255,255,255,0.3)' }), { m: 'up' });
};

// 14 — Kural yok / güvenli liman
S[14] = (p) => {
  const tK = cue(p, 'kriz'), tKu = cue(p, 'kural'), tG = cue(p, 'güvenli'), tKi = cue(p, 'kısa');
  A(tK - 0.25, W / 2, 250, () => {
    card(1300, 170, {});
    tx('KRİZ ÇIKTI  →  ALTIN KESİN YÜKSELİR', 0, 0, 58, { w: 900 });
    strike(-620, 0, 620, 0, P(tKu - 0.1, 0.5), C.red, 12);
  }, { m: 'down' });
  A(tKu + 0.1, 1420, 370, () => stamp('BÖYLE BİR KURAL YOK', 36, C.red, -0.1));
  A(tG - 0.2, 560, 680, () => {
    card(620, 400, { accent: C.teal });
    g.save(); g.translate(0, -30); shield(200, C.teal); g.restore();
    g.save(); g.translate(0, -40); goldBar(120); g.restore();
    tx('GÜVENLİ LİMAN', 0, 140, 44, { w: 900, c: C.teal });
    // dalgalar
    g.save(); g.strokeStyle = 'rgba(77,163,255,0.5)'; g.lineWidth = 4;
    for (let k = 0; k < 2; k++) { g.beginPath(); for (let x = -280; x <= 280; x += 8) g.lineTo(x, 95 + k * 14 + Math.sin(x / 30 + T * 3 + k) * 6); g.stroke(); }
    g.restore();
  }, { m: 'left' });
  A(tKi - 0.2, 1360, 680, () => {
    card(760, 400, { accent: C.red });
    tx('KISA VADE', -340, -150, 30, { w: 900, c: C.mute, a: 'left', ls: 2 });
    const pts = seq(40, (u, i) => 0.6 - 0.45 * Math.sin(u * 3.2) + noise(i, 5) * 0.1);
    lineChart(-320, -100, 640, 220, pts, eio(P(tKi, 1.4)), { c: C.red, fc: 'rgba(255,77,94,' });
    tx('zarar ETMEZ demek değil', 0, 160, 34, { w: 800 });
  }, { m: 'right' });
  A(tKi + 0.2, W / 2 - 60, 680, () => tx('≠', 0, 0, 120, { w: 900, c: C.red, glow: 30 }));
};

// 15 — Türkiye
S[15] = (p) => {
  const t0 = PS[p], tK = cue(p, 'kur'), tY = cue(p, 'yerel'), tE = cue(p, 'enflasyon'), tKu = cue(p, 'küresel'), tEk = cue(p, 'eksik');
  const shift = eio(P(tKu - 0.2, 0.8));
  const cx = lerp(W / 2, 1320, shift), cy = 520;
  A(t0 - 0.1, cx, cy, () => {
    g.save(); g.beginPath(); g.arc(0, 0, 150, 0, 7); g.fillStyle = 'rgba(227,10,23,0.9)'; g.shadowColor = '#e30a17'; g.shadowBlur = 40; g.fill(); g.restore();
    tx('TÜRKİYE', 0, -20, 44, { w: 900 });
    tx('₺', 0, 45, 56, { w: 900 });
  });
  const orb = [[tK, 'KUR', C.blue], [tY, 'YEREL FAİZ', C.gold], [tE, 'ENFLASYON', C.red]];
  orb.forEach(([tt, lab, col], i) => {
    const a = -Math.PI / 2 + i * (Math.PI * 2 / 3) + T * 0.35;
    const R = 290;
    A(tt - 0.1, cx + Math.cos(a) * R, cy + Math.sin(a) * R * 0.8, () => chip(lab, 34, { bg: col, c: col === C.red || col === C.blue ? '#fff' : C.ink, glow: 20 }));
  });
  A(tKu - 0.1, 460, 520, () => {
    card(520, 420, { accent: C.blue });
    g.save(); g.translate(-60, -40); globe(100); g.restore();
    g.save(); g.translate(90, 20); goldBar(160); g.restore();
    tx('KÜRESEL ALTIN ($)', 0, 160, 34, { w: 900 });
  }, { m: 'left' });
  A(tKu + 0.6, 840, 520, () => tx('+', 0, 0, 120, { w: 900, c: C.gold }), { sfx: false });
  A(tEk - 0.4, W / 2, 880, () => chip('AYRI AYRI BAKMAK = EKSİK RESİM', 36, { bg: C.red, c: '#fff' }), { m: 'up' });
};

// 16 — TCMB %37
S[16] = (p) => {
  const t0 = PS[p], tD = cue(p, '10'), tR = cue(p, '%37'), tS = cue(p, 'sabit'), tB = cue(p, 'bankanın'), tM = cue(p, 'mevduat');
  A(t0 - 0.2, 330, 480, () => {
    card(440, 460, { accent: C.red });
    g.save(); g.translate(0, -40); bank(240, 'TCMB', C.white); g.restore();
    tx('MERKEZ BANKASI', 0, 170, 32, { w: 900 });
  }, { m: 'left' });
  A(tD - 0.2, 330, 870, () => chip('10 EYLÜL', 34, { bg: C.red, c: '#fff' }), { m: 'up' });
  A(tR - 0.4, 880, 480, () => {
    card(520, 460, {});
    tx('POLİTİKA FAİZİ', 0, -170, 30, { w: 900, c: C.mute, ls: 2 });
    tx('%37', 0, -30, 150, { w: 900, c: C.gold, glow: 30 });
    g.save(); g.strokeStyle = C.gold; g.lineWidth = 6; g.setLineDash([16, 12]); g.lineDashOffset = -T * 40;
    g.beginPath(); g.moveTo(-200, 110); g.lineTo(lerp(-200, 200, eo(P(tS, 0.8))), 110); g.stroke(); g.restore();
    A(tS, 0, 170, () => chip('SABİT', 32, { bg: C.gold }));
  }, { m: 'up' });
  A(tB - 0.2, 1480, 480, () => {
    card(560, 460, { accent: C.teal });
    tx('SENİN MEVDUAT FAİZİN', 0, -170, 30, { w: 900, c: C.teal });
    g.save(); g.translate(0, -20);
    rr(-150, -90, 300, 180, 20); g.fillStyle = '#16304a'; g.fill(); g.lineWidth = 3; g.strokeStyle = C.teal; g.stroke();
    rr(-150, -50, 300, 36, 0); g.fillStyle = 'rgba(45,212,191,0.5)'; g.fill();
    tx('?', 60, 40, 70, { w: 900, c: C.white });
    g.restore();
    A(tM - 0.1, 0, 150, () => tx('≠ otomatik %37', 0, 0, 44, { w: 900, c: C.red }));
  }, { m: 'right' });
};

// 17 — Ağustos TÜFE
S[17] = (p) => {
  const t0 = PS[p], tR = cue(p, '%31,51'), tE = cue(p, 'eylül'), tT = cue(p, 'tarihi');
  A(t0 - 0.2, 470, 470, () => {
    g.save(); g.scale(1.6, 1.6); calendar(220, 'AĞUSTOS', 'TÜFE', { hc: C.gold }); g.restore();
  }, { m: 'left' });
  A(t0 + 0.4, 470, 820, () => tx('TÜKETİCİ ENFLASYONU', 0, 0, 36, { w: 900, c: C.mute, ls: 2 }), { sfx: false });
  A(tR - 0.4, 1080, 470, () => {
    const v = lerp(0, 31.51, eo(P(tR - 0.3, 1.0)));
    tx('%' + v.toFixed(2).replace('.', ','), 0, 0, 170, { w: 900, c: C.gold, glow: 35 });
    tx('yıllık', 0, 110, 36, { w: 700, c: C.mute });
  }, { m: 'up' });
  A(tE - 0.2, 1600, 470, () => {
    g.save(); g.scale(1.1, 1.1); g.globalAlpha *= 0.6; calendar(220, 'EYLÜL', '?', { hc: '#6b7896' }); g.restore();
    g.save(); g.translate(0, 10); cross(230, P(tE + 0.3, 0.5)); g.restore();
    tx('bu Eylül verisi DEĞİL', 0, 200, 30, { w: 800, c: C.red });
  }, { m: 'right' });
  A(tT - 0.2, W / 2, 870, () => chip('⚠  TARİHE DİKKAT', 38, { bg: C.gold }), { m: 'up' });
};

// 18 — Paranın yolu
S[18] = (p) => {
  const tH = cue(p, 'herkesin'), tB = cue(p, 'beklentiler');
  const boxes = [
    [cue(p, 'altını'), 'ALTIN', C.gold, W / 2, 230],
    [cue(p, 'tl'), 'TL MEVDUAT', C.teal, 1450, 500],
    [cue(p, 'döviz'), 'DÖVİZ', C.blue, W / 2, 770],
    [cue(p, 'diğer'), 'DİĞER VARLIKLAR', C.purple, 470, 500],
  ];
  const shrink = eo(P(tH - 0.2, 0.6));
  g.save(); g.translate(W / 2, 500); g.scale(1 - 0.25 * shrink, 1 - 0.25 * shrink); g.translate(-W / 2, -500 - 80 * shrink);
  // akışlar
  if (T > tB) {
    for (let k = 0; k < 10; k++) {
      const a = Math.floor(hash(k + 1) * 4), b = (a + 1 + Math.floor(hash(k + 9) * 3)) % 4;
      const ph = ((T - tB) * 0.6 + hash(k + 20)) % 1;
      const [, , , x1, y1] = boxes[a], [, , , x2, y2] = boxes[b];
      const mx = (x1 + x2) / 2 + (y2 - y1) * 0.25, my = (y1 + y2) / 2 - (x2 - x1) * 0.25;
      const u = eio(ph);
      const x = (1 - u) * (1 - u) * x1 + 2 * (1 - u) * u * mx + u * u * x2, y = (1 - u) * (1 - u) * y1 + 2 * (1 - u) * u * my + u * u * y2;
      g.save(); g.translate(x, y); g.globalAlpha *= Math.sin(ph * Math.PI) * clamp((T - tB) / 0.5); coin(24, '₺'); g.restore();
    }
  }
  boxes.forEach(([tt, lab, col, x, y]) => {
    A(tt - 0.15, x, y, () => {
      card(400, 150, { fill: 'rgba(20,32,64,0.95)', stroke: col, lw: 4 });
      tx(lab, 0, 0, lab.length > 10 ? 36 : 48, { w: 900, c: col });
    });
  });
  g.restore();
  // insanlar
  const cols = [C.gold, C.teal, C.blue, C.purple, C.gold, C.teal];
  for (let i = 0; i < 6; i++) {
    A(tH + i * 0.12, 560 + i * 160, 930, () => {
      person(80, 'rgba(244,246,251,0.85)');
      g.save(); g.translate(0, -75); g.rotate([-0.6, 0.3, 0.9, -0.2, 0.5, -0.9][i]); arr(0, 0, 0, -50, 1, { c: cols[i], w: 6, hs: 16 }); g.restore();
    }, { sfx: i === 0, m: 'up' });
  }
  A(tH + 0.9, W / 2, 1010 - 60, () => {}, { sfx: false });
};

// 19 — Banka vs kuyumcu
S[19] = (p) => {
  const tB = cue(p, 'bankadaki'), tK = cue(p, 'kuyumcudaki'), tF = cue(p, 'farklı');
  A(tB - 0.2, 380, 470, () => { shop(360, 'BANKA', C.blue); }, { m: 'left' });
  A(tK - 0.2, 900, 470, () => { shop(360, 'KUYUMCU', C.gold); }, { m: 'up' });
  A(tF - 0.2, 640, 790, () => {
    const q = eo(P(tF, 0.7)), hb = 110 * q, hk = 170 * q, yb = 90;
    g.save();
    rr(-260 - 60, yb - hb, 120, hb, 10); g.fillStyle = C.blue; g.fill();
    rr(260 - 60, yb - hk, 120, hk, 10); g.fillStyle = C.gold; g.fill();
    g.strokeStyle = C.white; g.lineWidth = 3; g.setLineDash([8, 8]);
    g.beginPath(); g.moveTo(-200, yb - hb); g.lineTo(200, yb - hb); g.stroke(); g.setLineDash([]);
    g.restore();
    tx('₺', -260, yb - hb / 2, 44, { w: 900, c: C.ink });
    tx('₺', 260, yb - hk / 2, 44, { w: 900, c: C.ink });
    arr(150, yb - hb, 150, yb - hk + 6, q, { c: C.red, w: 5, hs: 16 });
    tx('FARKLI FİYAT', 0, 20, 36, { w: 900, c: C.white });
  }, { m: 'up' });
  const fac = [[cue(p, 'alış'), 'ALIŞ–SATIŞ FARKI'], [cue(p, 'fiziki'), 'FİZİKİ TALEP'], [cue(p, 'ürün'), 'ÜRÜN MALİYETİ'], [cue(p, 'işlem'), 'İŞLEM MALİYETİ']];
  fac.forEach(([tt, lab], i) => {
    A(tt - 0.15, 1500, 280 + i * 150, () => {
      card(560, 120, { fill: 'rgba(20,32,64,0.95)' });
      g.save(); g.translate(-220, 0); g.beginPath(); g.arc(0, 0, 30, 0, 7); g.fillStyle = C.gold; g.fill(); g.restore();
      tx(String(i + 1), -220, 2, 32, { w: 900, c: C.ink });
      tx(lab, 30, 0, 36, { w: 900 });
    }, { m: 'right' });
  });
  A(cue(p, 'gördüğün') - 0.1, 1500, 900, () => tx('→ gördüğün rakamı etkiler', 0, 0, 32, { w: 800, c: C.mute }), { sfx: false });
};

// 20 — Doğru kıyas
S[20] = (p) => {
  const tI = cue(p, 'internetteki'), tBoz = cue(p, 'bozdurma'), tE = cue(p, 'eşitleme'), tA = [cue(p, 'aynı'), cue(p, 'aynı', 1), cue(p, 'aynı', 2)];
  A(tI - 0.2, 330, 520, () => {
    phone(300, 560);
    tx('İNTERNET', 0, -190, 26, { w: 900, c: C.mute, ls: 3 });
    tx('GRAM ALTIN', 0, -110, 30, { w: 900 });
    tx('₺ ••••', 0, -40, 54, { w: 900, c: C.gold });
    lineChart(-110, 30, 220, 140, seq(20, (u, i) => 0.5 + noise(i, 7) * 0.5), 1, { c: C.gold, w: 4, dot: false });
  }, { m: 'left' });
  A(tBoz - 0.2, 900, 520, () => {
    card(360, 480, { fill: '#F4F6FB' });
    tx('BOZDURMA FİŞİ', 0, -190, 28, { w: 900, c: C.ink });
    g.save(); g.strokeStyle = 'rgba(10,17,40,0.25)'; g.lineWidth = 3;
    for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(-130, -120 + i * 50); g.lineTo(130 - (i % 2) * 60, -120 + i * 50); g.stroke(); }
    g.restore();
    tx('SENİN FİYATIN', 0, 160, 30, { w: 900, c: C.red });
  }, { m: 'up' });
  A(tE - 0.3, 615, 520, () => tx('≠', 0, 0, 140, { w: 900, c: C.red, glow: 30 }));
  const lab = ['AYNI ÜRÜN', 'AYNI SAAT', 'AYNI İŞLEM YÖNÜ (ALIŞ / SATIŞ)'];
  lab.forEach((s, i) => {
    A(tA[i] - 0.15, 1480, 360 + i * 170, () => {
      card(700, 130, { fill: 'rgba(20,32,64,0.95)', stroke: 'rgba(47,227,154,0.4)' });
      g.save(); g.translate(-290, 0); check(70, P(tA[i], 0.4)); g.restore();
      tx(s, -220, 0, s.length > 12 ? 32 : 44, { w: 900, a: 'left' });
    }, { m: 'right' });
  });
  A(tA[0] - 0.4, 1480, 220, () => tx('KARŞILAŞTIRMADAN ÖNCE', 0, 0, 30, { w: 900, c: C.mute, ls: 3 }), { sfx: false });
};

// 21 — Zaman ölçeği
S[21] = (p) => {
  const tS = cue(p, 'sert'), tB = cue(p, 'bütün'), tE = cue(p, 'ekran'), tSo = cue(p, 'söylemez');
  A(PS[p] - 0.2, 420, 500, () => {
    card(460, 560, {});
    tx('1 GÜN', 0, -230, 40, { w: 900 });
    const q = eo(P(tS, 0.7));
    g.save(); g.strokeStyle = C.red; g.lineWidth = 5; g.beginPath(); g.moveTo(0, -180); g.lineTo(0, -150 + 330 * q + 20); g.stroke();
    rr(-60, -150, 120, Math.max(8, 300 * q), 8); g.fillStyle = C.red; g.shadowColor = C.red; g.shadowBlur = 30; g.fill(); g.restore();
    tx('SERT DÜŞÜŞ', 0, 240, 30, { w: 900, c: C.red });
  }, { m: 'left' });
  A(tB - 0.2, 1030, 500, () => {
    card(560, 560, {});
    tx('BÜTÜN AY', 0, -230, 40, { w: 900 });
    for (let i = 0; i < 30; i++) {
      const c = i % 7, r = Math.floor(i / 7);
      const q = P(tB + i * 0.03, 0.3); if (q <= 0) continue;
      const up = hash(i * 7 + 3) > 0.45;
      g.save(); g.globalAlpha *= q; rr(-230 + c * 66, -170 + r * 80, 56, 68, 8); g.fillStyle = i === 27 ? C.red : (up ? 'rgba(47,227,154,0.55)' : 'rgba(255,77,94,0.45)'); g.fill();
      if (i === 27) { g.lineWidth = 4; g.strokeStyle = '#fff'; g.stroke(); }
      g.restore();
    }
    note('TEMSİLİ', 200, 250);
  }, { m: 'up' });
  A(tB + 0.3, 725, 500, () => tx('≠', 0, 0, 110, { w: 900, c: C.red, glow: 25 }));
  A(tE - 0.3, 1580, 500, () => {
    phone(300, 560);
    lineChart(-110, -150, 110, 200, seq(12, (u, i) => 0.6 + noise(i, 3) * 0.5), 1, { c: C.gold, w: 4, dot: false });
    g.save(); g.fillStyle = 'rgba(143,160,194,0.18)'; rr(0, -170, 110, 240, 10); g.fill(); g.restore();
    tx('?', 55, -50, 90, { w: 900, c: C.white });
    tx('EKRAN GÖRÜNTÜSÜ', 0, 150, 22, { w: 900, c: C.mute });
  }, { m: 'right' });
  A(tSo - 0.4, 1580, 870, () => chip('GELECEĞİ TEK BAŞINA SÖYLEMEZ', 26, { bg: C.gold }), { m: 'up' });
};

// 22 — Üç parça
S[22] = (p) => {
  const tO = cue(p, 'ons'), tD = cue(p, 'dolar'), tF = cue(p, 'faiz'), tM = cue(p, 'manşet'), tBir = cue(p, 'birleştir');
  A(PS[p], W / 2, 150, () => tx('ÖNCE 3 PARÇAYI BİRLEŞTİR', 0, 0, 56, { w: 900, ls: 2 }), { m: 'down' });
  const join = eio(P(tM - 0.3, 0.7));
  const pcs = [[tO, 'ONS', 'ne yapıyor?', C.gold], [tD, 'DOLAR / TL', 'ne yapıyor?', C.blue], [tF, 'FAİZ BEKLENTİSİ', 'hangi yönde?', C.teal]];
  pcs.forEach(([tt, a, b, col], i) => {
    const gap = lerp(460, 380, join);
    A(tt - 0.2, W / 2 + (i - 1) * gap, 500 - 30 * join, () => {
      const w = 380, h = 280;
      g.save();
      g.beginPath(); g.roundRect(-w / 2, -h / 2, w, h, 20);
      g.fillStyle = 'rgba(20,32,64,0.96)'; g.fill(); g.lineWidth = 5; g.strokeStyle = col; g.shadowColor = col; g.shadowBlur = 25 * join; g.stroke();
      g.shadowBlur = 0;
      if (i < 2) { g.beginPath(); g.arc(w / 2, 0, 34, -Math.PI / 2, Math.PI / 2); g.fillStyle = col; g.fill(); }
      if (i > 0) { g.beginPath(); g.arc(-w / 2, 0, 34, -Math.PI / 2, Math.PI / 2); g.fillStyle = '#0b1431'; g.fill(); g.strokeStyle = col; g.stroke(); }
      g.restore();
      tx(a, 0, -30, a.length > 10 ? 36 : 56, { w: 900, c: col, max: 290 });
      tx(b, 0, 40, 32, { w: 700, c: C.mute });
    }, { m: 'up' });
  });
  A(tM - 0.1, W / 2, 830, () => {
    card(980, 140, { fill: '#F4F6FB' });
    tx('MANŞET', -380, 0, 30, { w: 900, c: C.red, ls: 3 });
    tx('ANCAK ŞİMDİ ANLAM KAZANIR', 90, 0, 42, { w: 900, c: C.ink });
  }, { m: 'up' });
};

// 23 — Kapanış
S[23] = (p) => {
  const t0 = PS[p], tD = cue(p, 'değişen'), tS = cue(p, 'sen'), tO = cue(p, 'onsu'), tGr = cue(p, 'gramı'), tY = cue(p, 'yorumlara'), tA = cue(p, 'abone');
  const out = tS - 0.2;
  A(t0 - 0.2, W / 2, 400, () => {
    g.save(); g.translate(0, Math.sin(T * 2) * 8); goldBar(420, { glow: 30 }); g.restore();
  }, { out });
  A(t0 + 0.3, W / 2, 180, () => tx('ALTIN AYNI ALTIN', 0, 0, 80, { w: 900, c: C.gold, glow: 25 }), { out, m: 'down' });
  const tags = [['FİYAT', -560, 380], ['FAİZ', 560, 330], ['KUR', -520, 580], ['SEÇENEKLER', 540, 590]];
  tags.forEach(([s, dx, y], i) => {
    A(tD + i * 0.3, W / 2 + dx, y, () => {
      g.save(); g.rotate(Math.sin(T * 2 + i) * 0.08); chip(s + '  ⇅', 34, { bg: i % 2 ? C.blue : C.gold, c: i % 2 ? '#fff' : C.ink }); g.restore();
    }, { out });
  });
  A(tD, W / 2, 780, () => tx('Değişen: ona biçilen fiyat ve paranın diğer seçenekleri', 0, 0, 36, { w: 700, c: C.mute }), { out, sfx: false });
  // anket
  A(tS - 0.1, W / 2, 220, () => tx('SEN HANGİSİNİ TAKİP EDİYORSUN?', 0, 0, 56, { w: 900 }), { m: 'down' });
  A(tO - 0.1, W / 2 - 280, 450, () => {
    const hl = 1 + 0.05 * Math.sin(T * 8) * P(tO, 0.3) * (T < tGr ? 1 : 0);
    g.save(); g.scale(hl, hl); card(440, 200, { fill: 'rgba(77,163,255,0.2)', stroke: C.blue, lw: 5 }); tx('ONS', 0, 0, 90, { w: 900, c: C.blue }); g.restore();
  });
  A(tO + 0.25, W / 2, 450, () => tx('mı', 0, 0, 44, { w: 800, c: C.mute }), { sfx: false });
  A(tGr - 0.1, W / 2 + 280, 450, () => {
    const hl = 1 + 0.05 * Math.sin(T * 8) * P(tGr, 0.3);
    g.save(); g.scale(hl, hl); card(440, 200, { fill: 'rgba(255,200,61,0.2)', stroke: C.gold, lw: 5 }); tx('GRAM', 0, 0, 90, { w: 900, c: C.gold }); g.restore();
  });
  A(tY - 0.1, W / 2 - 330, 720, () => {
    g.save(); rr(-230, -60, 460, 120, 30); g.fillStyle = C.white; g.fill();
    g.beginPath(); g.moveTo(-150, 55); g.lineTo(-180, 100); g.lineTo(-110, 55); g.fill(); g.restore();
    tx('💬 YORUMLARA YAZ', 0, 0, 36, { w: 900, c: C.ink });
  }, { m: 'up' });
  A(tA - 0.6, W / 2 + 320, 720, () => {
    const clicked = T > tA + 0.3;
    const pr = clicked ? 0.94 + 0.06 * eo(P(tA + 0.3, 0.25)) : 1;
    g.save(); g.scale(pr, pr);
    rr(-240, -60, 480, 120, 20); g.fillStyle = clicked ? '#3a4566' : '#FF1E2D'; g.shadowColor = clicked ? 'transparent' : '#FF1E2D'; g.shadowBlur = 40; g.fill();
    g.restore();
    tx(clicked ? 'ABONE OLUNDU ✓' : 'ABONE OL', 0, 2, 44, { w: 900, c: '#fff' });
    tx('TIKLA BAKALIM', 0, 100, 30, { w: 900, c: C.gold, ls: 4 });
    // imleç
    const mv = eio(P(tA - 0.4, 0.6));
    g.save(); g.translate(lerp(260, 60, mv), lerp(160, 20, mv));
    const sc = T > tA + 0.3 && T < tA + 0.5 ? 0.85 : 1; g.scale(sc, sc);
    g.beginPath(); g.moveTo(0, 0); g.lineTo(0, 56); g.lineTo(14, 44); g.lineTo(26, 68); g.lineTo(36, 63); g.lineTo(24, 40); g.lineTo(42, 40); g.closePath();
    g.fillStyle = '#fff'; g.fill(); g.lineWidth = 3; g.strokeStyle = C.ink; g.stroke(); g.restore();
  }, { m: 'up' });
};

// ---------------------------------------------------------------- altyazı
const LINES = [];
(() => {
  let cur = [];
  const flush = () => { if (cur.length) { LINES.push(cur); cur = []; } };
  for (const w of WORDS) {
    if (cur.length && w.p !== cur[0].p) flush();
    cur.push(w);
    const len = cur.map(x => x.w).join(' ').length;
    const end = /[.?!;:]$/.test(w.w), comma = /,$/.test(w.w);
    if (len >= 40 || (end && len >= 10) || (comma && len >= 24)) flush();
  }
  flush();
})();
function subtitles() {
  let li = -1;
  for (let i = 0; i < LINES.length; i++) if (T >= LINES[i][0].s - 0.08) li = i;
  if (li < 0) return;
  const L = LINES[li];
  const size = 40; font(size, 800);
  const sp = g.measureText(' ').width;
  const ws = L.map(w => g.measureText(w.w).width);
  const total = ws.reduce((a, b) => a + b, 0) + sp * (L.length - 1);
  const y = 1010, padX = 30, padY = 16;
  const fade = li === 0 ? 1 : clamp((T - (L[0].s - 0.08)) / 0.1);
  g.save(); g.globalAlpha = fade;
  rr(W / 2 - total / 2 - padX, y - size / 2 - padY, total + padX * 2, size + padY * 2, 18);
  g.fillStyle = 'rgba(4,8,20,0.78)'; g.fill();
  let x = W / 2 - total / 2;
  L.forEach((w, i) => {
    const active = T >= w.s - 0.03 && (i === L.length - 1 ? T < w.e + 0.4 : T < L[i + 1].s - 0.03);
    const done = T >= w.s;
    g.textAlign = 'left'; g.textBaseline = 'middle';
    g.fillStyle = active ? C.gold : done ? C.white : 'rgba(244,246,251,0.45)';
    if (active) { g.shadowColor = 'rgba(255,200,61,0.6)'; g.shadowBlur = 16; } else g.shadowBlur = 0;
    font(size, 800); g.fillText(w.w, x, y + 1);
    x += ws[i] + sp;
  });
  g.restore();
}

// ---------------------------------------------------------------- HUD + geçiş
function hud(k) {
  if (k > 0 || T > cue(0, 'düşüyor') + 2) {
    g.save(); g.translate(1760, 60);
    g.globalAlpha = 0.9;
    const tag = TAGS[k];
    if (tag) { const w = tw(tag, 22, 900) + 36; g.translate(-w / 2 + 110, 0); rr(-w / 2, -22, w, 44, 22); g.fillStyle = 'rgba(255,200,61,0.14)'; g.fill(); g.lineWidth = 2; g.strokeStyle = 'rgba(255,200,61,0.6)'; g.stroke(); tx(tag, 0, 1, 22, { w: 900, c: C.gold, ls: 2 }); }
    g.restore();
  }
  // ilerleme çubuğu
  g.save(); g.fillStyle = 'rgba(255,255,255,0.08)'; g.fillRect(0, H - 6, W, 6);
  g.fillStyle = C.gold; g.shadowColor = C.gold; g.shadowBlur = 10; g.fillRect(0, H - 6, W * clamp(T / DUR), 6); g.restore();
}
function wipe(k) {
  // her sahne değişiminde çapraz altın silme
  for (let j = 1; j < NP; j++) {
    const u = (T - (SW[j] - 0.2)) / 0.4;
    if (u < 0 || u > 1) continue;
    const lead = lerp(-500, W + 500, eio(clamp(u * 2)));
    const trail = lerp(-500, W + 500, eio(clamp(u * 2 - 1)));
    const sk = 260;
    g.save();
    g.beginPath(); g.moveTo(trail, 0); g.lineTo(lead + sk, 0); g.lineTo(lead - sk, H); g.lineTo(trail - 2 * sk, H); g.closePath();
    g.fillStyle = '#0a1330'; g.fill();
    for (const [x0, col] of [[lead, C.gold], [trail, C.gold]]) {
      g.beginPath(); g.moveTo(x0 + sk - 40, 0); g.lineTo(x0 + sk, 0); g.lineTo(x0 - sk, H); g.lineTo(x0 - sk - 40, H); g.closePath();
      g.fillStyle = col; g.shadowColor = col; g.shadowBlur = 30; g.fill();
    }
    g.restore();
  }
}

// ---------------------------------------------------------------- ana çizim
function sceneAt(t) { let k = 0; for (let j = 0; j < NP; j++) if (t >= SW[j]) k = j; return k; }
function render(t) {
  T = t;
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.filter = 'none';
  background();
  const k = sceneAt(t);
  const end = k + 1 < NP ? SW[k + 1] : DUR;
  const z = 1 + 0.03 * eio(clamp((t - SW[k]) / Math.max(1, end - SW[k])));
  g.save();
  g.translate(W / 2, H / 2); g.scale(z, z); g.translate(-W / 2, -H / 2);
  S[k](k);
  g.restore();
  vignette();
  hud(k);
  subtitles();
  wipe(k);
}

window.render = render;
window.DUR = DUR;
window.collect = function () {
  // pop() çağrıldığı anda kaydolur (öğe henüz görünmese bile); iç içe öğeler için
  // her sahneyi birkaç noktada çizmek yeter. Her çizimden sonra tuval boşaltılır.
  COLLECT = true; EV.length = 0; EVSEEN.clear();
  for (let k = 0; k < NP; k++) {
    const e = k + 1 < NP ? SW[k + 1] - 0.01 : DUR;
    for (let i = 1; i <= 8; i++) { render(lerp(SW[k], e, i / 8)); g.getImageData(0, 0, 1, 1); }
  }
  COLLECT = false;
  return { pops: EV.slice().sort((a, b) => a - b), switches: SW.slice(1), missing: [...MISSING], dur: DUR };
};
window.READY = (async () => {
  const faces = ['500', '700', '800', '900'].map(w => document.fonts.load(`${w} 40px Montserrat`, 'ĞÜŞİÖÇğüşıöç₺%'));
  faces.push(document.fonts.load('700 40px "JetBrains Mono"', '0,96'));
  await Promise.all(faces); await document.fonts.ready;
  render(0); return true;
})();

// ---------------------------------------------------------------- YouTube kapağı (1920x1080 -> 1280x720)
window.thumb = function () {
  T = 1.3;
  g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1;
  background();
  // kırmızı düşüş grafiği arka planda
  const pts = seq(40, (u, i) => clamp(0.85 - u * 0.75 + noise(i, 4) * 0.12 + (u < 0.3 ? 0.05 : 0), 0.05, 0.95));
  g.save(); g.globalAlpha = 0.9; lineChart(60, 180, 1800, 760, pts, 1, { c: C.red, w: 14, fc: 'rgba(255,77,94,', dot: false }); g.restore();
  vignette();
  g.save(); g.translate(1380, 600); g.rotate(0.16); goldBar(720, { glow: 60, shine: 0.45 }); g.restore();
  g.save(); g.translate(1720, 470); barrow(330, 1, C.red, 60); g.restore();
  tx('ALTIN', 90, 330, 250, { a: 'left', w: 900, c: C.white, stroke: 16, sc: 'rgba(0,0,0,0.7)' });
  tx('NEDEN', 90, 560, 200, { a: 'left', w: 900, c: C.white, stroke: 14, sc: 'rgba(0,0,0,0.7)' });
  tx('DÜŞÜYOR?', 90, 790, 230, { a: 'left', w: 900, c: C.gold, stroke: 16, sc: 'rgba(0,0,0,0.75)', glow: 40 });
  g.save(); g.translate(330, 975); chip('ONS ≠ GRAM', 56, { bg: C.red, c: '#fff', glow: 30 }); g.restore();
};
