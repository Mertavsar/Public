// Kâğıt kesme (papercut) modu — bolum.json "stil": "kesme". Sahneler tip "kesme", p.set = aşağıdaki SETLER'den biri.
// Her şey makasla kesilmiş kâğıt: titrek kesik kenar, kalınlık gölgesi, iç kontur, kâğıt lifi dokusu.
// Karakterler saniyede 12 adımda oynar (stop-motion), kamera/ışık 30 kare akar.
// Sahne geçişi: yırtık kâğıt sayfası sağdan gelir (beyaz lifli yırtık kenar + gölge).
// Teknik dil Lemo-Opuscar "Red Paper-cut" stil notlarından uyarlandı (MIT); kod ve tasarım bize ait.
// Deterministik: her şey t'den hesaplanır.
(function () {
const PAL = {
  gece: "#10142c", gece1: "#181e45", gece2: "#232a5e", gece3: "#2f3878", gece4: "#3d4791",
  kum: "#e8cd97", kum1: "#d6ad6c", kum2: "#bf8f4d", kum3: "#a3743a",
  krem: "#f4ecdb", krem1: "#e5d8bc", kir: "#e3141b", kir1: "#b40f16", kir2: "#7c0a10", kir3: "#4d070b",
  tur: "#f2871f", tur1: "#c9640e", sari: "#ffd25a", isik: "#ffe9a8",
  siyah: "#16161c", gri: "#8d93a6", yesil: "#4f9a3a", yesil1: "#2f6b26", mor: "#5c3596", mor1: "#3e2170",
  ten: "#f0c9a2", ten1: "#e9bd92", zombi: "#9fbf86", polM: "#2f6bff",
};
let W_ = 1080, H_ = 1920;
const GY = 1490;                          // zemin çizgisi: altı altyazı bandı
const q = t => Math.floor(t * 12) / 12;   // 12 fps adım
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const nz = (x, sd) => { const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f); return hash(i + sd * 57.3) * (1 - u) + hash(i + 1 + sd * 57.3) * u; };
const C = (a, b, x) => Math.max(a, Math.min(b, x));
const pr = (t, a, d) => C(0, 1, (t - a) / d);
const eo = x => 1 - Math.pow(1 - x, 3);
const eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
// pop: 12 fps adımda belirir; ilk adımda 1.15 taşma
const pop = (lt, a) => { const k = Math.floor((lt - a) * 12); return k < 0 ? 0 : k === 0 ? .55 : k === 1 ? 1.15 : 1; };

// ---- kesik kenar ------------------------------------------------------------
const MEMO = new Map();
const memo = (k, f) => { if (!MEMO.has(k)) MEMO.set(k, f()); return MEMO.get(k); };
function ring(pts, sd = 1, amp = 2, seg = 18) {   // kapalı çokgeni böl, kenara düşük frekanslı titreşim ver
  const out = [];
  let acc = 0;
  for (let i = 0; i < pts.length; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length];
    const L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(1, Math.ceil(L / seg));
    const nx = -(y1 - y0) / (L || 1), ny = (x1 - x0) / (L || 1);
    for (let k = 0; k < n; k++) {
      const u = k / n, d = (nz((acc + u * L) / 40, sd) - .5) * 2 * amp;
      out.push([x0 + (x1 - x0) * u + nx * d, y0 + (y1 - y0) * u + ny * d]);
    }
    acc += L;
  }
  return out;
}
function path(rings, sd = 1, amp = 2) {      // rings: [dış, delik, delik…]  (evenodd)
  const p = new Path2D();
  rings.forEach((r, j) => { const R = amp ? ring(r, sd + j * 7, amp) : r; R.forEach(([x, y], i) => i ? p.lineTo(x, y) : p.moveTo(x, y)); p.closePath(); });
  return p;
}
const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
const ell = (cx, cy, rx, ry, n = 36, a0 = 0) => Array.from({ length: n }, (_, i) => { const a = a0 + i / n * Math.PI * 2; return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; });
const tri = (x, y, w, h) => [[x - w / 2, y + h / 2], [x, y - h / 2], [x + w / 2, y + h / 2]];
const star = (cx, cy, R, r, n, a0 = -Math.PI / 2) => Array.from({ length: n * 2 }, (_, i) => { const a = a0 + i * Math.PI / n, rr = i % 2 ? r : R; return [cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]; });
const rrect = (x, y, w, h, r) => { const o = []; const c = [[x + w - r, y + r, -Math.PI / 2], [x + w - r, y + h - r, 0], [x + r, y + h - r, Math.PI / 2], [x + r, y + r, Math.PI]];
  c.forEach(([cx, cy, a]) => { for (let k = 0; k <= 6; k++) { const b = a + k / 6 * Math.PI / 2; o.push([cx + Math.cos(b) * r, cy + Math.sin(b) * r]); } }); return o; };

// ---- kâğıt parça ------------------------------------------------------------
// d: kalınlık (gölge boyu), ic: iç kontur (yin çizgisi) mesafesi
function P(ctx, p, col, o = {}) {
  const d = o.d ?? 1;
  ctx.save();
  if (d > 0) { ctx.shadowColor = `rgba(0,0,0,${o.sa ?? .45})`; ctx.shadowBlur = 6 + 7 * d; ctx.shadowOffsetX = 1.5 * d; ctx.shadowOffsetY = 4 * d; }
  ctx.fillStyle = col; ctx.fill(p, "evenodd");
  ctx.restore();
  if (o.duz) return;
  ctx.save(); ctx.clip(p, "evenodd");
  ctx.lineWidth = 6; ctx.strokeStyle = "rgba(0,0,0,.16)"; ctx.stroke(p);
  ctx.translate(1.6, 1.6); ctx.lineWidth = 2.4; ctx.strokeStyle = "rgba(255,255,255,.2)"; ctx.stroke(p);
  ctx.restore();
  if (o.ic) {   // makasla açılmış ince iç yarık: kenara paralel koyu çizgi
    ctx.save(); ctx.clip(p, "evenodd");
    ctx.lineWidth = o.ic * 2 + 3.2; ctx.strokeStyle = "rgba(0,0,0,.42)"; ctx.stroke(p);
    ctx.lineWidth = o.ic * 2; ctx.strokeStyle = col; ctx.stroke(p);
    ctx.restore();
  }
}
const PP = (ctx, key, mk, col, o) => P(ctx, memo(key, mk), col, o);

// ---- kâğıt lifi dokusu (bir kez üretilir) -----------------------------------
let GRAIN = null;
function grain() {
  const c = document.createElement("canvas"); c.width = 540; c.height = 960;
  const g = c.getContext("2d");
  g.fillStyle = "#808080"; g.fillRect(0, 0, 540, 960);
  const id = g.getImageData(0, 0, 540, 960), D = id.data;
  for (let i = 0; i < D.length; i += 4) { const v = 128 + (hash(i * .37) - .5) * 34; D[i] = D[i + 1] = D[i + 2] = v; }
  g.putImageData(id, 0, 0);
  for (let i = 0; i < 1400; i++) {          // lifler
    const x = hash(i * 3.1) * 540, y = hash(i * 7.7) * 960, a = hash(i * 1.9) * Math.PI, l = 6 + hash(i * 5.3) * 22;
    g.strokeStyle = hash(i * 2.2) > .5 ? "rgba(255,255,255,.25)" : "rgba(0,0,0,.2)"; g.lineWidth = .8;
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * l * .5 + 3, y + Math.sin(a) * l * .5, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
  return c;
}

// ---- yazı: kâğıt şerit, kırlangıç kuyruklu bayrak, mühür ---------------------
const font = (s, w = 900) => `${w} ${s}px M, sans-serif`;
function serit(ctx, txt, x, y, s, u, o = {}) {   // u: pop ölçeği (0 = yok)
  if (!u) return;
  ctx.save(); ctx.font = font(s, o.w || 900);
  const tw = ctx.measureText(txt).width, pw = tw + s * 1.1, ph = s * 1.45;
  ctx.translate(x, y); ctx.rotate((o.rot || 0) * Math.PI / 180); ctx.scale(u, u);
  const bg = o.bg || PAL.krem, ink = o.ink || PAL.siyah;
  let shape;
  if (o.bayrak) { const t = ph * .45; shape = [[-pw / 2 - t, -ph / 2], [pw / 2 + t, -ph / 2], [pw / 2, 0], [pw / 2 + t, ph / 2], [-pw / 2 - t, ph / 2], [-pw / 2, 0]]; }
  else shape = rect(-pw / 2, -ph / 2, pw, ph);
  P(ctx, memo("s" + txt + s + !!o.bayrak, () => path([shape], txt.length + s, 2.2)), bg, { d: 1.4, ic: o.bayrak ? 7 : 0 });
  ctx.fillStyle = ink; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(txt, 0, s * .06);
  ctx.restore();
}
function harfler(ctx, txt, x, y, s, lt, a, o = {}) {   // kesik harfler tek tek, 12 fps adımla düşer
  ctx.save(); ctx.font = font(s); ctx.textBaseline = "middle";
  const ws = [...txt].map(c => ctx.measureText(c).width), tw = ws.reduce((m, v) => m + v, 0) + (txt.length - 1) * (o.ara ?? 2);
  let cx = x - tw / 2;
  [...txt].forEach((c, i) => {
    const u = pop(lt, a + i * (o.hiz ?? .05));
    if (u && c !== " ") {
      ctx.save(); ctx.translate(cx + ws[i] / 2, y); ctx.rotate((hash(i + s) - .5) * .09); ctx.scale(u, u);
      ctx.shadowColor = "rgba(0,0,0,.55)"; ctx.shadowBlur = 12; ctx.shadowOffsetX = 2; ctx.shadowOffsetY = 6;
      ctx.fillStyle = o.renk || PAL.krem; ctx.textAlign = "center"; ctx.fillText(c, 0, 0);
      ctx.shadowColor = "transparent"; ctx.lineWidth = Math.max(1.5, s * .025); ctx.strokeStyle = "rgba(0,0,0,.25)"; ctx.strokeText(c, 0, 0);
      ctx.restore();
    }
    cx += ws[i] + (o.ara ?? 2);
  });
  ctx.restore();
}
function muhur(ctx, txt, x, y, s, lt, a, rot = -8) {   // kırmızı mühür: büyükten çarpar
  const k = Math.floor((lt - a) * 12);
  if (k < 0) return;
  const sc = k === 0 ? 1.9 : k === 1 ? 1.25 : k === 2 ? .96 : 1;
  ctx.save(); ctx.font = font(s);
  const tw = ctx.measureText(txt).width, pw = tw + s * .9, ph = s * 1.5;
  ctx.translate(x, y); ctx.rotate(rot * Math.PI / 180); ctx.scale(sc, sc);
  ctx.globalAlpha = k === 0 ? .6 : .93;
  ctx.strokeStyle = PAL.kir; ctx.lineWidth = s * .12;
  ctx.strokeRect(-pw / 2, -ph / 2, pw, ph);
  ctx.lineWidth = s * .04; ctx.strokeRect(-pw / 2 + s * .17, -ph / 2 + s * .17, pw - s * .34, ph - s * .34);
  ctx.fillStyle = PAL.kir; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(txt, 0, s * .05);
  // mürekkep boşlukları
  ctx.globalCompositeOperation = "destination-out";
  for (let i = 0; i < 40; i++) { ctx.beginPath(); ctx.arc((hash(i * 9 + s) - .5) * pw, (hash(i * 4 + s) - .5) * ph, 1 + hash(i) * 4, 0, 7); ctx.fill(); }
  ctx.restore();
}
const sars = (lt, a, g = 14) => { const k = Math.floor((lt - a) * 30); return k >= 0 && k < 8 ? [(hash(k * 3.3) - .5) * g * (1 - k / 8), (hash(k * 7.1) - .5) * g * (1 - k / 8)] : [0, 0]; };

// ---- ortak dekor ------------------------------------------------------------
function gok(ctx, col = PAL.gece, lt = 0) {
  ctx.fillStyle = col; ctx.fillRect(0, 0, W_, H_);
  for (let i = 0; i < 46; i++) {      // yıldızlar: delik delinmiş kâğıt, adımla kırpışır
    const x = hash(i * 11.3) * W_, y = hash(i * 5.9) * 1000, r = 2 + hash(i * 2.7) * 3.5;
    const on = hash(i + Math.floor(lt * 4)) > .12;
    ctx.fillStyle = on ? "rgba(255,240,200,.95)" : "rgba(255,240,200,.35)";
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill();
  }
}
function hilal(ctx, x, y, r) {
  PP(ctx, "hilal" + r, () => { const p = new Path2D(); const A = ring(ell(0, 0, r, r, 40), 3, 1.5), B = ring(ell(r * .42, -r * .18, r * .86, r * .86, 40), 4, 1.5);
    A.forEach(([a, b], i) => i ? p.lineTo(a, b) : p.moveTo(a, b)); p.closePath(); B.forEach(([a, b], i) => i ? p.lineTo(a, b) : p.moveTo(a, b)); p.closePath(); return p; }, PAL.krem, { d: 1 });
  void x; void y;
}
// Riyad silueti: Kingdom Centre (tepede ters kemer deliği), Faisaliah (küre), bloklar (pencere delikleri ışık)
function silueti(ctx, ox, yb, col, isik, sd = 1, olc = 1) {
  ctx.save(); ctx.translate(ox, yb); ctx.scale(olc, olc);
  const kule = memo("kule" + sd, () => {
    const out = [[-62, 0], [-62, -560], [-40, -720], [-18, -800], [18, -800], [40, -720], [62, -560], [62, 0]];
    const hole = []; for (let k = 0; k <= 14; k++) { const a = Math.PI + k / 14 * Math.PI; hole.push([Math.cos(a) * 34, -720 + Math.sin(a) * -60 + 60]); }
    hole.push([30, -770]); hole.push([-30, -770]);
    return path([out, hole.reverse()], sd, 1.6);
  });
  const blok = [];
  const bl = [[-470, 300, 90], [-370, 420, 110], [-250, 360, 90], [140, 330, 100], [250, 460, 120], [380, 380, 90], [480, 300, 110], [-560, 240, 100]];
  // ışıklı pencereler: önce sıcak ışık katmanı, sonra delikli bina
  ctx.fillStyle = isik; bl.forEach(([x, h, w]) => ctx.fillRect(x + 8, -h + 10, w - 16, h - 20));
  bl.forEach(([x, h, w], j) => {
    PP(ctx, `blok${sd}_${j}`, () => { const holes = [];
      for (let r = 0; r < Math.floor(h / 46) - 1; r++) for (let c = 0; c < Math.floor(w / 30); c++) if (hash(j * 31 + r * 7 + c) > .45) holes.push(rect(x + 10 + c * 28, -h + 22 + r * 46, 13, 20).reverse());
      return path([rect(x, -h, w, h), ...holes], sd + j, 1.4); }, col, { d: .8 });
  });
  P(ctx, kule, col, { d: 1 });
  // Faisaliah: piramit + küre
  PP(ctx, "fais" + sd, () => path([[[-330 + 600, 0], [-250 + 600, -520], [-170 + 600, 0]]], sd + 3, 1.4), col, { d: 1 });
  PP(ctx, "faisk" + sd, () => path([ell(350, -430, 26, 26, 24)], sd + 4, 1), isik, { d: .5 });
  void blok;
  ctx.restore();
}
function kumtepe(ctx, y, col, sd, amp = 40, d = 1) {
  PP(ctx, `tepe${y}${col}${sd}`, () => { const pts = [[-40, H_ + 40]]; for (let x = -40; x <= W_ + 40; x += 30) pts.push([x, y - amp * (nz(x / 260, sd) - .2) - amp * .4 * Math.sin(x / 170 + sd)]); pts.push([W_ + 40, H_ + 40]); return path([pts], sd, 1.2); }, col, { d });
}
function zemin(ctx, col = PAL.gece1, sd = 2) {   // altyazı bandı: düz kâğıt, testere dişli üst kenar
  PP(ctx, "zemin" + col + sd, () => { const pts = [[-20, H_ + 20], [-20, GY]]; for (let x = -20; x <= W_ + 20; x += 24) pts.push([x, GY + ((x / 24) % 2 ? -9 : 7)]); pts.push([W_ + 20, H_ + 20]); return path([pts], sd, 1.2); }, col, { d: 1.6, ic: 10 });
}
function hurma(ctx, x, y, s, lt, sd) {   // hurma ağacı: kesik yapraklar, rüzgârda adımla sallanır
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  PP(ctx, "govde" + sd, () => path([[[-12, 0], [12, 0], [6, -300], [-6, -300]]], sd, 1.2), PAL.kum3, { d: 1 });
  const sw = Math.sin(q(lt) * 2 + sd) * .05;
  for (let i = 0; i < 7; i++) {
    ctx.save(); ctx.translate(0, -300); ctx.rotate(-Math.PI / 2 + (i - 3) * .48 + sw);
    PP(ctx, "yap" + (i % 3), () => { const pts = [[0, -10]]; for (let k = 1; k <= 8; k++) pts.push([k * 22, -12 + k * 2 + (k % 2 ? -10 : 0)]); pts.push([190, 6]); for (let k = 8; k >= 1; k--) pts.push([k * 22, 10 + k + (k % 2 ? 9 : 0)]); return path([pts], i + 9, 1); }, i % 2 ? PAL.yesil : PAL.yesil1, { d: .8 });
    ctx.restore();
  }
  ctx.restore();
}
function yarasa(ctx, x, y, s, lt, sd) {
  const up = Math.floor(lt * 8 + sd) % 2;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  PP(ctx, "bat" + up, () => { const w = up ? -38 : 22;
    return path([[[0, -12], [10, -4], [34, w * .4 - 10], [60, w], [52, 8], [40, 2], [30, 12], [14, 6], [0, 18], [-14, 6], [-30, 12], [-40, 2], [-52, 8], [-60, w], [-34, w * .4 - 10], [-10, -4]]], 5, 1); }, PAL.siyah, { d: .8 });
  ctx.restore();
}
function cicekdizi(ctx, x0, x1, y, sag, lt, n = 14) {   // ampul zinciri: ip + adımla yanıp sönen kâğıt ampuller
  ctx.save(); ctx.strokeStyle = "rgba(20,20,30,.85)"; ctx.lineWidth = 3;
  ctx.beginPath(); for (let i = 0; i <= 30; i++) { const u = i / 30, x = x0 + (x1 - x0) * u, yy = y + Math.sin(u * Math.PI) * sag; i ? ctx.lineTo(x, yy) : ctx.moveTo(x, yy); } ctx.stroke();
  const cols = [PAL.tur, PAL.sari, PAL.kir, PAL.krem, PAL.mor];
  for (let i = 1; i < n; i++) {
    const u = i / n, x = x0 + (x1 - x0) * u, yy = y + Math.sin(u * Math.PI) * sag + 16;
    const on = (i + Math.floor(lt * 4)) % 3 !== 0;
    if (on) { const g = ctx.createRadialGradient(x, yy, 2, x, yy, 46); g.addColorStop(0, "rgba(255,220,140,.55)"); g.addColorStop(1, "rgba(255,220,140,0)");
      ctx.save(); ctx.globalCompositeOperation = "lighter"; ctx.fillStyle = g; ctx.fillRect(x - 46, yy - 46, 92, 92); ctx.restore(); }
    ctx.save(); ctx.translate(x, yy);
    PP(ctx, "amp", () => path([ell(0, 0, 13, 17, 16)], 2, .8), on ? cols[i % 5] : "#555a6e", { d: .6, duz: true });
    ctx.restore();
  }
  ctx.restore();
}
function isikhavuzu(ctx, x, y, r, col, a = 1) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, col.replace("A", a)); g.addColorStop(1, col.replace("A", 0));
  ctx.save(); ctx.globalCompositeOperation = "lighter"; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
}

// ---- kostümlü karakterler (perçinli eklem, 12 fps) --------------------------
// ayak tabanı (x, y), ölçek s. kind: kabak | cadi | hayalet | vampir | zombi | insan
function karakter(ctx, kind, x, y, s, lt, o = {}) {
  const tq = q(lt + (o.ofs || 0));
  const ph = tq * (o.hiz || 8);
  const yur = o.yuru ? Math.sin(ph) : 0, dans = o.dans ? Math.sin(ph * .9) : 0;
  const zom = kind === "zombi";
  ctx.save();
  ctx.translate(x, y - Math.abs(yur) * 7 * s - Math.max(0, dans) * 14 * s);
  ctx.scale(s * (o.yon || 1), s);
  ctx.rotate(dans * .05 + (zom ? .06 : 0));
  if (kind === "hayalet") {   // çarşaf: dalgalı etek, göz delikleri
    const f = Math.sin(tq * 5) * 6;
    ctx.translate(0, -30 + f);
    P(ctx, memo("hay", () => { const out = []; for (let k = 0; k <= 20; k++) { const a = Math.PI + k / 20 * Math.PI; out.push([Math.cos(a) * 80, -230 + Math.sin(a) * 80]); }
      out.push([86, -60]); for (let k = 0; k <= 8; k++) out.push([86 - k * 21.5, k % 2 ? -10 : -40]); out.push([-86, -60]);
      return path([out, ell(-28, -250, 14, 20, 16).reverse(), ell(28, -250, 14, 20, 16).reverse(), ell(0, -195, 16, 22, 16).reverse()], 21, 1.6); }), PAL.krem, { d: 1.3, ic: 6 });
    ctx.restore(); return;
  }
  const T = {
    kabak: { gov: PAL.siyah, kol: PAL.siyah, bac: PAL.gece2, ayak: PAL.kir2 },
    cadi: { gov: PAL.mor, kol: PAL.mor, bac: PAL.siyah, ayak: PAL.siyah },
    vampir: { gov: PAL.krem, kol: PAL.siyah, bac: PAL.siyah, ayak: PAL.siyah },
    zombi: { gov: "#5f7896", kol: "#5f7896", bac: "#3d4a5c", ayak: PAL.siyah },
    insan: { gov: o.renk || PAL.kir, kol: o.renk || PAL.kir, bac: PAL.gece2, ayak: PAL.siyah },
  }[kind];
  const ten = zom ? PAL.zombi : kind === "vampir" ? "#efe6dc" : PAL.ten;
  // pelerin (arkada)
  if (kind === "vampir") PP(ctx, "pel", () => path([[[-50, -236], [50, -236], [96, -20], [60, -6], [0, -24], [-60, -6], [-96, -20]]], 31, 1.6), PAL.siyah, { d: 1.2, ic: 5 });
  // bacaklar
  const ab = zom ? Math.sin(ph * .6) * .22 : yur * .5 + dans * .3;
  [[-16, ab], [16, -ab]].forEach(([hx, a]) => {
    ctx.save(); ctx.translate(hx, -112); ctx.rotate(a);
    PP(ctx, "bac", () => path([rect(-13, 0, 26, 104)], 41, 1.2), T.bac, { d: .9 });
    PP(ctx, "ayk", () => path([rrect(-15, 96, 38, 18, 8)], 42, 1), T.ayak, { d: .6 });
    ctx.restore();
  });
  // gövde
  if (kind === "cadi") PP(ctx, "cadigov", () => { const pts = [[-34, -236], [34, -236], [76, -40]]; for (let k = 0; k <= 8; k++) pts.push([76 - k * 19, k % 2 ? -20 : -44]); pts.push([-76, -40]); return path([pts], 51, 1.6); }, T.gov, { d: 1.1, ic: 6 });
  else if (zom) PP(ctx, "zomgov", () => { const pts = [[-40, -236], [40, -236], [44, -104]]; for (let k = 0; k <= 8; k++) pts.push([44 - k * 11, k % 2 ? -92 : -112]); return path([pts], 52, 1.6); }, T.gov, { d: 1.1, ic: 5 });
  else PP(ctx, "gov" + kind, () => path([[[-46, -236], [46, -236], [36, -104], [-36, -104]]], 53, 1.6), T.gov, { d: 1.1, ic: 5 });
  if (kind === "vampir") { PP(ctx, "yaka", () => path([[[-50, -236], [-70, -300], [-26, -246]], [[50, -236], [70, -300], [26, -246]]], 54, 1.2), PAL.kir1, { d: .8 });
    PP(ctx, "papyon", () => path([[[-18, -232], [0, -224], [18, -232], [18, -214], [0, -222], [-18, -214]]], 55, .8), PAL.kir, { d: .5 }); }
  // kollar
  const ak = zom ? [-1.45 + Math.sin(ph) * .08, -1.35 - Math.sin(ph) * .08] : o.elkaldir ? [-2.6 + dans * .3, 2.6 - dans * .3] : [-yur * .55 + dans * .6, yur * .55 - dans * .6];
  [[-44, ak[0]], [44, ak[1]]].forEach(([sx, a], j) => {
    ctx.save(); ctx.translate(sx, -226); ctx.rotate(zom ? (j ? -a : a) * (j ? -1 : 1) : a);
    if (zom) ctx.rotate(0);
    PP(ctx, "kol" + kind, () => path([rect(-11, 0, 22, 96)], 61, 1.1), T.kol, { d: .8 });
    PP(ctx, "el" + (zom ? "z" : ""), () => path([ell(0, 104, 13, 13, 14)], 62, .8), ten, { d: .5 });
    ctx.restore();
  });
  // baş
  ctx.save(); ctx.translate(0, -278);
  if (kind === "kabak") {   // oyulmuş kabak: delikler içteki mum ışığını gösterir
    ctx.fillStyle = PAL.sari; ctx.beginPath(); ctx.ellipse(0, 0, 44, 36, 0, 0, 7); ctx.fill();
    P(ctx, memo("kab", () => { const m = [[-34, 14], [-22, 8], [-12, 18], [0, 8], [12, 18], [22, 8], [34, 14], [24, 30], [0, 26], [-24, 30]];
      return path([ell(0, 0, 58, 48, 40), tri(-22, -10, 26, 22).reverse(), tri(22, -10, 26, 22).reverse(), m.reverse()], 71, 1.8); }), PAL.tur, { d: 1.1, ic: 4 });
    ctx.strokeStyle = "rgba(0,0,0,.28)"; ctx.lineWidth = 3; [-30, 30].forEach(x => { ctx.beginPath(); ctx.ellipse(x * .55, 0, 16, 46, 0, -1.2, 1.2); ctx.stroke(); });
    PP(ctx, "sap", () => path([[[-6, -46], [8, -46], [14, -70], [2, -66]]], 72, .8), PAL.yesil1, { d: .5 });
  } else {
    if (kind === "cadi") PP(ctx, "csac", () => { const p = []; for (let k = 0; k <= 10; k++) p.push([-50 + k * 10, k % 2 ? 56 : 34]); p.push([50, -20]); p.push([-50, -20]); return path([p], 83, 1); }, PAL.tur1, { d: .6 });   // saç başın arkasında
    PP(ctx, "bas" + kind, () => path([ell(0, 0, 36, 40, 30)], 81, 1.2), ten, { d: 1 });
    // yüz: göz delikleri (koyu), ağız
    ctx.fillStyle = PAL.siyah; [-13, 13].forEach(ex => { ctx.beginPath(); ctx.ellipse(ex, -4, 5, zom ? 3 : 6, 0, 0, 7); ctx.fill(); });
    ctx.strokeStyle = PAL.siyah; ctx.lineWidth = 3.5; ctx.beginPath();
    if (zom) { ctx.moveTo(-12, 18); ctx.lineTo(-4, 14); ctx.lineTo(4, 19); ctx.lineTo(12, 15); } else ctx.arc(0, 10, 11, .3, Math.PI - .3);
    ctx.stroke();
    if (kind === "vampir") { PP(ctx, "vsac", () => path([[[-38, -6], [-36, -34], [-12, -46], [0, -24], [12, -46], [36, -34], [38, -6], [30, -24], [0, -40], [-30, -24]]], 82, 1), PAL.siyah, { d: .6 });
      ctx.fillStyle = "#fff"; [-6, 6].forEach(fx => { ctx.beginPath(); ctx.moveTo(fx - 3, 17); ctx.lineTo(fx, 26); ctx.lineTo(fx + 3, 17); ctx.fill(); }); }
    if (kind === "cadi") { PP(ctx, "sapka", () => path([[[-74, -26], [74, -26], [70, -14], [-70, -14]], [[-38, -26], [-6, -130], [30, -150], [14, -118], [38, -26]]], 84, 1.4), PAL.siyah, { d: 1, ic: 3 });
      PP(ctx, "bant", () => path([rect(-36, -44, 74, 14)], 85, .8), PAL.tur, { d: .3 }); }
    if (zom) { PP(ctx, "zsac", () => path([[[-34, -20], [-20, -42], [-6, -30], [6, -46], [20, -32], [34, -40], [34, -18]]], 86, 1), "#4a4232", { d: .6 }); }
    if (kind === "insan") PP(ctx, "isac" + (o.sac || 0), () => path([[[-38, -2], [-34, -36], [0, -48], [34, -36], [38, -2], [26, -26], [-26, -26]]], 87, 1), o.sacr || "#4a2e1c", { d: .6 });
  }
  ctx.restore();
  ctx.restore();
}
// kâğıt bebek (zincir için): elbiseli, kollar yana açık — katlanıp kesilmiş
const bebekP = memo("bebek", () => path([[[-8, -150], [-26, -140], [-30, -112], [-20, -96], [-34, -92], [-66, -92], [-66, -78], [-30, -76], [-50, 0], [-14, 0], [-10, -26], [10, -26], [14, 0], [50, 0], [30, -76], [66, -78], [66, -92], [34, -92], [20, -96], [30, -112], [26, -140], [8, -150]],
  ell(0, -50, 8, 8, 12).reverse()], 101, 1.3));

// ---- nesneler ---------------------------------------------------------------
function polisArabasi(ctx, x, y, s, lt) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  PP(ctx, "pgov", () => path([[[-230, -40], [-220, -100], [-120, -110], [-70, -170], [90, -170], [140, -110], [230, -96], [236, -40]], rrect(-56, -158, 70, 46, 6).reverse(), rrect(26, -158, 70, 46, 6).reverse()], 111, 1.6), PAL.krem, { d: 1.4, ic: 6 });
  PP(ctx, "pser", () => path([rect(-228, -84, 462, 22)], 112, 1.2), PAL.yesil1, { d: .4 });
  ctx.save(); ctx.font = font(26); ctx.fillStyle = PAL.krem; ctx.textAlign = "center"; ctx.fillText("POLİS", 0, -66); ctx.restore();
  // tepe lambası: kırmızı/mavi adımla yanar
  const k = Math.floor(lt * 6) % 2;
  PP(ctx, "lamba0", () => path([rrect(-40, -190, 40, 22, 6)], 113, .8), k ? PAL.kir : "#6b1a1f", { d: .5 });
  PP(ctx, "lamba1", () => path([rrect(0, -190, 40, 22, 6)], 114, .8), k ? "#1c2a66" : PAL.polM, { d: .5 });
  [-140, 150].forEach(wx => { ctx.save(); ctx.translate(wx, -30); ctx.rotate(-lt * 6);
    PP(ctx, "teker", () => path([ell(0, 0, 40, 40, 28), ell(0, 0, 16, 16, 16).reverse()], 115, 1.2), PAL.siyah, { d: 1 });
    ctx.restore(); });
  ctx.restore();
}
function takvimYaprak(ctx, yil, x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0); ctx.scale(s, s);
  PP(ctx, "ty", () => path([rect(-230, -170, 460, 340)], 121, 1.8), PAL.krem, { d: o.d ?? 1.4, ic: 0 });
  PP(ctx, "tyb", () => path([rect(-230, -170, 460, 70)], 122, 1.4), PAL.kir, { d: .3 });
  ctx.fillStyle = PAL.krem; [-120, 0, 120].forEach(hx => { ctx.beginPath(); ctx.arc(hx, -136, 10, 0, 7); ctx.fill(); });
  ctx.font = font(170); ctx.fillStyle = PAL.siyah; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(String(yil), 0, 40);
  ctx.restore();
}
function suudiHarita(ctx, x, y, s) {
  const L = [[34.95, 29.35], [36.4, 29.2], [37.6, 30.4], [37.0, 31.5], [39.0, 32.2], [40.4, 31.9], [42.0, 31.1], [44.7, 29.2], [46.5, 29.1], [47.5, 28.5], [48.4, 28.0], [49.5, 26.8], [50.1, 25.9], [50.8, 24.8], [51.6, 24.2], [52.6, 22.9], [55.2, 22.7], [55.6, 22.0], [55.0, 20.0], [52.0, 19.0], [49.1, 18.6], [46.5, 17.3], [44.0, 17.4], [43.3, 16.7], [42.8, 16.4], [42.3, 17.5], [41.2, 19.0], [40.0, 20.5], [39.1, 21.5], [38.5, 23.5], [37.5, 24.3], [36.5, 25.8], [35.5, 27.5], [34.6, 28.1]];
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  PP(ctx, "harita", () => path([L.map(([lo, la]) => [(lo - 45.3) * 38, -(la - 24.3) * 42])], 131, 2.2), PAL.kum1, { d: 1.6, ic: 8 });
  ctx.restore();
  return [x + (46.7 - 45.3) * 38 * s, y - (24.7 - 24.3) * 42 * s];   // Riyad
}
function pin(ctx, x, y, lt, a) {
  const k = Math.floor((lt - a) * 12); if (k < 0) return;
  const dy = k === 0 ? -120 : k === 1 ? -40 : k === 2 ? 6 : 0;
  ctx.save(); ctx.translate(x, y + dy);
  PP(ctx, "pin", () => path([[[0, 0], [-26, -44], [-30, -70], [-16, -92], [0, -98], [16, -92], [30, -70], [26, -44]], ell(0, -66, 11, 11, 14).reverse()], 141, 1), PAL.kir, { d: 1.2 });
  ctx.restore();
}
function balon(ctx, x, y, w, h, u, ters) {   // konuşma balonu
  if (!u) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(u, u);
  PP(ctx, `bal${w}${h}${ters ? 1 : 0}`, () => { const b = rrect(-w / 2, -h / 2, w, h, 22); const tx = ters ? 1 : -1;
    const i = b.findIndex(([px, py]) => py > h / 2 - 1 && px * tx > -w / 4); b.splice(Math.max(1, i), 0, [tx * w / 8, h / 2], [tx * w / 3.2, h / 2 + 46], [tx * w / 4.5, h / 2]); return path([b], w + h, 1.6); }, PAL.krem, { d: 1.2 });
  ctx.restore();
}
function sekizYildiz(ctx, x, y, R, rot, col, sd = 1) {   // sekiz köşeli yıldız (hatem) rozeti: iç içe katmanlar
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  PP(ctx, "8y" + R + sd, () => { const sq = a => [0, 1, 2, 3].map(i => [Math.cos(a + i * Math.PI / 2) * R, Math.sin(a + i * Math.PI / 2) * R]);
    const pts = []; for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 - Math.PI / 2, r = i % 2 ? R * .78 : R; pts.push([Math.cos(a) * r, Math.sin(a) * r]); }
    void sq; return path([pts, star(0, 0, R * .55, R * .42, 8).reverse(), ell(0, 0, R * .22, R * .22, 20)], sd + 150, 1.6); }, col, { d: 1.2, ic: 6 });
  ctx.restore();
}

// ---- setler -----------------------------------------------------------------
// her set: (ctx, lt = sahne içi zaman, D = sahne süresi, p = parametreler)
const SET = {};
// 1 · HOOK: üst yarı 2018 (parmaklık iner, GÖZALTI), alt yarı 2022 (aynı kabak dans eder, BEDAVA bilet)
SET.hook = (ctx, lt, D, p) => {
  const yari = 760, b2 = D * (p.ikinci ?? .48);
  // üst: koyu kırmızı gece
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W_, yari); ctx.clip();
  ctx.fillStyle = PAL.kir3; ctx.fillRect(0, 0, W_, yari);
  silueti(ctx, 540, yari - 20, PAL.kir2, "rgba(255,120,90,.35)", 3, .62);
  karakter(ctx, "kabak", 540, yari - 40, 1.25, lt, { dans: false });
  // parmaklıklar iner
  const k = Math.floor(lt * 12), dy = k < 1 ? -yari * .25 : k < 2 ? 12 : 0;   // ilk karede parmaklık zaten iniyor
  const [sx, sy] = sars(lt, .08, 18);
  ctx.translate(sx, dy + sy);
  for (let i = 0; i < 9; i++) PP(ctx, "bar" + i, () => path([rect(80 + i * 115, -10, 26, yari + 20)], 160 + i, 1.2), PAL.siyah, { d: 1.4 });
  PP(ctx, "barY", () => path([rect(60, 60, 960, 30), rect(60, yari - 120, 960, 30)], 170, 1.4), PAL.siyah, { d: 1.4 });
  ctx.restore();
  serit(ctx, "2018", 170, 110, 64, pop(lt, .05), { bg: PAL.krem, rot: -5 });
  muhur(ctx, "GÖZALTI", 760, 610, 74, lt, .3, -7);
  // alt: 2022 açılana kadar karanlık, bekleyen sahne (gri boşluk kalmasın)
  ctx.fillStyle = PAL.gece; ctx.fillRect(0, yari, W_, H_ - yari);
  harfler(ctx, "4 YIL SONRA…", 540, yari + 330, 76, lt, .35, { hiz: .03, renk: "rgba(244,236,219,.85)" });
  // alt: aydınlık kum / festival
  const ac = b2 - .2;
  if (lt > ac) {
    const u = eo(pr(lt, ac, .35));
    ctx.save(); ctx.beginPath(); ctx.rect(0, yari, W_, (GY - yari) * u + 60); ctx.clip();
    ctx.fillStyle = PAL.gece2; ctx.fillRect(0, yari, W_, H_);
    cicekdizi(ctx, -20, 1100, yari + 70, 70, lt, 16);
    kumtepe(ctx, GY - 70, PAL.kum1, 4, 30);
    karakter(ctx, "kabak", 470, GY - 40, 1.25, lt - ac, { dans: true, elkaldir: true });
    // bilet
    const bu = pop(lt, b2 + .35);
    if (bu) { ctx.save(); ctx.translate(800, yari + 380); ctx.rotate(.12); ctx.scale(bu, bu);
      PP(ctx, "hbilet", () => { const o = rect(-150, -80, 300, 160); return path([o, ...[0, 1, 2, 3, 4].map(i => ell(70, -60 + i * 30, 5, 5, 8).reverse())], 180, 1.6); }, PAL.kir, { d: 1.5, ic: 6 });
      ctx.font = font(30); ctx.fillStyle = PAL.krem; ctx.textAlign = "center"; ctx.fillText("GİRİŞ", -40, -26); ctx.font = font(46); ctx.fillText("BEDAVA", -36, 30);
      ctx.restore(); }
    serit(ctx, "2022", 170, yari + 120, 64, pop(lt, ac + .1), { bg: PAL.kir, ink: PAL.krem, rot: 4 });
    ctx.restore();
    // yırtık ayraç
    ctx.save(); ctx.strokeStyle = PAL.krem; ctx.lineWidth = 9; ctx.shadowColor = "rgba(0,0,0,.6)"; ctx.shadowBlur = 16; ctx.shadowOffsetY = 6;
    ctx.beginPath(); for (let x = -10; x <= W_ + 10; x += 18) ctx.lineTo(x, yari + (hash(x) - .5) * 14); ctx.stroke(); ctx.restore();
  }
  zemin(ctx, PAL.gece, 5);
};
// 2 · Başlık: Riyad gecesi, hilal, dev kabak tepeden yükselir, kesik harfler
SET.baslik = (ctx, lt, D, p) => {
  gok(ctx, PAL.gece, lt);
  ctx.save(); ctx.translate(860, 300); hilal(ctx, 0, 0, 70); ctx.restore();
  const px = -q(lt) * 10;
  ctx.save(); ctx.translate(px, 0); silueti(ctx, 560, 1180, PAL.gece2, "rgba(255,214,140,.85)", 1, .95); ctx.restore();
  kumtepe(ctx, 1210, PAL.gece3, 6, 40);
  // dev kabak yükselir
  const up = eo(pr(q(lt), .1, .7));
  ctx.save(); ctx.translate(540, 1500 - up * 280); ctx.scale(2.4, 2.4);
  isikhavuzu(ctx, 0, 0, 120, "rgba(255,190,80,A)", .6);
  ctx.translate(0, 278); karakter(ctx, "kabak", 0, 0, 1, lt, {}); ctx.restore();
  kumtepe(ctx, 1330, PAL.gece1, 8, 26);
  harfler(ctx, "SUUDİ ARABİSTAN'DA", 540, 520, 74, lt, .15, { hiz: .035 });
  serit(ctx, "CADILAR BAYRAMI", 540, 650, 84, pop(lt, .85), { bg: PAL.kir, ink: PAL.krem, bayrak: true, rot: -2 });
  for (let i = 0; i < 4; i++) yarasa(ctx, ((q(lt) * 160 + i * 300) % 1300) - 100, 820 + Math.sin(q(lt) * 3 + i) * 60 + i * 30, .9, lt, i);
  zemin(ctx, PAL.gece, 5);
};
// 3 · Takvim: yıl (sabit) veya ileri sarma (yapraklar kopar, uçar)
SET.takvim = (ctx, lt, D, p) => {
  ctx.fillStyle = p.zemin || PAL.gece1; ctx.fillRect(0, 0, W_, H_);
  for (let i = 0; i < 9; i++) PP(ctx, "duvar" + i, () => path([rect(-20, i * 160 + 20, W_ + 40, 8)], 190 + i, 2), "rgba(0,0,0,.18)", { d: 0, duz: true });
  const yils = p.yillar || [p.yil];
  const per = p.sure_yaprak || .42, bas = p.bas ?? .35;
  const cx = 540, cy = 560;
  // alttaki yapraklar önce, en üstteki son
  for (let j = yils.length - 1; j >= 0; j--) {
    const kop = j < yils.length - 1 ? bas + j * per : 1e9;   // son yaprak kalır
    const u = pr(lt, kop, .7);
    if (u >= 1) continue;
    const uq = q(u * .7) / .7;
    takvimYaprak(ctx, yils[j], cx + uq * 520, cy - uq * 220 + uq * uq * 900, 1.15, { rot: uq * 1.4, d: 1.4 + uq * 3 });
  }
  PP(ctx, "spiral", () => path([rect(250, cy - 200, 580, 26)], 199, 1), PAL.siyah, { d: .8 });
  if (p.harita) {
    const [rx, ry] = suudiHarita(ctx, 520, 1080, .95);
    pin(ctx, rx, ry, lt, p.pin ?? .6);
    serit(ctx, "RİYAD", rx + 150, ry - 70, 46, pop(lt, (p.pin ?? .6) + .25), { bg: PAL.krem, rot: -3 });
  }
  if (p.etiket) serit(ctx, p.etiket, 540, 1250, 54, pop(lt, p.etiket_t ?? .3), { bg: PAL.kir, ink: PAL.krem, bayrak: true });
  zemin(ctx, PAL.gece, 5);
};
// 4 · Baskın: site duvarı, partideki pencere, şikâyet balonu, polis arabası gelir
SET.baskin = (ctx, lt, D, p) => {
  gok(ctx, PAL.gece, lt);
  ctx.save(); ctx.translate(140, 240); hilal(ctx, 0, 0, 50); ctx.restore();
  // komşu ev (sol) ve parti evi (sağ)
  ctx.fillStyle = PAL.isik; ctx.fillRect(130, 820, 120, 110); ctx.fillRect(560, 760, 300, 180);
  PP(ctx, "komsu", () => path([[[-30, 1260], [-30, 700], [190, 560], [400, 700], [400, 1260]], rect(130, 820, 120, 110).reverse()], 201, 1.8), PAL.gece3, { d: 1.2, ic: 6 });
  // parti penceresinde dans eden siluetler + kabak
  ctx.save(); ctx.beginPath(); ctx.rect(560, 760, 300, 180); ctx.clip();
  [["cadi", 620], ["vampir", 720], ["kabak", 810]].forEach(([k, x], i) => {
    ctx.save(); ctx.globalAlpha = .9; karakter(ctx, k, x, 990, .55, lt, { dans: true, ofs: i * .3 }); ctx.restore(); });
  ctx.restore();
  PP(ctx, "parti", () => path([[[440, 1260], [440, 640], [980, 640], [980, 1260]], rect(560, 760, 300, 180).reverse()], 202, 1.8), PAL.gece4, { d: 1.2, ic: 6 });
  PP(ctx, "pcam", () => path([rect(705, 760, 10, 180), rect(560, 845, 300, 10)], 203, 1), PAL.gece4, { d: .5 });
  // duvar
  PP(ctx, "duvar", () => { const pts = [[-20, 1450], [-20, 1130]]; for (let x = -20; x <= 1100; x += 60) { pts.push([x, 1130]); pts.push([x + 30, 1110]); } pts.push([1100, 1130]); pts.push([1100, 1450]); return path([pts], 204, 1.6); }, PAL.kum2, { d: 1.6, ic: 8 });
  const sk = p.sikayet ?? .3;
  balon(ctx, 260, 470, 330, 120, pop(lt, sk), false);
  if (pop(lt, sk)) { ctx.save(); ctx.font = font(44); ctx.fillStyle = PAL.kir; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText("ŞİKÂYET!", 260, 470); ctx.restore(); }
  // polis arabası sağdan gelir, adımla
  const pg = p.polis ?? D * .45;
  const u = eo(pr(q(lt), pg, .9));
  if (lt > pg) {
    const x = 1500 - u * 920;
    const k = Math.floor(lt * 6) % 2;
    isikhavuzu(ctx, x - 20, 1060, 520, k ? "rgba(255,40,50,A)" : "rgba(50,110,255,A)", .55 * u);
    polisArabasi(ctx, x, 1400, 1, lt);
  }
  serit(ctx, "RİYAD · 2018", 540, 330, 44, pop(lt, .1), { bg: PAL.krem, rot: 2 });
  zemin(ctx, PAL.gece, 5);
};
// 5 · 17 kâğıt bebek: katlı şeritten açılır, sayaç
SET.zincir = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.kir2; ctx.fillRect(0, 0, W_, H_);
  sekizYildiz(ctx, 540, 820, 560, q(lt) * .08, PAL.kir1, 2);
  const n = p.n || 17, sat = [6, 6, 5], hiz = Math.min(.09, (D - .9) / n);
  let k = 0;
  sat.forEach((m, r) => {
    for (let i = 0; i < m; i++, k++) {
      const a = .2 + k * hiz, u = pr(lt, a, .25);
      if (u <= 0) continue;
      const fl = Math.floor(u * 4) / 4;   // katlı kâğıt açılır: x ölçeği adımla
      ctx.save(); ctx.translate(540 + (i - (m - 1) / 2) * 140, 800 + r * 220); ctx.scale(Math.max(.08, fl), 1);
      P(ctx, bebekP, PAL.krem, { d: 1.1, ic: 5 });
      ctx.restore();
    }
  });
  const say = Math.min(n, Math.max(0, Math.floor((lt - .2) / hiz) + 1));
  harfler(ctx, String(say), 540, 420, 230, 1, 0, { renk: PAL.krem });
  serit(ctx, p.etiket || "FİLİPİNLİ KADIN GÖZALTINDA", 540, 1330, 46, pop(lt, .2 + n * hiz), { bg: PAL.siyah, ink: PAL.krem, bayrak: true });
  zemin(ctx, PAL.kir3, 5);
};
// 6 · Polis açıklaması: rapor kâğıdı, iki kelime kırmızı kalemle çevrilir, masada maskeler
SET.rapor = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.kum3; ctx.fillRect(0, 0, W_, H_);
  for (let i = 0; i < 12; i++) { ctx.fillStyle = `rgba(0,0,0,${.05 + hash(i) * .06})`; ctx.fillRect(0, i * 130, W_, 6); }   // tahta masa damarı
  // masadaki maske ve şapka
  ctx.save(); ctx.translate(200, 1240); ctx.rotate(-.3);
  PP(ctx, "maske", () => path([[[-120, -10], [-100, -50], [-40, -60], [0, -36], [40, -60], [100, -50], [120, -10], [80, 30], [30, 26], [0, 4], [-30, 26], [-80, 30]], ell(-56, -14, 24, 14, 16).reverse(), ell(56, -14, 24, 14, 16).reverse()], 211, 1.6), PAL.mor, { d: 1.4, ic: 5 });
  ctx.restore();
  // rapor kâğıdı
  ctx.save(); ctx.translate(540, 720); ctx.rotate(-.03 + q(lt) * .004);
  PP(ctx, "rapor", () => path([rect(-380, -470, 760, 940)], 212, 2), PAL.krem, { d: 2 });
  ctx.font = font(44); ctx.fillStyle = PAL.siyah; ctx.textAlign = "left"; ctx.fillText("POLİS AÇIKLAMASI", -320, -370);
  ctx.fillStyle = PAL.kir; ctx.fillRect(-320, -340, 200, 8);
  ctx.fillStyle = "rgba(30,30,40,.55)";
  const sat = [[-320, -270, 620], [-320, -210, 560], [-320, -150, 600], [-320, -30, 480], [-320, 30, 590], [-320, 150, 520], [-320, 210, 610], [-320, 330, 400]];
  sat.forEach(([x, y, w]) => ctx.fillRect(x, y, w, 16));
  ctx.font = font(52); ctx.fillStyle = PAL.siyah;
  ctx.fillText("MASKELER", -320, -80); ctx.fillText("TUHAF KOSTÜMLER", -320, 110);
  // kırmızı kalem halkaları kendini çizer
  [[-320 + 150, -95, 200, 52, p.k1 ?? .6], [-320 + 262, 95, 318, 54, p.k2 ?? 1.2]].forEach(([x, y, rx, ry, a]) => {
    const u = q(pr(lt, a, .5) * .5) / .5; if (u <= 0) return;
    ctx.save(); ctx.strokeStyle = PAL.kir; ctx.lineWidth = 9; ctx.lineCap = "round"; ctx.beginPath();
    for (let i = 0; i <= 40 * u; i++) { const b = -2.4 + i / 40 * Math.PI * 2.15, w = 1 + (hash(i) - .5) * .05; ctx.lineTo(x + Math.cos(b) * rx * w, y + Math.sin(b) * ry * w); }
    ctx.stroke(); ctx.restore();
  });
  ctx.restore();
  zemin(ctx, PAL.gece, 5);
};
// 8 · Riyad Bulvarı: kapı, ampul zincirleri, hurmalar, kalabalık
SET.bulvar = (ctx, lt, D, p) => {
  gok(ctx, PAL.gece1, lt);
  const cam = q(lt) * 12;
  ctx.save(); ctx.translate(-cam * .3, 0); silueti(ctx, 600, 1050, PAL.gece2, "rgba(255,214,140,.7)", 2, .7); ctx.restore();
  // kemer kapı
  ctx.save(); ctx.translate(540, 0);
  ctx.fillStyle = "rgba(255,200,120,.25)"; ctx.fillRect(-260, 560, 520, 600);
  PP(ctx, "kemer", () => { const out = [[-420, 1200], [-420, 470], [420, 470], [420, 1200], [270, 1200]]; for (let k = 0; k <= 20; k++) { const a = k / 20 * Math.PI; out.push([Math.cos(a) * 270, 760 - Math.sin(a) * 200]); } out.push([-270, 1200]); return path([out], 221, 2); }, PAL.kir1, { d: 1.6, ic: 10 });
  ctx.font = font(52); ctx.fillStyle = PAL.krem; ctx.textAlign = "center"; ctx.fillText("RİYAD BULVARI", 0, 530);
  ctx.restore();
  cicekdizi(ctx, 130, 950, 600, 40, lt, 18);
  hurma(ctx, 70, 1300, 1.1, lt, 1); hurma(ctx, 1010, 1310, 1.15, lt, 2);
  // kalabalık: iki sıra, yürür
  const kinds = ["cadi", "zombi", "vampir", "kabak", "hayalet"];
  for (let r = 0; r < 2; r++) for (let i = 0; i < 6; i++) {
    const x = ((i * 210 + q(lt) * (r ? 70 : 50) + r * 90) % 1300) - 110;
    karakter(ctx, kinds[(i + r * 2) % 5], x, r ? 1420 : 1290, r ? .78 : .58, lt, { yuru: true, ofs: i * .17 });
  }
  serit(ctx, p.etiket || "2022", 540, 330, 64, pop(lt, .1), { bg: PAL.kir, ink: PAL.krem, rot: -3 });
  zemin(ctx, PAL.gece, 5);
};
// 9 · Bilet: "ÜCRETLİ" parçası makasla kesilip düşer, BEDAVA mühürü çarpar
SET.bilet = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.gece2; ctx.fillRect(0, 0, W_, H_);
  sekizYildiz(ctx, 540, 860, 520, -q(lt) * .06, PAL.gece3, 3);
  serit(ctx, "KORKUNÇ KOSTÜMLE GELENE", 540, 330, 50, pop(lt, .1), { bg: PAL.krem, rot: -2 });
  const kes = p.kes ?? D * .55;
  ctx.save(); ctx.translate(540, 860); ctx.rotate(-.06);
  PP(ctx, "bilet", () => path([[[-400, -230], [400, -230], [400, -40], [380, 0], [400, 40], [400, 230], [-400, 230], [-400, 40], [-380, 0], [-400, -40]], ...Array.from({ length: 9 }, (_, i) => ell(170, -200 + i * 50, 7, 7, 10).reverse())], 231, 2), PAL.kir, { d: 2, ic: 9 });
  ctx.font = font(64); ctx.fillStyle = PAL.krem; ctx.textAlign = "center"; ctx.fillText("GİRİŞ", -110, -100);
  ctx.font = font(34); ctx.fillText("RİYAD BULVARI · 2022", -110, -40);
  ctx.save(); ctx.translate(290, 0); ctx.rotate(-Math.PI / 2); ctx.font = font(40); ctx.fillText("KORKU HAFTASONU", 0, 14); ctx.restore();
  // ücret parçası: kesilene kadar yerinde, sonra döner düşer
  const u = pr(lt, kes, .9), uq = q(u * .9) / .9;
  ctx.save(); ctx.translate(-110 + uq * 80, 110 + uq * uq * 900); ctx.rotate(uq * .9);
  PP(ctx, "ucret", () => path([rect(-230, -60, 460, 120)], 232, 2.4), PAL.krem, { d: 1.2 + uq * 2 });
  ctx.font = font(66); ctx.fillStyle = PAL.siyah; ctx.fillText("ÜCRETLİ", 0, 24);
  ctx.restore();
  // makas izi: kesik çizgi
  if (lt > kes - .5 && lt < kes + .1) { const m = pr(lt, kes - .5, .5); ctx.strokeStyle = "rgba(255,255,255,.8)"; ctx.setLineDash([14, 10]); ctx.lineWidth = 4; ctx.strokeRect(-346, 44, 472 * m, 0); ctx.setLineDash([]); }
  ctx.restore();
  muhur(ctx, "BEDAVA", 430, 1110, 104, lt, kes + .45, -10);
  zemin(ctx, PAL.gece, 5);
};
// 10 · Kostüm geçidi: üç sıra paralaks, isim etiketleri sırayla
SET.gecit = (ctx, lt, D, p) => {
  gok(ctx, PAL.gece, lt);
  ctx.save(); ctx.translate(780, 260); hilal(ctx, 0, 0, 60); ctx.restore();
  kumtepe(ctx, 980, PAL.gece2, 11, 50);
  cicekdizi(ctx, -40, 1120, 420, 60, lt, 18);
  for (let i = 0; i < 5; i++) yarasa(ctx, ((q(lt) * 200 + i * 260) % 1300) - 100, 560 + Math.sin(q(lt) * 3 + i * 2) * 50, .8, lt, i);
  const row = (kinds, y, s, sp, off) => kinds.forEach((k, i) => karakter(ctx, k, ((i * (1300 / kinds.length) + q(lt) * sp + off) % 1300) - 110, y, s, lt, { yuru: true, ofs: i * .21 }));
  row(["kabak", "hayalet", "cadi", "zombi", "vampir", "kabak"], 1080, .45, 40, 60);
  kumtepe(ctx, 1150, PAL.gece3, 12, 30);
  // ön sıra: konuşulan üç kostüm sahnede durur, adlar düşer
  const on = [["cadi", 230, p.t1 ?? .1, "CADI"], ["zombi", 540, p.t2 ?? D * .3, "ZOMBİ"], ["vampir", 850, p.t3 ?? D * .55, "VAMPİR"]];
  on.forEach(([k, x, a, ad]) => {
    const u = eo(pr(q(lt), a - .25, .35));
    karakter(ctx, k, x, 1440 - (1 - u) * 40, .95 * (u ? 1 : .001), lt, { dans: u >= 1, ofs: x * .001 });
    serit(ctx, ad, x, 760 + (x === 540 ? -60 : 0), 46, pop(lt, a), { bg: PAL.kir, ink: PAL.krem, rot: (x - 540) * .01 });
  });
  zemin(ctx, PAL.gece, 5);
};
// 11 · Soru: dönen sekiz köşeli yıldız, dev kesik "?"
SET.soru = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.gece; ctx.fillRect(0, 0, W_, H_);
  sekizYildiz(ctx, 540, 820, 620, q(lt) * .1, PAL.gece2, 4);
  sekizYildiz(ctx, 540, 820, 380, -q(lt) * .14, PAL.gece3, 5);
  const u = pop(lt, .1);
  if (u) { ctx.save(); ctx.translate(540, 840); ctx.scale(u, u); ctx.font = font(520); ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.shadowColor = "rgba(0,0,0,.6)"; ctx.shadowBlur = 30; ctx.shadowOffsetY = 14; ctx.fillStyle = PAL.kir; ctx.fillText("?", 0, 0);
    ctx.shadowColor = "transparent"; ctx.lineWidth = 8; ctx.strokeStyle = "rgba(0,0,0,.3)"; ctx.strokeText("?", 0, 0); ctx.restore(); }
  serit(ctx, p.yazi || "4 YILDA NE DEĞİŞTİ?", 540, 330, 58, pop(lt, .4), { bg: PAL.krem, rot: -2 });
  zaman(ctx, lt, p.zaman ?? -1);
  zemin(ctx, PAL.gece1, 5);
};
// zaman şeridi: 2016 · 2018 · 2022 — o anki iğne kırmızı yanar
function zaman(ctx, lt, aktif) {
  const ys = ["2016", "2018", "2022"], y = 1290;
  PP(ctx, "zserit", () => path([rect(80, y - 14, 920, 28)], 241, 1.4), PAL.krem, { d: 1 });
  ys.forEach((t, i) => { const x = 180 + i * 360, on = i <= aktif;
    ctx.save(); ctx.translate(x, y); PP(ctx, "zp" + (on ? 1 : 0), () => path([ell(0, 0, 30, 30, 22)], 242 + on, 1), on ? PAL.kir : PAL.gri, { d: 1 }); ctx.restore();
    ctx.save(); ctx.font = font(40); ctx.fillStyle = on ? PAL.krem : "rgba(244,236,219,.45)"; ctx.textAlign = "center"; ctx.fillText(t, x, y - 52); ctx.restore(); });
}
// 12 · 2016: din polisi rozeti, kelepçe kalkar ve düşer
SET.rozet = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.gece1; ctx.fillRect(0, 0, W_, H_);
  sekizYildiz(ctx, 540, 760, 500, q(lt) * .05, PAL.gece2, 6);
  ctx.save(); ctx.translate(540, 700);
  PP(ctx, "rozet", () => path([star(0, 0, 250, 200, 12), ell(0, 0, 120, 120, 30).reverse()], 251, 2), PAL.yesil1, { d: 2, ic: 8 });
  PP(ctx, "rozic", () => path([ell(0, 0, 112, 112, 30)], 252, 1.4), PAL.krem, { d: .8 });
  ctx.font = font(30); ctx.fillStyle = PAL.yesil1; ctx.textAlign = "center"; ctx.fillText("DİN", 0, -10); ctx.fillText("POLİSİ", 0, 30);
  ctx.restore();
  // kelepçe: önce rozetin üstünde, sonra kesilip düşer
  const kal = p.kalk ?? D * .5, u = q(pr(lt, kal, .9) * .9) / .9;
  ctx.save(); ctx.translate(540 + u * 200, 1020 + u * u * 700); ctx.rotate(u * 1.6);
  PP(ctx, "kelepce", () => path([ell(-90, 0, 70, 70, 28), ell(-90, 0, 46, 46, 24).reverse(), ell(90, 0, 70, 70, 28), ell(90, 0, 46, 46, 24).reverse(), rect(-26, -10, 52, 20)], 253, 1.4), PAL.gri, { d: 1.4 });
  ctx.restore();
  serit(ctx, "GÖZALTI YETKİSİ KALDIRILDI", 540, 340, 46, pop(lt, kal + .2), { bg: PAL.kir, ink: PAL.krem, bayrak: true });
  zaman(ctx, lt, 0);
  zemin(ctx, PAL.gece, 5);
};
// 13 · 2018: sinema perdesi açılır, ışık huzmesi, kilit "35 YIL" açılıp düşer
SET.sinema = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.kir3; ctx.fillRect(0, 0, W_, H_);
  // perde (beyaz ekran)
  const ac = eo(pr(q(lt), p.ac ?? .3, 1.0));
  ctx.fillStyle = PAL.krem; ctx.fillRect(140, 450, 800, 520);
  if (ac > .2) { ctx.save(); ctx.globalAlpha = ac; ctx.font = font(66); ctx.fillStyle = PAL.kir; ctx.textAlign = "center"; ctx.fillText("SİNEMA", 540, 690); ctx.font = font(40); ctx.fillStyle = PAL.siyah; ctx.fillText("35 YIL SONRA İLK GÖSTERİM", 540, 760); ctx.restore(); }
  // projektör huzmesi
  ctx.save(); ctx.globalCompositeOperation = "lighter"; ctx.globalAlpha = .25 * ac; ctx.fillStyle = "#fff3cc"; ctx.beginPath(); ctx.moveTo(540, 1360); ctx.lineTo(140, 450); ctx.lineTo(940, 450); ctx.closePath(); ctx.fill(); ctx.restore();
  // kadife perde kanatları (testere dişli etek)
  [-1, 1].forEach(sd => { ctx.save(); ctx.translate(540 + sd * (270 + ac * 330), 0);
    PP(ctx, "kanat" + sd, () => { const pts = [[-280, 380], [280, 380]]; for (let k = 0; k <= 14; k++) pts.push([280 - k * 40, 1080 + (k % 2 ? 26 : 0)]); return path([pts], 260 + sd, 1.6); }, PAL.kir, { d: 1.6, ic: 8 });
    ctx.restore(); });
  PP(ctx, "ustpelmet", () => { const pts = [[-20, 300], [1100, 300], [1100, 420]]; for (let x = 1100; x >= -20; x -= 60) pts.push([x - 30, 460], [x - 60, 420]); return path([pts], 263, 1.6); }, PAL.kir1, { d: 1.8, ic: 8 });
  // koltuk sıraları
  for (let r = 0; r < 2; r++) for (let i = 0; i < 9; i++) { ctx.save(); ctx.translate(80 + i * 115 + r * 50, 1250 + r * 110);
    PP(ctx, "koltuk", () => path([rrect(-46, -90, 92, 120, 22)], 264, 1.2), r ? PAL.kir2 : PAL.kir1, { d: 1 }); ctx.restore(); }
  // kilit "35 YIL" açılır, düşer
  const ka = p.kilit ?? D * .55, u = q(pr(lt, ka, .9) * .9) / .9, acik = lt > ka - .25;
  ctx.save(); ctx.translate(800 + u * 120, 1050 + u * u * 700); ctx.rotate(u * 1.2);
  PP(ctx, "kilitk" + (acik ? 1 : 0), () => { const k = []; for (let i = 0; i <= 16; i++) { const a = Math.PI + i / 16 * Math.PI; k.push([Math.cos(a) * 60 + (acik ? 34 : 0), -90 + Math.sin(a) * 70 - (acik ? 30 : 0)]); } const ic = []; for (let i = 16; i >= 0; i--) { const a = Math.PI + i / 16 * Math.PI; ic.push([Math.cos(a) * 36 + (acik ? 34 : 0), -90 + Math.sin(a) * 48 - (acik ? 30 : 0)]); } return path([[...k, ...ic]], 265, 1); }, PAL.gri, { d: 1 });
  PP(ctx, "kilit", () => path([rrect(-90, -90, 180, 150, 18)], 266, 1.4), PAL.sari, { d: 1.4, ic: 5 });
  ctx.font = font(44); ctx.fillStyle = PAL.siyah; ctx.textAlign = "center"; ctx.fillText("35 YIL", 0, 4);
  ctx.restore();
  serit(ctx, "BASKINLA AYNI YIL", 540, 210, 46, pop(lt, p.ayni ?? D * .35), { bg: PAL.krem, rot: -3 });
  zaman(ctx, lt, 1);
  zemin(ctx, PAL.gece, 5);
};
// 14 · Petrol → eğlence: terazi, varil iner, dönme dolap yükselir
SET.petrol = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.kum; ctx.fillRect(0, 0, W_, H_);
  kumtepe(ctx, 1150, PAL.kum1, 14, 60); kumtepe(ctx, 1280, PAL.kum2, 15, 40);
  const u = eio(pr(q(lt), p.don ?? .5, 1.4)), ang = lerp(-.22, .22, u);
  // terazi
  ctx.save(); ctx.translate(540, 560);
  PP(ctx, "tdirek", () => path([[[-18, 0], [18, 0], [30, 640], [-30, 640]], [[-120, 640], [120, 640], [100, 600], [-100, 600]]], 271, 1.4), PAL.siyah, { d: 1.2 });
  ctx.rotate(ang);
  PP(ctx, "tkol", () => path([rect(-380, -14, 760, 28)], 272, 1.4), PAL.siyah, { d: 1.2 });
  [-1, 1].forEach(sd => {
    const x = sd * 360;
    ctx.save(); ctx.translate(x, 0); ctx.rotate(-ang);
    ctx.strokeStyle = PAL.siyah; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-90, 200); ctx.lineTo(0, 0); ctx.lineTo(90, 200); ctx.stroke();
    PP(ctx, "kefe", () => path([[[-130, 200], [130, 200], [100, 240], [-100, 240]]], 273, 1.2), PAL.siyah, { d: 1 });
    if (sd < 0) { // petrol varili
      PP(ctx, "varil", () => path([rrect(-70, 20, 140, 180, 14)], 274, 1.4), PAL.siyah, { d: 1.2, ic: 4 });
      ctx.fillStyle = PAL.kir; ctx.fillRect(-70, 70, 140, 14); ctx.fillRect(-70, 140, 140, 14);
      ctx.font = font(30); ctx.fillStyle = PAL.krem; ctx.textAlign = "center"; ctx.fillText("PETROL", 0, 125);
    } else {      // dönme dolap + bilet
      ctx.save(); ctx.translate(0, 70); ctx.rotate(q(lt) * .8);
      PP(ctx, "dolap", () => { const sp = []; for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; sp.push([[Math.cos(a) * 8, Math.sin(a) * 8], [Math.cos(a + .1) * 98, Math.sin(a + .1) * 98], [Math.cos(a - .1) * 98, Math.sin(a - .1) * 98]]); }
        return path([ell(0, 0, 110, 110, 36), ell(0, 0, 96, 96, 36).reverse(), ...sp.map(s => s)], 275, 1); }, PAL.kir, { d: 1 });
      for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 - q(lt) * .8; ctx.save(); ctx.rotate(i * Math.PI / 4); ctx.translate(110, 0); ctx.rotate(-i * Math.PI / 4 - q(lt) * .8 + a - a);
        PP(ctx, "kab" + (i % 3), () => path([rrect(-16, -4, 32, 26, 6)], 276 + i % 3, .8), [PAL.tur, PAL.krem, PAL.mor][i % 3], { d: .6 }); ctx.restore(); }
      ctx.restore();
      ctx.save(); ctx.translate(0, 196); PP(ctx, "dolayak", () => path([[[-60, 0], [0, -120], [60, 0]], [[-40, 0], [0, -90], [40, 0]]], 279, 1), PAL.kir1, { d: .6 }); ctx.restore();
    }
    ctx.restore();
  });
  ctx.restore();
  serit(ctx, "PETROLDEN SONRASI", 540, 300, 56, pop(lt, .1), { bg: PAL.siyah, ink: PAL.krem, rot: -2 });
  serit(ctx, "EĞLENCE + TURİZM", 760, 1340, 50, pop(lt, (p.don ?? .5) + 1), { bg: PAL.kir, ink: PAL.krem, bayrak: true, rot: 2 });
  zemin(ctx, PAL.gece, 5);
};
// 14b · 2026: kutlama otel ve eğlence merkezlerinde — sahne, spot ışığı, kostüm yarışması, kupa
SET.y2026 = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.mor1; ctx.fillRect(0, 0, W_, H_);
  for (let i = 0; i < 7; i++) PP(ctx, "duvar26_" + i, () => path([rect(i * 160 - 10, 0, 70, 1500)], 300 + i, 2), "rgba(0,0,0,.14)", { d: 0, duz: true });
  // avize ışıkları (adımla parlayan)
  cicekdizi(ctx, -30, 1110, 640, 50, lt, 16);
  // sahne
  PP(ctx, "sahne26", () => path([[[-20, 1200], [1100, 1200], [1100, 1300], [-20, 1300]]], 310, 1.6), PAL.kir1, { d: 1.6, ic: 7 });
  // spot ışıkları adımla yarışmacılar arasında gezer
  const xs = [250, 540, 830], sec = Math.floor(q(lt) * 1.6) % 3;
  ctx.save(); ctx.globalCompositeOperation = "lighter";
  xs.forEach((x, i) => { ctx.globalAlpha = i === sec ? .32 : .08; ctx.fillStyle = "#fff3cc"; ctx.beginPath(); ctx.moveTo(x - 30, 560); ctx.lineTo(x - 170, 1220); ctx.lineTo(x + 170, 1220); ctx.lineTo(x + 30, 560); ctx.closePath(); ctx.fill(); });
  ctx.restore();
  // yarışmacılar + numara kartı
  [["cadi", 250], ["vampir", 540], ["kabak", 830]].forEach(([k, x], i) => {
    karakter(ctx, k, x, 1205, .95, lt, { dans: i === sec, ofs: i * .2 });
    ctx.save(); ctx.translate(x, 1110); PP(ctx, "no26", () => path([rect(-34, -26, 68, 52)], 320, 1), PAL.krem, { d: .7 });
    ctx.font = font(34); ctx.fillStyle = PAL.siyah; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(String(i + 1), 0, 2); ctx.restore();
  });
  // kupa
  const ku = pop(lt, p.kupa ?? D * .55);
  if (ku) { ctx.save(); ctx.translate(830, 760); ctx.scale(ku, ku);
    isikhavuzu(ctx, 0, 0, 140, "rgba(255,210,90,A)", .5);
    PP(ctx, "kupa", () => path([[[-60, -70], [60, -70], [50, 0], [18, 22], [14, 60], [44, 70], [44, 86], [-44, 86], [-44, 70], [-14, 60], [-18, 22], [-50, 0]],
      [[-60, -60], [-92, -52], [-80, -6], [-52, -6], [-56, -22], [-74, -24], [-78, -44], [-58, -46]], [[60, -60], [92, -52], [80, -6], [52, -6], [56, -22], [74, -24], [78, -44], [58, -46]]], 330, 1.2), PAL.sari, { d: 1.4, ic: 4 });
    ctx.restore(); }
  takvimYaprak(ctx, 2026, 230, 330, .62, { rot: -.06 });
  serit(ctx, "KOSTÜM YARIŞMASI", 660, 300, 50, pop(lt, .2), { bg: PAL.kir, ink: PAL.krem, bayrak: true, rot: 2 });
  serit(ctx, "OTEL · RESTORAN · EĞLENCE MERKEZİ", 540, 1380, 36, pop(lt, p.mekan ?? D * .25), { bg: PAL.krem, rot: -1 });
  zemin(ctx, PAL.gece, 5);
};
// 15 · Telefon: yorum balonları yağar
SET.telefon = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.gece1; ctx.fillRect(0, 0, W_, H_);
  sekizYildiz(ctx, 540, 820, 600, q(lt) * .05, PAL.gece2, 7);
  ctx.save(); ctx.translate(540, 820); ctx.rotate(-.04);
  PP(ctx, "tel", () => path([rrect(-280, -560, 560, 1120, 60), rrect(-245, -490, 490, 960, 20).reverse()], 281, 2), PAL.siyah, { d: 2.4, ic: 6 });
  ctx.fillStyle = "#e9e3d6"; ctx.fillRect(-245, -490, 490, 960);
  ctx.beginPath(); ctx.rect(-245, -490, 490, 960); ctx.clip();
  const em = ["😡", "❤️", "👎", "👏", "🤔", "😱", "🙏", "🔥"];
  const n = C(0, 16, Math.floor((lt - .15) / .22) + 1);
  for (let i = 0; i < n; i++) {
    const a = .15 + i * .22, u = pop(lt, a);
    const sl = i === n - 1 ? 1 - C(0, 1, Math.floor((lt - a) * 12) / 3) : 0;   // en yeni yorum alttan kayar
    const y = 400 - (n - 1 - i) * 118 + sl * 118;
    const sol = i % 2 === 0;
    ctx.save(); ctx.translate(sol ? -70 : 70, y); ctx.scale(u, u);
    PP(ctx, "yb" + (sol ? 1 : 0), () => path([rrect(-150, -48, 300, 96, 26)], 282 + sol, 1.2), sol ? PAL.krem : "#d7e4f7", { d: .8 });
    ctx.font = "56px sans-serif"; ctx.textAlign = "left"; ctx.textBaseline = "middle"; ctx.fillText(em[i % 8], -134, 4);
    ctx.fillStyle = "rgba(30,30,40,.5)"; ctx.fillRect(-58, -18, 170 - (i % 3) * 30, 12); ctx.fillRect(-58, 8, 120 - (i % 2) * 40, 12);
    ctx.restore();
  }
  ctx.restore();
  serit(ctx, "TEPKİ YAĞIYOR", 540, 170, 56, pop(lt, .1), { bg: PAL.kir, ink: PAL.krem, bayrak: true });
  zemin(ctx, PAL.gece, 5);
};
// 16 · İki görüş: katlı kâğıttan kesilmiş ayna çift, sayfa açılır
SET.ikiyuz = (ctx, lt, D, p) => {
  ctx.fillStyle = PAL.gece; ctx.fillRect(0, 0, W_, H_);
  const ac = eo(pr(q(lt), .15, .6));
  [-1, 1].forEach(sd => {
    ctx.save(); ctx.translate(540, 0); ctx.scale(sd * Math.max(.04, sd < 0 ? 1 : ac), 1);
    PP(ctx, "yari", () => path([rect(0, 420, 470, 900)], 291, 1.8), sd < 0 ? PAL.krem : PAL.kir, { d: 1.4 });
    ctx.restore();
  });
  ctx.strokeStyle = "rgba(0,0,0,.35)"; ctx.lineWidth = 3; ctx.setLineDash([12, 10]); ctx.beginPath(); ctx.moveTo(540, 430); ctx.lineTo(540, 1310); ctx.stroke(); ctx.setLineDash([]);
  karakter(ctx, "insan", 300, 1180, 1.25, lt, { elkaldir: true, dans: true, renk: PAL.kir, sac: 1, sacr: "#6a3d1e" });
  if (ac > .3) karakter(ctx, "insan", 780, 1180, 1.25 * Math.min(1, ac), lt, { yon: -1, renk: PAL.krem, sac: 2, sacr: "#2b2b2b" });
  serit(ctx, "ÖZGÜRLÜK", 300, 560, 52, pop(lt, p.t1 ?? .2), { bg: PAL.kir, ink: PAL.krem, rot: -3 });
  serit(ctx, "GELENEKTEN KOPUŞ", 780, 560, 44, pop(lt, p.t2 ?? D * .5), { bg: PAL.krem, ink: PAL.siyah, rot: 3 });
  zemin(ctx, PAL.gece1, 5);
};
// 17 · Kapanış: SENCE HANGİSİ? + logo kâğıt mühür gibi
SET.kapanis = (ctx, lt, D, p, img) => {
  ctx.fillStyle = PAL.kir2; ctx.fillRect(0, 0, W_, H_);
  sekizYildiz(ctx, 540, 860, 640, q(lt) * .1, PAL.kir1, 8);
  harfler(ctx, "SENCE", 540, 420, 110, lt, .05, { hiz: .04 });
  harfler(ctx, "HANGİSİ?", 540, 560, 130, lt, .3, { hiz: .04 });
  const u = pop(lt, p.logo_t ?? D * .45);
  if (u && img && img.complete) {
    ctx.save(); ctx.translate(540, 960); ctx.scale(u, u); ctx.rotate(-.05);
    ctx.shadowColor = "rgba(0,0,0,.55)"; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12;
    ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(0, 0, 196, 0, 7); ctx.fill(); ctx.shadowColor = "transparent";
    ctx.save(); ctx.beginPath(); ctx.arc(0, 0, 182, 0, 7); ctx.clip(); ctx.drawImage(img, -182, -182, 364, 364); ctx.restore();
    ctx.restore();
  }
  serit(ctx, "MERAK ETTİYSEN", 540, 1260, 50, pop(lt, (p.logo_t ?? D * .45) + .2), { bg: PAL.krem, rot: -2 });
  zemin(ctx, PAL.kir3, 5);
};

// ---- dünya ------------------------------------------------------------------
window.buildKesme = function (stage, tl) {
  W_ = W; H_ = H;
  const cv = document.createElement("canvas"); cv.width = W_; cv.height = H_;
  Object.assign(cv.style, { position: "absolute", inset: "0", width: W_ + "px", height: H_ + "px" });
  stage.appendChild(cv);
  const ctx = cv.getContext("2d");
  GRAIN = grain();
  const ks = tl.scenes.filter(s => s.tip === "kesme");
  let img = null;
  const lg = ks.find(s => s.p.src);
  if (lg) { img = new Image(); img.src = lg.p.src; img.style.display = "none"; stage.appendChild(img); }
  const TR = .32;   // yırtık sayfa geçişi
  const ciz = (s, t) => { const f = SET[s.p.set]; if (!f) throw new Error("bilinmeyen kesme seti: " + s.p.set);
    ctx.save(); f(ctx, Math.max(0, t - s.t0), s.t1 - s.t0, s.p, img); ctx.restore(); };
  return function (t) {
    let k = 0; ks.forEach((s, i) => { if (t >= s.t0) k = i; });
    const cur = ks[k], lt = t - cur.t0;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (k > 0 && lt < TR && !cur.p.kesik) {
      ciz(ks[k - 1], t);
      const e = eio(C(0, 1, lt / TR)), xe = W_ * (1 - e) - 30 * (1 - e);
      const edge = []; for (let y = -20; y <= H_ + 20; y += 26) edge.push([xe + (hash(y * .7 + k) - .5) * 26, y]);
      const reg = new Path2D(); edge.forEach(([x, y], i) => i ? reg.lineTo(x, y) : reg.moveTo(x, y)); reg.lineTo(W_ + 40, H_ + 20); reg.lineTo(W_ + 40, -20); reg.closePath();
      ctx.save(); ctx.shadowColor = "rgba(0,0,0,.6)"; ctx.shadowBlur = 40; ctx.shadowOffsetX = -12; ctx.fillStyle = "#000"; ctx.fill(reg); ctx.restore();
      ctx.save(); ctx.clip(reg); ciz(cur, t); ctx.restore();
      ctx.save(); ctx.strokeStyle = "#fbf6ea"; ctx.lineWidth = 7; ctx.beginPath(); edge.forEach(([x, y], i) => i ? ctx.lineTo(x + 3, y) : ctx.moveTo(x + 3, y)); ctx.stroke(); ctx.restore();
    } else ciz(cur, t);
    // kâğıt dokusu
    ctx.save(); ctx.globalCompositeOperation = "soft-light"; ctx.globalAlpha = .55; ctx.drawImage(GRAIN, 0, 0, W_, H_); ctx.restore();
  };
};
SCENES.kesme = () => () => {};
})();
