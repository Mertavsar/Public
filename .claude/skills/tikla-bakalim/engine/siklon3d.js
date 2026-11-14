// 3D siklon dünyası — "dunya": "siklon" (stil "3d"). Gece/uydu görünümü, Tıkla Bakalım kırmızısı.
// Birim: 1 = 2 km. Kuzey = −z, doğu = +x. Kıyı: Andhra Pradesh (Hindistan doğu kıyısı).
// Sahne p:
//   saat   [h0, h1]  fırtına saati (0 = 2 Kasım 14:30 IST), sahne boyunca doğrusal
//   kam    { mod: "sabit", konum, konum2?, hedef: [x,y,z] | "goz" } | { mod: "takip", geri, yan, yuk }
//   hud    { rota, tahmin, sehir, buhar, akis, goz, kabarma, ruzgar, temsili }
// Rota TEMSİLİDİR: IMD konum/hız/karaya çıkış bölgesi bilgisine göre kuruldu.
window.build3D_siklon = function (stage, tl) {
  const T = window.THREE;
  const canvas = document.createElement("canvas");
  canvas.width = W; canvas.height = H;
  Object.assign(canvas.style, { position: "absolute", inset: "0", width: W + "px", height: H + "px" });
  stage.appendChild(canvas);
  document.documentElement.classList.add("t3-gece");
  const R = new T.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  R.setPixelRatio(1); R.setSize(W, H, false); R.setClearColor(0x04070e, 1);
  const scene = new T.Scene();
  scene.fog = new T.FogExp2(0x04070e, .0022);
  const cam = new T.PerspectiveCamera(FORMAT === "yatay" ? 45 : 60, W / H, .1, 3000);
  if (FORMAT !== "yatay") cam.setViewOffset(W, H, 0, 170, W, H);
  let sd = 7; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const dotTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d");
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(.45, "rgba(255,255,255,.55)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); const t = new T.CanvasTexture(c); return t; })();
  const LS = (arr, col, op) => { const g = new T.BufferGeometry(); g.setAttribute("position", new T.Float32BufferAttribute(arr, 3));
    const m = new T.LineSegments(g, new T.LineBasicMaterial({ color: col, transparent: true, opacity: op, depthWrite: false })); scene.add(m); return m; };

  // --- kıyı çizgisi (Chennai → Visakhapatnam) ve kara ---
  const COAST = [[4, 260], [-2, 134], [-10, 80], [-16, 40], [-12, 0], [0, -30], [30, -50], [64, -56], [100, -80], [145, -121], [190, -170], [240, -230]];
  const coastX = z => { for (let i = 0; i < COAST.length - 1; i++) { const [x1, z1] = COAST[i], [x2, z2] = COAST[i + 1];
    if (z <= z1 && z >= z2) return lerp(x1, x2, (z1 - z) / (z1 - z2)); } return z > 0 ? 4 : 240; };
  const cl = []; for (let i = 0; i < COAST.length - 1; i++) cl.push(COAST[i][0], .1, COAST[i][1], COAST[i + 1][0], .1, COAST[i + 1][1]);
  LS(cl, 0xffffff, .95);
  // kara: kıyının batısında seyrek tarama + şehir ışıkları; deniz: ince ızgara
  const land = [], sea = [];
  for (let z = -300; z <= 300; z += 6) { const cx = coastX(z); land.push(-420, .02, z, cx - 1, .02, z); }
  for (let x = -400; x <= 420; x += 20) for (let z = -300; z < 300; z += 20) { if (x > coastX(z) + 4) sea.push(x, .01, z, Math.min(x + 20, 420), .01, z, x, .01, z, x, .01, Math.min(z + 20, 300)); }
  LS(land, 0x8090a8, .16); LS(sea, 0x3a5a86, .22);
  { // kara poligonu (kıyının batısı). Şekil xy düzleminde: y = −z, sonra yatırılır.
    const sh = new T.Shape(); sh.moveTo(-420, -300); sh.lineTo(4, -300);
    COAST.forEach(([x, z]) => sh.lineTo(x, -z)); sh.lineTo(240, 300); sh.lineTo(-420, 300); sh.lineTo(-420, -300);
    const g = new T.ShapeGeometry(sh); g.rotateX(-Math.PI / 2);
    const m = new T.Mesh(g, new T.MeshBasicMaterial({ color: 0x161d2b, side: T.DoubleSide })); m.position.y = -.05; scene.add(m); }
  const cp = [], cc = []; const warm = new T.Color(0xffb85c);
  for (let i = 0; i < 2200; i++) { const z = -300 + rnd() * 600, x = coastX(z) - 2 - Math.pow(rnd(), 1.8) * 300; cp.push(x, .05, z); cc.push(warm.r, warm.g, warm.b); }
  const cg = new T.BufferGeometry(); cg.setAttribute("position", new T.Float32BufferAttribute(cp, 3)); cg.setAttribute("color", new T.Float32BufferAttribute(cc, 3));
  const cityPts = new T.Points(cg, new T.PointsMaterial({ size: 2.2, map: dotTex, vertexColors: true, transparent: true, opacity: .8, depthWrite: false, blending: T.AdditiveBlending })); scene.add(cityPts);
  const CITIES = [["Chennai", -12, 134], ["Nellore", -27, 59], ["Ongole", -24, 0], ["Narsapur", 64, -52], ["Visakhapatnam", 145, -121]];

  // --- rota (temsili) ---
  const WP = [[-48, 262, 212], [-24, 150, 140], [0, 23, 59], [10, -13, 4], [18, -60, -40], [30, -120, -95]];
  const pos = h => { h = Math.max(WP[0][0], Math.min(WP[WP.length - 1][0], h));
    for (let i = 0; i < WP.length - 1; i++) { const a = WP[i], b = WP[i + 1]; if (h <= b[0]) { const u = (h - a[0]) / (b[0] - a[0]); return [lerp(a[1], b[1], u), lerp(a[2], b[2], u)]; } }
    return [WP[WP.length - 1][1], WP[WP.length - 1][2]]; };
  const power = h => h < 10 ? 1 : Math.exp(-(h - 10) / 7);
  const trackG = new T.BufferGeometry(), track = new T.Line(trackG, new T.LineBasicMaterial({ color: 0xff2d3a })); scene.add(track);
  const fcG = new T.BufferGeometry(), fc = new T.LineSegments(fcG, new T.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .7 })); scene.add(fc);

  // --- dalgalı okyanus (tel örgü yüzey; fırtınanın altında dalga büyür) ---
  const OX = 60, OZ = 46, ocean = new T.PlaneGeometry(900, 700, OX, OZ); ocean.rotateX(-Math.PI / 2); ocean.translate(30, 0, 0);
  const oBase = ocean.attributes.position.array.slice();
  const oceanM = new T.Mesh(ocean, new T.MeshBasicMaterial({ color: 0x2b5c9a, wireframe: true, transparent: true, opacity: .28, depthWrite: false }));
  scene.add(oceanM);
  // --- yağmur perdeleri (gözün çevresinde düşen çizgiler) ---
  const RN = 2200, rainG = new T.BufferGeometry(), rainP = new Float32Array(RN * 6), rainM = [];
  for (let i = 0; i < RN; i++) rainM.push(10 + Math.pow(rnd(), .7) * 75, rnd() * Math.PI * 2, rnd());
  rainG.setAttribute("position", new T.BufferAttribute(rainP, 3));
  const rain = new T.LineSegments(rainG, new T.LineBasicMaterial({ color: 0xbcd0e8, transparent: true, opacity: .22, depthWrite: false })); scene.add(rain);
  // --- şimşek parlamaları ---
  const flashM = new T.SpriteMaterial({ map: dotTex, color: 0xdfe8ff, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending });
  const flashes = [0, 1, 2].map(() => { const sp = new T.Sprite(flashM.clone()); sp.scale.set(40, 40, 1); scene.add(sp); return sp; });
  // --- bulut sarmalı: 4 kol, göz duvarı yoğun; saat yönünün tersine döner (kuzey yarımküre) ---
  const N = 15000, P = new Float32Array(N * 3), meta = [];
  for (let i = 0; i < N; i++) {
    const wall = i < N * .3;
    const r = wall ? 7 + rnd() * 9 : 10 + Math.pow(rnd(), .8) * 80;
    const arm = Math.floor(rnd() * 4);
    const th = wall ? rnd() * Math.PI * 2 : arm * Math.PI / 2 + Math.log(r) * 2.4 + (rnd() - .5) * (.35 + r / 160);
    const y = (wall ? 5 + rnd() * 7 : 1.5 + 6 * Math.exp(-r / 35) + rnd() * 2.5);
    meta.push(r, th, y);
  }
  const cloudG = new T.BufferGeometry(); cloudG.setAttribute("position", new T.BufferAttribute(P, 3));
  // kızılötesi uydu paleti: soğuk/yüksek bulut tepesi (göz duvarı) beyaz-kırmızı, dışa doğru turuncu → sarı → yeşil → camgöbeği
  const IR = [[1, 1, 1], [1, .25, .3], [1, .55, .15], [1, .9, .2], [.35, .9, .4], [.2, .75, 1]];
  const CC = new Float32Array(N * 3), CCw = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) { const r = meta[i * 3], f = Math.min(.999, Math.max(0, (r - 6) / 80)) * (IR.length - 1), a = Math.floor(f), b = Math.min(IR.length - 1, a + 1), u = f - a;
    for (let k = 0; k < 3; k++) { CC[i * 3 + k] = IR[a][k] * (1 - u) + IR[b][k] * u; CCw[i * 3 + k] = CC[i * 3 + k]; } }
  cloudG.setAttribute("color", new T.BufferAttribute(CC, 3));
  const cloud = new T.Points(cloudG, new T.PointsMaterial({ vertexColors: true, size: 2.0, map: dotTex, sizeAttenuation: true, transparent: true, opacity: .4, depthWrite: false }));
  scene.add(cloud);
  const hazeG = new T.BufferGeometry(), HN = Math.floor(N / 5), HP = new Float32Array(HN * 3); hazeG.setAttribute("position", new T.BufferAttribute(HP, 3));
  const haze = new T.Points(hazeG, new T.PointsMaterial({ color: 0xc8d6ea, size: 7, map: dotTex, sizeAttenuation: true, transparent: true, opacity: .06, depthWrite: false, blending: T.AdditiveBlending }));
  scene.add(haze);
  // göz halkası
  const eyeRing = new T.Mesh(new T.RingGeometry(6, 6.8, 64), new T.MeshBasicMaterial({ color: 0xff2d3a, side: T.DoubleSide, transparent: true, opacity: 0 }));
  eyeRing.rotation.x = -Math.PI / 2; scene.add(eyeRing);
  // içe akan hava (kırmızı noktalar, sarmal yollar boyunca)
  const FL = 220, flowG = new T.BufferGeometry(), flowP = new Float32Array(FL * 3); flowG.setAttribute("position", new T.BufferAttribute(flowP, 3));
  const flow = new T.Points(flowG, new T.PointsMaterial({ color: 0xff3b45, size: 3.2, map: dotTex, sizeAttenuation: true, transparent: true, opacity: 0, depthWrite: false })); scene.add(flow);
  // buharlaşma (sıcak deniz): yükselen turuncu noktalar
  const EV = 1600, evG = new T.BufferGeometry(), evP = new Float32Array(EV * 3), evM = [];
  for (let i = 0; i < EV; i++) evM.push((rnd() * 2 - 1) * 110, (rnd() * 2 - 1) * 110, rnd());
  evG.setAttribute("position", new T.BufferAttribute(evP, 3));
  const evap = new T.Points(evG, new T.PointsMaterial({ color: 0xffa040, size: 1.8, map: dotTex, sizeAttenuation: true, transparent: true, opacity: 0, depthWrite: false, blending: T.AdditiveBlending })); scene.add(evap);
  // fırtına kabarması: kıyı boyunca yükselen şerit (abartılı ölçek)
  const surgeG = new T.PlaneGeometry(1, 1, 1, 40);
  const surge = new T.Mesh(surgeG, new T.MeshBasicMaterial({ color: 0xff2d3a, transparent: true, opacity: 0, side: T.DoubleSide, depthWrite: false })); scene.add(surge);
  const SZ = [-40, 50];

  // --- HUD ---
  const hud = el("div", null, null, stage);
  Object.assign(hud.style, { position: "absolute", inset: "0", pointerEvents: "none", zIndex: 5, fontFamily: "M, sans-serif" });
  const lbl = (txt, css) => { const e = el("div", null, txt, hud); Object.assign(e.style, { position: "absolute", whiteSpace: "nowrap", fontWeight: 900, textShadow: "0 2px 10px #000", opacity: 0 }, css); return e; };
  const cityL = CITIES.map(c => lbl(`<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#fff;margin-right:8px"></span>${c[0]}`, { fontSize: "26px", color: "#fff" }));
  const eyeL = lbl("GÖZ · sakin bölge", { fontSize: "28px", color: "#fff", background: "#e3141b", padding: "4px 14px", borderRadius: "8px", textShadow: "none" });
  const surgeL = lbl("1,5 m'ye kadar KABARMA", { fontSize: "28px", color: "#fff", background: "#e3141b", padding: "4px 14px", borderRadius: "8px", textShadow: "none" });
  const landL = lbl("KARAYA ÇIKIŞ (beklenen)", { fontSize: "24px", color: "#fff", border: "3px solid #fff", padding: "3px 12px", borderRadius: "8px" });
  const big = el("div", null, null, hud);
  Object.assign(big.style, { position: "absolute", left: "150px", right: "150px", top: FORMAT === "yatay" ? "60px" : "250px", textAlign: "center", fontWeight: 900, opacity: 0,
    textShadow: "0 4px 20px #000", background: "rgba(4,7,14,.8)", borderRadius: "26px", padding: "16px 0 20px", transformOrigin: "50% 0" });
  big.innerHTML = `<div style="display:inline-block;background:#e3141b;color:#fff;font-size:30px;letter-spacing:4px;padding:6px 20px;border-radius:10px;text-shadow:none">RÜZGÂR HAMLESİ</div>
    <div class="bn" style="white-space:nowrap;font-size:${FORMAT === "yatay" ? 140 : 168}px;line-height:1;color:#fff;letter-spacing:-3px;margin-top:8px">110 km/sa</div>
    <div class="bm" style="font-size:38px;color:#fff;margin-top:6px">hamle · sürekli 100–110 km/sa</div>`;
  const bn = big.querySelector(".bn");
  const repr = el("div", null, "temsili rota · IMD konum ve tahminlerine göre", hud);
  Object.assign(repr.style, { position: "absolute", right: "40px", bottom: FORMAT === "yatay" ? "18px" : "438px", fontSize: "18px", fontWeight: 700, color: "rgba(255,255,255,.45)" });
  const clock = el("div", null, null, hud);
  Object.assign(clock.style, { position: "absolute", left: "60px", top: FORMAT === "yatay" ? "780px" : "1340px", fontSize: "30px", fontWeight: 800, color: "#fff",
    padding: "12px 20px", borderLeft: "8px solid #e3141b", borderRadius: "6px", background: "rgba(4,7,14,.78)", opacity: 0 });

  const flashDiv = el("div", null, null, hud);
  Object.assign(flashDiv.style, { position: "absolute", inset: "0", background: "radial-gradient(circle at 50% 35%, rgba(220,232,255,.9), rgba(220,232,255,0) 70%)", opacity: 0 });
  const sc = tl.scenes.filter(s => s.tip === "uc3d");
  const sceneAt = t => { let i = 0; for (let k = 0; k < sc.length; k++) if (t >= sc[k].t0) i = k; return i; };
  const hAt = (s, t) => { const [a, b] = s.p.saat || [0, 0]; return lerp(a, b, clamp((t - s.t0) / Math.max(.01, s.t1 - s.t0))); };
  const camFor = (spec, h, u) => {
    const [ex, ez] = pos(h);
    if (spec.mod === "takip") return { p: [ex - spec.geri, spec.yuk, ez + spec.yan], q: [ex, 4, ez] };
    if (spec.mod === "goz") { const a = (spec.aci || 0) + u * (spec.don || 1.2);     // gözün içinden duvara bakan, dönen kamera
      return { p: [ex, spec.yuk || 2.5, ez], q: [ex + 20 * Math.cos(a), (spec.bak || 9), ez + 20 * Math.sin(a)] }; }
    const q = spec.hedef === "goz" ? [ex, 3, ez] : spec.hedef;
    const uu = spec.hizli ? 1 - Math.pow(1 - clamp(u * spec.hizli), 4) : eInOut(u);       // hizli: uzaydan dalış
    const p = spec.konum2 ? spec.konum.map((v, k) => lerp(v, spec.konum2[k], uu)) : spec.konum;
    return { p, q };
  };
  const proj = (x, y, z) => { const v = new T.Vector3(x, y, z).project(cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H, v.z]; };
  const place = (e, x, y, z, on, dx = 0, dy = 0) => { const [sx, sy, sz] = proj(x, y, z); e.style.left = sx + dx + "px"; e.style.top = sy + dy + "px"; e.style.opacity = on && sz < 1 && sx > -200 && sx < W + 50 ? 1 : 0; };
  const hhmm = h => { let m = Math.round((14.5 + h) * 60); const d = 2 + Math.floor(m / 1440); m = ((m % 1440) + 1440) % 1440;
    return `${d} Kasım · ${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")} (IST)`; };

  return t => {
    const i = sceneAt(t), s = sc[i], hd = s.p.hud || {};
    const u = clamp((t - s.t0) / Math.max(.01, s.t1 - s.t0));
    const h = hAt(s, t), [ex, ez] = pos(h), pw = power(h);
    const cur = camFor(s.p.kam, h, u), prev = i > 0 ? camFor(sc[i - 1].p.kam, h, 1) : cur;
    const m = eInOut(clamp((t - s.t0) / Math.min(1.4, Math.max(.6, (s.t1 - s.t0) * .45))));
    const Pc = cur.p.map((v, k) => lerp(prev.p[k], v, m)), Q = cur.q.map((v, k) => lerp(prev.q[k], v, m));
    const sh = hd.sars ? Math.max(0, 1 - (t - s.t0) / 1.2) * 1.6 : 0;
    cam.position.set(Pc[0] + .6 * Math.sin(t * .6) + sh * Math.sin(t * 61), Pc[1] + .4 * Math.sin(t * .45) + sh * Math.sin(t * 47), Pc[2] + sh * Math.cos(t * 53));
    cam.lookAt(Q[0], Q[1], Q[2]);
    // bulut: diferansiyel dönüş (içerisi hızlı), karada zayıflar ve dağılır
    for (let k = 0; k < N; k++) {
      const r0 = meta[k * 3], th0 = meta[k * 3 + 1], y0 = meta[k * 3 + 2];
      const r = r0 * (1 + (1 - pw) * .6), th = th0 - t * .42 - .25 * Math.sin(t * .8 + r0) / (1 + r0 / 10);   // − : saat yönünün tersi; kollar korunur
      P[k * 3] = ex + r * Math.cos(th); P[k * 3 + 1] = y0 * (.4 + .6 * pw); P[k * 3 + 2] = ez + r * Math.sin(th);
    }
    cloudG.attributes.position.needsUpdate = true;
    for (let k = 0; k < HN; k++) { HP[k * 3] = P[k * 15]; HP[k * 3 + 1] = P[k * 15 + 1]; HP[k * 3 + 2] = P[k * 15 + 2]; }
    hazeG.attributes.position.needsUpdate = true;
    if (Math.abs((cloud._pw || 1) - pw) > .01) { cloud._pw = pw;
      for (let k = 0; k < N * 3; k += 3) { CC[k] = lerp(.25, CCw[k], pw); CC[k + 1] = lerp(.55, CCw[k + 1], pw); CC[k + 2] = lerp(1, CCw[k + 2], pw); }
      cloudG.attributes.color.needsUpdate = true; }
    cloud.material.opacity = .62 * (.35 + .65 * pw) * (hd.bulut !== undefined ? hd.bulut : 1);
    const inEye = s.p.kam && s.p.kam.mod === "goz";            // göz içi: yakın noktalar dev olmasın (yavaşlatıyor)
    cloud.material.size = inEye ? .8 : 2.0; haze.visible = !inEye; rain.visible = !inEye;
    // okyanus dalgası
    { const a = ocean.attributes.position.array;
      for (let k = 0; k < a.length; k += 3) { const x = oBase[k], z = oBase[k + 2];
        if (x < coastX(z) + 2) { a[k + 1] = -1; continue; }
        const d = Math.hypot(x - ex, z - ez), st = 2.2 * pw * Math.exp(-d * d / 5000);
        a[k + 1] = .35 * Math.sin(x * .07 + t * 1.8) + .25 * Math.cos(z * .09 + t * 1.3) + st * Math.sin(d * .18 - t * 3.5); }
      ocean.attributes.position.needsUpdate = true; }
    // yağmur
    for (let k = 0; k < RN; k++) { const r = rainM[k * 3], th = rainM[k * 3 + 1] - t * .42, ph = (t * 1.6 + rainM[k * 3 + 2]) % 1;
      const x = ex + r * Math.cos(th), z = ez + r * Math.sin(th), y = 7 * (1 - ph) * (.4 + .6 * pw);
      rainP.set([x, y, z, x - .3, y - 1.4, z], k * 6); }
    rainG.attributes.position.needsUpdate = true; rain.material.opacity = .22 * pw;
    // şimşek: deterministik, ~0,6 sn'de bir; karada seyrekleşir
    let flk = 0;
    flashes.forEach((sp, j) => { const slot = Math.floor(t * 1.7 + j * .37), f = (t * 1.7 + j * .37) - slot;
      const hsh = Math.sin(slot * 12.9898 + j * 78.233) * 43758.5453, rr = hsh - Math.floor(hsh);
      const on = rr < .55 * pw, a = on ? Math.max(0, 1 - f * 6) * (f < .05 ? .6 : 1) : 0;
      const rad = 12 + rr * 50, an = rr * 40;
      sp.position.set(ex + rad * Math.cos(an), 4 + rr * 5, ez + rad * Math.sin(an)); sp.material.opacity = a * .9; flk = Math.max(flk, a * (rr < .2 ? 1 : .3)); });
    flashDiv.style.opacity = flk * .16;
    // göz
    eyeRing.position.set(ex, .3, ez); eyeRing.material.opacity = hd.goz ? .95 : 0;
    // içe akış
    flow.material.opacity = hd.akis ? .95 : 0;
    if (hd.akis) for (let k = 0; k < FL; k++) {
      const arm = k % 8, ph = ((t * .25 + k / FL * 7.3) % 1);
      const r = 90 - ph * 80, th = arm * Math.PI / 4 + Math.log(r) * 2.3 - t * .4;
      flowP[k * 3] = ex + r * Math.cos(th); flowP[k * 3 + 1] = .6 + ph * 2; flowP[k * 3 + 2] = ez + r * Math.sin(th);
    }
    flowG.attributes.position.needsUpdate = true;
    // buharlaşma
    evap.material.opacity = hd.buhar ? .85 : 0;
    if (hd.buhar) for (let k = 0; k < EV; k++) {
      const yy = ((t * .35 + evM[k * 3 + 2]) % 1) * 9;
      evP[k * 3] = ex + evM[k * 3]; evP[k * 3 + 1] = yy; evP[k * 3 + 2] = ez + evM[k * 3 + 1];
    }
    evG.attributes.position.needsUpdate = true;
    // kabarma şeridi (kıyı boyunca, karaya çıkış bölgesinde)
    const sg = hd.kabarma ? eOut(clamp((t - s.t0) / 2)) : 0;
    surge.material.opacity = sg * .38;
    if (sg) { const pa = surgeG.attributes.position;
      for (let k = 0; k < pa.count; k++) { const v = k % 2, row = Math.floor(k / 2), z = lerp(SZ[0], SZ[1], row / 40);
        const near = Math.exp(-Math.pow((z - 2) / 28, 2)); pa.setXYZ(k, coastX(z) + 1 + v * 3, v ? 0 : 3 * near * sg * (1 + .08 * Math.sin(t * 4 + z)), z); }
      pa.needsUpdate = true; }
    // rota + tahmin
    const tp = []; if (hd.rota) for (let k = -48; k <= h; k += .5) { const [x, z] = pos(k); tp.push(x, .4, z); }
    trackG.setAttribute("position", new T.Float32BufferAttribute(tp.length > 3 ? tp : [0, 0, 0, 0, 0, 0], 3)); track.visible = tp.length > 3;
    const fp = []; if (hd.tahmin) for (let k = Math.max(h, -48); k < 18; k += 1) { if (Math.floor(k) % 2) continue; const [x1, z1] = pos(k), [x2, z2] = pos(k + 1); fp.push(x1, .4, z1, x2, .4, z2); }
    fcG.setAttribute("position", new T.Float32BufferAttribute(fp.length ? fp : [0, 0, 0, 0, 0, 0], 3)); fc.visible = fp.length > 0;
    R.render(scene, cam);
    canvas.style.filter = hd.bulanik ? "blur(10px) brightness(.4)" : "none";
    // HUD
    CITIES.forEach((c, k) => place(cityL[k], c[1], 0, c[2], hd.sehir, 0, -14));
    place(eyeL, ex, 3, ez, hd.goz, 30, -60);
    place(surgeL, coastX(2) + 4, 6, 2, hd.kabarma && sg > .5, 30, -40);
    const [lx, lz] = pos(10); place(landL, lx, 0, lz, hd.tahmin, -110, 20);
    big.style.opacity = hd.ruzgar ? 1 : 0;
    big.style.top = hd.ruzgarAlt ? (FORMAT === "yatay" ? "720px" : "1240px") : (FORMAT === "yatay" ? "60px" : "250px");
    big.style.transform = hd.ruzgarAlt ? "scale(.7)" : "none";
    if (hd.ruzgar) bn.textContent = Math.round(lerp(0, 120, eOut(clamp((t - s.t0) / 1.4)))) + " km/sa";
    clock.style.opacity = hd.saat ? 1 : 0;
    if (hd.saat) clock.innerHTML = `<span style="color:#ff4d57">SAAT</span> ${hhmm(h)}`;
    repr.style.opacity = hd.temsili === false ? 0 : (hd.rota || hd.tahmin ? 1 : 0);
  };
};
