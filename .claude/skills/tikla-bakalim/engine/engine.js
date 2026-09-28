/*
 * Tıkla Bakalım animasyon motoru.
 *
 * Deterministik: hiçbir CSS animasyonu veya zamanlayıcı yok. Her kare
 * `seek(t)` ile saniye cinsinden kurulur, yakalayıcı (capture.mjs) ekran
 * görüntüsünü alır. Aynı t her zaman aynı kareyi verir — paralel render ve
 * tek kare önizleme bu sayede mümkün.
 *
 * Zaman çizelgesi (render.py üretir):
 *   { dur, scenes: [{t0, t1, tip, bolum, p, kaynak}], words: [{w, s, e, c}] }
 */

// ---------- yardımcılar ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const prog = (lt, at, dur) => clamp((lt - at) / Math.max(dur, 1e-6));
const eOut = x => 1 - Math.pow(1 - x, 3);
const eInOut = x => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const eBack = x => { const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const lerp = (a, b, x) => a + (b - a) * x;

function el(tag, cls, html, parent) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  if (parent) parent.appendChild(e);
  return e;
}

// *sarı* ~kırmızı~ +yeşil+ işaretlemesi
function md(s) {
  return String(s ?? "")
    .replace(/\*([^*]+)\*/g, '<span class="sari">$1</span>')
    .replace(/~([^~]+)~/g, '<span class="kirmizi">$1</span>')
    .replace(/\+([^+]+)\+/g, '<span class="yesil">$1</span>')
    .replace(/\n/g, "<br>");
}

// Türkçe sayı biçimi: 12.480,50 — ICU'ya güvenmiyoruz (headless kabukta eksik olabiliyor)
function fmt(v, dec = 0) {
  const neg = v < 0; v = Math.abs(v);
  let [i, f] = v.toFixed(dec).split(".");
  i = i.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return (neg ? "−" : "") + i + (f ? "," + f : "");
}

// Giriş: ölçekle zıplayarak belir. at anından itibaren dur saniyede.
function pop(e, lt, at, dur = .38, from = .4) {
  const x = prog(lt, at, dur);
  e.style.opacity = clamp(x * 3);
  e.style.transform = `scale(${lerp(from, 1, eBack(x))})`;
  return x;
}
function slide(e, lt, at, dx = 0, dy = 80, dur = .4) {
  const x = eOut(prog(lt, at, dur));
  e.style.opacity = clamp(prog(lt, at, dur) * 2.5);
  e.style.transform = `translate(${dx * (1 - x)}px, ${dy * (1 - x)}px)`;
  return x;
}
// Tek satıra sığdır: taşarsa yazı boyunu küçült. Ölçüm ancak öğe görünürken
// yapılabilir (gizli sahnede genişlik 0) — fit() işaretler, seek() sahne ilk
// açıldığında ölçer. fitNow() görünür öğede hemen ölçer.
// Sahne içeriğinin genişliği: dikey 940, yatay 1300 (load() ayarlar)
let SCW = 940;
function fitNow(e, base, maxW = SCW) {
  e.style.whiteSpace = "nowrap";
  e.style.fontSize = base + "px";
  const w = e.scrollWidth;
  if (w > maxW) e.style.fontSize = (base * maxW / w) + "px";
}
function fit(e, base, maxW = SCW) {
  e.dataset.fit = base; e.dataset.fitw = maxW;
  e.style.whiteSpace = "nowrap"; e.style.fontSize = base + "px";
}

// Sürekli hafif hareket — hiçbir öğe tamamen durmasın
const bob = (lt, amp = 8, per = 2.4, ph = 0) => Math.sin((lt / per + ph) * Math.PI * 2) * amp;

// Sahnenin aşamaları sahne süresine yayılır: giriş ilk %15'te, son öğe en geç %80'de
function stagger(i, n, d, start = .15, end = .8) {
  if (n <= 1) return start * d;
  return (start + (end - start) * (i / (n - 1))) * d;
}

const COL = { sari: "--sari", kirmizi: "--kirmizi", yesil: "--yesil", mavi: "--mavi", mor: "--mor", turuncu: "--turuncu", beyaz: "--ink" };
const cvar = c => `var(${COL[c] || "--sari"})`;

// ---------- sahneler ----------
// Her sahne: build(p, root, meta) -> update(lt, d). lt = sahne içi zaman.
const SCENES = {};

// Büyük başlık: ikon + satırlar. Hook ve bölüm açılışı.
SCENES.baslik = (p, r) => {
  const ic = p.ikon ? el("div", "emoji", p.ikon, r) : null;
  if (ic) { ic.style.fontSize = (p.ikon_boy || 250) + "px"; ic.style.marginBottom = "40px"; }
  const lines = (p.satirlar || [p.metin]).map(s => {
    const e = el("div", "h", md(s), r);
    e.style.fontSize = (p.boy || 108) + "px"; e.style.margin = "6px 0";
    return e;
  });
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "40px";
  return (lt, d) => {
    if (ic) { pop(ic, lt, 0, .45, .2); ic.style.transform += ` translateY(${bob(lt, 14)}px) rotate(${bob(lt, 4, 3.1)}deg)`; }
    lines.forEach((e, i) => pop(e, lt, .12 + i * .16));
    if (note) slide(note, lt, .2 + lines.length * .16 + .15);
  };
};

// Soru kartı: bölüm geçişi. Arkada dev soru işareti döner.
SCENES.soru = (p, r) => {
  const q = el("div", "h sari", "?", r);
  Object.assign(q.style, { position: "absolute", fontSize: "900px", opacity: .12, top: "-40px" });
  const ic = p.ikon ? el("div", "emoji", p.ikon, r) : null;
  if (ic) { ic.style.fontSize = "200px"; ic.style.marginBottom = "30px"; }
  const t = el("div", "h", md(p.metin), r);
  t.style.fontSize = (p.boy || 120) + "px";
  return (lt) => {
    q.style.transform = `rotate(${bob(lt, 8, 3)}deg) scale(${1 + .04 * Math.sin(lt * 3)})`;
    if (ic) { pop(ic, lt, 0, .4, .2); ic.style.transform += ` translateY(${bob(lt, 12)}px)`; }
    pop(t, lt, .1);
  };
};

// Tek sayı: sayarak büyür, yanında yön oku.
SCENES.sayi = (p, r) => {
  const ic = p.ikon ? el("div", "emoji", p.ikon, r) : null;
  if (ic) { ic.style.fontSize = "190px"; ic.style.marginBottom = "24px"; }
  const lb = el("div", "lbl", md(p.etiket), r);
  const row = el("div", null, null, r);
  Object.assign(row.style, { display: "flex", alignItems: "center", gap: "26px", margin: "20px 0", whiteSpace: "nowrap" });
  const num = el("div", "h", "", row);
  const nb = p.boy || 190;
  num.style.color = cvar(p.renk || "sari");
  let ar = null;
  if (p.yon) {
    ar = el("div", "h", p.yon === "up" ? "▲" : "▼", row);
    Object.assign(ar.style, { fontSize: "120px", color: cvar(p.yon === "up" ? "kirmizi" : "yesil") });
    if (p.ok_renk) ar.style.color = cvar(p.ok_renk);
  }
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "30px";
  const from = p.baslangic ?? 0, to = p.deger, dec = p.ondalik ?? 0;
  return (lt, d) => {
    if (ic) { pop(ic, lt, 0, .4, .2); ic.style.transform += ` translateY(${bob(lt, 10)}px)`; }
    slide(lb, lt, .08, 0, 40);
    const cd = Math.min(1.3, d * .45);
    // sayma:false -> sayı doğrudan son değerle belirir (hook: ilk kare yanlış sayı göstermesin)
    const x = p.sayma === false ? 1 : eOut(prog(lt, .2, cd));
    num.textContent = (p.onek || "") + fmt(lerp(from, to, x), dec) + (p.sonek || "");
    // son değere göre sığdır — sayarken boy zıplamasın
    if (!num._fs) { const t = num.textContent; num.textContent = (p.onek || "") + fmt(to, dec) + (p.sonek || "");
      fitNow(num, nb, SCW - (ar ? 150 : 0)); num._fs = num.style.fontSize; num.textContent = t; }
    num.style.fontSize = num._fs;
    pop(num, lt, .15, .35, .7);
    if (x >= 1) num.style.transform = `scale(${1 + .03 * Math.sin((lt - .2 - cd) * 5)})`;
    if (ar) { pop(ar, lt, .2 + cd * .6); ar.style.transform += ` translateY(${bob(lt, 10, 1.1) * (p.yon === "up" ? -1 : 1)}px)`; }
    if (note) slide(note, lt, .3 + cd);
  };
};

// Önce / sonra: iki sütun, sıfırdan başlayan dürüst ölçek.
SCENES.karsilastir = (p, r) => {
  const title = p.baslik ? el("div", "h", md(p.baslik), r) : null;
  if (title) { fit(title, 62); title.style.marginBottom = "36px"; }
  const box = el("div", null, null, r);
  Object.assign(box.style, { display: "flex", alignItems: "flex-end", justifyContent: "center", gap: "80px", height: "600px" });
  const H = 380, max = Math.max(p.sol.deger, p.sag.deger);
  const dec = p.ondalik ?? 2;
  const cols = [p.sol, p.sag].map((c, i) => {
    const col = el("div", null, null, box);
    Object.assign(col.style, { display: "flex", flexDirection: "column", alignItems: "center", width: "360px" });
    const v = el("div", "h", "", col); v.style.marginBottom = "18px";
    v.style.color = cvar(c.renk || (i ? "kirmizi" : "beyaz"));
    const bar = el("div", null, null, col);
    Object.assign(bar.style, { width: "220px", borderRadius: "26px 26px 8px 8px", background: cvar(c.renk || (i ? "kirmizi" : "beyaz")), height: "0px" });
    const lb = el("div", "lbl", md(c.etiket), col); lb.style.marginTop = "20px"; lb.style.fontSize = "44px"; lb.style.lineHeight = "1.15";
    return { col, v, bar, lb, c, h: H * c.deger / max };
  });
  const diff = p.fark ? el("div", "h", md(p.fark), r) : null;
  if (diff) Object.assign(diff.style, { fontSize: "74px", background: "var(--kirmizi)", color: "#fff", padding: "10px 34px", borderRadius: "22px", marginTop: "34px" });
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "26px";
  return (lt, d) => {
    if (title) slide(title, lt, 0, 0, 40);
    const gap = Math.min(.9, d * .25);
    cols.forEach((o, i) => {
      const at = .15 + i * gap;
      const x = eOut(prog(lt, at, .8));
      o.bar.style.height = (o.h * x) + "px";
      o.col.style.opacity = clamp(prog(lt, at, .2));
      o.v.textContent = (p.onek || "") + fmt(o.c.deger * x, dec) + (p.sonek || "");
      if (!o.v._fs) { const t = o.v.textContent; o.v.textContent = (p.onek || "") + fmt(o.c.deger, dec) + (p.sonek || "");
        fitNow(o.v, 72, 360); o.v._fs = o.v.style.fontSize; o.v.textContent = t; }
      o.v.style.fontSize = o.v._fs;
    });
    if (diff) { pop(diff, lt, .15 + gap + .7); diff.style.transform += ` translateY(${bob(lt, 6, 1.4)}px)`; }
    if (note) slide(note, lt, Math.min(d * .7, 2.4));
  };
};

// Liste: ikon + metin + değer satırları sırayla kayar.
SCENES.liste = (p, r) => {
  const title = p.baslik ? el("div", "h", md(p.baslik), r) : null;
  if (title) { fit(title, 68); title.style.marginBottom = "40px"; }
  const rows = p.satirlar.map(s => {
    const row = el("div", "card", null, r);
    Object.assign(row.style, { display: "flex", alignItems: "center", width: "100%", padding: "30px 40px", margin: "14px 0", gap: "30px", textAlign: "left" });
    const ic = el("div", "emoji", s.ikon || "•", row); ic.style.fontSize = "96px";
    const tx = el("div", "h", md(s.metin), row); Object.assign(tx.style, { fontSize: "60px", flex: "1" });
    if (s.deger != null) { const v = el("div", "h", md(s.deger), row); v.style.fontSize = "68px"; v.style.color = cvar(s.renk || "sari"); }
    return row;
  });
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "26px";
  return (lt, d) => {
    if (title) slide(title, lt, 0, 0, 40);
    rows.forEach((e, i) => slide(e, lt, stagger(i, rows.length, d, .1, .6), 260, 0, .45));
    if (note) slide(note, lt, d * .72);
  };
};

// Sebep → sonuç zinciri. Her adım sahne süresine yayılır; etkin adım vurgulanır.
SCENES.akis = (p, r) => {
  const title = p.baslik ? el("div", "h", md(p.baslik), r) : null;
  if (title) { fit(title, 64); title.style.marginBottom = "24px"; }
  const n = p.adimlar.length;
  const items = [];
  p.adimlar.forEach((s, i) => {
    const node = el("div", "card", null, r);
    Object.assign(node.style, { display: "flex", alignItems: "center", gap: "30px", width: "100%", padding: n > 3 ? "20px 36px" : "30px 40px", textAlign: "left" });
    const ic = el("div", "emoji", s.ikon || "", node); ic.style.fontSize = n > 3 ? "80px" : "100px";
    const tx = el("div", "h", md(s.metin), node); tx.style.fontSize = (n > 3 ? 52 : 60) + "px";
    let ar = null;
    if (i < n - 1) {
      ar = el("div", "h sari", "↓", r);
      Object.assign(ar.style, { fontSize: n > 3 ? "70px" : "84px", lineHeight: "1", margin: "4px 0" });
    }
    items.push({ node, ar });
  });
  return (lt, d) => {
    if (title) slide(title, lt, 0, 0, 40);
    const at = items.map((_, i) => stagger(i, n, d, .08, .75));
    let cur = 0; at.forEach((a, i) => { if (lt >= a) cur = i; });
    items.forEach((o, i) => {
      slide(o.node, lt, at[i], 0, 70, .38);
      const on = i === cur;
      o.node.style.borderColor = on ? "var(--sari)" : "var(--line)";
      o.node.style.background = on ? "rgba(255,200,61,.14)" : "var(--card)";
      if (lt >= at[i] + .38) o.node.style.transform = `scale(${on ? 1.03 : .97})`;
      o.node.style.opacity = lt < at[i] ? 0 : (on ? 1 : .6);
      if (o.ar) {
        const x = prog(lt, at[i] + .25, .3);
        o.ar.style.opacity = x; o.ar.style.transform = `translateY(${(1 - eOut(x)) * -30 + bob(lt, 5, 1)}px)`;
      }
    });
  };
};

// Yığın çubuk: bir toplamın parçaları. Durumlar arasında geçiş yapar.
// Mekanizma anlatmak için (vergi küçüldü, maliyet büyüdü, toplam aynı kaldı).
SCENES.yigin = (p, r) => {
  const title = p.baslik ? el("div", "h", md(p.baslik), r) : null;
  if (title) { fit(title, 64); title.style.marginBottom = "20px"; }
  const wrap = el("div", null, null, r);
  Object.assign(wrap.style, { position: "relative", display: "flex", alignItems: "flex-end", gap: "50px", height: "640px" });
  const bar = el("div", null, null, wrap);
  Object.assign(bar.style, { width: "300px", height: "600px", display: "flex", flexDirection: "column-reverse", position: "relative" });
  const legend = el("div", null, null, wrap);
  Object.assign(legend.style, { display: "flex", flexDirection: "column-reverse", height: "600px", width: "420px", textAlign: "left", position: "relative" });
  const names = p.durumlar[0].parcalar.map(x => x.ad);
  const segs = names.map((nm, i) => {
    const c = p.durumlar[0].parcalar[i].renk || ["mavi", "sari", "kirmizi", "yesil"][i];
    const s = el("div", null, null, bar);
    Object.assign(s.style, { width: "100%", background: cvar(c), borderRadius: i === names.length - 1 ? "24px 24px 0 0" : (i === 0 ? "0 0 12px 12px" : "0") });
    const l = el("div", "h", md(nm), legend);
    Object.assign(l.style, { position: "absolute", left: "0", fontSize: "54px", color: cvar(c) });
    return { s, l };
  });
  const tot = el("div", "h", "", r); tot.style.fontSize = "72px"; tot.style.marginTop = "20px";
  const lab = el("div", "lbl", "", r); lab.style.marginTop = "10px";
  const temsili = p.temsili !== false ? el("div", "temsili", "temsili", r) : null;
  const totals = p.durumlar.map(s => s.parcalar.reduce((a, b) => a + b.deger, 0));
  const max = Math.max(...totals) * 1.05;
  return (lt, d) => {
    if (title) slide(title, lt, 0, 0, 40);
    const n = p.durumlar.length;
    const at = p.durumlar.map((_, i) => stagger(i, n, d, .05, .7));
    // k. duruma geçiş at[k] anında başlar, T saniyede biter
    let k = 0; at.forEach((a, i) => { if (lt >= a) k = i; });
    const T = n > 1 ? Math.min(.9, (at[1] - at[0]) * .6) : .5;
    const x = k === 0 ? 1 : eInOut(prog(lt, at[k], T));
    const A = p.durumlar[Math.max(0, k - 1)], B = p.durumlar[k];
    const grow = eOut(prog(lt, 0, .6));
    let y = 0;
    segs.forEach((o, i) => {
      const v = lerp(A.parcalar[i].deger, B.parcalar[i].deger, x);
      const h = 600 * v / max * grow;
      o.s.style.height = h + "px";
      o.l.style.bottom = (y + h / 2 - 32) + "px";
      o.l.style.opacity = clamp(prog(lt, .3, .3)) * (v > 0.02 * max ? 1 : 0);
      y += h;
    });
    const tv = lerp(totals[Math.max(0, k - 1)], totals[k], x);
    const cur = x > .5 ? B : A;
    tot.innerHTML = (p.toplam_etiket ? md(p.toplam_etiket) + " " : "") +
      `<span style="color:${cvar(cur.renk || "sari")}">${cur.toplam_metin ? md(cur.toplam_metin) : (p.onek || "") + fmt(tv, p.ondalik ?? 0) + (p.sonek || "")}</span>`;
    lab.innerHTML = md(cur.etiket || "");
    tot.style.opacity = clamp(prog(lt, .3, .3));
    lab.style.opacity = clamp(prog(lt, .35, .3));
  };
};

// Çizgi grafik: kendini çizer, uçta değer etiketi.
SCENES.grafik = (p, r) => {
  const title = p.baslik ? el("div", "h", md(p.baslik), r) : null;
  if (title) { title.style.fontSize = "64px"; title.style.marginBottom = "30px"; }
  const W = 900, H = 560, pad = 40;
  const vals = p.noktalar.map(x => x[1]);
  const lo = p.y_min ?? Math.min(...vals) * .96, hi = p.y_max ?? Math.max(...vals) * 1.04;
  const X = i => pad + (W - 2 * pad) * i / (vals.length - 1);
  const Y = v => H - pad - (H - 2 * pad) * (v - lo) / (hi - lo);
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", W); svg.setAttribute("height", H + 70); svg.style.overflow = "visible";
  r.appendChild(svg);
  const c = `var(${COL[p.renk || "sari"]})`;
  for (let g = 0; g <= 3; g++) {
    const ln = document.createElementNS(ns, "line");
    const yy = pad + (H - 2 * pad) * g / 3;
    Object.entries({ x1: pad, x2: W - pad, y1: yy, y2: yy, stroke: "rgba(255,255,255,.12)", "stroke-width": 3 }).forEach(([k, v]) => ln.setAttribute(k, v));
    svg.appendChild(ln);
  }
  const d = vals.map((v, i) => `${i ? "L" : "M"}${X(i)},${Y(v)}`).join(" ");
  const area = document.createElementNS(ns, "path");
  area.setAttribute("d", d + ` L${X(vals.length - 1)},${H - pad} L${X(0)},${H - pad} Z`);
  area.setAttribute("fill", c); area.setAttribute("opacity", ".14");
  // dolgu, çizginin ucundan ileri geçmesin: soldan açılan kırpma
  const cid = "clip" + Math.random().toString(36).slice(2);
  const defs = document.createElementNS(ns, "defs"), cp = document.createElementNS(ns, "clipPath"), cr = document.createElementNS(ns, "rect");
  cp.setAttribute("id", cid); cr.setAttribute("x", 0); cr.setAttribute("y", 0); cr.setAttribute("height", H); cr.setAttribute("width", 0);
  cp.appendChild(cr); defs.appendChild(cp); svg.appendChild(defs);
  area.setAttribute("clip-path", `url(#${cid})`);
  svg.appendChild(area);
  const path = document.createElementNS(ns, "path");
  Object.entries({ d, fill: "none", stroke: c, "stroke-width": 12, "stroke-linecap": "round", "stroke-linejoin": "round" }).forEach(([k, v]) => path.setAttribute(k, v));
  svg.appendChild(path);
  const dot = document.createElementNS(ns, "circle"); dot.setAttribute("r", 20); dot.setAttribute("fill", c); svg.appendChild(dot);
  const labs = p.noktalar.map((pt, i) => {
    if (!(i === 0 || i === vals.length - 1 || pt[2])) return null;
    const t = document.createElementNS(ns, "text");
    Object.entries({ x: X(i), y: H + 40, "text-anchor": "middle", fill: "rgba(255,255,255,.7)", "font-size": 38, "font-weight": 800, "font-family": "M" }).forEach(([k, v]) => t.setAttribute(k, v));
    t.textContent = pt[0]; svg.appendChild(t); return { t, i };
  }).filter(Boolean);
  const tag = el("div", "h", "", r);
  Object.assign(tag.style, { position: "absolute", whiteSpace: "nowrap", fontSize: "64px", padding: "6px 22px", borderRadius: "18px", background: c, color: "#111" });
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "10px";
  let L = 0;
  return (lt, dd) => {
    if (!L) L = path.getTotalLength();
    if (title) slide(title, lt, 0, 0, 40);
    const x = eInOut(prog(lt, .2, Math.min(dd * .65, 3.2)));
    path.setAttribute("stroke-dasharray", `${L}`);
    path.setAttribute("stroke-dashoffset", `${L * (1 - x)}`);
    const pt = path.getPointAtLength(L * x);
    cr.setAttribute("width", pt.x);
    dot.setAttribute("cx", pt.x); dot.setAttribute("cy", pt.y);
    dot.setAttribute("r", 18 + 4 * Math.sin(lt * 6));
    // etiket değeri noktanın yatay konumundan: yol uzunluğu segmentlere eşit dağılmıyor
    const fi = clamp((pt.x - pad) / (W - 2 * pad)) * (vals.length - 1), i0 = Math.floor(fi), i1 = Math.min(i0 + 1, vals.length - 1);
    const v = lerp(vals[i0], vals[i1], fi - i0);
    tag.textContent = (p.onek || "") + fmt(v, p.ondalik ?? 0) + (p.sonek || "");
    const box = svg.getBoundingClientRect(), rb = r.getBoundingClientRect();
    const lx = box.left - rb.left + pt.x - tag.offsetWidth / 2;
    tag.style.left = clamp(lx, 0, r.clientWidth - tag.offsetWidth) + "px";
    tag.style.top = (box.top - rb.top + pt.y - 120) + "px";
    tag.style.opacity = clamp(prog(lt, .2, .2));
    labs.forEach(o => o.t.setAttribute("opacity", x >= o.i / (vals.length - 1) - 1e-6 ? 1 : 0));
    if (note) slide(note, lt, .4 + Math.min(dd * .65, 3.2));
  };
};

// Hesap: öğeler sırayla belirir, sonuç büyük ve parlak.
SCENES.hesap = (p, r) => {
  const title = p.baslik ? el("div", "h", md(p.baslik), r) : null;
  if (title) { fit(title, 64); title.style.marginBottom = "40px"; }
  const ic = p.ikon ? el("div", "emoji", p.ikon, r) : null;
  if (ic) { ic.style.fontSize = "170px"; ic.style.marginBottom = "30px"; }
  const items = p.ogeler.map((s, i) => {
    const last = i === p.ogeler.length - 1;
    const op = /^[×x+\-−=÷]$/.test(s);
    const e = el("div", "h", md(s), r);
    e.style.fontSize = last ? "170px" : (op ? "90px" : "100px");
    e.style.color = last ? "var(--sari)" : (op ? "var(--dim)" : "var(--ink)");
    e.style.margin = op ? "0" : "6px 0";
    if (last) e.style.textShadow = "0 0 60px rgba(255,200,61,.45)";
    return e;
  });
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "30px";
  return (lt, d) => {
    if (title) slide(title, lt, 0, 0, 40);
    if (ic) { pop(ic, lt, 0); ic.style.transform += ` translateY(${bob(lt, 10)}px)`; }
    items.forEach((e, i) => {
      pop(e, lt, stagger(i, items.length, d, .1, .6), .35, .5);
      if (i === items.length - 1 && lt > stagger(i, items.length, d, .1, .6) + .4)
        e.style.transform = `scale(${1 + .04 * Math.sin(lt * 5)})`;
    });
    if (note) slide(note, lt, d * .72);
  };
};

// Takvim yaprağı: son tarih, geri sayım hissi.
SCENES.takvim = (p, r) => {
  const cal = el("div", null, null, r);
  Object.assign(cal.style, { width: "600px", borderRadius: "44px", overflow: "hidden", background: "#fff", boxShadow: "0 30px 80px rgba(0,0,0,.45)" });
  const head = el("div", "h", md(p.ay), cal);
  Object.assign(head.style, { background: "var(--kirmizi)", color: "#fff", fontSize: "70px", padding: "26px 0" });
  const day = el("div", "h", p.gun, cal);
  Object.assign(day.style, { color: "#111", fontSize: "300px", lineHeight: "1.05", padding: "20px 0 0" });
  const wd = el("div", "h", md(p.gunadi || ""), cal);
  Object.assign(wd.style, { color: "#555", fontSize: "56px", paddingBottom: "36px" });
  const clk = p.saat ? el("div", "h", "⏰ " + p.saat, r) : null;
  if (clk) { clk.style.fontSize = "90px"; clk.style.marginTop = "44px"; clk.style.color = "var(--sari)"; clk.firstChild && (clk.innerHTML = `<span class="emoji">⏰</span> ${p.saat}`); }
  const note = p.not ? el("div", "note", md(p.not), r) : null;
  if (note) note.style.marginTop = "26px";
  return (lt, d) => {
    const x = prog(lt, 0, .5);
    cal.style.opacity = clamp(x * 3);
    cal.style.transform = `perspective(1400px) rotateX(${(1 - eBack(x)) * 70}deg) rotate(${bob(lt, 2.2, 2.6)}deg)`;
    if (clk) { pop(clk, lt, .35); clk.style.transform += ` rotate(${Math.sin(lt * 26) * (lt % 1.2 < .3 ? 4 : 0)}deg)`; }
    if (note) slide(note, lt, .6);
  };
};

// Kapanış: kanal adı + takip çağrısı. Parmak "tıklar".
SCENES.kapanis = (p, r) => {
  const ring = el("div", null, null, r);
  Object.assign(ring.style, { position: "absolute", width: "260px", height: "260px", borderRadius: "50%", border: "10px solid var(--sari)", top: "340px" });
  const hand = el("div", "emoji", "👆", r); hand.style.fontSize = "240px";
  const t1 = el("div", "h", md(p.metin || "TIKLA *BAKALIM*"), r); t1.style.fontSize = "120px"; t1.style.marginTop = "40px";
  const t2 = el("div", "note", md(p.alt || "Gündemi basitçe öğrenmek için takip et"), r); t2.style.marginTop = "30px";
  return (lt) => {
    pop(hand, lt, 0);
    const tap = (lt % 1.1) / 1.1;
    hand.style.transform += ` translateY(${tap < .2 ? -40 * Math.sin(tap / .2 * Math.PI) : 0}px)`;
    ring.style.opacity = tap < .15 ? 0 : (1 - tap) * .9;
    ring.style.transform = `scale(${.4 + tap * 1.2})`;
    pop(t1, lt, .2);
    slide(t2, lt, .45);
  };
};

// Kapak — sadece kapak.png için. Büyük, tek fikir.
// Dikey: tek sütun. Yatay (YouTube küçük resmi): solda yazı, sağda dev ikon.
SCENES.kapak = (p, r) => {
  const yatay = FORMAT === "yatay";
  if (yatay) Object.assign(r.style, { left: "70px", right: "70px", width: "auto", top: "60px", height: "960px",
    flexDirection: "row", justifyContent: "space-between", textAlign: "left", transform: "none" });
  else { r.style.top = "200px"; r.style.height = "1300px"; }
  const col = yatay ? el("div", null, null, r) : r;
  if (yatay) Object.assign(col.style, { display: "flex", flexDirection: "column", alignItems: "flex-start", width: "1150px" });
  const ic = p.ikon ? el("div", "emoji", p.ikon, yatay ? r : col) : null;
  if (ic) { ic.style.fontSize = yatay ? "560px" : "300px"; ic.style.marginBottom = yatay ? "0" : "30px";
    if (yatay) ic.style.filter = "drop-shadow(0 30px 60px rgba(0,0,0,.5))"; }
  const u = el("div", "h", md(p.ust || ""), col); fit(u, yatay ? 170 : 120, yatay ? 1150 : SCW);
  const b = el("div", "h", md(p.buyuk || ""), col);
  fit(b, yatay ? 300 : 250, yatay ? 1150 : SCW);
  Object.assign(b.style, { color: "var(--sari)", margin: "10px 0", textShadow: "0 0 80px rgba(255,200,61,.4)" });
  const a = el("div", "h", md(p.alt || ""), col);
  Object.assign(a.style, { fontSize: yatay ? "130px" : "110px", background: "var(--kirmizi)", padding: "10px 44px", borderRadius: "28px", marginTop: "20px" });
  const brand = el("div", "h", "TIKLA <span class='sari'>BAKALIM</span> <span class='emoji'>👆</span>", col);
  Object.assign(brand.style, { fontSize: yatay ? "50px" : "54px", marginTop: yatay ? "50px" : "80px", opacity: ".85" });
  return () => {};
};

// ---------- sahne kurulum + seek ----------
const SECTIONS = {
  ne: { i: 0, t: "1 · NE OLDU?" },
  neden: { i: 1, t: "2 · NEDEN OLDU?" },
  etki: { i: 2, t: "3 · BİZİ NASIL ETKİLER?" },
};
let TL = null, BUILT = [], WORDS = [], LINES = [], FORMAT = "dikey", W = 1080, H = 1920;
let SCALE = 1;          // sahne kutusunun ölçeği (yatayda 930 px yüksek kutu ekrana sığsın)

function background(stage) {
  const bg = el("div", null, null, stage);
  Object.assign(bg.style, { position: "absolute", inset: "0" });
  el("div", null, null, bg).id = "grid";
  const cols = ["#2b6cff", "#ffb020", "#ff3d6e", "#18c29c"];
  const blobs = cols.map((c, i) => {
    const b = el("div", "blob", null, bg);
    Object.assign(b.style, { width: "720px", height: "720px", background: c });
    return b;
  });
  return t => {
    blobs.forEach((b, i) => {
      const a = t * .11 + i * 1.7;
      const x = W / 2 - 360 + (W * .36) * Math.cos(a) + (i % 2 ? 1 : -1) * W * .1;
      const y = H / 2 - 360 + (H * .28) * Math.sin(a * 1.3 + i);
      b.style.transform = `translate(${x}px, ${y}px)`;
    });
    document.getElementById("grid").style.transform = `translateY(${(t * 18) % 120}px)`;
  };
}

// Geçişler — iki tür:
//  * sahne → sahne (aynı bölüm): çapraz çözülme. Eski sahne 0.35 sn boyunca hafif
//    bulanıklaşıp yukarı kayarak söner, yenisi aşağıdan belirir. Ses yok.
//  * bölüm → bölüm (ne / neden / etki): temiz bir bölüm kartı. Koyu panel soldan
//    kayar, ortada "2 · NEDEN OLDU?", ince altın çizgi; sonra sağa açılır.
//    Kullanıcı altın videosundaki kalın çapraz silmeyi "profesyonel değil" buldu.
const XF = .35;                       // çözülme süresi
const CARD = { in: .32, hold: .38, out: .32 };   // bölüm kartı: kapan / bekle / açıl
function sectionStarts() {
  const out = [];
  TL.scenes.forEach((s, i) => {
    if (SECTIONS[s.bolum] && (i === 0 || TL.scenes[i - 1].bolum !== s.bolum)) out.push({ t: s.t0, sec: SECTIONS[s.bolum] });
  });
  return out;
}
// Bölüm kartı ekranı tam t0 anında kaplar; sahne animasyonları kart açılınca başlar
const cardReveal = t0 => t0 + CARD.hold / 2 + CARD.out * .6;
function sectionCard(stage) {
  const box = el("div", null, null, stage); box.id = "seccard";
  const panel = el("div", "scpanel", null, box);
  const edge = el("div", "scedge", null, panel);
  const inner = el("div", "scinner", null, panel);
  const num = el("div", "scnum", "", inner);
  const ttl = el("div", "scttl", "", inner);
  const line = el("div", "scline", null, inner);
  const starts = () => (TL._ss ||= sectionStarts());
  return t => {
    box.style.display = "none";
    if (TL.gecis === false) return;
    for (const c of starts()) {
      const a = c.t - CARD.in - CARD.hold / 2, z = c.t + CARD.hold / 2 + CARD.out;
      if (t < a || t > z) continue;
      box.style.display = "block";
      const [n, ...rest] = c.sec.t.split(" · ");
      num.textContent = n; ttl.textContent = rest.join(" · ");
      const pin = eInOut(prog(t, a, CARD.in)), pout = eInOut(prog(t, c.t + CARD.hold / 2, CARD.out));
      // giriş: -100% → 0 ; çıkış: 0 → +100%
      const x = pout > 0 ? pout * 100 : (pin - 1) * 100;
      panel.style.transform = `translateX(${x}%)`;
      edge.style.left = pout > 0 ? "0" : "auto"; edge.style.right = pout > 0 ? "auto" : "0";
      const ti = prog(t, a + CARD.in * .6, .35);
      inner.style.opacity = clamp(ti * 1.6) * (1 - clamp(pout * 2.2));
      inner.style.transform = `translateX(${(1 - eOut(ti)) * -60 + pout * 60}px)`;
      line.style.transform = `scaleX(${eOut(prog(t, a + CARD.in, .45))})`;
    }
  };
}

// Yatay altyazı: satır satır, konuşulan kelime altın (altın videosundaki gibi)
function buildLines() {
  let cur = [];
  const flush = () => { if (cur.length) { LINES.push(cur); cur = []; } };
  for (const w of WORDS) {
    if (cur.length && w.p !== cur[0].p) flush();
    cur.push(w);
    const len = cur.map(x => x.w).join(" ").length;
    const end = /[.?!;:]$/.test(w.w), comma = /,$/.test(w.w);
    if (len >= 42 || (end && len >= 10) || (comma && len >= 26)) flush();
  }
  flush();
}
let LINE_I = -1;
function lineCaption(t) {
  const box = document.getElementById("capline");
  let li = -1;
  for (let i = 0; i < LINES.length; i++) if (t >= LINES[i][0].s - .08) li = i;
  if (li < 0 || t > LINES[li][LINES[li].length - 1].e + .6) { box.style.opacity = 0; return; }
  const L = LINES[li];
  if (li !== LINE_I) {
    box.innerHTML = L.map(w => `<span>${w.w.replace(/</g, "&lt;")}</span>`).join(" ");
    LINE_I = li;
  }
  box.style.opacity = li === 0 ? 1 : clamp((t - (L[0].s - .08)) / .1);
  [...box.children].forEach((sp, i) => {
    const w = L[i];
    const active = t >= w.s - .03 && (i === L.length - 1 ? t < w.e + .4 : t < L[i + 1].s - .03);
    sp.className = active ? "on" : t >= w.s ? "done" : "";
  });
}

// Dikey altyazı: tek kelime, büyük, konturlu
function wordCaption(t) {
  const cap = document.querySelector("#cap span");
  const w = WORDS.find(w => t >= w.s && t < w.e);
  if (!w) { cap.style.opacity = 0; return; }
  cap.textContent = w.w.replace(/[.,!?;:…"]+$/, "").replace(/^["(]+/, "");
  cap.style.color = { yellow: "var(--sari)", red: "var(--kirmizi)", green: "var(--yesil)" }[w.c] || "#fff";
  cap.style.transform = `scale(${lerp(.75, 1, eOut(prog(t, w.s, .09)))})`;
  cap.style.opacity = 1;
  cap.style.fontSize = "96px";
  if (cap.scrollWidth > 1000) cap.style.fontSize = (96 * 1000 / cap.scrollWidth) + "px";
}

// Abone ol / beğen çağrısı — YouTube tarzı alt bant kartı. Kanal simgesi + adı,
// "Abone ol" butonu, zil, beğen. Gerçek fare imleci butona gider ve tıklar
// (dalga), buton "Abone olundu"ya döner, zil sallanır; sonra beğen maviye
// dolar, küçük parçacıklar saçılır. İnce bir ok kendini çizerek aşağıyı —
// oynatıcının altındaki gerçek butonları — gösterir.
// Tıklama anları render.py'den (tl.cta[].abone / .begen); tık sesi aynı ana oturur.
const ICON = {
  bell: "M12 22a2.4 2.4 0 0 0 2.4-2.2H9.6A2.4 2.4 0 0 0 12 22zm6.5-6.2V11a6.5 6.5 0 0 0-4.9-6.3V4a1.6 1.6 0 0 0-3.2 0v.7A6.5 6.5 0 0 0 5.5 11v4.8L3.8 17.5v.9h16.4v-.9z",
  like: "M2 20.5h3.6V9.3H2zM21.6 11a2 2 0 0 0-2-2h-6.2l.9-4.4v-.3a1.5 1.5 0 0 0-.4-1L13 2.5 7 8.5a1.9 1.9 0 0 0-.6 1.4v9a2 2 0 0 0 2 2h8.5a2 2 0 0 0 1.8-1.2l2.8-6.6a2 2 0 0 0 .1-.7z",
  check: "M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z",
  cursor: "M3 2 3 25 9.2 19.3 13.2 28.4 17.3 26.6 13.3 17.7 21.6 17.7z",
};
const svgIcon = (d, cls, vb = "0 0 24 24") =>
  `<svg class="${cls}" viewBox="${vb}"><path d="${d}"/></svg>`;
function ctaLayer(stage) {
  const box = el("div", null, null, stage); box.id = "cta";
  const card = el("div", "ctacard", null, box);
  el("div", "ctaava", "<span class='emoji'>👆</span>", card);
  el("div", "ctameta", "<b>Tıkla Bakalım</b><span>Gündemi basitçe öğren</span>", card);
  const sub = el("div", "ctasub", "<span class='t1'>Abone ol</span><span class='t2'>" + svgIcon(ICON.check, "ic") + "Abone olundu</span>", card);
  const ripple = el("div", "ctaripple", null, sub);
  const bell = el("div", "ctaicon bell", svgIcon(ICON.bell, "ic"), card);
  const like = el("div", "ctaicon like", svgIcon(ICON.like, "ic"), card);
  const parts = [...Array(8)].map(() => el("i", "ctapart", null, like));
  const ns = "http://www.w3.org/2000/svg";
  const arr = document.createElementNS(ns, "svg"); arr.setAttribute("class", "ctaarrow"); arr.setAttribute("viewBox", "0 0 60 170");
  const ap = document.createElementNS(ns, "path"); ap.setAttribute("d", "M30 4 C 30 60, 30 110, 30 150 M 14 134 L 30 152 L 46 134");
  arr.appendChild(ap); box.appendChild(arr);
  const hint = el("div", "ctahint", "Butonlar videonun hemen altında", box);
  const cur = el("div", "ctacursor", svgIcon(ICON.cursor, "ic", "0 0 24 30"), box);
  let AL = 0;
  const center = e => { const r = e.getBoundingClientRect(), b = box.getBoundingClientRect();
    return [r.left - b.left + r.width * .5, r.top - b.top + r.height * .55]; };
  return t => {
    const c = (TL.cta || []).find(c => t >= c.t0 && t < c.t1);
    box.style.display = c ? "block" : "none";
    if (!c) return;
    const lt = t - c.t0, D = c.t1 - c.t0, A = c.abone - c.t0, B = c.begen - c.t0;
    const inn = eOut(prog(lt, 0, .5)), out = eInOut(prog(lt, D - .5, .45));
    card.style.opacity = clamp(inn * 1.5) * (1 - out);
    card.style.transform = `translateY(${(1 - inn) * 40 + out * 40}px) scale(${lerp(.96, 1, inn)})`;
    // abone
    const subDone = lt >= A;
    sub.classList.toggle("done", subDone);
    const pa = prog(lt, A, .5);
    ripple.style.opacity = subDone ? (1 - pa) * .6 : 0;
    ripple.style.transform = `translate(-50%,-50%) scale(${eOut(pa) * 3})`;
    sub.style.transform = `scale(${lt >= A && lt < A + .12 ? .94 : 1})`;
    // zil: tıklamadan sonra sönümlenen sallanma
    const rb = lt - A - .15;
    bell.classList.toggle("on", lt >= A + .15);
    bell.firstChild.style.transform = rb > 0 ? `rotate(${Math.sin(rb * 22) * 18 * Math.exp(-rb * 3.2)}deg)` : "none";
    // beğen
    const likeDone = lt >= B, pb = prog(lt, B, .45);
    like.classList.toggle("on", likeDone);
    like.firstChild.style.transform = `scale(${likeDone ? lerp(1.35, 1, eOut(pb)) : (lt >= B - .1 && lt < B ? .9 : 1)})`;
    parts.forEach((p, i) => {
      const a = i / parts.length * Math.PI * 2, r = 12 + 34 * eOut(pb);
      p.style.opacity = likeDone ? (1 - pb) : 0;
      p.style.transform = `translate(${Math.cos(a) * r}px, ${Math.sin(a) * r}px)`;
    });
    // imleç: karta girer → abone → beğen → çıkar
    const pS = center(sub), pL = center(like), pOut = [pL[0] + 160, pL[1] + 140], pIn = [pS[0] + 220, pS[1] + 170];
    let pos;
    if (lt < A) pos = [lerp(pIn[0], pS[0], eInOut(prog(lt, A - .75, .6))), lerp(pIn[1], pS[1], eInOut(prog(lt, A - .75, .6)))];
    else if (lt < B) { const m = eInOut(prog(lt, A + .25, B - A - .4)); pos = [lerp(pS[0], pL[0], m), lerp(pS[1], pL[1], m)]; }
    else { const m = eInOut(prog(lt, B + .35, .5)); pos = [lerp(pL[0], pOut[0], m), lerp(pL[1], pOut[1], m)]; }
    const press = (lt >= A && lt < A + .12) || (lt >= B && lt < B + .12);
    cur.style.opacity = clamp(prog(lt, A - .8, .25)) * (1 - clamp(prog(lt, B + .45, .35)));
    cur.style.transform = `translate(${pos[0]}px, ${pos[1]}px) scale(${press ? .85 : 1})`;
    // ok + ipucu: beğenden sonra kendini çizer
    if (!AL) AL = ap.getTotalLength();
    const pd = eOut(prog(lt, B + .3, .6));
    ap.style.strokeDasharray = AL; ap.style.strokeDashoffset = AL * (1 - pd);
    arr.style.opacity = (pd > 0 ? 1 : 0) * (1 - out);
    arr.style.transform = `translateY(${Math.sin(lt * 3.5) * 6}px)`;
    hint.style.opacity = clamp(prog(lt, B + .6, .35)) * (1 - out);
  };
}

let BG = null, CARDFX = null, CTA = null;
window.load = async function (tl, opts = {}) {
  // Fontlar yüklenmeden ölçüm yapılırsa sığdırma yedek fonta göre hesaplanır
  await Promise.all([600, 800, 900].map(w => document.fonts.load(`${w} 60px M`, "AaŞşĞğİıÇçÖöÜü₺0123")));
  TL = tl;
  FORMAT = tl.format === "yatay" ? "yatay" : "dikey";
  [W, H] = FORMAT === "yatay" ? [1920, 1080] : [1080, 1920];
  SCW = FORMAT === "yatay" ? 1300 : 940;
  SCALE = FORMAT === "yatay" ? .84 : 1;
  document.documentElement.classList.add(FORMAT);
  const stage = document.getElementById("stage");
  BG = background(stage);
  stage.appendChild(document.getElementById("top"));
  const root = el("div", null, null, stage);
  BUILT = tl.scenes.map(s => {
    const r = el("div", "scene", null, root);
    const fn = SCENES[s.tip];
    if (!fn) throw new Error("bilinmeyen sahne tipi: " + s.tip);
    return { s, r, up: fn(s.p || {}, r, s) };
  });
  for (const id of ["cap", "capline", "tag", "src", "bar"]) stage.appendChild(document.getElementById(id));
  CTA = ctaLayer(stage);
  CARDFX = sectionCard(stage);
  WORDS = tl.words || [];
  if (FORMAT === "yatay") buildLines();
  if (opts.cover) stage.classList.add("cover");
  return document.fonts.ready.then(() => true);
};

window.seek = function (t) {
  BG(t);
  let cur = null;
  const last = TL.scenes[TL.scenes.length - 1];
  const starts = (TL._ss ||= sectionStarts()).map(c => c.t);
  BUILT.forEach((b, i) => {
    const { t0, t1 } = b.s;
    const secStart = starts.includes(t0) && i > 0;
    // sahne biraz uzar: çıkarken XF sn boyunca söner (bölüm kartında gerek yok)
    const nextSec = i + 1 < BUILT.length && starts.includes(BUILT[i + 1].s.t0);
    const tail = b.s === last || nextSec ? 0 : XF;
    const on = t >= t0 && (t < t1 + tail || b.s === last);
    b.r.classList.toggle("on", on);
    if (!on) return;
    if (t < t1 || b.s === last) cur = b;
    if (!b.fitted) { b.r.querySelectorAll("[data-fit]").forEach(e => fitNow(e, +e.dataset.fit, +e.dataset.fitw)); b.fitted = true; }
    // İlk sahne boş ekranla açılmasın; bölüm başı sahnesi kart açılınca başlasın
    const start = i === 0 ? t0 - .3 : secStart ? cardReveal(t0) : t0;
    const d = t1 - start;
    b.up(Math.max(0, t - start), d);
    const z = 1 + .03 * eInOut(clamp((t - t0) / Math.max(1, t1 - t0)));
    if (b.s.tip === "kapak") return;
    // eski sahne önce söner (0.22 sn), yenisi 0.08 sn sonra gelir — iki sahne üst üste okunmasın
    const fin = secStart || i === 0 ? 1 : eOut(prog(t, t0 + .08, XF - .03));   // giriş
    const fo = t >= t1 && tail ? eInOut(prog(t, t1, .22)) : 0;           // çıkış
    b.r.style.zIndex = fo > 0 ? 1 : 2;
    b.r.style.opacity = fin * (1 - fo);
    b.r.style.filter = fo > 0 ? `blur(${fo * 10}px)` : fin < 1 ? `blur(${(1 - fin) * 6}px)` : "none";
    b.r.style.transform = `translateY(${(1 - fin) * 26 - fo * 30}px) scale(${SCALE * z * (1 - .03 * fo)})`;
  });
  // Bölüm şeridi
  const sec = cur && SECTIONS[cur.s.bolum];
  const top = document.getElementById("top");
  top.style.opacity = sec ? 1 : 0;
  if (sec) {
    const chip = document.getElementById("chip");
    chip.textContent = sec.t;
    const first = TL.scenes.find(s => s.bolum === cur.s.bolum);
    const x = prog(t - first.t0, 0, .35);
    chip.style.transform = `scale(${lerp(.6, 1, eBack(x))})`;
    const secs = TL.scenes.filter(s => s.bolum === cur.s.bolum);
    const s0 = secs[0].t0, s1 = secs[secs.length - 1].t1;
    document.querySelectorAll("#prog b").forEach((b, i) => {
      b.style.width = (i < sec.i ? 100 : i > sec.i ? 0 : 100 * clamp((t - s0) / (s1 - s0))) + "%";
    });
  }
  // Sahne etiketi (sağ üst, yatay) ve alt ilerleme çubuğu
  const tag = document.getElementById("tag");
  tag.textContent = cur && cur.s.etiket ? cur.s.etiket : "";
  tag.style.opacity = cur && cur.s.etiket ? 1 : 0;
  document.querySelector("#bar b").style.width = (100 * clamp(t / TL.dur)) + "%";
  if (FORMAT === "yatay") lineCaption(t); else wordCaption(t);
  document.getElementById("src").textContent = cur && cur.s.kaynak ? "Kaynak: " + cur.s.kaynak : "";
  CTA(t);
  CARDFX(t);
};
