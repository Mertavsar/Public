// ================= KUM MİDYESİ çekimleri (dikey 1080×1920) =================
// Ölçek: 1 birim ≈ 1 m. Su derinliği 14 m. Midyeler görünürlük için ~3 kat büyük çizilir.
const EN = location.search.includes("en=1");
if (EN) { document.querySelectorAll("#ctaLogo,#logo").forEach(e => e.src = "logo_en.jpg"); document.querySelector("#cta .nm").innerHTML = "Sea Secrets<small>Fishing, explained simply</small>"; $("bSh").textContent = "↗ Share";
  CHIPS.like = "<i>❤</i> Like if it's useful"; CHIPS.comment = "<i>💬</i> Pick the next one"; }
const SY = -14;                                   // kum tabanı
const CL = .1;                                    // midye yarıçapı (çizim)
// ---- kum ----
const sandGeo = new THREE.PlaneGeometry(420, 420, 260, 260); sandGeo.rotateX(-Math.PI / 2);
{ const p = sandGeo.attributes.position, c = []; for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i);
    const h = Math.sin(x * 1.7 + Math.sin(z * .3) * 2) * .05 + Math.sin(x * .21 + z * .17) * .35 + Math.sin(z * .13) * .25; p.setY(i, h);
    const k = .92 + .08 * Math.sin(x * 3.1 + z * 2.3); c.push(.66 * k, .55 * k, .38 * k); }
  sandGeo.setAttribute("color", new THREE.Float32BufferAttribute(c, 3)); sandGeo.computeVertexNormals(); }
const sandH = (x, z) => Math.sin(x * 1.7 + Math.sin(z * .3) * 2) * .05 + Math.sin(x * .21 + z * .17) * .35 + Math.sin(z * .13) * .25;
const sand = new THREE.Mesh(sandGeo, new THREE.MeshStandardMaterial({ vertexColors: true, color: 0x8f8068, roughness: .95, envMapIntensity: .1 })); sand.position.y = SY; scene.add(sand);
const sandAt = (x, z) => SY + sandH(x, z);
// ---- midye geometrisi (iki kabuk, halka + zikzak desen) ----
function clamGeo(seg = 14, rng = 7) {
  const g = new THREE.SphereGeometry(1, seg, rng * 2); const p = g.attributes.position, c = [];
  for (let i = 0; i < p.count; i++) { let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const r = Math.hypot(x + 1, z) / 2;                                    // menteşeden uzaklık
    y *= .42 * (1 - .25 * r); x *= 1.0; z *= .88 - .1 * (x + 1) * .5; p.setXYZ(i, x, y, z);
    const ring = .5 + .5 * Math.sin(r * 46), zig = Math.sin(Math.atan2(z, x + 1) * 26 + r * 8) > .55 && r > .25;
    let cr = .97 - .12 * ring, cg = .86 - .16 * ring, cb = .68 - .2 * ring; if (r > .72) { cg *= .9; cb *= .8; } if (zig) { cr = .58; cg = .27; cb = .12; } if (Math.abs(y) < .03) { cr *= .7; cg *= .7; cb *= .7; }
    c.push(cr, cg, cb); }
  g.setAttribute("color", new THREE.Float32BufferAttribute(c, 3)); g.computeVertexNormals(); return g; }
const clamMat = new THREE.MeshStandardMaterial({ vertexColors: true, color: 0xe2d6c2, roughness: .4, metalness: .05, envMapIntensity: .3 });
// ---- tarla: kafes yolundaki ve çevredeki midyeler ----
const X0 = -24, X1 = 34, W2 = 1.55;               // kafes yolu |z| < W2
const NC = 3200, CI = [];
for (let i = 0; i < NC; i++) { const path = i < 1500; const x = X0 + rnd() * (X1 - X0), z = path ? (rnd() * 2 - 1) * (W2 - .1) : (rnd() < .5 ? -1 : 1) * (W2 + .2 + rnd() * 9);
  CI.push({ x, z, ry: rnd() * 6.28, rz: (rnd() - .5) * .9, bury: .25 + rnd() * .45, small: path && rnd() < .3, path, s: .85 + rnd() * .3, ph: rnd() * 6.28, r1: rnd(), r2: rnd(), r3: rnd() }); }
{ const pb = CI.filter(c => c.path && !c.small).sort((a, b) => a.x - b.x); pb.forEach((c, k) => c.rank = k); CI.NBIG = pb.length; }
const CLAMS = new THREE.InstancedMesh(clamGeo(), clamMat, NC); CLAMS.frustumCulled = false; scene.add(CLAMS);
// büyük tek midye (yakın plan)
const bigClam = new THREE.Mesh(clamGeo(64, 32), new THREE.MeshStandardMaterial({ vertexColors: true, color: 0xe6dac6, roughness: .3, metalness: .05, envMapIntensity: .3 })); bigClam.visible = false; scene.add(bigClam);
// ---- hidrolik kafes (direç) ----
const DL = 2.6, DW = 3.5, DH = 1.1;               // ağız +x yönünde
const DR = new THREE.Group(); scene.add(DR);
const ironM = new THREE.MeshStandardMaterial({ color: 0x59636b, metalness: .75, roughness: .35 });
const barM = new THREE.MeshStandardMaterial({ color: 0x8e979e, metalness: .8, roughness: .3, emissive: 0x000000 });
const bx = (sx, sy, sz, x, y, z, m = ironM) => { const o = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), m); o.position.set(x, y, z); DR.add(o); return o; };
const cy = (r, l, x, y, z, ax, m = ironM) => { const o = new THREE.Mesh(new THREE.CylinderGeometry(r, r, l, 8), m); o.position.set(x, y, z); if (ax === "x") o.rotation.z = Math.PI / 2; if (ax === "z") o.rotation.x = Math.PI / 2; DR.add(o); return o; };
// çerçeve
for (const y of [0, DH]) for (const z of [-DW / 2, DW / 2]) cy(.05, DL, -DL / 2, y, z, "x");
for (const x of [0, -DL]) for (const y of [0, DH]) cy(.05, DW, x, y, 0, "z");
for (const x of [0, -DL / 2, -DL]) for (const z of [-DW / 2, DW / 2]) cy(.05, DH, x, DH / 2, z);
// yan ve üst ızgara
for (let i = 1; i < 9; i++) { const x = -DL * i / 9; for (const z of [-DW / 2, DW / 2]) cy(.022, DH, x, DH / 2, z); cy(.022, DW, x, DH, 0, "z"); }
cy(.022, DL, -DL / 2, DH, 0, "x"); cy(.022, DL, -DL / 2, DH * .5, -DW / 2, "x"); cy(.022, DL, -DL / 2, DH * .5, DW / 2, "x");
// TABAN ÇUBUKLARI (eleme)
const floorBars = []; for (let i = 0; i <= 22; i++) floorBars.push(cy(.026, DL, -DL / 2, .02, -DW / 2 + DW * i / 22, "x", barM));
// bıçak + kızaklar + meme borusu
const blade = bx(.04, .14, DW, .06, -.05, 0); blade.rotation.z = -.5;
for (const z of [-DW / 2 - .1, DW / 2 + .1]) { const k = bx(DL + .5, .08, .14, -DL / 2 + .1, -.1, z); const nose = bx(.5, .08, .14, .45, .05, z); nose.rotation.z = .5; }
cy(.09, DW, .02, DH + .02, 0, "z", new THREE.MeshStandardMaterial({ color: 0xd9a21a, metalness: .4, roughness: .4 }));
const NOZ = []; for (let i = 0; i < 9; i++) { const z = -DW / 2 + .2 + i * (DW - .4) / 8; const n = cy(.035, .5, .1, DH - .2, z, null, ironM); n.rotation.z = .5; NOZ.push(z); }
DR.visible = false;
const ceil = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshBasicMaterial({ color: 0x8fdcf0, side: THREE.DoubleSide })); ceil.rotation.x = Math.PI / 2; ceil.position.y = -.35; ceil.visible = false; scene.add(ceil);
// ---- tekne, halat, hortum ----
const kb = makeBoat(0xe3141b); kb.scale.setScalar(.72); scene.add(kb);
const wire = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshStandardMaterial({ color: 0x2a2d30, roughness: .7 })); wire.frustumCulled = false; scene.add(wire);
const hoseK = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshStandardMaterial({ color: 0xffb21a, roughness: .5 })); hoseK.frustumCulled = false; scene.add(hoseK);
let hoseKC = null;
// ---- parçacıklar: kum bulutu, su jetleri, hortum akışı, düşen kum ----
const DOT = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d"); const r = g.createRadialGradient(32, 32, 0, 32, 32, 32); r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(.5, "rgba(255,255,255,.6)"); r.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
function pts(n, col, size, op) { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(n * 3), 3));
  const m = new THREE.Points(g, new THREE.PointsMaterial({ color: col, size, map: DOT, transparent: true, opacity: op, depthWrite: false })); m.frustumCulled = false; scene.add(m); return m; }
const NSD = 4200, SAND = pts(NSD, 0xc9ad7a, .22, .5), NJ = 900, JET = pts(NJ, 0xeafcff, .07, .9), NF = 500, FLOW = pts(NF, 0xbff4ff, .22, .95), NDR = 900, DROP = pts(NDR, 0xcdb68a, .07, .8);
const PR = []; for (let i = 0; i < 5000; i++) PR.push([rnd(), rnd(), rnd(), rnd()]);
// ---- güverte yığını + büyük çuvallar ----
const NPL = 900, PILE = new THREE.InstancedMesh(clamGeo(10, 5), clamMat, NPL); PILE.frustumCulled = false; scene.add(PILE);
const bags = []; for (let i = 0; i < 10; i++) { const g = new THREE.Group(); const b = new THREE.Mesh(new THREE.BoxGeometry(1.1, 1.05, 1.1), new THREE.MeshStandardMaterial({ color: 0xf2f2ee, roughness: .85 })); b.position.y = .52; g.add(b);
  for (const [x, z] of [[-.4, -.4], [.4, -.4], [-.4, .4], [.4, .4]]) { const l = new THREE.Mesh(new THREE.TorusGeometry(.12, .03, 6, 10, Math.PI), new THREE.MeshStandardMaterial({ color: 0x2a7ad9 })); l.position.set(x, 1.06, z); g.add(l); }
  scene.add(g); bags.push(g); }
// ---- makarna tabağı (vongole) ----
const P_PL = V(4000, 300, 0); const plate = new THREE.Group(); plate.position.copy(P_PL); scene.add(plate);
{ const wood = new THREE.Mesh(new THREE.BoxGeometry(80, 1, 80), new THREE.MeshStandardMaterial({ color: 0x5a341f, roughness: .55 })); wood.position.y = -.5; plate.add(wood);
  const cloth = new THREE.Mesh(new THREE.BoxGeometry(14, .05, 30), new THREE.MeshStandardMaterial({ color: 0xc4482e, roughness: .9 })); cloth.position.set(-7, .03, 0); plate.add(cloth);
  const pl = new THREE.Mesh(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(4.2, 0), new THREE.Vector2(4.7, .3), new THREE.Vector2(6.2, .9), new THREE.Vector2(6.4, 1.0), new THREE.Vector2(6.3, .82), new THREE.Vector2(4.6, .2), new THREE.Vector2(0, .14)], 64),
    new THREE.MeshStandardMaterial({ color: 0x1b3550, roughness: .18, metalness: .1, side: THREE.DoubleSide })); pl.position.y = .06; plate.add(pl);
  const pm = new THREE.MeshStandardMaterial({ color: 0xeea21a, roughness: .3, emissive: 0x221200, envMapIntensity: .6 });
  for (let k = 0; k < 90; k++) { const pts2 = []; const r0 = .3 + rnd() * 3.2, a0 = rnd() * 6.28, turns = .7 + rnd() * 1.2;
    for (let s = 0; s <= 24; s++) { const u = s / 24, a = a0 + u * turns * 6.28, r = r0 * (1 - .3 * Math.sin(u * 3.14)) + Math.sin(u * 9 + k) * .2; pts2.push(V(Math.cos(a) * r, .45 + (1 - r / 4) * 1.4 + u * .25 + Math.sin(u * 7 + k) * .08, Math.sin(a) * r)); }
    const t = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts2), 40, .055, 6), pm); plate.add(t); }
  const sh = clamGeo(24, 12);
  for (let k = 0; k < 14; k++) { const a = k / 14 * 6.28 + rnd() * .3, r = 1.2 + rnd() * 2.4; const g = new THREE.Group(); g.position.set(Math.cos(a) * r, 1.6 + (1 - r / 4) * .8, Math.sin(a) * r); g.rotation.y = rnd() * 6.28;
    const top = new THREE.Mesh(sh, clamMat); top.scale.setScalar(.42); top.rotation.z = -1.1; top.position.set(-.35, .25, 0); g.add(top);
    const bot = new THREE.Mesh(sh, clamMat); bot.scale.setScalar(.42); bot.position.y = .02; g.add(bot);
    const meat = new THREE.Mesh(new THREE.SphereGeometry(.13, 12, 8), new THREE.MeshStandardMaterial({ color: 0xd9733a, roughness: .35, emissive: 0x2a0c00 })); meat.scale.y = .5; meat.position.y = .14; g.add(meat); plate.add(g); }
  for (let k = 0; k < 130; k++) { const a = rnd() * 6.28, r = rnd() * 3.6, chili = k % 4 === 0; const p = new THREE.Mesh(chili ? new THREE.BoxGeometry(.07, .02, .05) : new THREE.SphereGeometry(.045, 6, 4), new THREE.MeshStandardMaterial({ color: chili ? 0xe3141b : 0x3fae35, emissive: chili ? 0x3a0000 : 0x0a2a08 })); p.position.set(Math.cos(a) * r, 2.1 + (1 - r / 4) * .4, Math.sin(a) * r); plate.add(p); }
  const fork = new THREE.Mesh(new THREE.BoxGeometry(.35, .08, 9), new THREE.MeshStandardMaterial({ color: 0xd8dde0, metalness: .9, roughness: .2 })); fork.position.set(-8, .12, 1); plate.add(fork);
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(200, 120), new THREE.MeshStandardMaterial({ color: 0x3b2a22, roughness: 1 })); wall.position.set(0, 30, -40); plate.add(wall);
  const lamp = new THREE.PointLight(0xffd29a, 150, 0, 1.6); lamp.position.set(6, 14, 8); plate.add(lamp); const rim = new THREE.PointLight(0x9fd0ff, 60, 0, 1.6); rim.position.set(-8, 6, -10); plate.add(rim); }
plate.visible = false;

// ---- kafes kinematiği ----
const VD = 1.1;                                   // kafes hızı m/s
function dState(st) { return st.dr; }
function placeDredge(st, T) {
  const d = st.dr; DR.visible = !!d; wire.visible = hoseK.visible = !!d && !d.noLines;
  if (!d) return;
  const mx = d.x, y = d.y ?? sandAt(mx, 0) + .1;
  DR.position.set(mx, y, 0); DR.rotation.set(0, 0, d.tilt || 0); DR.updateMatrixWorld(true);
  floorBars.forEach(b => { b.material.emissive.set(st.glowBars ? 0xff7a00 : 0x000000); b.material.emissiveIntensity = st.glowBars ? 1.4 : 1; });
  if (!d.noLines) { const st0 = V(-10.5, 8, 0).multiplyScalar(.72).applyMatrix4(kb.matrixWorld); const a = V(.1, DH * .6, 0).applyMatrix4(DR.matrixWorld);
    const mid = st0.clone().lerp(a, .5); mid.y -= 1.2; wire.geometry.dispose(); wire.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([st0, mid, a]), 40, .045, 6);
    const h0 = V(-6, 3, 1.6).multiplyScalar(.72).applyMatrix4(kb.matrixWorld), h1 = V(.05, DH + .05, .6).applyMatrix4(DR.matrixWorld); const hm = h0.clone().lerp(h1, .5); hm.y -= 2.2; hm.z += 1.5;
    hoseKC = new THREE.CatmullRomCurve3([h0, hm, h1.clone().add(V(-.6, .8, 0)), h1]); hoseK.geometry.dispose(); hoseK.geometry = new THREE.TubeGeometry(hoseKC, 80, .11, 8); }
}
function placeClams(st, T) {
  const d = st.dr, mx = d && !d.lifted ? d.x : -999, cap = d && d.lifted ? d.capX : mx, fillK = d ? (d.fill ?? null) : null;
  let nBigIn = 0; if (d) for (const c of CI) if (c.path && !c.small && c.x < cap) nBigIn++;
  for (let i = 0; i < NC; i++) { const c = CI[i]; let p, s = CL * c.s * (st.clamScale || 1), rx = 0, ry = c.ry, rz = c.rz;
    const inCage = d && c.path && c.x < cap;
    if (st.noField) { dummy.scale.setScalar(0); dummy.position.set(0, -900, 0); dummy.updateMatrix(); CLAMS.setMatrixAt(i, dummy.matrix); continue; }
    if (!inCage) { p = V(c.x, sandAt(c.x, c.z) + CL * (.5 - c.bury) * .9, c.z); if (st.jetHit && Math.abs(c.x - st.jetHit) < 3) { p.y += Math.max(0, Math.sin(T * 3 + c.ph)) * .3 * (1 - Math.abs(c.x - st.jetHit) / 3); ry += T; } }
    else { const age = (cap - c.x) / VD;                 // kafese gireli kaç sn
      const into = clamp(age / .45);
      const slot = V(-.25 - c.r1 * (DL - .5), .08, (c.r2 * 2 - 1) * (DW / 2 - .2));
      if (c.small) { const f = clamp((age - .6) / .7);   // aradan düşer
        if (f <= 0) slot.y = .1; else if (f >= 1) { p = V(c.x + .8, sandAt(c.x + .8, c.z) + .02, c.z); }
        if (!p) { const w = slot.clone().applyMatrix4(DR.matrixWorld); if (f > 0) { w.y = lerp(w.y, sandAt(w.x, w.z), f * f); w.x = lerp(w.x, c.x + .8, f); } p = w; rx = T * 3 + c.ph; } }
      else { const layer = Math.floor(c.rank / 70); slot.y = .1 + (layer % 6) * .12 + c.r3 * .05; if (d.full) slot.y = .1 + c.r3 * (DH - .2);
        p = slot.applyMatrix4(DR.matrixWorld); ry = c.ry + T * .2; rx = c.ph; }
      if (into < 1) { const g = V(c.x, sandAt(c.x, c.z), c.z); p = g.lerp(p, ease(into)); p.y += Math.sin(into * Math.PI) * .5; rx += into * 4; }
      if (d.lifted && !c.small && d.dump > 0) { const k = clamp((d.dump - c.r1 * .5) / .5); if (k > 0) { dummy.scale.setScalar(0); dummy.position.set(0, -900, 0); dummy.updateMatrix(); CLAMS.setMatrixAt(i, dummy.matrix); continue; } } }
    dummy.position.copy(p); dummy.rotation.set(rx, ry, rz); dummy.scale.set(s, s, s); dummy.updateMatrix(); CLAMS.setMatrixAt(i, dummy.matrix); }
  CLAMS.instanceMatrix.needsUpdate = true;
}
function placeParticles(st, T) {
  const d = st.dr, on = d && d.jets && !d.lifted; SAND.visible = JET.visible = DROP.visible = !!on; FLOW.visible = !!(d && !d.noLines && hoseKC);
  if (on) { const sp = SAND.geometry.attributes.position, jp = JET.geometry.attributes.position, dp = DROP.geometry.attributes.position, mv = d.moving ? VD : 0;
    for (let i = 0; i < NSD; i++) { const r = PR[i], life = 3.2, a = ((T / life + r[0]) % 1) * life, ex = d.x - mv * a;
      const z = (r[1] * 2 - 1) * DW / 2 * (1 + a * .5), up = (.15 + r[2] * 1.4) * Math.sqrt(a) * 1.3;
      sp.setXYZ(i, ex + .2 - a * (.25 + r[3] * .6), sandAt(ex, z) + .15 + up, z); }
    sp.needsUpdate = true; SAND.material.opacity = .5 * (d.cloud ?? 1);
    for (let i = 0; i < NJ; i++) { const r = PR[i + 400], s = (T * 2.2 + r[0]) % 1, z = NOZ[i % 9] + (r[1] - .5) * .08;
      jp.setXYZ(i, d.x + .1 + s * .55 + (r[2] - .5) * .05, DR.position.y + DH - .2 - s * (DH - .05), z + (r[3] - .5) * s * .25); } jp.needsUpdate = true;
    for (let i = 0; i < NDR; i++) { const r = PR[i + 1400], s = (T * .9 + r[0]) % 1; const x = d.x - .2 - r[1] * (DL - .3) - mv * s * .7, z = (r[2] * 2 - 1) * (DW / 2 - .1);
      dp.setXYZ(i, x, DR.position.y - s * .9, z); } dp.needsUpdate = true; DROP.material.opacity = .8 * (d.sieve ?? .6); }
  if (FLOW.visible) { const fp = FLOW.geometry.attributes.position; for (let i = 0; i < NF; i++) { const r = PR[i + 2400], s = (T * .45 + r[0]) % 1; const p = hoseKC.getPointAt(s); fp.setXYZ(i, p.x + (r[1] - .5) * .1, p.y + (r[2] - .5) * .1, p.z); } fp.needsUpdate = true; FLOW.material.opacity = st.flow ? .95 : 0; }
}
function placeDeck(st, T) {
  const k = st.pile || 0; PILE.visible = k > 0;
  if (PILE.visible) { for (let i = 0; i < NPL; i++) { const r = PR[i + 3000], a = r[0] * 6.28, rr = Math.sqrt(r[1]) * 2.2, h = (1 - rr / 2.2) * 1.1 * k;
      const p = V(-4 + Math.cos(a) * rr * 1.3, 2.3 + r[2] * h, Math.sin(a) * rr * .9).applyMatrix4(kb.matrixWorld);
      const vis = r[3] < k; dummy.position.copy(p); dummy.rotation.set(r[1] * 6, r[2] * 6, r[3] * 6); dummy.scale.setScalar(vis ? CL * 1.1 : 0); dummy.updateMatrix(); PILE.setMatrixAt(i, dummy.matrix); }
    PILE.instanceMatrix.needsUpdate = true; }
  bags.forEach((b, i) => { const v = st.bags != null && i < st.bags; b.visible = v; if (v) { const p = V(-11.6 + Math.floor(i / 4) * 1.5, 2.05, -2.4 + (i % 4) * 1.6).applyMatrix4(kb.matrixWorld); b.position.copy(p); b.rotation.y = kb.rotation.y; const pop = clamp((st.bagT - i * .32) / .25); b.scale.setScalar(1.0 * (pop < 1 ? ease(pop) * 1.08 : 1)); } });
}
// harita: Karadeniz → İtalya
function mapItaly(t, a) {
  const c = $("map"); c.style.opacity = a; const g = MP; g.clearRect(0, 0, 1080, 1920); if (a <= 0) return;
  const lon0 = 5, lat0 = 50, span = 38, k = 1080 / span, py = 300; const X = lo => (lo - lon0) * k, Y = la => py + (lat0 - la) * k * 1.25;
  const gr = g.createLinearGradient(0, 0, 0, 1920); gr.addColorStop(0, "#1f86b8"); gr.addColorStop(1, "#155f88"); g.fillStyle = gr; g.fillRect(0, 0, 1080, 1920);
  for (const o of DUNYA) { const xs = o.r; if (xs.every(([lo]) => lo < lon0 - 8 || lo > lon0 + span + 8)) continue;
    g.beginPath(); xs.forEach(([lo, la], i) => i ? g.lineTo(X(lo), Y(la)) : g.moveTo(X(lo), Y(la))); g.closePath();
    g.fillStyle = o.c === "TUR" ? "#f1ebdc" : o.c === "ITA" ? `rgb(${lerp(141, 227, sm((t - 1.4) / .4))},${lerp(154, 20, sm((t - 1.4) / .4))},${lerp(158, 27, sm((t - 1.4) / .4))})` : "#8d9a9e"; g.fill(); g.strokeStyle = "#0e3550"; g.lineWidth = 1.5; g.stroke(); }
  const R = [[30.3, 41.2], [29.0, 41.1], [26.4, 40.1], [25.3, 38.3], [23.0, 36.1], [20.0, 37.8], [16.0, 38.6], [14.2, 40.6]];
  const p = clamp((t - .3) / 1.2); g.strokeStyle = "#ffd54a"; g.lineWidth = 8; g.setLineDash([26, 16]); g.lineDashOffset = -t * 60; g.beginPath();
  const N = R.length - 1, upto = p * N; g.moveTo(X(R[0][0]), Y(R[0][1]));
  for (let i = 1; i <= N; i++) { const f = clamp(upto - (i - 1)); if (f <= 0) break; g.lineTo(X(lerp(R[i - 1][0], R[i][0], f)), Y(lerp(R[i - 1][1], R[i][1], f))); } g.stroke(); g.setLineDash([]);
  const pulse = (lo, la, al) => { g.globalAlpha = al; g.fillStyle = "#e3141b"; g.beginPath(); g.arc(X(lo), Y(la), 16, 0, 7); g.fill(); const r = 16 + 40 * ((t * 1.2) % 1); g.strokeStyle = `rgba(227,20,27,${1 - (r - 16) / 40})`; g.lineWidth = 4; g.beginPath(); g.arc(X(lo), Y(la), r, 0, 7); g.stroke(); g.globalAlpha = 1; };
  pulse(30.3, 41.2, 1); g.font = "52px AN"; g.fillStyle = "#fff"; g.textAlign = "center"; g.fillText(EN ? "BLACK SEA" : "KARADENİZ", X(34.5), Y(43.4));
  const e = sm((t - 1.4) / .4); if (e > 0) { pulse(12.5, 41.9, e); g.globalAlpha = e; g.font = "64px AN"; g.fillText(EN ? "ITALY" : "İTALYA", X(9.2), Y(38.4)); g.globalAlpha = 1; }
  g.textAlign = "left";
}

// ================= çekimler =================
const K = (o) => base(Object.assign({ tuna: "hide", ham: "hide", mood: "day" }, o));
const BOATX = 12;                                    // tekne kafesin önünde, halat boyu yatay
const BOAT = (mx) => ({ p: V(mx + BOATX, 0, 0), h: 0, run: true });
const RUN = (lt, x0 = 0, o = {}) => Object.assign({ x: x0 + lt * VD, jets: 1, moving: 1 }, o);
const UW = (p, tg, fov = 50) => camSet(p, tg, fov);                          // su altı kamera
const S3 = {
  hook: (lt, d) => { if (lt < d * .45) { const u = sm(lt / (d * .45)); camSet(P_PL.clone().add(V(lerp(8, 6, u), lerp(6.5, 5.5, u), lerp(10, 8, u))), P_PL.clone().add(V(0, 1.4, 0)), 40); return K({ plateOn: 1, noField: 1 }); }
    const u = sm((lt - d * .45) / (d * .55)), x = 4 + (lt - d * .45) * VD; UW(V(lerp(x + 3, x + 2, u), SY + lerp(2.6, 2.1, u), lerp(5.5, 4.6, u)), V(x - .3, SY + .3, 0), 52);
    return K({ dr: RUN(lt - d * .45, 4, { cloud: 1 }), boat: BOAT(x) }); },
  hookQ: (lt, d) => { const x = 6 + lt * VD, u = sm(lt / d); UW(V(x + 5, SY + lerp(3.5, 4, u), lerp(9, 10, u)), V(x - .5, SY + .6, 0), 54); return K({ dr: RUN(lt, 6), boat: BOAT(x) }); },
  step: (lt, d) => { const u = sm(lt / d), x = 10 + lt * VD; camSet(V(x + BOATX + lerp(26, 22, u), lerp(14, 12, u), lerp(30, 26, u)), V(x + BOATX - 2, 1, 0), 46); return K({ boat: BOAT(x), dr: RUN(lt, 10) }); },
  cta: (lt, d) => { const u = sm(lt / d); UW(V(lerp(-6, -5, u), SY + 1.6, lerp(3.2, 2.8, u)), V(-6.5, SY + .1, -.6), 46); return K({ cta: lt, ctaD: d }); },
  name: (lt, d) => { UW(V(-30 + .4, SY + 1.1, 2.2), V(-30, SY + .7, 0), 40); return K({ big: lt, noField: 0 }); },
  cik: (lt, d) => { const u = sm(lt / d); UW(V(lerp(-12, -10, u), SY + lerp(1.4, 1.2, u), 2.6), V(lerp(-12, -10, u) - .4, SY + .05, 0), 44); return K({}); },
  live: (lt, d) => { const u = sm(lt / d); UW(V(lerp(-16, -18, u), -7, lerp(27, 25, u)), V(-19, -7.5, 0), 62); return K({ depth: sm(lt / .8) }); },
  howq: (lt, d) => { const u = sm(lt / d); UW(V(-8.6, SY + .9, lerp(1.8, 1.5, u)), V(-8.9, SY + .05, 0), 40); return K({ clamScale: 1 }); },
  water: (lt, d) => { UW(V(-6.5, SY + 1.4, 3.2), V(-7.2, SY + .2, 0), 46); return K({ dr: { x: -8 + lt * .4, jets: 1, cloud: 1.4, moving: 0, noLines: 1 }, jetHit: -9 }); },
  lower: (lt, d) => { const u = ease(clamp(lt / (d * .85))); const x = 0; UW(V(x + 5, -7, 22), V(x + 5, -7, 0), 62);
    return K({ boat: { p: V(x + BOATX, 0, 0), h: 0 }, dr: { x, y: lerp(1, sandAt(x, 0) + .1, u), jets: 0 } }); },
  pump: (lt, d) => { const x = lt * .3; UW(V(x + 5, -7, 21), V(x + 5, -7.5, 0), 62); return K({ boat: BOAT(x), dr: RUN(lt * .3, 0, { jets: lt > d * .5 ? 1 : 0, cloud: .6 }), flow: 1 }); },
  jets: (lt, d) => { const x = 2 + lt * .25, u = sm(lt / d); UW(V(x + lerp(3, 2.4, u), SY + lerp(1.8, 1.6, u), lerp(2.6, 2.2, u)), V(x + .1, SY + .5, 0), 46); return K({ dr: { x, jets: 1, moving: 1, cloud: 1.2 } }); },
  fill: (lt, d) => { const x = 4 + lt * VD, u = sm(lt / d); UW(V(x - lerp(1.5, 2.5, u), SY + 2.6, 4.4), V(x - 1.3, SY + .4, 0), 54); return K({ dr: RUN(lt, 4) }); },
  like: (lt, d) => { const x = 4 + (lt + 4.5) * VD; UW(V(x - 3, SY + 2.6, 4.6), V(x - 1.3, SY + .4, 0), 54); return K({ dr: RUN(lt + 4.5, 4), chip: ["like", fadeIO(lt, d)] }); },
  sepq: (lt, d) => { const x = 14; const a = .4 + lt / d * .5; UW(V(x - 1.3 + Math.cos(a) * 5, SY + 2.2, Math.sin(a) * 5), V(x - 1.3, SY + .5, 0), 50); return K({ dr: { x, jets: 1, moving: 0, cloud: .5, sieve: .4 } }); },
  secret: (lt, d) => { const x = 14, u = ease(clamp(lt / d)); UW(V(x - 1.3 + lerp(2.5, .4, u), SY + lerp(1.4, -.05, u) + .3, lerp(4, 3.2, u)), V(x - 1.3, SY + .2, 0), 52); return K({ dr: { x, y: sandAt(x, 0) + .7, jets: 0, moving: 0 }, glowBars: 1 }); },
  bars: (lt, d) => { const x = 14, u = sm(lt / d); UW(V(x - 1.3 + lerp(2.6, 1.8, u), SY + .2, lerp(4.4, 4, u)), V(x - 1.3, SY + .9, 0), 56); return K({ dr: { x, y: sandAt(x, 0) + .7, jets: 0, moving: 0 }, glowBars: 1 }); },
  fall: (lt, d) => { const x = 14 + lt * .5; UW(V(x - 1.3, SY + .9, 3.4), V(x - 1.3, SY + .45, 0), 54); return K({ dr: { x, y: sandAt(x, 0) + .45, jets: 1, moving: 1, cloud: .2, sieve: 1 }, glowBars: 1, cut: 1 }); },
  sieve: (lt, d) => { const x = 18 + lt * VD, u = sm(lt / d); UW(V(x - lerp(6, 8, u), SY + 5, 9), V(x - 3, SY + .2, 0), 56); return K({ dr: RUN(lt, 18, { sieve: 1 }) }); },
  haul: (lt, d) => { const x = 24, u = ease(clamp(lt / (d * .55))), dmp = clamp((lt - d * .55) / (d * .35)); const st0 = V(x + BOATX - 6, 3.6, 0);
    const p = V(x, sandAt(x, 0) + .1, 0).lerp(st0, u); camSet(V(x + BOATX + 8, 14, 24), V(x + BOATX - 6, -2, 0), 52);
    return K({ xray: .5, boat: { p: V(x + BOATX, 0, 0), h: 0 }, dr: { x: p.x, y: p.y, lifted: 1, capX: x, full: 1, tilt: -dmp * .9, dump: dmp, noLines: 0 }, pile: dmp }); },
  ton: (lt, d) => { const u = sm(lt / d); camSet(V(BOATX + lerp(9, 7, u), lerp(12, 11, u), lerp(14, 12, u)), V(BOATX - 4, 1.5, 0), 48); return K({ boat: { p: V(BOATX, 0, 0), h: 0 }, bags: 10, bagT: lt, ton: lt, pile: 1 }); },
  export: (lt) => { camSet(V(0, 300, 1), V(0, 0, 0)); return K({ italy: lt }); },
  plate: (lt, d) => { const u = sm(lt / d), a = .3 + u * .5; camSet(P_PL.clone().add(V(Math.cos(a) * 14, lerp(11, 9, u), Math.sin(a) * 14)), P_PL.clone().add(V(0, 1, 0)), 44); return K({ plateOn: 1, noField: 1 }); },
  comment: (lt, d) => { const x = 26 + lt * VD; UW(V(x + 2.5, SY + 3, 7), V(x - 1, SY + .4, 0), 54); return K({ dr: RUN(lt, 26), chip: ["comment", fadeIO(lt, d)] }); },
  loop: (lt, d) => { const x = 28 + lt * VD, u = sm(lt / d); UW(V(x + lerp(5, 3, u), SY + lerp(3.8, 2.8, u), lerp(9, 6, u)), V(x - .4, SY + .4, 0), 54); return K({ dr: RUN(lt, 28) }); },
};
for (const k in S3) S[k] = S3[k];

function apply2(st, T) {
  placeHamsi({ ham: "hide" }, T);
  [predator, plank, bigH, harbor, kulac, brail, crates, pblock, sCone, RINGS, pline].forEach(o => o.visible = false); crew.forEach(o => o.visible = false); pulses.forEach(o => o.visible = false);
  putBoat(kb, st.boat || null, T);
  const under = camera.position.y < 0;
  if (under) { scene.fog.color.set(0x2f9cc4); scene.fog.density = .03; renderer.toneMappingExposure = .95; }
  ceil.visible = under; if (under) ceil.position.set(camera.position.x, -.35, camera.position.z);
  sand.visible = !st.plateOn && !st.italy; plate.visible = !!st.plateOn;
  placeDredge(st, T); placeClams(st, T); placeParticles(st, T); placeDeck(st, T);
  bigClam.visible = st.big != null; if (bigClam.visible) { bigClam.position.set(-30, SY + .7, 0); bigClam.scale.setScalar(.55); bigClam.rotation.set(.25, -.6 + st.big * .35, .1); }
  // derinlik çizgisi (yüzey → kum): 2D ölçü
  if (st.depth) { const a = V(-22, -.2, 0), b = V(-22, sandAt(-22, 0), 0); dimLine2(a, b, st.depth, "20 m"); }
  if (st.ton != null) { const n = Math.min(10, Math.floor(st.ton / .32) + 1), al = sm(st.ton / .3); LN.save(); LN.globalAlpha = al; LN.textAlign = "center"; LN.font = "230px AN"; LN.fillStyle = "#fff";
    LN.shadowColor = "rgba(0,0,0,.5)"; LN.shadowBlur = 30; LN.fillText(EN ? `${n} TONNES` : `${n} TON`, 540, 520); LN.restore(); LN.textAlign = "left"; }
  if (st.italy != null) mapItaly(st.italy, sm(st.italy / .3));
  if (st.plateOn) { renderer.toneMappingExposure = 1.05; scene.fog.density = 0; }
}
function dimLine2(a, b, al, txt) { const [x1, y1] = proj(a), [x2, y2] = proj(b); LN.save(); LN.globalAlpha = al; LN.strokeStyle = "#ffd54a"; LN.lineWidth = 6;
  LN.beginPath(); LN.moveTo(x1, y1); LN.lineTo(x2, y2); LN.stroke(); for (const [x, y] of [[x1, y1], [x2, y2]]) { LN.beginPath(); LN.moveTo(x - 26, y); LN.lineTo(x + 26, y); LN.stroke(); }
  LN.font = "64px AN"; LN.fillStyle = "#fff"; LN.shadowColor = "rgba(0,0,0,.6)"; LN.shadowBlur = 16; LN.fillText(txt, x1 + 40, (y1 + y2) / 2); LN.restore(); }
const _applyBase = apply; apply = (st, T) => { _applyBase(st, T); apply2(st, T); };
