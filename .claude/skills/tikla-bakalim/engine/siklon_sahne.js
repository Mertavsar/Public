// Siklon videosu için 3D'nin önüne gelen SVG "set" sahneleri (her biri farklı görsel dil).
// Kullanım (uc3d sahnesi): "p": { "sahne": "kesit1" | "kesit2" | "kure" | "kabarma" | "tahliye", ... }
// Arkadaki 3D dünya bu sahnelerde bulanıklaşıp kararır (siklon3d.js: hud.bulanik).
window.SIKLON_SAHNE = {};
const SS_NS = "http://www.w3.org/2000/svg";
const ssSvg = (r, h = 1000, top = 330) => {
  const s = document.createElementNS(SS_NS, "svg");
  s.setAttribute("viewBox", `0 0 1080 ${h}`); s.setAttribute("width", 1080); s.setAttribute("height", h);
  Object.assign(s.style, { position: "absolute", left: "0", top: (FORMAT === "yatay" ? 40 : top) + "px", overflow: "visible" });
  if (FORMAT === "yatay") { s.style.left = "420px"; s.style.transform = "scale(.9)"; s.style.transformOrigin = "0 0"; }
  r.appendChild(s); return s;
};
const ssE = (par, tag, a, txt) => { const e = document.createElementNS(SS_NS, tag); for (const k in a) e.setAttribute(k, a[k]); if (txt != null) e.textContent = txt; par.appendChild(e); return e; };
const ssDefs = svg => ssE(svg, "defs", {}).innerHTML = `
  <linearGradient id="ssSea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff7a2f"/><stop offset=".35" stop-color="#d1442b"/><stop offset="1" stop-color="#14204a"/></linearGradient>
  <linearGradient id="ssCool" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f7fd8"/><stop offset="1" stop-color="#0b1838"/></linearGradient>
  <radialGradient id="ssHeat"><stop offset="0" stop-color="#ffb347" stop-opacity=".85"/><stop offset="1" stop-color="#ff5a2a" stop-opacity="0"/></radialGradient>
  <marker id="ssArR" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#ff3b45"/></marker>
  <marker id="ssArB" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#5fb4ff"/></marker>
  <marker id="ssArW" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#fff"/></marker>`;
const ssTxt = (svg, x, y, t, size = 34, col = "#fff", anchor = "middle", w = 900) =>
  ssE(svg, "text", { x, y, "text-anchor": anchor, fill: col, "font-family": "M, sans-serif", "font-weight": 900, "font-size": size, style: "paint-order:stroke;stroke:#04070e;stroke-width:6px" }, t);

// ---- kesit (yandan kesit): sıcak deniz, buhar, yükselen kuleler, göz ----
const kesit = (r, asama) => {
  const svg = ssSvg(r, 820); ssDefs(svg);
  const sea = ssE(svg, "path", { fill: "url(#ssSea)" });
  const surf = ssE(svg, "path", { fill: "none", stroke: "#ffd08a", "stroke-width": 4 });
  const drops = Array.from({ length: 60 }, (_, i) => ssE(svg, "circle", { r: 5 + (i % 3) * 2, fill: "#ffb36b", opacity: 0 }));
  // termometre
  const th = ssE(svg, "g", {});
  ssE(th, "rect", { x: 930, y: 300, width: 44, height: 300, rx: 22, fill: "rgba(255,255,255,.12)", stroke: "#fff", "stroke-width": 4 });
  const merc = ssE(th, "rect", { x: 940, y: 590, width: 24, height: 0, rx: 12, fill: "#ff3b45" });
  ssE(th, "circle", { cx: 952, cy: 618, r: 34, fill: "#ff3b45", stroke: "#fff", "stroke-width": 4 });
  const thT = ssTxt(th, 952, 280, "", 40, "#fff");
  // kuleler (göz duvarı) + oklar
  const towers = [ssE(svg, "path", { fill: "#e9eef6" }), ssE(svg, "path", { fill: "#e9eef6" })];
  const tops = [ssE(svg, "path", { fill: "#ff5a3c", opacity: .9 }), ssE(svg, "path", { fill: "#ff5a3c", opacity: .9 })];
  const ups = [0, 1, 2, 3].map(i => ssE(svg, "path", { d: "", fill: "none", stroke: "#ff3b45", "stroke-width": 10, "stroke-dasharray": "26 22", "marker-end": "url(#ssArR)", "stroke-linecap": "round" }));
  const outs = [0, 1].map(i => ssE(svg, "path", { d: "", fill: "none", stroke: "#fff", "stroke-width": 6, "stroke-dasharray": "18 16", "marker-end": "url(#ssArW)", opacity: 0 }));
  const ins = [0, 1].map(i => ssE(svg, "path", { d: "", fill: "none", stroke: "#5fb4ff", "stroke-width": 10, "stroke-dasharray": "26 22", "marker-end": "url(#ssArB)", opacity: 0 }));
  const eyeDn = ssE(svg, "path", { d: "M540 170 V430", stroke: "#5fb4ff", "stroke-width": 8, "stroke-dasharray": "16 16", "marker-end": "url(#ssArB)", opacity: 0, fill: "none" });
  const heat = [ssE(svg, "circle", { cx: 330, cy: 330, r: 0, fill: "url(#ssHeat)" }), ssE(svg, "circle", { cx: 750, cy: 330, r: 0, fill: "url(#ssHeat)" })];
  const lab1 = ssTxt(svg, 540, 760, asama === 1 ? "SICAK DENİZ → BUHAR" : asama === 2 ? "YÜKSELEN HAVA → BULUT + ISI" : "ÇEVREDEN İÇE AKAN HAVA", 40, "#fff");
  const labEye = ssTxt(svg, 540, 140, "GÖZ", 34, "#5fb4ff");
  return lt => {
    const W2 = 1080, base = 560;
    let d = `M0 ${base}`;
    for (let x = 0; x <= W2; x += 20) d += ` L${x} ${base + 10 * Math.sin(x / 60 + lt * 3) + 6 * Math.sin(x / 23 - lt * 2)}`;
    surf.setAttribute("d", d); sea.setAttribute("d", d + ` L${W2} 820 L0 820 Z`);
    // buhar damlaları (aşama 1'de belirgin)
    drops.forEach((c, i) => { const ph = (lt * .55 + i / drops.length * 3) % 1, x = 60 + (i * 137) % 800;
      c.setAttribute("cx", x + 12 * Math.sin(lt * 2 + i)); c.setAttribute("cy", base - ph * (asama === 1 ? 420 : 220)); c.setAttribute("opacity", (asama === 1 ? .9 : .45) * (1 - ph)); });
    // termometre (aşama 1)
    th.style.opacity = asama === 1 ? 1 : 0;
    const q = eOut(clamp(lt / 1.6)); merc.setAttribute("y", 590 - 270 * q * .9); merc.setAttribute("height", 270 * q * .9 + 10);
    thT.textContent = (q * 26.5).toFixed(1).replace(".", ",") + " °C";
    // kuleler büyür (aşama ≥ 2)
    const g = asama >= 2 ? eOut(clamp(lt / 1.8)) : asama === 1 ? .15 : 1;
    [[330, 1], [750, -1]].forEach(([cx, sg], k) => {
      const hgt = 380 * g, w = 150;
      let p = `M${cx - w} ${base}`;
      for (let j = 0; j <= 6; j++) { const y = base - hgt * j / 6, bulge = 18 * Math.sin(j * 1.7 + lt * 1.5 + k); p += ` Q${cx - w - 30 + bulge} ${y + 25} ${cx - w + 10 * Math.sin(j)} ${y}`; }
      p += ` Q${cx} ${base - hgt - 90} ${cx + w} ${base - hgt}`;
      for (let j = 6; j >= 0; j--) { const y = base - hgt * j / 6, bulge = 18 * Math.sin(j * 1.3 - lt * 1.5 + k); p += ` Q${cx + w + 30 + bulge} ${y - 25} ${cx + w - 10 * Math.sin(j)} ${y}`; }
      towers[k].setAttribute("d", p + " Z"); towers[k].setAttribute("opacity", .92);
      tops[k].setAttribute("d", `M${cx - w * .8} ${base - hgt + 30} Q${cx} ${base - hgt - 110} ${cx + w * .8} ${base - hgt + 30} Z`);
      tops[k].setAttribute("opacity", g > .5 ? .85 : 0);
      heat[k].setAttribute("r", asama === 2 ? 170 * g * (1 + .08 * Math.sin(lt * 4)) : 0);
    });
    ups.forEach((u, i) => { const cx = i < 2 ? 330 + (i ? 50 : -50) : 750 + (i === 3 ? 50 : -50);
      u.setAttribute("d", `M${cx} ${base - 20} V${base - 360 * g}`); u.style.strokeDashoffset = -lt * 120; u.setAttribute("opacity", asama >= 2 ? 1 : 0); });
    outs.forEach((o, i) => { const sg = i ? 1 : -1; o.setAttribute("d", `M${540 + sg * 260} ${base - 400 * g} Q${540 + sg * 420} ${base - 470 * g} ${540 + sg * 520} ${base - 380 * g}`);
      o.style.strokeDashoffset = -lt * 90; o.setAttribute("opacity", asama >= 2 && g > .8 ? .9 : 0); });
    ins.forEach((o, i) => { const sg = i ? 1 : -1; o.setAttribute("d", `M${540 + sg * 540} ${base - 40} Q${540 + sg * 360} ${base - 70} ${540 + sg * 240} ${base - 50}`);
      o.style.strokeDashoffset = -lt * 140; o.setAttribute("opacity", asama === 3 ? 1 : 0); });
    eyeDn.style.strokeDashoffset = -lt * 60; eyeDn.setAttribute("opacity", asama === 3 ? .9 : 0); labEye.style.opacity = asama === 3 ? 1 : 0;
  };
};
SIKLON_SAHNE.kesit1 = r => kesit(r, 1);
SIKLON_SAHNE.kesit2 = r => kesit(r, 2);
SIKLON_SAHNE.kesit3 = r => kesit(r, 3);

// ---- dönen dünya + Coriolis sapması ----
SIKLON_SAHNE.kure = r => {
  const svg = ssSvg(r, 900, 300); ssDefs(svg);
  const cx = 540, cy = 430, R = 330;
  ssE(svg, "circle", { cx, cy, r: R + 30, fill: "rgba(95,180,255,.12)" });
  ssE(svg, "circle", { cx, cy, r: R, fill: "url(#ssCool)", stroke: "#9fd0ff", "stroke-width": 4 });
  const lat = [-60, -30, 0, 30, 60].map(a => ssE(svg, "ellipse", { cx, cy: cy - R * Math.sin(a * Math.PI / 180), rx: R * Math.cos(a * Math.PI / 180), ry: 18, fill: "none", stroke: a === 0 ? "#ffd08a" : "rgba(200,225,255,.45)", "stroke-width": a === 0 ? 5 : 2 }));
  const mer = Array.from({ length: 6 }, () => ssE(svg, "ellipse", { cx, cy, rx: 10, ry: R, fill: "none", stroke: "rgba(200,225,255,.35)", "stroke-width": 2 }));
  const spin = ssE(svg, "path", { d: `M${cx - 200} ${cy + R + 70} Q${cx} ${cy + R + 120} ${cx + 200} ${cy + R + 70}`, fill: "none", stroke: "#fff", "stroke-width": 6, "marker-end": "url(#ssArW)" });
  ssTxt(svg, cx, cy + R + 160, "DÜNYA DÖNÜYOR", 34, "#fff");
  const arr = ssE(svg, "path", { d: "", fill: "none", stroke: "#ff3b45", "stroke-width": 12, "stroke-linecap": "round", "marker-end": "url(#ssArR)" });
  const ghost = ssE(svg, "path", { d: `M${cx - 60} ${cy - 40} L${cx - 60} ${cy - 250}`, fill: "none", stroke: "rgba(255,255,255,.6)", "stroke-width": 5, "stroke-dasharray": "12 12" });
  ssTxt(svg, cx + 150, cy - 280, "SAĞA SAPAR", 36, "#ff3b45");
  ssTxt(svg, cx, cy - R - 40, "KUZEY YARIMKÜRE", 34, "#9fd0ff");
  return lt => {
    mer.forEach((m, i) => { const a = ((i / 6) + lt * .08) % 1 * Math.PI; m.setAttribute("rx", Math.abs(R * Math.cos(a))); });
    const u = eOut(clamp((lt - .4) / 1.6));
    let d = `M${cx - 60} ${cy - 40}`;
    for (let k = 1; k <= 20; k++) { const v = k / 20 * u; d += ` L${cx - 60 + 190 * v * v} ${cy - 40 - 220 * v}`; }
    arr.setAttribute("d", d);
    ghost.setAttribute("opacity", u > .1 ? .6 : 0);
  };
};

// ---- insan ölçeğinde fırtına kabarması ----
SIKLON_SAHNE.kabarma = r => {
  const svg = ssSvg(r, 900, 300); ssDefs(svg);
  const gy = 720, m = 260;   // 1 m = 260 px
  ssE(svg, "rect", { x: 0, y: gy, width: 1080, height: 180, fill: "#3a2f28" });
  // ev
  ssE(svg, "path", { d: `M650 ${gy} V${gy - 420} L820 ${gy - 560} L990 ${gy - 420} V${gy} Z`, fill: "#2a3346", stroke: "#cfd8e6", "stroke-width": 5 });
  ssE(svg, "rect", { x: 780, y: gy - 230, width: 90, height: 230, fill: "#1a2030", stroke: "#cfd8e6", "stroke-width": 4 });
  // insan silueti 1,75 m
  const ph = 1.75 * m, px = 400;
  const man = ssE(svg, "g", { fill: "#e9eef6" });
  ssE(man, "circle", { cx: px, cy: gy - ph + 34, r: 34 });
  ssE(man, "rect", { x: px - 42, y: gy - ph + 76, width: 84, height: ph * .42, rx: 26 });
  ssE(man, "rect", { x: px - 38, y: gy - ph * .5, width: 32, height: ph * .5, rx: 14 });
  ssE(man, "rect", { x: px + 6, y: gy - ph * .5, width: 32, height: ph * .5, rx: 14 });
  ssE(man, "rect", { x: px - 70, y: gy - ph + 86, width: 26, height: ph * .36, rx: 12 });
  ssE(man, "rect", { x: px + 44, y: gy - ph + 86, width: 26, height: ph * .36, rx: 12 });
  ssTxt(svg, px, gy - ph - 20, "1,75 m", 30, "#e9eef6");
  // cetvel
  const rul = ssE(svg, "g", {});
  for (let k = 0; k <= 20; k++) ssE(rul, "line", { x1: 90, x2: k % 10 ? 110 : 130, y1: gy - k * m / 10, y2: gy - k * m / 10, stroke: "#fff", "stroke-width": k % 10 ? 2 : 4 });
  ssE(rul, "line", { x1: 90, x2: 90, y1: gy, y2: gy - 2 * m, stroke: "#fff", "stroke-width": 4 });
  ssTxt(rul, 160, gy - m + 10, "1 m", 28, "#fff", "start"); ssTxt(rul, 160, gy - 2 * m + 10, "2 m", 28, "#fff", "start");
  const water = ssE(svg, "path", { fill: "rgba(47,127,216,.72)" });
  const wl = ssE(svg, "path", { fill: "none", stroke: "#9fd0ff", "stroke-width": 5 });
  const lab = ssTxt(svg, 540, 140, "", 64, "#fff");
  return lt => {
    const u = eOut(clamp((lt - .3) / 2.2)), lvl = 1.5 * u, y0 = gy - lvl * m;
    let d = `M0 ${y0}`; for (let x = 0; x <= 1080; x += 20) d += ` L${x} ${y0 + 10 * Math.sin(x / 50 + lt * 4)}`;
    wl.setAttribute("d", d); water.setAttribute("d", d + ` L1080 ${gy + 180} L0 ${gy + 180} Z`);
    lab.textContent = "DENİZ +" + lvl.toFixed(1).replace(".", ",") + " m";
  };
};

// ---- 30.000 kişi: her simge 100 kişi ----
SIKLON_SAHNE.tahliye = r => {
  const svg = ssSvg(r, 900, 320);
  const cols = 20, rows = 15, sx = 46, sy = 54, x0 = 540 - (cols - 1) * sx / 2, y0 = 120;
  const ppl = [];
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const g = ssE(svg, "g", { transform: `translate(${x0 + i * sx} ${y0 + j * sy})`, opacity: .18 });
    ssE(g, "circle", { cx: 0, cy: 0, r: 9, fill: "#fff" });
    ssE(g, "rect", { x: -11, y: 12, width: 22, height: 24, rx: 9, fill: "#fff" });
    ppl.push(g);
  }
  ssTxt(svg, 540, 70, "1 simge = 100 kişi", 30, "rgba(255,255,255,.75)");
  return lt => {
    const n = Math.floor(ppl.length * eOut(clamp((lt - .3) / 2.4)));
    ppl.forEach((g, k) => { g.setAttribute("opacity", k < n ? 1 : .15); g.querySelectorAll("*").forEach(e => e.setAttribute("fill", k < n ? "#ff3b45" : "#fff")); });
  };
};
