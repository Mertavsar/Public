// ================= MİDYE DOLMANIN MİDYESİ (dikey 1080×1920) =================
const EN = false;
// 1 birim ≈ 1 m. Halat çiftliği: yüzeyde şamandıralar, ana halat -1.5 m, çoraplar 6 m sarkıyor. Midyeler ~2 kat büyük çizilir.
const SY = -22;
const DOT = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d"); const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(.45, "rgba(255,255,255,.55)"); r.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
function pts(n, col, size, op) { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(n * 3), 3));
  const m = new THREE.Points(g, new THREE.PointsMaterial({ color: col, size, map: DOT, transparent: true, opacity: op, depthWrite: false })); m.frustumCulled = false; scene.add(m); return m; }
const PR = []; for (let i = 0; i < 9000; i++) PR.push([rnd(), rnd(), rnd(), rnd()]);
// ---- deniz tabanı (çamurlu kum) ----
const bedG = new THREE.PlaneGeometry(400, 400, 160, 160); bedG.rotateX(-Math.PI / 2);
{ const p = bedG.attributes.position, c = []; for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, Math.sin(x * .2 + z * .1) * .4 + Math.sin(x * 1.3) * .05);
    const k = .9 + .1 * Math.sin(x * 2.1 + z * 1.7); c.push(.5 * k, .47 * k, .36 * k); } bedG.setAttribute("color", new THREE.Float32BufferAttribute(c, 3)); bedG.computeVertexNormals(); }
const seabed = new THREE.Mesh(bedG, new THREE.MeshStandardMaterial({ vertexColors: true, color: 0x8a8070, roughness: 1, envMapIntensity: .1 })); seabed.position.y = SY; scene.add(seabed);
const ceil = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshBasicMaterial({ color: 0x8fdcf0, side: THREE.DoubleSide })); ceil.rotation.x = Math.PI / 2; ceil.position.y = -.35; scene.add(ceil);
// ---- midye geometrisi: uzun, damla biçimli, mavi-siyah parlak kabuk ----
function musselGeo(seg = 12, rng = 7) {
  const g = new THREE.SphereGeometry(1, seg, rng * 2); const p = g.attributes.position, c = [];
  for (let i = 0; i < p.count; i++) { let x = p.getX(i), y = p.getY(i), z = p.getZ(i); const u = (x + 1) / 2;   // 0 sivri uç (menteşe) → 1 geniş uç
    const w = Math.pow(Math.sin(Math.PI * Math.pow(u, .7) * .5 + .02), .8); p.setXYZ(i, x * 1.0, y * .5 * w + (y > 0 ? .05 * u : 0), z * .38 * w);
    const ring = .5 + .5 * Math.sin(u * 30); const edge = Math.abs(y) < .04;
    let r = .035 + .025 * ring, gg = .04 + .03 * ring, b = .075 + .05 * ring; if (u < .15) { r += .06; gg += .05; b += .08; } if (u > .9) { r = .2; gg = .16; b = .1; } if (edge) { r = .35; gg = .26; b = .3; }
    c.push(r, gg, b); }
  g.setAttribute("color", new THREE.Float32BufferAttribute(c, 3)); g.computeVertexNormals(); return g; }
const musMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .3, metalness: .15, envMapIntensity: .45 });
// ---- çiftlik düzeni ----
const LINES = [-7, 0, 7], LX0 = -30, LX1 = 30, SOCKD = 1.6, SOCKL = 6, TOP = -1.5;
const SOCKS = []; LINES.forEach(z => { for (let x = LX0 + 1; x < LX1; x += SOCKD) SOCKS.push({ x, z, ph: rnd() * 6.28 }); });
const PER = 90, NMU = SOCKS.length * PER, MUS = new THREE.InstancedMesh(musselGeo(), musMat, NMU); MUS.frustumCulled = false; scene.add(MUS);
const MI = []; for (let s = 0; s < SOCKS.length; s++) for (let k = 0; k < PER; k++) MI.push({ s, v: rnd(), a: rnd() * 6.28, tilt: (rnd() - .5) * 1.4, sc: .8 + rnd() * .4, ph: rnd() * 6.28 });
const ropeM = new THREE.MeshStandardMaterial({ color: 0x7a6a52, roughness: .95, envMapIntensity: .2 });
const backbones = LINES.map(z => { const m = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, LX1 - LX0, 6), ropeM); m.rotation.z = Math.PI / 2; m.position.set(0, TOP, z); scene.add(m); return m; });
const sockCore = new THREE.InstancedMesh(new THREE.CylinderGeometry(.08, .08, SOCKL, 6), ropeM, SOCKS.length); sockCore.frustumCulled = false; scene.add(sockCore);
const netM = new THREE.MeshBasicMaterial({ color: 0x3fa06a, wireframe: true, transparent: true, opacity: .35 });
const sockNet = new THREE.InstancedMesh(new THREE.CylinderGeometry(.42, .42, SOCKL, 10, 14, true), netM, SOCKS.length); sockNet.frustumCulled = false; scene.add(sockNet);
const buoyG = new THREE.CylinderGeometry(.55, .55, 1.2, 18); const buoyM = new THREE.MeshStandardMaterial({ color: 0x1f3fa8, roughness: .45 });
const BUOYS = []; LINES.forEach(z => { for (let x = LX0; x <= LX1; x += 6) BUOYS.push({ x, z }); });
const buoys = new THREE.InstancedMesh(buoyG, buoyM, BUOYS.length); buoys.frustumCulled = false; scene.add(buoys);
const buoyLines = new THREE.InstancedMesh(new THREE.CylinderGeometry(.03, .03, 1.5, 4), ropeM, BUOYS.length); buoyLines.frustumCulled = false; scene.add(buoyLines);
const sw = (s, T) => Math.sin(T * .6 + s.ph) * .12;                     // akıntıda hafif salınım
function sockPoint(s, v, T) { return V(s.x + sw(s, T) * v * 2, TOP - .2 - v * SOCKL, s.z + Math.cos(T * .5 + s.ph) * .06 * v); }
function placeFarm(st, T) {
  const on = !st.noFarm; [MUS, sockCore, sockNet, buoys, buoyLines].forEach(o => o.visible = on); backbones.forEach(b => b.visible = on); if (!on) return;
  const grow = st.grow ?? 1, net = st.net ?? .35, spat = !!st.spat;
  SOCKS.forEach((s, i) => { const c = sockPoint(s, .5, T); dummy.position.copy(c); dummy.rotation.set(0, 0, sw(s, T) * .3); dummy.scale.set(1, 1, 1); dummy.updateMatrix(); sockCore.setMatrixAt(i, dummy.matrix);
    dummy.scale.set(.7 + .5 * grow, 1, .7 + .5 * grow); dummy.updateMatrix(); sockNet.setMatrixAt(i, dummy.matrix); });
  sockCore.instanceMatrix.needsUpdate = sockNet.instanceMatrix.needsUpdate = true; netM.opacity = net;
  const S0 = st.only != null ? st.only : -1;
  for (let i = 0; i < NMU; i++) { const m = MI[i], s = SOCKS[m.s]; let sc = (spat ? .06 : .1 + .14 * grow) * m.sc;
    if (S0 >= 0 && m.s !== S0) sc = st.othersGrow != null ? (.12 + .2 * st.othersGrow) * m.sc : sc;
    if (spat && st.attach != null) { const k = clamp((st.attach - m.v * .6 - m.sc * .2) / .4); sc *= k; }
    const p = sockPoint(s, m.v, T), r = (spat ? .09 : .14 + .16 * grow);
    p.x += Math.cos(m.a) * r; p.z += Math.sin(m.a) * r;
    dummy.position.copy(p); dummy.rotation.set(0, -m.a + Math.PI / 2, -Math.PI / 2 + m.tilt * .6); dummy.scale.setScalar(sc); dummy.updateMatrix(); MUS.setMatrixAt(i, dummy.matrix); }
  MUS.instanceMatrix.needsUpdate = true;
  BUOYS.forEach((b, i) => { const y = waveY(b.x, b.z, T, seaU.uAmp.value) * .7; dummy.position.set(b.x, y + .1, b.z); dummy.rotation.set(Math.PI / 2, 0, 0); dummy.scale.set(1, 1, 1); dummy.updateMatrix(); buoys.setMatrixAt(i, dummy.matrix);
    dummy.position.set(b.x, (y + TOP) / 2, b.z); dummy.rotation.set(0, 0, 0); dummy.updateMatrix(); buoyLines.setMatrixAt(i, dummy.matrix); });
  buoys.instanceMatrix.needsUpdate = buoyLines.instanceMatrix.needsUpdate = true;
}
// ---- doğal yatak: kayalar üzerinde midye kümeleri ----
const P_BED = V(-60, SY, 0); const rocks = new THREE.Group(); scene.add(rocks);
const rockM = new THREE.MeshStandardMaterial({ color: 0x6b6f6a, roughness: .95, flatShading: true, envMapIntensity: .2 });
const RK = []; for (let i = 0; i < 9; i++) { const r = new THREE.Mesh(new THREE.DodecahedronGeometry(1.6 + rnd() * 1.8, 1), rockM); r.scale.y = .6; r.position.set(P_BED.x + (rnd() - .5) * 16, SY + .4, (rnd() - .5) * 10); r.rotation.y = rnd() * 6; rocks.add(r); RK.push(r); }
const NBM = 900, BEDM = new THREE.InstancedMesh(musselGeo(10, 5), musMat, NBM); BEDM.frustumCulled = false; scene.add(BEDM);
{ for (let i = 0; i < NBM; i++) { const r = RK[i % RK.length], a = PR[i][0] * 6.28, e = PR[i][1] * 1.1, R = r.geometry.parameters.radius;
    const p = V(Math.cos(a) * Math.cos(e) * R, Math.sin(e) * R * .6, Math.sin(a) * Math.cos(e) * R).add(r.position);
    dummy.position.copy(p); dummy.rotation.set(PR[i][2] * 6, a, PR[i][3] * 2); dummy.scale.setScalar(.3); dummy.updateMatrix(); BEDM.setMatrixAt(i, dummy.matrix); } }
// ---- büyük midye (yakın plan, aralık açık; içi turuncu) ----
const bigM = new THREE.Group(); scene.add(bigM);
{ const half = musselGeo(48, 24); const top = new THREE.Mesh(half, musMat); top.scale.set(1, .5, 1); top.position.y = .02; bigM.add(top); bigM.userData.top = top;
  const bot = new THREE.Mesh(half, musMat); bot.scale.set(1, .5, 1); bot.position.y = -.02; bigM.add(bot);
  const mantle = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 12), new THREE.MeshStandardMaterial({ color: 0xff9a3c, roughness: .4, emissive: 0x401800 })); mantle.scale.set(.85, .08, .3); mantle.position.x = .1; bigM.add(mantle); bigM.userData.mantle = mantle; }
bigM.visible = false;
// ---- parçacıklar: larva, plankton akışı ----
const NL = 2600, LAR = pts(NL, 0xf3fff0, .06, .9), NPK = 2200, PLK = pts(NPK, 0x9be86a, .09, .85);
// ---- tekne + hasat ----
const mb = makeBoat(0x1f3fa8); mb.scale.setScalar(.6); scene.add(mb);
const hSock = new THREE.Group(); scene.add(hSock);
{ const core = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, SOCKL, 6), ropeM); hSock.add(core); const NH2 = 240, hm = new THREE.InstancedMesh(musselGeo(10, 5), musMat, NH2);
  for (let i = 0; i < NH2; i++) { const a = PR[i][0] * 6.28, v = PR[i][1]; dummy.position.set(Math.cos(a) * .38, (v - .5) * SOCKL, Math.sin(a) * .38); dummy.rotation.set(PR[i][2], -a, Math.PI / 2); dummy.scale.setScalar(.3); dummy.updateMatrix(); hm.setMatrixAt(i, dummy.matrix); }
  hSock.add(hm); }
const deckPile = new THREE.InstancedMesh(musselGeo(10, 5), musMat, 700); deckPile.frustumCulled = false; scene.add(deckPile);
const crt = []; for (let i = 0; i < 6; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(.9, .4, .6), new THREE.MeshStandardMaterial({ color: 0x2b7ad9, roughness: .6 })); scene.add(c); crt.push(c); }
// ---- midye dolma tabağı ----
const P_PL = V(4000, 300, 0); const plate = new THREE.Group(); plate.position.copy(P_PL); scene.add(plate);
{ const wood = new THREE.Mesh(new THREE.BoxGeometry(80, 1, 80), new THREE.MeshStandardMaterial({ color: 0x5a341f, roughness: .55 })); wood.position.y = -.5; plate.add(wood);
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(200, 120), new THREE.MeshStandardMaterial({ color: 0x2f2620, roughness: 1 })); wall.position.set(0, 30, -40); plate.add(wall);
  const pl = new THREE.Mesh(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(5.4, 0), new THREE.Vector2(6.2, .25), new THREE.Vector2(6.6, .45), new THREE.Vector2(6.5, .35), new THREE.Vector2(5.2, .12), new THREE.Vector2(0, .1)], 64),
    new THREE.MeshStandardMaterial({ color: 0x1b3550, roughness: .18, metalness: .1, side: THREE.DoubleSide })); plate.add(pl);
  const half = musselGeo(32, 16), rice = new THREE.MeshStandardMaterial({ color: 0xc8602a, roughness: .65, emissive: 0x2a0c00 });
  const nac = new THREE.MeshStandardMaterial({ color: 0xc8c6e0, roughness: .2, metalness: .5 });
  for (let k = 0; k < 12; k++) { const a = k / 12 * 6.28, r = k % 2 ? 3.6 : 2.4; const g = new THREE.Group(); g.position.set(Math.cos(a) * r, .45, Math.sin(a) * r); g.rotation.y = -a + Math.PI / 2;
    const bot = new THREE.Mesh(half, musMat); bot.scale.set(1.3, .55, 1.3); g.add(bot);
    const inner = new THREE.Mesh(half, nac); inner.scale.set(1.22, .3, 1.15); inner.position.y = .1; g.add(inner);
    const fill = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 10), rice); fill.scale.set(.85, .28, .3); fill.position.y = .25; g.add(fill);
    for (let j = 0; j < 14; j++) { const gr = new THREE.Mesh(new THREE.SphereGeometry(.07, 6, 4), rice); gr.position.set((PR[j + k * 20][0] - .5) * 1.3, .42, (PR[j + k * 20][1] - .5) * .35); gr.scale.set(1.6, .7, .7); g.add(gr); }
    for (let j = 0; j < 4; j++) { const cu = new THREE.Mesh(new THREE.SphereGeometry(.07, 6, 4), new THREE.MeshStandardMaterial({ color: 0x2a1410 })); cu.position.set((PR[j + k * 9][2] - .5) * 1.4, .5, (PR[j + k * 9][3] - .5) * .4); g.add(cu); }
    plate.add(g); }
  const lemM = new THREE.MeshStandardMaterial({ color: 0xffd21a, roughness: .35, emissive: 0x3a3000 }), lemIn = new THREE.MeshStandardMaterial({ color: 0xfff27a, roughness: .5, emissive: 0x2a2a00 });
  for (const [x, z, ry] of [[0, 0, 0], [1.1, .5, 1.3]]) { const h = new THREE.Mesh(new THREE.SphereGeometry(.9, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), lemM); h.rotation.set(Math.PI / 2 + .35, ry, 0); h.position.set(x, .95, z); plate.add(h);
    const f = new THREE.Mesh(new THREE.CircleGeometry(.88, 24), lemIn); f.rotation.copy(h.rotation); f.rotateX(-Math.PI / 2); f.position.copy(h.position); f.translateZ(.005); plate.add(f);
    for (let j = 0; j < 8; j++) { const sg = new THREE.Mesh(new THREE.BoxGeometry(.02, .02, .8), new THREE.MeshBasicMaterial({ color: 0xfff8c8 })); sg.rotation.copy(f.rotation); sg.position.copy(f.position); sg.rotateZ(j / 8 * Math.PI); sg.translateZ(.01); plate.add(sg); } }
  for (let k = 0; k < 40; k++) { const a = rnd() * 6.28, r = rnd() * 4.5; const p = new THREE.Mesh(new THREE.SphereGeometry(.05, 6, 4), new THREE.MeshStandardMaterial({ color: 0x3fae35, emissive: 0x0a2a08 })); p.position.set(Math.cos(a) * r, 1.0, Math.sin(a) * r); plate.add(p); }
  const lamp = new THREE.PointLight(0xffd29a, 150, 0, 1.6); lamp.position.set(6, 14, 8); plate.add(lamp); const rim = new THREE.PointLight(0x9fd0ff, 60, 0, 1.6); rim.position.set(-8, 6, -10); plate.add(rim); }
plate.visible = false;
// ---- harita: Ege, Marmara, Karadeniz ----
function mapSeas(t, a) {
  const c = $("map"); c.style.opacity = a; const g = MP; g.clearRect(0, 0, 1080, 1920); if (a <= 0) return;
  const lon0 = 22, lat0 = 46, span = 21, k = 1080 / span, py = 380; const X = lo => (lo - lon0) * k, Y = la => py + (lat0 - la) * k * 1.25;
  const gr = g.createLinearGradient(0, 0, 0, 1920); gr.addColorStop(0, "#1f86b8"); gr.addColorStop(1, "#155f88"); g.fillStyle = gr; g.fillRect(0, 0, 1080, 1920);
  for (const o of DUNYA) { const xs = o.r; if (xs.every(([lo]) => lo < lon0 - 8 || lo > lon0 + span + 8)) continue;
    g.beginPath(); xs.forEach(([lo, la], i) => i ? g.lineTo(X(lo), Y(la)) : g.moveTo(X(lo), Y(la))); g.closePath(); g.fillStyle = o.c === "TUR" ? "#f1ebdc" : "#8d9a9e"; g.fill(); g.strokeStyle = "#0e3550"; g.lineWidth = 1.5; g.stroke(); }
  const L = [[25.3, 38.6, "EGE", .2], [28.0, 40.75, "MARMARA", .7], [34.5, 42.9, "KARADENİZ", 1.2]];
  g.textAlign = "center"; L.forEach(([lo, la, nm, t0]) => { const e = sm((t - t0) / .35); if (e <= 0) return; g.globalAlpha = e;
    for (let j = 0; j < 7; j++) { const aa = PR[j][0] * 6.28, rr = PR[j][1] * 40; g.fillStyle = "#0b1d2a"; g.beginPath(); g.ellipse(X(lo) + Math.cos(aa) * rr, Y(la) + Math.sin(aa) * rr * .6, 11, 6, aa, 0, 7); g.fill(); }
    const r = 30 + 40 * ((t * 1.1 + t0) % 1); g.strokeStyle = `rgba(255,213,74,${1 - (r - 30) / 40})`; g.lineWidth = 5; g.beginPath(); g.arc(X(lo), Y(la), r, 0, 7); g.stroke();
    g.font = nm === "MARMARA" ? "52px AN" : "64px AN"; g.fillStyle = "#fff"; g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 12; g.fillText(nm, X(lo), Y(la) - 70); g.shadowBlur = 0; g.globalAlpha = 1; });
  g.textAlign = "left";
}

// ================= çekimler =================
const K = (o) => base(Object.assign({ tuna: "hide", ham: "hide", mood: "day" }, o));
const UW = (p, tg, fov = 50) => camSet(p, tg, fov);
const SK = (i) => SOCKS[i];                                               // 0..: 1. hat; orta hat = 37.. ; seçilen çorap
const MID = 37 + 18;                                                      // orta hattın ortası (x ≈ -0.2, z = 0)
const near = (i, dx, dy, dz) => { const s = SOCKS[i]; return V(s.x + dx, TOP - 3.5 + dy, s.z + dz); };
const S4 = {
  hook: (lt, d) => { const u = sm(lt / d); UW(V(lerp(-6, -2, u), -6, 12), V(lerp(-6, -2, u) + 4, -5, 0), 62); return K({}); },
  nofeed: (lt, d) => { const s = SOCKS[MID]; UW(V(s.x + 1.4, TOP - 3 + .2, s.z + 2.2), V(s.x, TOP - 3.2, s.z), 44); return K({ plk: 1, gape: 1 }); },
  step: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-36, -30, u), lerp(26, 22, u), lerp(30, 26, u)), V(-2, -3, 0), 52); return K({ xray: .5, boat: { p: V(-20, 0, 13), h: 0, run: true } }); },
  cta: (lt, d) => { const u = sm(lt / d); UW(V(lerp(2, 4, u), -7, 10), V(lerp(2, 4, u) + 3, -5, 0), 60); return K({ cta: lt, ctaD: d }); },
  name: (lt, d) => { UW(V(.8, -9.6, 3.4), V(0, -10, 0), 36); return K({ noFarm: 1, big: lt }); },
  live: (lt) => { camSet(V(0, 300, 1), V(0, 0, 0)); return K({ seas: lt, noFarm: 1 }); },
  two: (lt, d) => { if (lt < d * .5) { const u = sm(lt / (d * .5)); UW(V(P_BED.x + lerp(3, 1, u), SY + 3, lerp(9, 8, u)), V(P_BED.x, SY + .8, 0), 54); return K({}); } const u = sm((lt - d * .5) / (d * .5)); UW(V(lerp(-8, -5, u), -6, 11), V(lerp(-8, -5, u) + 4, -5, 0), 62); return K({}); },
  howq: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-14, -10, u), 4, lerp(20, 16, u)), V(0, 0, 0), 52); return K({ grow: 1 }); },
  rope: (lt, d) => { const u = ease(clamp(lt / (d * .8))); UW(V(-1, -4, 9), V(0, -4.5, 0), 58); return K({ noFarm: 1, single: u, boat: { p: V(3, 0, -2), h: Math.PI / 2 } }); },
  larvae: (lt, d) => { UW(V(lt * .2, -4, 3.2), V(lt * .2, -4.2, 0), 46); return K({ noFarm: 1, single: 1, lar: 1 }); },
  attach: (lt, d) => { UW(V(.6, -3.6, 2.6), V(0, -4.2, 0), 46); return K({ noFarm: 1, single: 1, lar: 1, attach: clamp(lt / (d * .9)), spat: 1, singleSpat: 1 }); },
  like: (lt, d) => { UW(V(.6, -3.6, 2.6), V(0, -4.2, 0), 46); return K({ noFarm: 1, single: 1, lar: .5, attach: 1, spat: 1, singleSpat: 1, chip: ["like", fadeIO(lt, d)] }); },
  socks: (lt, d) => { const s = SOCKS[MID], u = sm(lt / d); UW(V(s.x + lerp(2.6, 2, u), -4, s.z + lerp(4.2, 3.4, u)), V(s.x, -4.5, s.z), 50); return K({ grow: 0, net: lerp(0, .7, sm(lt / 1.2)) }); },
  longline: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-34, -28, u), lerp(10, 8, u), lerp(24, 20, u)), V(-6, -4, 0), 56); return K({ xray: .5, grow: .4, net: .6 }); },
  whofeeds: (lt, d) => { const s = SOCKS[MID]; UW(V(s.x + 1.8, TOP - 3 + .3, s.z + 2.6), V(s.x, TOP - 3.2, s.z), 44); return K({ grow: .7 }); },
  secret: (lt, d) => { const u = ease(clamp(lt / d)); UW(V(lerp(1.4, .6, u), -10 + lerp(.4, .25, u), lerp(3.2, 1.8, u)), V(.2, -10, 0), 38); return K({ noFarm: 1, big: 2, gapeK: u }); },
  filter: (lt, d) => { UW(V(.9, -9.7, 2.2), V(.1, -10, 0), 40); return K({ noFarm: 1, big: 2, gapeK: 1, plkBig: 1 }); },
  liters: (lt, d) => { UW(V(2.2, -9.4, 4.6), V(.6, -9.6, 0), 44); return K({ noFarm: 1, big: 2, gapeK: 1, plkBig: 1, liters: lt }); },
  seafeeds: (lt, d) => { const u = sm(lt / d); UW(V(lerp(-10, -6, u), -8, 14), V(-2, -5, 0), 62); return K({ plk: 1, plkWide: 1 }); },
  growth: (lt, d) => { const s = SOCKS[MID]; UW(V(s.x + 2.4, -4.2, s.z + 3.6), V(s.x, -4.6, s.z), 50); return K({ grow: sm(lt / (d * .9)), net: .6 }); },
  kg: (lt, d) => { const s = SOCKS[MID]; UW(V(s.x + 1.6, -4.2, s.z + 2.6), V(s.x, -4.4, s.z), 48); return K({ grow: 1, net: .5, kg: lt }); },
  harvest: (lt, d) => { const u = ease(clamp(lt / (d * .5))), k = clamp((lt - d * .5) / (d * .4)); camSet(V(10, 9, 14), V(1, 1.5, 0), 50);
    return K({ boat: { p: V(0, 0, 0), h: 0 }, hsock: u, pile: k, crates: k }); },
  plate: (lt, d) => { const u = sm(lt / d), a = .4 + u * .5; camSet(P_PL.clone().add(V(Math.cos(a) * 12, lerp(10, 8.5, u), Math.sin(a) * 12)), P_PL.clone().add(V(0, .5, 0)), 44); return K({ plateOn: 1, noFarm: 1 }); },
  comment: (lt, d) => { const u = sm(lt / d); UW(V(lerp(8, 10, u), -7, 10), V(lerp(8, 10, u) + 3, -5, 0), 60); return K({ chip: ["comment", fadeIO(lt, d)] }); },
  loop: (lt, d) => { const u = sm(lt / d); UW(V(lerp(-14, -6, u), -6, 12), V(lerp(-14, -6, u) + 4, -5, 0), 62); return K({}); },
};
for (const k in S4) S[k] = S4[k];

const singleRope = new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, SOCKL, 6), ropeM); scene.add(singleRope);
const NSP = 600, SPAT = new THREE.InstancedMesh(musselGeo(8, 4), musMat, NSP); SPAT.frustumCulled = false; scene.add(SPAT);
function apply2(st, T) {
  placeHamsi({ ham: "hide" }, T);
  [predator, plank, bigH, harbor, kulac, brail, crates, pblock, sCone, RINGS, pline].forEach(o => { if (o && o.visible !== undefined && !Array.isArray(o)) o.visible = false; }); crew.forEach(o => o.visible = false); pulses.forEach(o => o.visible = false);
  putBoat(mb, st.boat || null, T);
  const under = camera.position.y < 0; ceil.visible = under; if (under) { ceil.position.set(camera.position.x, -.35, camera.position.z); scene.fog.color.set(0x2f9cc4); scene.fog.density = .045; renderer.toneMappingExposure = 1.0; }
  seabed.visible = !st.plateOn; plate.visible = !!st.plateOn; if (st.plateOn) { scene.fog.density = 0; renderer.toneMappingExposure = 1.05; }
  placeFarm(st, T);
  rocks.visible = BEDM.visible = !st.noFarm;
  // tek ip (yavru tutunması)
  singleRope.visible = st.single != null; if (singleRope.visible) { const L = SOCKL * st.single; singleRope.scale.y = Math.max(.01, st.single); singleRope.position.set(0, -1 - L / 2, 0); }
  SPAT.visible = !!st.singleSpat; if (SPAT.visible) { for (let i = 0; i < NSP; i++) { const r = PR[i + 100], a = r[0] * 6.28, v = r[1]; const k = clamp((st.attach - v * .5 - r[2] * .3) / .3);
      dummy.position.set(Math.cos(a) * .07, -1 - v * SOCKL, Math.sin(a) * .07); dummy.rotation.set(r[3] * 2, -a, Math.PI / 2); dummy.scale.setScalar(.035 * k); dummy.updateMatrix(); SPAT.setMatrixAt(i, dummy.matrix); } SPAT.instanceMatrix.needsUpdate = true; }
  // larvalar
  LAR.visible = !!st.lar; if (LAR.visible) { const p = LAR.geometry.attributes.position; for (let i = 0; i < NL; i++) { const r = PR[i + 1000]; let x = (r[0] - .5) * 10 + Math.sin(T * .4 + r[3] * 9) * .4, y = -1 - r[1] * 7, z = (r[2] - .5) * 6 + Math.cos(T * .3 + r[3] * 7) * .3;
      if (st.attach != null && i % 3 === 0) { const k = clamp((st.attach - r[1] * .5) / .4); x = lerp(x, Math.cos(r[0] * 6.28) * .08, k); z = lerp(z, Math.sin(r[0] * 6.28) * .08, k); } p.setXYZ(i, x, y, z); } p.needsUpdate = true; LAR.material.opacity = .9 * st.lar; }
  // plankton
  PLK.visible = !!(st.plk || st.plkBig); if (PLK.visible) { const p = PLK.geometry.attributes.position;
    for (let i = 0; i < NPK; i++) { const r = PR[i + 4000]; let x, y, z;
      if (st.plkBig) { const s = (T * .35 + r[0]) % 1; const sx = 3.5 - s * 3.4, spread = (1 - s) * 1.4; x = .2 + sx; y = -10 + (r[1] - .5) * spread * .6 + .02; z = (r[2] - .5) * spread; }
      else if (st.plkWide) { x = (r[0] - .5) * 40 + Math.sin(T * .3 + r[3] * 9) * .5; y = -1 - r[1] * 12; z = (r[2] - .5) * 20; }
      else { const s = SOCKS[MID]; const f = (T * .3 + r[0]) % 1; const R = (1 - f) * 2.2 + .3, a = r[1] * 6.28; x = s.x + Math.cos(a) * R; y = TOP - 3.2 + (r[2] - .5) * 4 * (1 - f * .5); z = s.z + Math.sin(a) * R; }
      p.setXYZ(i, x, y, z); } p.needsUpdate = true; PLK.material.size = st.plkBig ? .05 : .09; }
  // büyük midye
  bigM.visible = st.big != null; if (bigM.visible) { bigM.position.set(0, -10, 0); const gk = st.big === 2 ? (st.gapeK ?? 0) : .2 + .1 * Math.sin(T); bigM.userData.top.rotation.z = gk * .22; bigM.userData.top.position.y = .02 + gk * .06;
    bigM.rotation.set(.15, st.big === 2 ? -.5 : -.6 + st.big * .3, .05); bigM.scale.setScalar(1.2); }
  // hasat
  hSock.visible = st.hsock != null; if (hSock.visible) { const a = V(-5, 2.6, 0).multiplyScalar(.6).applyMatrix4(mb.matrixWorld); hSock.position.set(a.x - 1.2, lerp(-4, 4.2, st.hsock), a.z + 2.6); hSock.rotation.z = lerp(0, -.5, st.hsock); }
  deckPile.visible = (st.pile || 0) > 0; if (deckPile.visible) { for (let i = 0; i < 700; i++) { const r = PR[i + 7000], a = r[0] * 6.28, rr = Math.sqrt(r[1]) * 2.2, h = (1 - rr / 2.2) * 1.2;
      const p = V(-3 + Math.cos(a) * rr * 1.4, 2.3 + r[2] * h, Math.sin(a) * rr).multiplyScalar(1).applyMatrix4(mb.matrixWorld); dummy.position.copy(p); dummy.rotation.set(r[1] * 6, r[2] * 6, r[3] * 6); dummy.scale.setScalar(r[3] < st.pile ? .2 : 0); dummy.updateMatrix(); deckPile.setMatrixAt(i, dummy.matrix); } deckPile.instanceMatrix.needsUpdate = true; }
  crt.forEach((c, i) => { const v = (st.crates || 0) > i / 6; c.visible = v; if (v) { c.position.copy(V(-9 + (i % 3) * 1.6, 2.6, i < 3 ? -1.4 : 1.4).applyMatrix4(mb.matrixWorld)); c.rotation.y = mb.rotation.y; } });
  if (st.seas != null) mapSeas(st.seas, sm(st.seas / .3));
  const big2 = (txt, al) => { LN.save(); LN.globalAlpha = al; LN.textAlign = "center"; LN.font = "220px AN"; LN.fillStyle = "#fff"; LN.shadowColor = "rgba(0,0,0,.5)"; LN.shadowBlur = 30; LN.fillText(txt, 540, 560); LN.restore(); LN.textAlign = "left"; };
  if (st.liters != null) { const n = Math.min(5, Math.floor(st.liters / .45) + 1); big2(`${n} LİTRE`, sm(st.liters / .3)); }
  if (st.kg != null) { const n = Math.min(8, Math.floor(st.kg / .3) + 1); big2(`${n} KG`, sm(st.kg / .3)); }
}
const _applyBase = apply; apply = (st, T) => { _applyBase(st, T); apply2(st, T); };
