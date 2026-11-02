// 3D veri görselleştirme modu (three.js) — uçuş verisi, nokta bulutu, çizgi şehir.
// bolum.json: "stil": "3d", "dunya": "learjet". Sahneler tip "uc3d":
//   p.ucus  [s0, s1]  sahne başında/sonunda uçuş saniyesi (0 = tırmanış başı). Arada doğrusal.
//   p.kam   { mod: "takip", geri, yan, yuk }  uçağın yönüne göre kamera ofseti (birim = 100 m)
//           { mod: "sabit", konum: [x,y,z], hedef: "ucak" | [x,y,z] }
//   p.hud   { halka, veri, iz, damla, son, kaynak: "ADS-B · ..." }
//   p.baslik / p.buyuk / p.alt / p.ust   ekran yazısı (üst orta)
// Deterministik: her kare seek(t) ile kurulur ve hemen çizilir.

// Tıkla Bakalım marka paleti (logo): kırmızı #e3141b, beyaz, siyah. Şehir: sıcak gece ışıkları.
const U3 = { tur: "#ffffff", turF: "#ff2d3a", sari: "#ff2d3a", ink: "#f4f6fa", isik: "#ffb85c" };

// ---------------- uçuş modeli (temsili, basına yansıyan verilere göre) ----------------
// s < 0: 35.000 ft seyir, doğuya · 0–15: 35.250 ft'e kısa tırmanış · 15–80: sağa dönerek dalış,
// 80'de son sinyal 8.750 ft. Dikey hız tepe ~30–32 bin ft/dk.
const FT = 0.3048 / 100;                       // ft → dünya birimi (100 m)
function altFt(s) {
  if (s < 0) return 35000;
  if (s < 15) { const u = s / 15; return 35000 + 250 * u * u * (3 - 2 * u); }
  const u = Math.min(1, (s - 15) / 65), sm = u * u * (3 - 2 * u);
  return 35250 - 26500 * (.5 * sm + .5 * u);
}
const TRACK = (() => {
  const pts = []; let x = -2.3 * 140, z = 0, h = 0;
  for (let s = -140; s <= 80.001; s += .05) {
    const turn = s < 15 ? 0 : Math.min(1, (s - 15) / 10) * (200 * Math.PI / 180) / 65;   // sağa dönüş hızı
    h += turn * .05;
    const v = s < 15 ? 2.3 : lerp(2.3, 1.6, Math.min(1, (s - 15) / 30));                // yatay hız (birim/sn)
    x += Math.cos(h) * v * .05; z += Math.sin(h) * v * .05;
    pts.push({ s, x, z, h, y: altFt(s) * FT, turn });
  }
  return pts;
})();
function stateAt(s) {
  s = Math.max(-140, Math.min(80, s));
  const i = Math.min(TRACK.length - 2, Math.floor((s + 140) / .05));
  const a = TRACK[i], b = TRACK[i + 1], f = clamp((s - a.s) / .05);
  const st = { s, x: lerp(a.x, b.x, f), y: lerp(a.y, b.y, f), z: lerp(a.z, b.z, f), h: lerp(a.h, b.h, f), turn: a.turn };
  const vs = (altFt(s + .25) - altFt(s - .25)) / .5 * 60;          // ft/dk
  const vh = s < 15 ? 2.3 : lerp(2.3, 1.6, Math.min(1, (s - 15) / 30));
  st.alt = altFt(s); st.vs = vs;
  st.pitch = Math.atan2(vs / 60 * FT, vh);
  st.bank = Math.min(1.1, st.turn * 9);
  return st;
}

window.buildWorld3D = function (stage, tl) {
  const T = window.THREE;
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  Object.assign(canvas.style, { position: "absolute", inset: "0", width: W + "px", height: H + "px" });
  stage.appendChild(canvas);
  const R = new T.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(W, H, false); R.setClearColor(0x05070d, 1);
  const scene = new T.Scene();
  scene.fog = new T.FogExp2(0x05070d, .0038);
  const cam = new T.PerspectiveCamera(FORMAT === "yatay" ? 45 : 62, W / H, .1, 2000);
  // dikeyde hedef ekranın ~%40'ında dursun (altyazı ve veri kutusu altta)
  if (FORMAT !== "yatay") cam.setViewOffset(W, H, 0, 190, W, H);
  // rastgele ama deterministik
  let sd = 11; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;

  // --- gece şehri: yollar boyunca sıcak ışık noktaları; doğuda (x > 150) okyanus, ışık yok ---
  const cp = [], cc = [];
  const warm = new T.Color(U3.isik), white = new T.Color(0xfff4e0), red = new T.Color(0xff5a4a);
  const dot = (x, z, k) => { cp.push(x, .05, z); const c = k < .82 ? warm : k < .97 ? white : red; cc.push(c.r, c.g, c.b); };
  for (let gx = -460; gx <= 150; gx += 3) for (let gz = -320; gz <= 320; gz += 3) {
    const onRoad = (Math.abs((gz - 6) % 22) < 1.2) || (Math.abs((gx - 10) % 40) < 1.2);
    const dens = onRoad ? .9 : .16 * (1 + Math.sin(gx * .02) * Math.cos(gz * .025));
    if (rnd() < dens) dot(gx + rnd() * 2.4, gz + rnd() * 2.4, rnd());
  }
  const cityG = new T.BufferGeometry();
  cityG.setAttribute("position", new T.Float32BufferAttribute(cp, 3));
  cityG.setAttribute("color", new T.Float32BufferAttribute(cc, 3));
  scene.add(new T.Points(cityG, new T.PointsMaterial({ size: .5, sizeAttenuation: true, vertexColors: true, transparent: true, opacity: .9, depthWrite: false })));
  // kıyı çizgisi + okyanus üstünde seyrek ızgara
  const coast = [];
  for (let z = -320; z < 320; z += 4) coast.push(150 + 6 * Math.sin(z * .05), .03, z, 150 + 6 * Math.sin((z + 4) * .05), .03, z + 4);
  for (let x = 170; x <= 460; x += 20) coast.push(x, .02, -320, x, .02, 320);
  for (let z = -320; z <= 320; z += 20) coast.push(160, .02, z, 460, .02, z);
  const coastG = new T.BufferGeometry(); coastG.setAttribute("position", new T.Float32BufferAttribute(coast, 3));
  scene.add(new T.LineSegments(coastG, new T.LineBasicMaterial({ color: 0x5f7896, transparent: true, opacity: .35 })));

  // --- yağmur: kısa dikey çizgiler; fırtına hücresinde yoğun (dalışın başladığı yer) ---
  const N = 16000, rp = [];
  for (let i = 0; i < N; i++) {
    const storm = i < N * .55;
    const x = (storm ? 30 : 0) + (rnd() * 2 - 1) * (storm ? 70 : 380), z = (storm ? 20 : 0) + (rnd() * 2 - 1) * (storm ? 60 : 260);
    const y = storm ? 20 + rnd() * 100 : rnd() * 130, l = storm ? 1.6 : 1.1;
    rp.push(x, y, z, x - .15, y - l, z);
  }
  const ptsG = new T.BufferGeometry(); ptsG.setAttribute("position", new T.Float32BufferAttribute(rp, 3));
  const pts = new T.LineSegments(ptsG, new T.LineBasicMaterial({ color: 0xc9d6e6, transparent: true, opacity: .28, depthWrite: false }));
  scene.add(pts);

  // --- tel kafes Learjet (burun +x, ~4 birim; gerçek boyutun çok üstünde — görünür olsun diye) ---
  const plane = new T.Group();
  const fillM = new T.MeshBasicMaterial({ color: U3.turF, transparent: true, opacity: .26, side: T.DoubleSide, depthWrite: false });
  const lineM = new T.LineBasicMaterial({ color: U3.tur });
  const add = (geo, wire) => {
    plane.add(new T.Mesh(geo, fillM));
    plane.add(new T.LineSegments(wire ? new T.WireframeGeometry(geo) : new T.EdgesGeometry(geo, 25), lineM));
  };
  const fus = new T.CylinderGeometry(.22, .2, 3.2, 10, 5, true); fus.rotateZ(-Math.PI / 2); add(fus, true);
  const nose = new T.ConeGeometry(.22, .7, 10, 2, true); nose.rotateZ(-Math.PI / 2); nose.translate(1.95, 0, 0); add(nose, true);
  const tailc = new T.ConeGeometry(.2, .6, 10, 2, true); tailc.rotateZ(Math.PI / 2); tailc.translate(-1.9, 0, 0); add(tailc, true);
  const flat = (poly, rotX) => {
    const sh = new T.Shape(); poly.forEach(([a, b], i) => i ? sh.lineTo(a, b) : sh.moveTo(a, b));
    const g = new T.ShapeGeometry(sh); if (rotX) g.rotateX(rotX); return g;
  };
  // kanatlar (xz düzlemi): kök x .3..-.6, uç x -.55..-.85, z ±2.1
  for (const sg of [1, -1]) {
    const g = flat([[.3, .18 * sg], [-.6, .18 * sg], [-.85, 2.1 * sg], [-.55, 2.1 * sg]], Math.PI / 2); g.translate(0, -.08, 0); add(g);
    const ht = flat([[-1.62, 0], [-1.95, 0], [-2.12, .78 * sg], [-1.92, .78 * sg]], Math.PI / 2); ht.translate(0, .98, 0); add(ht);
    const eng = new T.CylinderGeometry(.12, .1, .62, 8, 1, true); eng.rotateZ(-Math.PI / 2); eng.translate(-1.15, .16, .36 * sg); add(eng, true);
  }
  add(flat([[-1.2, .18], [-1.75, .18], [-2.0, 1.0], [-1.68, 1.0]]));          // dikey kuyruk (T-kuyruk)
  scene.add(plane);

  // --- iz, düşey damla çizgileri, son sinyal ---
  const trailG = new T.BufferGeometry();
  const trail = new T.Line(trailG, new T.LineBasicMaterial({ color: U3.sari, transparent: true, opacity: .95 }));
  scene.add(trail);
  const dropG = new T.BufferGeometry();
  const drops = new T.LineSegments(dropG, new T.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .3 }));
  scene.add(drops);
  const last = stateAt(80);
  const lastDot = new T.Mesh(new T.SphereGeometry(.7, 12, 8), new T.MeshBasicMaterial({ color: U3.sari }));
  lastDot.position.set(last.x, last.y, last.z); scene.add(lastDot);

  // --- HUD katmanı (HTML) ---
  const hud = el("div", null, null, stage);
  Object.assign(hud.style, { position: "absolute", inset: "0", pointerEvents: "none", zIndex: 5 });
  const svgNS = "http://www.w3.org/2000/svg";
  const sv = document.createElementNS(svgNS, "svg");
  sv.setAttribute("width", W); sv.setAttribute("height", H);
  Object.assign(sv.style, { position: "absolute", inset: "0" });
  hud.appendChild(sv);
  const rings = [1, 1.9, 3].map(k => { const c = document.createElementNS(svgNS, "circle"); c.setAttribute("fill", "none");
    c.setAttribute("stroke", U3.sari); c.setAttribute("stroke-width", k === 1 ? 3 : 2); c.dataset.k = k; sv.appendChild(c); return c; });
  const mono = "M, sans-serif";
  const box = el("div", null, null, hud);
  Object.assign(box.style, { position: "absolute", left: FORMAT === "yatay" ? "70px" : "60px", top: FORMAT === "yatay" ? "780px" : "1340px",
    fontFamily: mono, fontWeight: 800, color: U3.ink, fontSize: "30px", lineHeight: "1.5", padding: "14px 22px", borderLeft: "8px solid #e3141b", borderRadius: "6px", background: "rgba(5,7,13,.78)" });
  const chip = el("div", null, null, hud);
  Object.assign(chip.style, { position: "absolute", left: "50%", transform: "translateX(-50%)", top: FORMAT === "yatay" ? "925px" : "1288px",
    fontFamily: mono, fontWeight: 800, color: "#fff", fontSize: "22px", letterSpacing: "2px", padding: "7px 16px", background: "#e3141b", borderRadius: "8px", whiteSpace: "nowrap" });
  const lastLbl = el("div", null, null, hud);
  Object.assign(lastLbl.style, { position: "absolute", fontFamily: mono, color: U3.sari, fontSize: "30px", fontWeight: 900, whiteSpace: "nowrap", textShadow: "0 2px 8px #000" });
  lastLbl.innerHTML = "SON SİNYAL<br><span style='font-size:22px;opacity:.85'>8.750 ft · ~2.700 m</span>";
  const repr = el("div", "", "temsili rota · basına yansıyan ADS-B verilerine göre", hud);
  Object.assign(repr.style, { position: "absolute", right: "40px", bottom: FORMAT === "yatay" ? "18px" : "438px", fontFamily: mono, fontSize: "18px", color: "rgba(232,238,246,.45)" });

  const sc = tl.scenes.filter(s => s.tip === "uc3d");
  const sceneAt = t => { let i = 0; for (let k = 0; k < sc.length; k++) if (t >= sc[k].t0) i = k; return i; };
  const sAt = (s, t) => { const [a, b] = s.p.ucus || [0, 0]; return lerp(a, b, clamp((t - s.t0) / Math.max(.01, s.t1 - s.t0))); };
  const camFor = (spec, st) => {
    if (!spec || spec.mod !== "sabit") {
      const g = spec ? spec.geri : 9, y = spec ? spec.yan : 3, u = spec ? spec.yuk : 2.5;
      const fx = Math.cos(st.h), fz = Math.sin(st.h), rx = -fz, rz = fx;     // ileri ve sağ
      return { p: [st.x - fx * g + rx * y, st.y + u, st.z - fz * g + rz * y], q: [st.x, st.y, st.z] };
    }
    const q = spec.hedef === "ucak" ? [st.x, st.y, st.z] : spec.hedef;
    return { p: spec.konum, q };
  };
  const proj = (x, y, z) => { const v = new T.Vector3(x, y, z).project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H, v.z]; };
  const fmt = n => Math.round(n).toLocaleString("tr-TR");

  return t => {
    const i = sceneAt(t), s = sc[i], hd = s.p.hud || {};
    const fs = sAt(s, t), st = stateAt(fs);
    // kamera: önceki sahnenin kamera tanımından bu sahneninkine yumuşak geçiş
    const cur = camFor(s.p.kam, st);
    const prev = i > 0 ? camFor(sc[i - 1].p.kam, st) : cur;
    const u = eInOut(clamp((t - s.t0) / Math.min(1.4, Math.max(.6, (s.t1 - s.t0) * .45))));
    const P = cur.p.map((v, k) => lerp(prev.p[k], v, u)), Q = cur.q.map((v, k) => lerp(prev.q[k], v, u));
    cam.position.set(P[0] + .3 * Math.sin(t * .7), P[1] + .2 * Math.sin(t * .5), P[2]);
    cam.lookAt(Q[0], Q[1], Q[2]);
    // uçak
    const vis = fs < 80 ? 1 : 0;
    plane.visible = !!vis;
    plane.position.set(st.x, st.y, st.z);
    plane.rotation.order = "YZX";
    plane.rotation.set(st.bank, -st.h, st.pitch);
    // yağmur: noktalar yavaşça aşağı akar
    pts.position.y = -((t * 14) % 8);
    // iz
    const tp = [];
    if (hd.iz !== false) for (let k = Math.max(-140, fs - 70); k <= fs; k += .25) { const a = stateAt(k); tp.push(a.x, a.y, a.z); }
    trailG.setAttribute("position", new T.Float32BufferAttribute(tp.length ? tp : [0, 0, 0, 0, 0, 0], 3));
    trail.visible = tp.length > 3;
    // damla çizgileri (irtifa)
    const dp = [];
    if (hd.damla) for (let k = 0; k <= Math.min(fs, 80); k += 2.5) { const a = stateAt(k); dp.push(a.x, a.y, a.z, a.x, 0, a.z); }
    dropG.setAttribute("position", new T.Float32BufferAttribute(dp.length ? dp : [0, 0, 0, 0, 0, 0], 3));
    drops.visible = dp.length > 0;
    lastDot.visible = !!hd.son && fs >= 79.5;
    R.render(scene, cam);
    // HUD
    const [px, py, pz] = proj(st.x, st.y, st.z);
    const dist = Math.hypot(P[0] - st.x, P[1] - st.y, P[2] - st.z);
    const base = 2600 / Math.max(4, dist);
    rings.forEach(c => {
      const k = +c.dataset.k;
      c.setAttribute("cx", px); c.setAttribute("cy", py);
      c.setAttribute("r", base * k * (1 + .04 * Math.sin(t * 3 + k)));
      c.style.opacity = hd.halka && vis && pz < 1 ? (k === 1 ? .9 : .45) : 0;
    });
    box.style.opacity = hd.veri ? 1 : 0;
    if (hd.veri) {
      const vsTxt = st.vs < -500 ? `<span style="color:#fff">−${fmt(Math.round(-st.vs / 250) * 250)} ft/dk</span>` : st.vs > 300 ? `+${fmt(st.vs)} ft/dk` : "0 ft/dk";
      box.innerHTML = `<span style="color:#ff4d57">İRTİFA</span> ${fmt(Math.round(st.alt / 50) * 50)} ft · ${(st.alt * .3048 / 1000).toFixed(1).replace(".", ",")} km<br>` +
        `<span style="color:#ff4d57">DİKEY HIZ</span> ${vsTxt}`;
    }
    chip.style.opacity = hd.kaynak ? 1 : 0;
    if (hd.kaynak) chip.textContent = hd.kaynak;
    const [lx, ly, lz] = proj(last.x, last.y, last.z);
    lastLbl.style.opacity = lastDot.visible && lz < 1 ? 1 : 0;
    lastLbl.style.left = (lx + 26) + "px"; lastLbl.style.top = (ly - 30) + "px";
    repr.style.opacity = hd.temsili === false ? 0 : 1;
  };
};

// Ekran yazısı (üst orta) — 3D sahnenin üstüne
SCENES.uc3d = (p, r) => {
  Object.assign(r.style, { left: "0", right: "auto", top: "0", width: W + "px", height: H + "px", justifyContent: "flex-start",
    paddingTop: FORMAT === "yatay" ? "80px" : "330px" });
  const items = [];
  const mk = (txt, css, cls) => { const e = el("div", cls || null, md(txt), r); Object.assign(e.style, css); items.push(e); return e; };
  if (p.ust) mk(p.ust, { color: "#fff", background: "#e3141b", fontWeight: 900, fontSize: "30px", letterSpacing: "3px", padding: "6px 20px", borderRadius: "10px", marginBottom: "10px" });
  if (p.baslik) mk(p.baslik, { fontSize: (p.boy || 84) + "px", color: "#fff", textShadow: "0 4px 18px #000", margin: "8px 40px", textAlign: "center" }, "h");
  if (p.buyuk) mk(p.buyuk, { fontSize: (p.boy || 150) + "px", color: "#fff", textShadow: "0 0 34px rgba(227,20,27,.75), 0 4px 18px #000" }, "h");
  if (p.alt) mk(p.alt, { color: "rgba(232,238,246,.85)", fontWeight: 700, fontSize: "32px", marginTop: "8px", textShadow: "0 2px 10px #000", textAlign: "center", padding: "0 50px" });
  if (p.logo && p.src) { const im = el("img", null, null, r); im.src = p.src;
    Object.assign(im.style, { width: "300px", height: "300px", borderRadius: "50%", marginTop: "30px", boxShadow: "0 0 0 8px #fff, 0 20px 50px rgba(0,0,0,.6)" }); items.push(im); }
  return lt => items.forEach((e, i) => slide(e, lt, .2 + i * .12, 0, 24, .45));
};
