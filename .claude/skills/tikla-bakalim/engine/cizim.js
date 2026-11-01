// Teknik çizim (blueprint) modu — "nasıl çalışır?" videoları için.
// bolum.json: "stil": "cizim", "dunya": "baraj". Sahneler tip "cizim":
//   p.kamera  [cx, cy, zoom]   dünyada bakılan nokta (zoom = ekran px / dünya birimi)
//   p.kamera2 [cx, cy, zoom]   (isteğe bağlı) sahne boyunca buraya kayar
//   p.adim    N                N'e kadarki çizim adımları görünür; yeni adımlar kendini çizer
//   p.baslik / p.alt / p.buyuk ekran üstü yazı (ortada üstte)
// Tek bir dünya çizilir, sahneler arasında kesme yok: kamera bir sonraki noktaya akar.
// Deterministik: her şey t'den hesaplanır.

const CZ = {
  ink: "#dbe7ff", dim: "rgba(219,231,255,.35)", su: "#5fb4ff", suF: "rgba(95,180,255,.16)",
  tur: "#4fe0d2", sari: "#ffc83d", kir: "#ff5a6e", mav: "#5b8cff", glow: "rgba(255,200,61,.85)",
};
const CZ_DRAW = 1.1;   // bir öğenin kendini çizme süresi (sn)

window.buildWorld = function (stage, tl) {
  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  Object.assign(svg.style, { position: "absolute", inset: "0", width: W + "px", height: H + "px" });
  stage.appendChild(svg);
  const cam = document.createElementNS(NS, "g");
  svg.appendChild(cam);
  const REG = [];
  const S = (tag, a, par) => { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); (par || cam).appendChild(e); return e; };
  // mk: dünyaya öğe ekle. kind: stroke (kendini çizer) | fill (belirir) | label | flow | pulse | custom
  const mk = (tag, a, step, kind = "stroke", o = {}) => {
    const base = kind === "stroke" ? { fill: "none", stroke: CZ.ink, "stroke-width": 2.6, "stroke-linecap": "round", "stroke-linejoin": "round" } : {};
    const e = S(tag, { ...base, ...a }, o.par);
    REG.push({ e, step, kind, delay: o.delay || 0, dur: o.dur || CZ_DRAW });
    return e;
  };
  // adım → başlangıç zamanı (o adımı ilk gösteren sahnenin başı)
  const cz = tl.scenes.filter(s => s.tip === "cizim");
  const stepT = k => { const s = cz.find(s => (s.p.adim || 0) >= k); return s ? s.t0 : 1e9; };
  const W0 = (window.WORLDS[tl.dunya || "baraj"])(mk, S, stepT);
  REG.forEach(r => {
    r.t = stepT(r.step) + r.delay;
    if (r.kind === "stroke" && r.e.getTotalLength) {
      r.len = r.e.getTotalLength() + 2;
      r.e.style.strokeDasharray = r.len;
    }
  });
  // kamera yolu
  const camAt = t => {
    let i = 0;
    for (let k = 0; k < cz.length; k++) if (t >= cz[k].t0) i = k;
    const s = cz[i], d = s.t1 - s.t0;
    const prev = i > 0 ? (cz[i - 1].p.kamera2 || cz[i - 1].p.kamera) : s.p.kamera;
    const a = s.p.kamera, b = s.p.kamera2;
    const mv = Math.min(1.5, Math.max(.6, d * .45));
    const lc = (p, q, u) => [lerp(p[0], q[0], u), lerp(p[1], q[1], u), Math.exp(lerp(Math.log(p[2]), Math.log(q[2]), u))];
    let c = lc(prev, a, eInOut(clamp((t - s.t0) / mv)));
    if (b) c = lc(c, b, eInOut(clamp((t - s.t0 - mv) / Math.max(.5, d - mv))));
    // hafif nefes: kamera hiç tam durmaz
    c[0] += 6 * Math.sin(t * .5); c[1] += 4 * Math.sin(t * .37);
    return c;
  };
  const CY = FORMAT === "yatay" ? 470 : 820;
  return t => {
    const [cx, cy, z] = camAt(t);
    cam.setAttribute("transform", `translate(${W / 2 - cx * z} ${CY - cy * z}) scale(${z})`);
    REG.forEach(r => {
      const u = clamp((t - r.t) / r.dur);
      if (r.kind === "stroke") {
        r.e.style.opacity = u > 0 ? 1 : 0;
        if (r.len) r.e.style.strokeDashoffset = r.len * (1 - eInOut(u));
      } else if (r.kind === "fill") r.e.style.opacity = eOut(u) * (+r.e.dataset.op || 1);
      else if (r.kind === "label") {
        r.e.style.opacity = eOut(u);
        r.e.style.transform = `translateY(${(1 - eOut(u)) * 12}px)`;
      }
    });
    W0(t);
  };
};

window.WORLDS = {};

// ---------------- Dünya: baraj → türbin → jeneratör → trafo → hat → ev ----------------
// Adımlar: 1 dağ+baraj+rezervuar · 2 ev · 3 baraj etiketleri · 4 su yükselir · 5 yükseklik=enerji
// 6 cebri boru · 7 kapak açılır, su akar · 8 santral+türbin · 9 türbin döner · 10 mil+jeneratör
// 11 jeneratör içi (mıknatıs/bobin) · 13 trafo · 14 nakil hattı · 15 indirici trafo + ev ışığı · 16 nehre dönüş
WORLDS.baraj = (mk, S, stepT) => {
  const G = 1000;                                  // zemin
  const lbl = (x, y, tx, ty, text, step, o = {}) => {
    const g = mk("g", {}, step, "label", { delay: o.delay || 0, dur: .5 });
    S("path", { d: `M${x} ${y} L${tx} ${ty} H${tx + (o.sol ? -1 : 1) * (o.w || 150)}`, fill: "none", stroke: o.renk || CZ.tur, "stroke-width": 2 }, g);
    S("circle", { cx: x, cy: y, r: 5, fill: o.renk || CZ.tur }, g);
    const tx2 = tx + (o.sol ? -1 : 1) * 6;
    const te = S("text", { x: tx2, y: ty - 12, fill: o.renk || CZ.tur, "font-family": "Montserrat, sans-serif", "font-weight": 800,
      "font-size": o.boy || 26, "letter-spacing": 2, "text-anchor": o.sol ? "end" : "start" }, g);
    te.textContent = text;
    return g;
  };
  // --- 1: dağlar, zemin, rezervuar, baraj
  mk("polyline", { points: "0,1000 0,560 170,430 320,520 470,370 640,490 800,420 960,540 1120,470 1140,480", stroke: CZ.dim }, 1);
  mk("path", { d: `M1140 ${G} H3400` }, 1, "stroke", { delay: .2 });
  for (let x = 1480; x < 3400; x += 60) mk("path", { d: `M${x} ${G} l-22 22`, stroke: CZ.dim, "stroke-width": 1.6 }, 1, "stroke", { delay: .5 });
  const water = mk("polygon", { points: "", fill: CZ.suF, stroke: "none" }, 1, "fill", { delay: .6 });
  const surf = mk("path", { d: "", stroke: CZ.su, "stroke-width": 3, fill: "none" }, 1, "fill", { delay: .6 });
  const waves = [0, 1, 2].map(i => mk("path", { d: "", stroke: CZ.su, "stroke-width": 2, fill: "none", opacity: .6 }, 1, "fill", { delay: .8 }));
  // baraj gövdesi (ağırlık barajı kesiti)
  mk("polygon", { points: `1140,460 1232,460 1470,${G} 1140,${G}`, "stroke-width": 3.2 }, 1, "stroke", { delay: .1 });
  for (let k = 0; k < 9; k++) {
    const y = 520 + k * 55;
    mk("path", { d: `M1146 ${y} l${Math.min(40 + k * 26, 300)} 0`, stroke: CZ.dim, "stroke-width": 1.4 }, 1, "stroke", { delay: .7 + k * .04 });
  }
  mk("path", { d: `M1100 ${G + 30} H1520`, stroke: CZ.dim, "stroke-dasharray": "10 8" }, 1, "fill", { delay: .9 });
  // --- 2: ev (sağda, ışıklar 15'te yanar)
  mk("polygon", { points: `3200,${G} 3200,860 3360,860 3360,${G}` }, 2);
  mk("polyline", { points: "3182,862 3280,782 3378,862" }, 2, "stroke", { delay: .2 });
  const win = [[3222, 890], [3302, 890]].map(([x, y], i) => {
    mk("rect", { x, y, width: 40, height: 40 }, 2, "stroke", { delay: .4 + i * .1 });
    return S("rect", { x: x + 2, y: y + 2, width: 36, height: 36, fill: CZ.sari, opacity: 0 });
  });
  mk("rect", { x: 3266, y: 940, width: 28, height: 60 }, 2, "stroke", { delay: .5 });
  const lamp = S("circle", { cx: 3280, cy: 760, r: 120, fill: "url(#czglow)", opacity: 0 });
  // --- 3: etiketler
  lbl(1200, 640, 1300, 520, "BARAJ", 3);
  lbl(560, 860, 470, 700, "REZERVUAR", 3, { delay: .4, sol: true, w: 190 });
  // --- 5: yükseklik = enerji ölçü çizgisi
  const dimG = mk("g", {}, 5, "label", { dur: .6 });
  S("path", { d: `M1050 560 V${G} M1030 560 H1070 M1030 ${G} H1070`, stroke: CZ.sari, "stroke-width": 2.5, fill: "none" }, dimG);
  S("path", { d: `M1040 580 L1050 560 L1060 580 M1040 ${G - 20} L1050 ${G} L1060 ${G - 20}`, stroke: CZ.sari, "stroke-width": 2.5, fill: "none" }, dimG);
  const dt = S("text", { x: 1030, y: 790, fill: CZ.sari, "font-family": "Montserrat, sans-serif", "font-weight": 800, "font-size": 30, "text-anchor": "end" }, dimG);
  dt.textContent = "YÜKSEKLİK = ENERJİ";
  // --- 6: cebri boru + giriş kapağı
  const pc = "M1150 830 L1300 905 L1520 1090";
  mk("path", { d: "M1150 812 L1306 890 L1528 1077" }, 6);
  mk("path", { d: "M1150 848 L1294 920 L1512 1103" }, 6, "stroke", { delay: .1 });
  mk("rect", { x: 1112, y: 800, width: 30, height: 60 }, 6, "stroke", { delay: .3 });
  const gate = S("rect", { x: 1116, y: 804, width: 22, height: 52, fill: CZ.kir, opacity: 0 });
  lbl(1330, 912, 1390, 790, "CEBRİ BORU", 6, { delay: .6 });
  // --- 7: su akışı
  const flow = S("path", { d: pc, fill: "none", stroke: CZ.su, "stroke-width": 14, "stroke-dasharray": "26 30", "stroke-linecap": "round", opacity: 0 });
  // --- 8: santral binası + türbin
  mk("polyline", { points: `1470,${G} 1470,880 1810,880 1810,1190 1470,1190 1470,${G}` }, 8);
  mk("path", { d: "M1450 880 H1830", "stroke-width": 4 }, 8, "stroke", { delay: .2 });
  mk("circle", { cx: 1560, cy: 1110, r: 78, stroke: CZ.dim, "stroke-dasharray": "8 8" }, 8, "stroke", { delay: .3 });
  const turb = S("g", { opacity: 0 });
  S("circle", { cx: 0, cy: 0, r: 58, fill: "none", stroke: CZ.ink, "stroke-width": 3 }, turb);
  S("circle", { cx: 0, cy: 0, r: 14, fill: CZ.ink }, turb);
  for (let k = 0; k < 8; k++) {
    const a = k * Math.PI / 4;
    S("path", { d: `M${14 * Math.cos(a)} ${14 * Math.sin(a)} Q ${40 * Math.cos(a + .5)} ${40 * Math.sin(a + .5)} ${56 * Math.cos(a + .25)} ${56 * Math.sin(a + .25)}`,
      fill: "none", stroke: CZ.ink, "stroke-width": 3 }, turb);
  }
  lbl(1610, 1150, 1690, 1250, "TÜRBİN", 8, { delay: .7 });
  // --- 10: mil + jeneratör
  mk("path", { d: "M1560 1052 V962", "stroke-width": 6 }, 10);
  mk("rect", { x: 1500, y: 900, width: 120, height: 62, rx: 6, "stroke-width": 3 }, 10, "stroke", { delay: .2 });
  const rotor = S("g", { opacity: 0 });
  S("circle", { r: 20, fill: "none", stroke: CZ.ink, "stroke-width": 2.5 }, rotor);
  S("path", { d: "M0 -20 V20", stroke: CZ.kir, "stroke-width": 5 }, rotor);
  lbl(1620, 920, 1700, 830, "JENERATÖR", 10, { delay: .6 });
  // --- 11: jeneratörün içi (büyüteç dairesi)
  const det = mk("g", {}, 11, "label", { dur: .6 });
  S("path", { d: "M1560 900 V712", stroke: CZ.tur, "stroke-width": 2, "stroke-dasharray": "6 6", fill: "none" }, det);
  S("circle", { cx: 1560, cy: 560, r: 152, fill: "rgba(10,22,44,.92)", stroke: CZ.tur, "stroke-width": 3 }, det);
  // stator bobinleri (sol/sağ)
  for (const sx of [-1, 1]) {
    S("path", { d: `M${1560 + sx * 118} 470 A 120 120 0 0 ${sx > 0 ? 1 : 0} ${1560 + sx * 118} 650`, fill: "none", stroke: "#e0975a", "stroke-width": 16, opacity: .9 }, det);
    for (let k = 0; k < 7; k++) {
      const a = (-.62 + k * .2) * (sx > 0 ? 1 : -1) + (sx > 0 ? 0 : Math.PI);
      S("path", { d: `M${1560 + 104 * Math.cos(a)} ${560 + 104 * Math.sin(a)} L${1560 + 132 * Math.cos(a)} ${560 + 132 * Math.sin(a)}`, stroke: "#8a4a20", "stroke-width": 3 }, det);
    }
  }
  const mag = S("g", {}, det);
  S("rect", { x: -70, y: -24, width: 70, height: 48, fill: CZ.kir }, mag);
  S("rect", { x: 0, y: -24, width: 70, height: 48, fill: CZ.mav }, mag);
  const tN = S("text", { x: -35, y: 11, fill: "#fff", "font-family": "Montserrat", "font-weight": 900, "font-size": 30, "text-anchor": "middle" }, mag); tN.textContent = "N";
  const tS = S("text", { x: 35, y: 11, fill: "#fff", "font-family": "Montserrat", "font-weight": 900, "font-size": 30, "text-anchor": "middle" }, mag); tS.textContent = "S";
  const wire = S("path", { d: "M1680 488 C 1760 470 1780 560 1860 560", fill: "none", stroke: "#e0975a", "stroke-width": 5 }, det);
  const elec = [0, 1, 2, 3, 4].map(() => S("circle", { r: 7, fill: CZ.sari, opacity: 0 }, det));
  const tm = S("text", { x: 1560, y: 380, fill: CZ.tur, "font-family": "Montserrat", "font-weight": 800, "font-size": 24, "text-anchor": "middle", "letter-spacing": 2 }, det);
  tm.textContent = "MIKNATIS + BOBİN = AKIM";
  // --- 13: yükseltici trafo
  mk("rect", { x: 1870, y: 900, width: 100, height: 100, rx: 6 }, 13);
  mk("circle", { cx: 1906, cy: 950, r: 24 }, 13, "stroke", { delay: .2 });
  mk("circle", { cx: 1934, cy: 950, r: 24 }, 13, "stroke", { delay: .3 });
  const w1 = "M1620 930 H1870";
  mk("path", { d: w1, stroke: CZ.sari, "stroke-width": 2 }, 13, "stroke", { delay: .3 });
  lbl(1960, 905, 2010, 820, "TRAFO · GERİLİM ↑", 13, { delay: .6, w: 270 });
  // --- 14: enerji nakil hattı (direkler + teller)
  const tower = (x, d) => {
    mk("path", { d: `M${x - 44} ${G} L${x - 9} 640 M${x + 44} ${G} L${x + 9} 640 M${x - 9} 640 L${x} 600 L${x + 9} 640` }, 14, "stroke", { delay: d });
    let z = "";
    for (let k = 0; k < 6; k++) {
      const y1 = G - k * 60, y2 = y1 - 60, w1_ = 44 - k * 5.8, w2_ = 44 - (k + 1) * 5.8;
      z += `M${x - w1_} ${y1} L${x + w2_} ${y2} M${x + w1_} ${y1} L${x - w2_} ${y2} `;
    }
    mk("path", { d: z, "stroke-width": 1.6, stroke: CZ.dim }, 14, "stroke", { delay: d + .2 });
    mk("path", { d: `M${x - 70} 680 H${x + 70}`, "stroke-width": 3 }, 14, "stroke", { delay: d + .3 });
  };
  [2160, 2560, 2960].forEach((x, i) => tower(x, i * .35));
  const line = "M1970 920 Q2050 760 2090 680 Q2360 760 2630 680 Q2760 740 2890 680 Q2960 720 3030 680 Q3070 820 3120 940";
  mk("path", { d: "M1970 920 Q2050 760 2090 680 Q2360 760 2630 680", stroke: CZ.ink, "stroke-width": 2 }, 14, "stroke", { delay: .5 });
  mk("path", { d: "M2230 680 Q2360 744 2490 680 M2630 680 Q2760 744 2890 680", stroke: CZ.ink, "stroke-width": 2 }, 14, "stroke", { delay: .8 });
  lbl(2560, 600, 2620, 520, "ENERJİ NAKİL HATTI", 14, { delay: 1, w: 300 });
  // --- 15: indirici trafo + eve bağlantı
  mk("path", { d: "M3030 680 Q3070 820 3110 930" , "stroke-width": 2 }, 15);
  mk("rect", { x: 3090, y: 930, width: 60, height: 70, rx: 4 }, 15, "stroke", { delay: .2 });
  mk("path", { d: "M3150 950 H3200", stroke: CZ.sari, "stroke-width": 2 }, 15, "stroke", { delay: .4 });
  lbl(3120, 930, 3040, 1080, "GERİLİM ↓", 15, { delay: .5, sol: true, w: 170 });
  // --- 16: nehre dönüş
  mk("path", { d: `M1810 1150 H1900 Q1960 1150 1990 1060 L2020 ${G}` }, 16);
  const river = S("path", { d: `M1660 1150 H1900 Q1960 1150 1990 1060 L2040 1030 H2400`, fill: "none", stroke: CZ.su, "stroke-width": 12, "stroke-dasharray": "22 26", opacity: 0, "stroke-linecap": "round" });
  lbl(2200, 1030, 2260, 1130, "NEHRE DÖNÜŞ", 16, { delay: .5, w: 210 });
  // ışıma tanımı
  const defs = S("defs", {});
  defs.innerHTML = `<radialGradient id="czglow"><stop offset="0" stop-color="#ffd75e" stop-opacity=".55"/><stop offset="1" stop-color="#ffd75e" stop-opacity="0"/></radialGradient>`;
  // elektrik darbeleri (sarı noktalar) yol boyunca
  const pulsePath = S("path", { d: w1 + " " + line.replace(/^M1970 920/, "L1970 920"), fill: "none", stroke: "none" });
  const PL = pulsePath.getTotalLength();
  const pulses = Array.from({ length: 14 }, () => S("circle", { r: 7, fill: CZ.sari, opacity: 0, filter: "drop-shadow(0 0 6px #ffc83d)" }));
  const T = k => stepT(k);
  const wireL = wire.getTotalLength();
  return t => {
    // su seviyesi: adım 4'te yükselir
    const lv = lerp(740, 560, eInOut(clamp((t - T(4)) / 2.2)));
    water.setAttribute("points", `0,${lv} 1140,${lv} 1140,${G} 0,${G}`);
    surf.setAttribute("d", `M0 ${lv} H1140`);
    waves.forEach((w, i) => {
      let d = "";
      for (let x = 20; x <= 1120; x += 20) d += (x === 20 ? "M" : "L") + x + " " + (lv + 26 + i * 36 + 5 * Math.sin(x / 40 + t * 2 + i * 1.7)).toFixed(1) + " ";
      w.setAttribute("d", d);
    });
    // kapak (7'de kalkar), akış
    const g7 = eInOut(clamp((t - T(7)) / .6));
    gate.style.opacity = t >= T(6) + .3 ? 1 : 0;
    gate.setAttribute("y", 804 - 56 * g7);
    flow.style.opacity = clamp((t - T(7) - .4) / .4) * .9;
    flow.style.strokeDashoffset = -(t * 240);
    // türbin + rotor: 9'da dönmeye başlar
    turb.style.opacity = clamp((t - T(8) - .4) / .5);
    const tau = Math.max(0, t - T(9)), wv = 380;
    const ang = tau < 1.6 ? wv * tau * tau / 3.2 : wv * (tau - .8);
    turb.setAttribute("transform", `translate(1560 1110) rotate(${ang})`);
    rotor.style.opacity = clamp((t - T(10) - .3) / .4);
    rotor.setAttribute("transform", `translate(1560 931) rotate(${ang})`);
    mag.setAttribute("transform", `translate(1560 560) rotate(${t >= T(11) ? ang * .5 : 0})`);
    elec.forEach((e, i) => {
      const u = ((t - T(11)) * .55 + i / elec.length) % 1;
      if (t < T(11) + .6) { e.style.opacity = 0; return; }
      const p = wire.getPointAtLength(u * wireL);
      e.setAttribute("cx", p.x); e.setAttribute("cy", p.y); e.style.opacity = 1;
    });
    // elektrik darbeleri: 13'te trafoya, 14'te hatta
    const reach = t < T(13) + .8 ? 0 : t < T(14) + 1 ? 250 : PL;
    pulses.forEach((c, i) => {
      const s = ((t * 300) + i * (PL / pulses.length)) % PL;
      const ok = reach > 0 && s <= reach;
      c.style.opacity = ok ? 1 : 0;
      if (ok) { const p = pulsePath.getPointAtLength(s); c.setAttribute("cx", p.x); c.setAttribute("cy", p.y); }
    });
    // ev ışıkları: 15'in sonunda
    const li = eOut(clamp((t - T(15) - 1.6) / .5));
    win.forEach(w => w.style.opacity = li);
    lamp.style.opacity = li;
    // nehir akışı
    river.style.opacity = clamp((t - T(16) - .5) / .5) * .85;
    river.style.strokeDashoffset = -(t * 160);
  };
};

// Ekran üstü yazılar (dünya kendi katmanında çizilir; sahne sadece başlık/sayı taşır)
SCENES.cizim = (p, r) => {
  Object.assign(r.style, { left: "0", right: "auto", top: "0", width: W + "px", height: H + "px", justifyContent: "flex-start", paddingTop: FORMAT === "yatay" ? "70px" : "300px" });
  const items = [];
  if (p.baslik || p.buyuk) {
    const box = el("div", null, null, r);
    Object.assign(box.style, { display: "flex", flexDirection: "column", alignItems: "center", padding: "22px 54px 26px",
      background: "radial-gradient(closest-side, rgba(10,22,44,.92), rgba(10,22,44,.6) 70%, rgba(10,22,44,0))" });
    if (p.ust) { const e = el("div", null, md(p.ust), box); Object.assign(e.style, { color: CZ.tur, fontWeight: 800, fontSize: "30px", letterSpacing: "4px" }); items.push(e); }
    if (p.baslik) { const e = el("div", "h", md(p.baslik), box); Object.assign(e.style, { fontSize: (p.boy || 84) + "px", letterSpacing: "2px" }); items.push(e); }
    if (p.buyuk) { const e = el("div", "h sari", md(p.buyuk), box); Object.assign(e.style, { fontSize: (p.boy || 150) + "px", textShadow: "0 0 30px rgba(255,200,61,.35)" }); items.push(e); }
    if (p.alt) { const e = el("div", null, md(p.alt), box); Object.assign(e.style, { color: "rgba(219,231,255,.8)", fontWeight: 700, fontSize: "30px", marginTop: "6px", letterSpacing: "1px" }); items.push(e); }
  }
  return (lt) => items.forEach((e, i) => slide(e, lt, .25 + i * .12, 0, 24, .45));
};
