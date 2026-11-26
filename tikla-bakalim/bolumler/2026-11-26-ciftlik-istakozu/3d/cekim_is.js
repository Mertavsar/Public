// ================= ÇİFTLİK ISTAKOZU (dikey 1080×1920) =================
const EN = location.search.includes("en=1");
if (EN) { document.querySelectorAll("#ctaLogo,#logo").forEach(e => e.src = "logo_en.jpg"); document.querySelector("#cta .nm").innerHTML = "Sea Secrets<small>Fishing, explained simply</small>"; $("bSh").textContent = "↗ Share";
  CHIPS.like = "<i>❤</i> Like if it's useful"; CHIPS.comment = "<i>💬</i> Pick the next one"; }
const DOT = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d"); const r = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  r.addColorStop(0, "rgba(255,255,255,1)"); r.addColorStop(.45, "rgba(255,255,255,.55)"); r.addColorStop(1, "rgba(255,255,255,0)"); g.fillStyle = r; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
function pts(n, col, size, op) { const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(n * 3), 3));
  const m = new THREE.Points(g, new THREE.PointsMaterial({ color: col, size, map: DOT, transparent: true, opacity: op, depthWrite: false })); m.frustumCulled = false; scene.add(m); m.visible = false; return m; }
const PR = []; for (let i = 0; i < 9000; i++) PR.push([rnd(), rnd(), rnd(), rnd()]);
const STD = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: .6 }, o));

// ---------- geometri birleştirme (vertex renkli) ----------
const _o = new THREE.Object3D();
function MX(px, py, pz, rx = 0, ry = 0, rz = 0, sx = 1, sy = sx, sz = sx) { _o.position.set(px, py, pz); _o.rotation.set(rx, ry, rz); _o.scale.set(sx, sy, sz); _o.updateMatrix(); return _o.matrix.clone(); }
function mergeG(list) { const P = [], N = [], C = []; const col = new THREE.Color();
  for (const [geo, m, hex, vary = .08] of list) { let g = geo.index ? geo.toNonIndexed() : geo.clone(); g.applyMatrix4(m); const p = g.attributes.position, n = g.attributes.normal; col.set(hex);
    for (let i = 0; i < p.count; i++) { P.push(p.getX(i), p.getY(i), p.getZ(i)); N.push(n.getX(i), n.getY(i), n.getZ(i));
      const k = 1 + vary * Math.sin(p.getX(i) * 23 + p.getZ(i) * 17 + p.getY(i) * 11); C.push(col.r * k, col.g * k, col.b * k); } }
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(P, 3)); g.setAttribute("normal", new THREE.Float32BufferAttribute(N, 3)); g.setAttribute("color", new THREE.Float32BufferAttribute(C, 3)); return g; }

// ---------- ıstakoz ----------
// yerel eksen: baş +x, sırt +y. Kuyruk yelpazesi -1.35, kıskaç ucu +1.95 → boy ≈ 3.3
const PAL = { live: { b: 0x14305e, b2: 0x1f4a86, leg: 0x2c5a9e, tip: 0xf0a640, ant: 0xc8642c, eye: 0x0a0a0a },
  cooked: { b: 0xd2381c, b2: 0xe2562a, leg: 0xe8642e, tip: 0xf6dcb4, ant: 0xd2381c, eye: 0x1a0a06 } };
const SPH = (w = 14, h = 9) => new THREE.SphereGeometry(1, w, h), CYL = (a, b, h, s = 8) => new THREE.CylinderGeometry(a, b, h, s), CON = (r, h, s = 10) => new THREE.ConeGeometry(r, h, s);
function partsBody(P, lo) { const s = lo ? [8, 5] : [16, 10], L = [];
  L.push([SPH(...s), MX(.32, .05, 0, 0, 0, 0, .64, .3, .3), P.b]);
  L.push([SPH(...s), MX(.62, .1, 0, 0, 0, -.12, .32, .2, .22), P.b2]);
  L.push([CON(.1, .42, 8), MX(1.0, .12, 0, 0, 0, -Math.PI / 2), P.b]);
  for (const s2 of [-1, 1]) L.push([SPH(6, 4), MX(.86, .2, s2 * .1, 0, 0, 0, .055), P.eye]);
  for (let j = 0; j < 4; j++) for (const s2 of [-1, 1]) { const x = .52 - j * .17; L.push([CYL(.025, .018, .55, 5), MX(x, -.2, s2 * .32, s2 * 1.05, 0, 0), P.leg]); L.push([CYL(.018, .012, .4, 5), MX(x + .02, -.36, s2 * .58, s2 * .25, 0, 0), P.leg]); }
  for (const s2 of [-1, 1]) { const d = V(1, .12, s2 * .32).normalize(), L0 = 2.3; const c = V(1.0, .14, s2 * .07).add(d.clone().multiplyScalar(L0 / 2));
    _o.position.copy(c); _o.quaternion.setFromUnitVectors(V(0, 1, 0), d); _o.scale.set(1, 1, 1); _o.updateMatrix(); L.push([CYL(.006, .02, L0, 4), _o.matrix.clone(), P.ant]);
    const d2 = V(1, .4, s2 * .1).normalize(); _o.position.copy(V(1.0, .16, s2 * .04).add(d2.clone().multiplyScalar(.3))); _o.quaternion.setFromUnitVectors(V(0, 1, 0), d2); _o.updateMatrix(); L.push([CYL(.006, .012, .6, 4), _o.matrix.clone(), P.ant]); }
  for (let k = 0; k < 10; k++) L.push([SPH(5, 3), MX(.1 + PR[k][0] * .5, .05 + PR[k][1] * .2, (PR[k][2] - .5) * .5, 0, 0, 0, .035), 0xc9b04a, 0]);
  return L; }
function partsTail(P, lo) { const s = lo ? [8, 5] : [14, 9], L = [];
  for (let i = 0; i < 6; i++) L.push([SPH(...s), MX(-.08 - i * .17, .03 - i * .012, 0, 0, 0, 0, .13, .2 - i * .014, .25 - i * .02), i % 2 ? P.b2 : P.b]);
  for (let k = -2; k <= 2; k++) { const a = k * .38; L.push([SPH(...s), MX(-1.12 - Math.cos(a) * .14, -.03, Math.sin(a) * .16, 0, a, 0, .22, .025, .075), P.b2]); }
  return L; }
function partsClaw(P, s2, lo) { const s = lo ? [8, 5] : [16, 10], L = [];
  L.push([CYL(.06, .055, .42, 6), MX(.16, 0, s2 * .11, 0, -s2 * .55, Math.PI / 2), P.b]);
  L.push([CYL(.07, .06, .36, 6), MX(.48, .02, s2 * .27, 0, -s2 * .25, Math.PI / 2), P.b2]);
  L.push([SPH(...s), MX(.86, .02, s2 * .36, 0, -s2 * .12, 0, .3, .13, .17), P.b]);
  L.push([CON(.075, .48, 8), MX(1.36, .0, s2 * .43, 0, 0, -Math.PI / 2), P.b2]);
  L.push([CON(.03, .14, 6), MX(1.62, .0, s2 * .43, 0, 0, -Math.PI / 2), P.tip, 0]);
  return L; }
function partsFinger(P) { return [[CON(.065, .46, 8), MX(.23, 0, 0, 0, 0, -Math.PI / 2), P.b2], [CON(.028, .13, 6), MX(.49, 0, 0, 0, 0, -Math.PI / 2), P.tip, 0]]; }
const lobMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .32, metalness: .08, envMapIntensity: .55 });
const lobMatC = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .4, metalness: 0, envMapIntensity: .5, emissive: 0x200400 });
// toplu (instanced) düşük poligon ıstakoz
function lobsterGeoLo(P) { const L = [...partsBody(P, 1), ...partsTail(P, 1).map(([g, m, c]) => [g, MX(-.24, 0, 0).multiply(m), c])];
  for (const s2 of [-1, 1]) { const sh = MX(.72, -.02, s2 * .16); partsClaw(P, s2, 1).forEach(([g, m, c, v]) => L.push([g, sh.clone().multiply(m), c, v])); partsFinger(P).forEach(([g, m, c, v]) => L.push([g, sh.clone().multiply(MX(1.2, .06, s2 * .43, 0, 0, .15)).multiply(m), c, v])); }
  return mergeG(L); }
const LOGEO = lobsterGeoLo(PAL.live);
// animasyonlu kahraman ıstakoz
function makeLobster(P = PAL.live, mat = lobMat) {
  const g = new THREE.Group(); g.add(new THREE.Mesh(mergeG(partsBody(P)), mat));
  const tail = new THREE.Group(); tail.position.set(-.24, 0, 0); tail.add(new THREE.Mesh(mergeG(partsTail(P)), mat)); g.add(tail);
  const eggs = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 8, 6), STD(0x3c7a2c, { roughness: .3, metalness: .1, emissive: 0x0c1a06 }), 420);
  for (let i = 0; i < 420; i++) { const r = PR[i + 2000]; const u = r[0]; dummy.position.set(-.05 - u * .9, -.16 - r[1] * .08, (r[2] - .5) * (.42 - u * .2)); dummy.scale.setScalar(.04); dummy.rotation.set(0, 0, 0); dummy.updateMatrix(); eggs.setMatrixAt(i, dummy.matrix); }
  eggs.visible = false; tail.add(eggs);
  const claws = [-1, 1].map(s2 => { const c = new THREE.Group(); c.position.set(.72, -.02, s2 * .16); c.add(new THREE.Mesh(mergeG(partsClaw(P, s2)), mat));
    const f = new THREE.Group(); f.position.set(1.2, .06, s2 * .43); f.add(new THREE.Mesh(mergeG(partsFinger(P)), mat)); c.add(f); c.userData.f = f; g.add(c); return c; });
  g.userData = { tail, claws, eggs }; return g; }
function poseLob(g, T, o = {}) { const { tail, claws } = g.userData, ph = o.ph || 0, act = o.act ?? 1;
  tail.rotation.z = (o.flap ?? 0) + Math.sin(T * 1.3 + ph) * .04 * act;
  claws.forEach((c, i) => { const s2 = i ? 1 : -1; c.rotation.set(0, s2 * (.1 + Math.sin(T * .9 + ph + i) * .06 * act) - s2 * (o.spread || 0), (o.raise || 0) + Math.sin(T * .7 + ph + i * 2) * .05 * act);
    c.userData.f.rotation.z = .12 + (.5 + .5 * Math.sin(T * 2.2 + ph + i * 1.7)) * .25 * act + (o.snap || 0); c.scale.setScalar(o.clawS ?? 1); });
  g.userData.eggs.visible = !!o.eggs; }

// ================= SETLER =================
// SALON (kuluçka + büyütme): P_H, zemin y=300
const P_H = V(4000, 300, 0); const hall = new THREE.Group(); hall.position.copy(P_H); scene.add(hall);
{ const room = new THREE.Mesh(new THREE.BoxGeometry(170, 44, 170), new THREE.MeshStandardMaterial({ color: 0x8fa6b4, roughness: .9, side: THREE.BackSide })); room.position.y = 22; hall.add(room);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(169, 169), STD(0x34505f, { roughness: .35, metalness: .1 })); floor.rotation.x = -Math.PI / 2; floor.position.y = .01; hall.add(floor);
  for (let i = -3; i <= 3; i++) { const l = new THREE.Mesh(new THREE.BoxGeometry(2, .3, 120), new THREE.MeshBasicMaterial({ color: 0xffffff })); l.position.set(i * 18, 43.6, 0); hall.add(l); }
  const lamps = [[-30, 30, 20], [30, 30, 20], [0, 30, -30], [0, 26, 40]]; lamps.forEach(([x, y, z]) => { const p = new THREE.PointLight(0xfff4e6, 120, 0, 1.4); p.position.set(x, y, z); hall.add(p); });
  // pencere (arka duvar, dışarıda kar)
  const win = new THREE.Mesh(new THREE.PlaneGeometry(80, 22), new THREE.MeshBasicMaterial({ color: 0x1b3557 })); win.position.set(0, 18, -84.8); hall.add(win);
  const hills = new THREE.Mesh(new THREE.PlaneGeometry(80, 7), new THREE.MeshBasicMaterial({ color: 0xdfe9f2 })); hills.position.set(0, 10.5, -84.7); hall.add(hills);
  for (let i = -2; i <= 2; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(.8, 22, .6), STD(0xf4f6f7)); b.position.set(i * 20, 18, -84.5); hall.add(b); }
  for (const y of [7, 29]) { const b = new THREE.Mesh(new THREE.BoxGeometry(81, .8, .6), STD(0xf4f6f7)); b.position.set(0, y, -84.5); hall.add(b); } }
const SNOW = pts(900, 0xffffff, .5, .95);
// raflar ve hücreli tepsiler
const CS = 2, NXC = 4, NZC = 8, RACKX = [-13, 0, 13], LEV = [1.2, 3.6, 6.0], TOPY = LEV[2];
const trayBase = STD(0x23527e, { roughness: .4 }), wallM = STD(0xf2f5f7, { roughness: .35 }), metal = STD(0x9aa6ae, { roughness: .3, metalness: .7 });
const waterM = new THREE.MeshStandardMaterial({ color: 0x1f9cc8, roughness: .05, metalness: .1, transparent: true, opacity: .42, depthWrite: false });
const WALLS = []; { for (const rx of RACKX) for (const ly of LEV) { const t = new THREE.Group(); t.position.set(rx, ly, 0); hall.add(t);
    const b = new THREE.Mesh(new THREE.BoxGeometry(NXC * CS + .3, .16, NZC * CS + .3), trayBase); b.position.y = -.08; t.add(b);
    for (let i = 0; i <= NXC; i++) { const w = new THREE.Mesh(new THREE.BoxGeometry(.08, .55, NZC * CS), wallM); w.position.set((i - NXC / 2) * CS, .27, 0); t.add(w); }
    for (let j = 0; j <= NZC; j++) { const w = new THREE.Mesh(new THREE.BoxGeometry(NXC * CS, .55, .08), wallM); w.position.set(0, .27, (j - NZC / 2) * CS); t.add(w); }
    const wt = new THREE.Mesh(new THREE.PlaneGeometry(NXC * CS, NZC * CS), waterM); wt.rotation.x = -Math.PI / 2; wt.position.y = .42; t.add(wt);
    // su borusu (her tepsinin başında)
    const pipe = new THREE.Mesh(CYL(.12, .12, NXC * CS + 1, 10), STD(0x2f7fd0, { roughness: .3 })); pipe.rotation.z = Math.PI / 2; pipe.position.set(0, .75, -NZC - .2); t.add(pipe); WALLS.push(t); }
  for (const rx of RACKX) for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const p = new THREE.Mesh(CYL(.09, .09, TOPY + 1.2, 8), metal); p.position.set(rx + sx * (NXC + .2), (TOPY + 1.2) / 2, sz * (NZC + .2)); hall.add(p); } }
const cellPos = (r, ix, iz, ly = TOPY) => V(RACKX[r] + (ix - 1.5) * CS, ly + .1, (iz - 3.5) * CS);   // hall-yerel
const NLO = 3 * NXC * NZC, LOB = new THREE.InstancedMesh(LOGEO, lobMat, NLO); LOB.frustumCulled = false; hall.add(LOB);
const LI = []; for (let r = 0; r < 3; r++) for (let ix = 0; ix < NXC; ix++) for (let iz = 0; iz < NZC; iz++) LI.push({ r, ix, iz, yaw: rnd() * 6.28, ph: rnd() * 6.28, sc: .5 + rnd() * .08 });
const HC = { r: 1, ix: 1, iz: 5 };                                       // kahramanın hücresi
const HCP = () => cellPos(HC.r, HC.ix, HC.iz).add(P_H);
// konik tanklar
const CON_X = [-22, -14, -6].map(x => x), CON_Z = 34; const coneTanks = new THREE.Group(); hall.add(coneTanks);
{ const glass = new THREE.MeshStandardMaterial({ color: 0x8fd6ee, roughness: .05, transparent: true, opacity: .45, side: THREE.DoubleSide, depthWrite: false });
  const wat = new THREE.MeshStandardMaterial({ color: 0x1f8fc0, roughness: .1, transparent: true, opacity: .5, depthWrite: false });
  CON_X.forEach(x => { const g = new THREE.Group(); g.position.set(x, 0, CON_Z);
    const cyl = new THREE.Mesh(CYL(2.4, 2.4, 3.2, 32, 1), glass); cyl.position.y = 5.4; g.add(cyl); const cone = new THREE.Mesh(new THREE.ConeGeometry(2.4, 2.4, 32, 1, true), glass); cone.rotation.x = Math.PI; cone.position.y = 2.6; g.add(cone);
    const w1 = new THREE.Mesh(CYL(2.3, 2.3, 2.8, 32), wat); w1.position.y = 5.2; g.add(w1); const w2 = new THREE.Mesh(new THREE.ConeGeometry(2.3, 2.3, 32), wat); w2.rotation.x = Math.PI; w2.position.y = 2.65; g.add(w2);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(2.42, .09, 8, 40), STD(0xffffff)); rim.rotation.x = Math.PI / 2; rim.position.y = 7.0; g.add(rim);
    for (let k = 0; k < 3; k++) { const a = k / 3 * 6.28; const l = new THREE.Mesh(CYL(.08, .08, 4.2, 6), metal); l.position.set(Math.cos(a) * 1.9, 2.1, Math.sin(a) * 1.9); g.add(l); }
    const air = new THREE.Mesh(CYL(.03, .03, 5.5, 4), STD(0x333333)); air.position.set(.6, 4.2, .2); g.add(air); coneTanks.add(g); }); }
const SWIRL = pts(1800, 0xffa25a, .13, .95);
// ortak tank (birbirini yeme anlatımı) — salonun sağ ön köşesi
const P_SH = V(22, 0, 30); const shTank = new THREE.Group(); shTank.position.copy(P_SH); hall.add(shTank);
{ const w = new THREE.Mesh(new THREE.BoxGeometry(14, 2.4, 10), new THREE.MeshStandardMaterial({ color: 0xbfe9f5, transparent: true, opacity: .22, roughness: .05, side: THREE.DoubleSide, depthWrite: false })); w.position.y = 2.2; shTank.add(w);
  const b = new THREE.Mesh(new THREE.BoxGeometry(14.2, .3, 10.2), trayBase); b.position.y = .85; shTank.add(b);
  const sand = new THREE.Mesh(new THREE.BoxGeometry(13.8, .12, 9.8), STD(0x9c8f72, { roughness: 1, envMapIntensity: .1 })); sand.position.y = 1.05; shTank.add(sand);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const l = new THREE.Mesh(CYL(.1, .1, 1, 6), metal); l.position.set(sx * 6.8, .5, sz * 4.8); shTank.add(l); }
  for (let k = 0; k < 5; k++) { const r = new THREE.Mesh(new THREE.DodecahedronGeometry(.35 + PR[k][0] * .25, 0), STD(0x76808a, { flatShading: true })); r.position.set((k % 2 ? 1 : -1) * 6, 1.25, (PR[k][2] - .5) * 8); shTank.add(r); } }
const SMALL = []; for (let i = 0; i < 10; i++) { const m = new THREE.Mesh(LOGEO, lobMat.clone()); m.material.transparent = true; scene.add(m); SMALL.push(m); }

// STÜDYO (anne ıstakoz, larvalar, evreler) — su içi gibi
const P_S = V(4000, 300, 500); const studio = new THREE.Group(); studio.position.copy(P_S); scene.add(studio);
{ const g = document.createElement("canvas"); g.width = 8; g.height = 256; const x = g.getContext("2d"); const gr = x.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, "#8fe0f2"); gr.addColorStop(.5, "#2f9cc4"); gr.addColorStop(1, "#1a6a90"); x.fillStyle = gr; x.fillRect(0, 0, 8, 256);
  const room = new THREE.Mesh(new THREE.SphereGeometry(80, 32, 16), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(g), side: THREE.BackSide, fog: false })); studio.add(room);
  const bed = new THREE.PlaneGeometry(160, 160, 80, 80); bed.rotateX(-Math.PI / 2); { const p = bed.attributes.position, c = []; for (let i = 0; i < p.count; i++) { const X = p.getX(i), Z = p.getZ(i); p.setY(i, Math.sin(X * .3 + Z * .2) * .15); const k = .9 + .1 * Math.sin(X * 2 + Z * 1.3); c.push(.62 * k, .58 * k, .46 * k); } bed.setAttribute("color", new THREE.Float32BufferAttribute(c, 3)); bed.computeVertexNormals(); }
  studio.add(new THREE.Mesh(bed, new THREE.MeshStandardMaterial({ vertexColors: true, color: 0x8a8070, roughness: 1, envMapIntensity: .1 })));
  for (let k = 0; k < 7; k++) { const r = new THREE.Mesh(new THREE.DodecahedronGeometry(1.2 + PR[k + 50][0] * 1.4, 1), STD(0x6d7a80, { flatShading: true, roughness: .9 })); r.scale.y = .6; const a = PR[k + 50][1] * 3 + 3.6, d = 9 + PR[k + 50][2] * 6; r.position.set(Math.cos(a) * d, .2, Math.sin(a) * d); studio.add(r); }
  const l1 = new THREE.PointLight(0xffffff, 60, 0, 1.5); l1.position.set(6, 14, 10); studio.add(l1); const l2 = new THREE.PointLight(0x9fe8ff, 30, 0, 1.5); l2.position.set(-10, 6, -6); studio.add(l2); }
const HERO = makeLobster(); scene.add(HERO);
const HERO2 = makeLobster(); scene.add(HERO2);
const GHOST = makeLobster(); GHOST.traverse(o => { if (o.isMesh) o.material = new THREE.MeshBasicMaterial({ color: 0xcfefff, transparent: true, opacity: .3, depthWrite: false }); }); scene.add(GHOST);
const LARV = pts(1400, 0xff9a40, .16, 1), MOTE = pts(700, 0xe8fbff, .1, .6), FLOW = pts(1600, 0xbff3ff, .12, .9), PEL = pts(240, 0x6a3c18, .2, 1);
PEL.material.blending = THREE.NormalBlending; PEL.material.map = DOT;
// pipet
const pip = new THREE.Group(); { const t = new THREE.Mesh(CYL(.16, .06, 3.4, 12), new THREE.MeshStandardMaterial({ color: 0xe8f6ff, transparent: true, opacity: .45, roughness: .05 })); pip.add(t);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(.38, 16, 10), STD(0xe3141b, { roughness: .4 })); bulb.scale.y = 1.4; bulb.position.y = 2.0; pip.add(bulb); } hall.add(pip);

// DIŞ (Norveç kıyısı: veri merkezi + çiftlik)
const P_O = V(-4000, 300, 0); const outs = new THREE.Group(); outs.position.copy(P_O); scene.add(outs);
{ const gg = new THREE.PlaneGeometry(900, 900, 90, 90); gg.rotateX(-Math.PI / 2); { const p = gg.attributes.position, c = []; for (let i = 0; i < p.count; i++) { const X = p.getX(i), Z = p.getZ(i); const sea = Z > 30 + Math.sin(X * .05) * 8;
      p.setY(i, sea ? -1.5 : Math.max(0, (Math.sin(X * .04) + Math.cos(Z * .05)) * 1.2) * (Z < -60 ? 3 : 0)); const k = .9 + .1 * Math.sin(X * .7 + Z * .4); c.push(...(sea ? [.12, .42, .6] : [.42 * k, .52 * k, .36 * k])); } gg.setAttribute("color", new THREE.Float32BufferAttribute(c, 3)); gg.computeVertexNormals(); }
  outs.add(new THREE.Mesh(gg, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: .9 })));
  const sw = new THREE.Mesh(new THREE.PlaneGeometry(900, 420), STD(0x2a7fae, { roughness: .15, metalness: .2 })); sw.rotation.x = -Math.PI / 2; sw.position.set(0, -.6, 245); outs.add(sw);
  for (let k = 0; k < 9; k++) { const h = 40 + PR[k + 60][0] * 50, r = 50 + PR[k + 60][1] * 40; const m = new THREE.Mesh(new THREE.ConeGeometry(r, h, 7), STD(0x4e5c55, { flatShading: true, roughness: 1 })); m.position.set(-200 + k * 50, h / 2 - 2, -170 - PR[k + 60][2] * 60); outs.add(m);
    const cap = new THREE.Mesh(new THREE.ConeGeometry(r * .32, h * .32, 7), STD(0xf4f7fa, { flatShading: true })); cap.position.set(m.position.x, h - h * .16 - 2, m.position.z); outs.add(cap); }
   }
const DC = new THREE.Group(); DC.position.set(-16, 0, 0); outs.add(DC);
{ const b = new THREE.Mesh(new THREE.BoxGeometry(18, 8, 14), STD(0x2b3138, { roughness: .5, metalness: .3 })); b.position.y = 4; DC.add(b);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(18.4, .5, 14.4), STD(0x434b54)); roof.position.y = 8.2; DC.add(roof);
  for (let k = 0; k < 4; k++) { const f = new THREE.Mesh(CYL(1, 1, .6, 16), STD(0x6b747c, { metalness: .6 })); f.position.set(-6 + k * 4, 8.7, 0); DC.add(f); } }
const LEDN = 2 * 6 * 16, LEDS = new THREE.InstancedMesh(new THREE.PlaneGeometry(.5, .28), new THREE.MeshBasicMaterial({ color: 0xffffff }), LEDN); LEDS.frustumCulled = false; DC.add(LEDS);
{ let n = 0; for (let row = 0; row < 6; row++) for (let col = 0; col < 16; col++) for (const side of [0, 1]) { dummy.position.set(side ? 9.02 : -8 + col * 1.05, 1.2 + row * 1.1, side ? -6.5 + col * .85 : 7.02); dummy.rotation.set(0, side ? Math.PI / 2 : 0, 0); dummy.scale.setScalar(1); dummy.updateMatrix(); LEDS.setMatrixAt(n++, dummy.matrix); } }
const FARM = new THREE.Group(); FARM.position.set(18, 0, 2); outs.add(FARM);
{ const b = new THREE.Mesh(new THREE.BoxGeometry(24, 7, 14), STD(0xeef2f4, { roughness: .6 })); b.position.y = 3.5; FARM.add(b);
  const st = new THREE.Mesh(new THREE.BoxGeometry(24.1, 1.2, 14.1), STD(0xe3141b)); st.position.y = 5.4; FARM.add(st);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(24.6, .5, 14.6), STD(0x56616a)); roof.position.y = 7.2; FARM.add(roof);
  for (let k = 0; k < 6; k++) { const w = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 1.6), new THREE.MeshBasicMaterial({ color: 0x9fdcf0 })); w.position.set(-9 + k * 3.6, 3.4, 7.02); FARM.add(w); } }
const PIPE = new THREE.Mesh(CYL(.55, .55, 17, 14), STD(0xb8c2c8, { metalness: .6, roughness: .3 })); PIPE.rotation.z = Math.PI / 2; PIPE.position.set(1.5, 3, 3); outs.add(PIPE);
for (const x of [-4, 1.5, 7]) { const s = new THREE.Mesh(CYL(.2, .2, 3, 6), metal); s.position.set(x, 1.5, 3); outs.add(s); }
const HOTF = pts(220, 0xff8a2a, .9, 1); const STEAM = pts(300, 0xffffff, 1.6, .35);

// TABAK (pişmiş ıstakoz)
const P_PL = V(4000, 300, -900); const plate = new THREE.Group(); plate.position.copy(P_PL); scene.add(plate);
{ const wood = new THREE.Mesh(new THREE.BoxGeometry(90, 1, 90), STD(0x5a341f, { roughness: .55 })); wood.position.y = -.5; plate.add(wood);
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(220, 130), STD(0x2f2620, { roughness: 1 })); wall.position.set(0, 30, -42); plate.add(wall);
  const cloth = new THREE.Mesh(new THREE.BoxGeometry(26, .1, 18), STD(0xb7322a, { roughness: .9 })); cloth.position.y = .02; cloth.rotation.y = .2; plate.add(cloth);
  const pl = new THREE.Mesh(new THREE.LatheGeometry([new THREE.Vector2(0, 0), new THREE.Vector2(6.2, 0), new THREE.Vector2(7.0, .25), new THREE.Vector2(7.4, .5), new THREE.Vector2(7.3, .4), new THREE.Vector2(6.0, .14), new THREE.Vector2(0, .12)], 64),
    STD(0x14304f, { roughness: .18, metalness: .1, side: THREE.DoubleSide })); pl.position.y = .1; plate.add(pl);
  const cl = makeLobster(PAL.cooked, lobMatC); cl.scale.setScalar(3.4); cl.position.set(-.6, 1.1, 0); cl.rotation.y = .5; poseLob(cl, 0, { act: 0 }); plate.add(cl); plate.userData.cl = cl;
  const lemM = STD(0xffd21a, { roughness: .35, emissive: 0x3a3000 }), lemIn = STD(0xfff27a, { roughness: .5, emissive: 0x2a2a00 });
  for (const [x, z, ry] of [[4.6, 3.6, .4], [5.6, 2.4, 1.6]]) { const h = new THREE.Mesh(new THREE.SphereGeometry(.95, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), lemM); h.rotation.set(Math.PI / 2 + .35, ry, 0); h.position.set(x, 1.05, z); plate.add(h);
    const f = new THREE.Mesh(new THREE.CircleGeometry(.93, 24), lemIn); f.rotation.copy(h.rotation); f.rotateX(-Math.PI / 2); f.position.copy(h.position); f.translateZ(.005); plate.add(f); }
  const cup = new THREE.Mesh(CYL(1.2, 1, 1.1, 24), STD(0xf4f4f4, { roughness: .2 })); cup.position.set(-9.5, .55, 5); plate.add(cup);
  const but = new THREE.Mesh(new THREE.CircleGeometry(1.1, 24), STD(0xffd65a, { roughness: .2, emissive: 0x3a2a00 })); but.rotation.x = -Math.PI / 2; but.position.set(-9.5, 1.08, 5); plate.add(but);
  for (let k = 0; k < 50; k++) { const a = rnd() * 6.28, r = 2 + rnd() * 4.5; const p = new THREE.Mesh(new THREE.SphereGeometry(.07, 6, 4), STD(0x3fae35, { emissive: 0x0a2a08 })); p.position.set(Math.cos(a) * r, .45, Math.sin(a) * r); plate.add(p); }
  const lamp = new THREE.PointLight(0xffd29a, 120, 0, 1.6); lamp.position.set(6, 18, 10); plate.add(lamp); const rim = new THREE.PointLight(0x9fd0ff, 80, 0, 1.6); rim.position.set(-10, 8, -12); plate.add(rim); }

// ---------- harita: Norveç ----------
function mapNor(t, a) {
  const c = $("map"); c.style.opacity = a; const g = MP; g.clearRect(0, 0, 1080, 1920); if (a <= 0) return;
  const lon0 = -6, lat0 = 72, span = 40, k = 1080 / span, py = 330; const X = lo => (lo - lon0) * k, Y = la => py + (lat0 - la) * k * 1.75;
  const gr = g.createLinearGradient(0, 0, 0, 1920); gr.addColorStop(0, "#1f86b8"); gr.addColorStop(1, "#155f88"); g.fillStyle = gr; g.fillRect(0, 0, 1080, 1920);
  for (const o of DUNYA) { const xs = o.r; if (xs.every(([lo]) => lo < lon0 - 10 || lo > lon0 + span + 10)) continue;
    g.beginPath(); xs.forEach(([lo, la], i) => i ? g.lineTo(X(lo), Y(la)) : g.moveTo(X(lo), Y(la))); g.closePath(); g.fillStyle = o.c === "NOR" ? "#f1ebdc" : "#8d9a9e"; g.fill(); g.strokeStyle = "#0e3550"; g.lineWidth = 1.5; g.stroke(); }
  const [lo, la] = [5.7, 59.0], e = sm((t - .3) / .35); if (e <= 0) return; g.globalAlpha = e;
  g.fillStyle = "#e3141b"; g.beginPath(); g.arc(X(lo), Y(la), 18, 0, 7); g.fill();
  const r = 20 + 46 * ((t * 1.1) % 1); g.strokeStyle = `rgba(255,213,74,${1 - (r - 20) / 46})`; g.lineWidth = 6; g.beginPath(); g.arc(X(lo), Y(la), r, 0, 7); g.stroke();
  g.textAlign = "center"; g.font = "80px AN"; g.fillStyle = "#fff"; g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 12; g.fillText(EN ? "NORWAY" : "NORVEÇ", X(12), Y(64.5)); g.shadowBlur = 0; g.globalAlpha = 1; g.textAlign = "left";
}

function mapTr(t, a) {
  const c = $("map"); c.style.opacity = a; const g = MP; g.clearRect(0, 0, 1080, 1920); if (a <= 0) return;
  const lon0 = 22.5, lat0 = 44, span = 23, k = 1080 / span, py = 520; const X = lo => (lo - lon0) * k, Y = la => py + (lat0 - la) * k * 1.3;
  const gr = g.createLinearGradient(0, 0, 0, 1920); gr.addColorStop(0, "#1f86b8"); gr.addColorStop(1, "#155f88"); g.fillStyle = gr; g.fillRect(0, 0, 1080, 1920);
  for (const o of DUNYA) { const xs = o.r; if (xs.every(([lo]) => lo < lon0 - 8 || lo > lon0 + span + 8)) continue;
    g.beginPath(); xs.forEach(([lo, la], i) => i ? g.lineTo(X(lo), Y(la)) : g.moveTo(X(lo), Y(la))); g.closePath(); g.fillStyle = o.c === "TUR" ? "#f1ebdc" : "#8d9a9e"; g.fill(); g.strokeStyle = "#0e3550"; g.lineWidth = 1.5; g.stroke(); }
  const [lo, la] = [26.4, 40.15], e = sm((t - .3) / .35); if (e <= 0) return; g.globalAlpha = e;
  g.fillStyle = "#e3141b"; g.beginPath(); g.arc(X(lo), Y(la), 18, 0, 7); g.fill();
  const r = 20 + 46 * ((t * 1.1) % 1); g.strokeStyle = `rgba(255,213,74,${1 - (r - 20) / 46})`; g.lineWidth = 6; g.beginPath(); g.arc(X(lo), Y(la), r, 0, 7); g.stroke();
  g.textAlign = "center"; g.font = "80px AN"; g.fillStyle = "#fff"; g.shadowColor = "rgba(0,0,0,.5)"; g.shadowBlur = 12; g.fillText(EN ? "TURKEY" : "ÇANAKKALE", X(lo) + 60, Y(la) - 80); g.shadowBlur = 0; g.globalAlpha = 1; g.textAlign = "left";
}
// ================= çekimler =================
const K = (o) => base(Object.assign({ tuna: "hide", ham: "hide", mood: "day", amp: 0 }, o));
const H = (x, y, z) => P_H.clone().add(V(x, y, z)), SD = (x, y, z) => P_S.clone().add(V(x, y, z)), OU = (x, y, z) => P_O.clone().add(V(x, y, z));
const cellCam = (dx, dy, dz, fov = 48, o = V(0, 0, 0)) => { const c = HCP(); camSet(c.clone().add(V(dx, dy, dz)), c.clone().add(o), fov); };
const TRAY = (u, fov = 50) => { const c = H(0, TOPY, 0); camSet(c.clone().add(V(lerp(1.5, -1, u), 10.5 + u * 2.5, 10 + u * 3)), c.clone().add(V(0, 0, -.8)), fov); };
const S4 = {
  hook: (lt, d) => { TRAY(sm(lt / d) * .5); return K({ set: "hall" }); },
  room: (lt, d) => { const u = sm(lt / d); cellCam(lerp(3, 2, u), lerp(6.4, 5, u), lerp(6, 4.6, u), 48); return K({ set: "hall", hero: "cell", gs: .56, ring: lt }); },
  hot: (lt, d) => { const u = sm(lt / d); camSet(H(lerp(4, 0, u), 11, 34), H(0, 9, -40), 52); return K({ set: "hall", snow: 1 }); },
  whyq: (lt, d) => { const u = sm(lt / d); camSet(H(lerp(34, 30, u), 22, lerp(30, 26, u)), H(-2, 3, -4), 52); return K({ set: "hall" }); },
  step: (lt, d) => { const u = sm(lt / d); camSet(H(lerp(30, 22, u), lerp(22, 18, u), lerp(26, 22, u)), H(-2, 4, -4), 52); return K({ set: "hall" }); },
  cta: (lt, d) => { TRAY(.5 + sm(lt / d) * .5); return K({ set: "hall", cta: lt, ctaD: d }); },
  name: (lt, d) => { const u = sm(lt / d); camSet(OU(lerp(40, 30, u), 22, lerp(70, 62, u)), OU(2, 3, 0), 50); return K({ set: "out", leds: 1 }); },
  live: (lt) => { camSet(OU(0, 60, 80), OU(0, 0, 0)); return K({ set: "out", nor: lt }); },
  tr: (lt) => { camSet(OU(0, 60, 80), OU(0, 0, 0)); return K({ set: "out", trm: lt }); },
  mother: (lt, d) => { const u = sm(lt / d); camSet(SD(lerp(-11.5, -10.5, u), 2.2, lerp(2.4, 1.6, u)), SD(0, .7, 0), 55); return K({ set: "studio", hero: "studio", gs: 1.5, eggs: 1, roll: 0 }); },
  hatch: (lt, d) => { camSet(SD(-11.5, 3.4, 2.2), SD(0, 2.2, 0), 58); return K({ set: "studio", hero: "studio", gs: 1.5, eggs: 1, roll: 0, larv: lt }); },
  tanks: (lt, d) => { const u = sm(lt / d); camSet(H(lerp(4, 2, u), 9, CON_Z + lerp(13, 11, u)), H(-12, 3.8, CON_Z), 50); return K({ set: "hall", swirl: 1 }); },
  molt: (lt, d) => { camSet(SD(2, 2.8, 6.4), SD(0, 2.2, 0), 44); return K({ set: "studio", hero: "larva", molt: lt, moltD: d }); },
  mini: (lt, d) => { const u = ease(clamp(lt / (d * .8))); camSet(SD(3.2, lerp(3.4, 2.4, u), 6.6), SD(0, lerp(2.2, .5, u), 0), 46); return K({ set: "studio", hero: "larva", gs: .9, settle: u, n4: lt }); },
  like: (lt, d) => { camSet(SD(3.2, 2.4, 6.6), SD(0, .5, 0), 46); return K({ set: "studio", hero: "larva", gs: .9, settle: 1, chip: ["like", fadeIO(lt, d)] }); },
  rooms: (lt, d) => { const u = ease(clamp(lt / (d * .75))); cellCam(2.6, 6.2, 5.6, 48); return K({ set: "hall", hero: "cell", gs: .42, drop: u, empty: 1 }); },
  flow: (lt, d) => { const u = sm(lt / d); cellCam(lerp(4.5, 3.5, u), 8.5, 9, 50, V(0, 0, -1.5)); return K({ set: "hall", hero: "cell", gs: .46, flow: 1, temp: lt }); },
  cold: (lt, d) => { cellCam(1.9, 4.6, 4.3, 46); return K({ set: "hall", hero: "cell", gs: .46, cold: 1, act: .05 }); },
  warm: (lt, d) => { cellCam(1.9, 4.6, 4.3, 46); return K({ set: "hall", hero: "cell", gs: lerp(.46, .54, sm(lt / d)), warm: 1, act: 1.3 }); },
  dc: (lt, d) => { const u = sm(lt / d); camSet(OU(lerp(-30, -20, u), 16, 44), OU(-4, 3, 0), 50); return K({ set: "out", leds: 1 }); },
  pipe: (lt, d) => { const u = sm(lt / d); camSet(OU(lerp(-6, 4, u), 13, 32), OU(2, 3, 2), 52); return K({ set: "out", leds: 1, hot: 1 }); },
  feed: (lt, d) => { cellCam(2, 5, 4.6, 46); return K({ set: "hall", hero: "cell", gs: .54, pel: lt }); },
  kg: (lt, d) => { cellCam(2.2, 5.4, 5, 48); return K({ set: "hall", hero: "cell", gs: .56, pel: lt + 3, kg: lt }); },
  growth: (lt, d) => { const u = sm(lt / (d * .6)); cellCam(2.3, 5.6, 5.2, 48); return K({ set: "hall", hero: "cell", gs: lerp(.56, .7, u), grow: lt, growD: d }); },
  plate: (lt, d) => { const u = sm(lt / d), a = .5 + u * .5; const C0 = P_PL.clone().add(V(-.5, 1, .5)); camSet(C0.clone().add(V(Math.cos(a) * 17, lerp(16, 13, u), Math.sin(a) * 17)), C0, 46); return K({ set: "plate" }); },
  answerq: (lt, d) => { const u = sm(lt / d); TRAY(.3 + u * .4); return K({ set: "hall", ring: lt }); },
  fight: (lt, d) => { camSet(H(P_SH.x + 5, 15, P_SH.z + 6), H(P_SH.x, 1.2, P_SH.z - .3), 50); return K({ set: "hall", fight: lt, fightD: d }); },
  ninety: (lt, d) => { camSet(H(P_SH.x + 5, 15, P_SH.z + 6), H(P_SH.x, 1.2, P_SH.z - .3), 50); return K({ set: "hall", ninety: lt, ninetyD: d }); },
  comment: (lt, d) => { cellCam(2.3, 5.6, 5.2, 48); return K({ set: "hall", hero: "cell", gs: .62, chip: ["comment", fadeIO(lt, d + 1.2)] }); },
  comment2: (lt, d) => { cellCam(2.3, 5.6, 5.2, 48); return K({ set: "hall", hero: "cell", gs: .62, chip: ["comment", fadeIO(lt + 1.2, d + 1.2)] }); },
  loop: (lt, d) => { TRAY(sm(lt / d) * .5); return K({ set: "hall" }); },
};
for (const k in S4) S[k] = S4[k];

function apply2(st, T) {
  placeHamsi({ ham: "hide" }, T);
  [predator, plank, bigH, harbor, kulac, brail, crates, pblock, sCone, RINGS, pline, LEADS].forEach(o => { if (o && o.visible !== undefined) o.visible = false; }); crew.forEach(o => o.visible = false); pulses.forEach(o => o.visible = false);
  const set = st.set; hall.visible = set === "hall"; studio.visible = set === "studio"; outs.visible = set === "out"; plate.visible = set === "plate";
  scene.fog.density = 0; renderer.toneMappingExposure = set === "out" ? .95 : .9; sea.visible = false; bed.visible = false; abyss.visible = false;
  [SNOW, SWIRL, LARV, MOTE, FLOW, PEL, HOTF, STEAM].forEach(p => p.visible = false); HERO.visible = HERO2.visible = GHOST.visible = pip.visible = false; SMALL.forEach(m => m.visible = false);
  // toplu ıstakozlar (salon)
  if (hall.visible) { LI.forEach((l, i) => { const hide = (st.hero === "cell" || st.empty) && l.r === HC.r && l.ix === HC.ix && l.iz === HC.iz; const p = cellPos(l.r, l.ix, l.iz);
      dummy.position.copy(p); dummy.rotation.set(0, l.yaw + Math.sin(T * .4 + l.ph) * .25, 0); dummy.scale.setScalar(hide ? 0 : l.sc); dummy.updateMatrix(); LOB.setMatrixAt(i, dummy.matrix); }); LOB.instanceMatrix.needsUpdate = true;
    waterM.color.set(st.cold ? 0xbfe6f5 : 0x1f9cc8); waterM.opacity = st.cold ? .55 : .42; }
  // kahraman
  if (st.hero) { HERO.visible = true; const gs = st.gs ?? 1; let p, yaw = .6, roll = st.roll || 0, act = st.act ?? 1;
    if (st.hero === "cell") { p = HCP(); p.y += .02; if (st.drop != null) p.y += (1 - st.drop) * 4.2; yaw = .7 + Math.sin(T * .3) * .2; }
    else if (st.hero === "studio") { p = SD(0, .55 + (roll ? .35 : 0), 0); yaw = -.75; }
    else { p = SD(0, 2.2, 0); yaw = -.6; }
    if (st.settle != null) p.y = P_S.y + lerp(2.2, .25, st.settle);
    HERO.position.copy(p); HERO.rotation.set(roll, yaw, st.hero === "larva" && st.settle == null ? Math.sin(T * 2) * .1 : 0);
    let s = gs, clawS = 1, flap = 0; if (st.hero === "larva" && st.molt != null) { const k = clamp(st.molt / (st.moltD * .9)), n = Math.min(3, Math.floor(k * 3) + 1); s = .6 + .1 * n; clawS = .25 + .15 * n; flap = Math.sin(T * 6) * .35;
      const e = st.molt / (st.moltD * .9) * 3 % 1; GHOST.visible = e < .5 && st.molt > .2; GHOST.position.copy(p).add(V(-.8 * e, .3 * e, 0)); GHOST.rotation.copy(HERO.rotation); GHOST.scale.setScalar(s * .95); GHOST.traverse(o => { if (o.isMesh) o.material.opacity = .35 * (1 - e * 2); });
      bigTxt(String(n), 1, 380); }
    if (st.hero === "larva" && st.molt == null && st.settle != null) { clawS = .85; flap = (1 - st.settle) * Math.sin(T * 6) * .3; }
    HERO.scale.setScalar(s); poseLob(HERO, T, { act, clawS, flap, eggs: st.eggs, ph: 1 }); if (GHOST.visible) poseLob(GHOST, T, { clawS, act: 0 });
    if (st.drop != null) { pip.visible = true; const c = HCP().sub(P_H); pip.position.set(c.x + .1, c.y + 2.2 + (1 - st.drop) * 3.6, c.z); HERO.visible = st.drop > .02; } }
  // pencere karı
  if (st.snow) { SNOW.visible = true; const p = SNOW.geometry.attributes.position; for (let i = 0; i < 900; i++) { const r = PR[i]; p.setXYZ(i, P_H.x + (r[0] - .5) * 78, P_H.y + 7.5 + ((r[1] - T * .08 * (.6 + r[2])) % 1 + 1) % 1 * 21, P_H.z - 84 + r[3] * .5); } p.needsUpdate = true; }
  // konik tank girdabı
  if (st.swirl) { SWIRL.visible = true; const p = SWIRL.geometry.attributes.position; for (let i = 0; i < 1800; i++) { const r = PR[i + 3000], k = i % 3, a = r[0] * 6.28 + T * (1.2 + r[1]), y = 1.8 + r[2] * 4.8, R = Math.min(2.1, (y - 1.4) * .9) * (.3 + .7 * r[3]);
      p.setXYZ(i, P_H.x + CON_X[k] + Math.cos(a) * R, P_H.y + y + Math.sin(T * 2 + r[1] * 9) * .1, P_H.z + CON_Z + Math.sin(a) * R); } p.needsUpdate = true; }
  // larvalar (yumurtadan çıkış)
  if (st.larv != null) { LARV.visible = true; const p = LARV.geometry.attributes.position; for (let i = 0; i < 1400; i++) { const r = PR[i + 5000], t0 = r[0] * 1.6, e = clamp((st.larv - t0) / 3.5);
      const base0 = HERO.localToWorld(V(-.5 - r[1] * .5, -.2, (r[2] - .5) * .3)); p.setXYZ(i, base0.x + (r[3] - .5) * 9 * e + Math.sin(T + i) * .1 * e, base0.y + e * (1 + r[2] * 5), base0.z + (r[1] - .5) * 6 * e); } p.needsUpdate = true;
    LARV.material.size = .16; }
  if (set === "studio") { MOTE.visible = true; const p = MOTE.geometry.attributes.position; for (let i = 0; i < 700; i++) { const r = PR[i + 7000]; p.setXYZ(i, P_S.x + (r[0] - .5) * 30, P_S.y + r[1] * 12 + Math.sin(T * .3 + i) * .2, P_S.z + (r[2] - .5) * 24); } p.needsUpdate = true; }
  // su akışı
  if (st.flow) { FLOW.visible = true; const p = FLOW.geometry.attributes.position; for (let i = 0; i < 1600; i++) { const r = PR[i + 1000], f = (T * .25 + r[0]) % 1; p.setXYZ(i, P_H.x + RACKX[HC.r] + (r[1] - .5) * NXC * CS, P_H.y + TOPY + .3 + r[2] * .12, P_H.z - NZC + f * NZC * CS); } p.needsUpdate = true;
    bigTxt(EN ? "64–72°F" : "18–22°C", sm(st.temp / .3), 520); }
  if (st.cold) { SNOW.visible = true; const c = HCP(), p = SNOW.geometry.attributes.position; for (let i = 0; i < 900; i++) { const r = PR[i]; p.setXYZ(i, c.x + (r[0] - .5) * 8, c.y + .5 + ((r[1] - T * .05 * (.5 + r[2])) % 1 + 1) % 1 * 6, c.z + (r[3] - .5) * 8); } p.needsUpdate = true;
    bigTxt(EN ? "COLD" : "SOĞUK", 1, 520, "#bfeaff"); }
  if (st.warm) bigTxt(EN ? "WARM" : "SICAK", 1, 520, "#ffb347");
  // yem
  if (st.pel != null) { PEL.visible = true; const c = HCP(), p = PEL.geometry.attributes.position; for (let i = 0; i < 240; i++) { const r = PR[i + 8000], t0 = r[0] * 2.5, e = clamp((st.pel - t0) / 1.4);
      p.setXYZ(i, c.x + (r[1] - .5) * 1.6, c.y + .15 + (1 - e) * 4.5, c.z + (r[2] - .5) * 1.6); } p.needsUpdate = true; }
  if (st.kg != null) { const a = sm(st.kg / .3), c = HCP(); const [x1, y1] = proj(c.clone().add(V(-.2, 1.6, 0))); bigTxt(EN ? "1 KG FEED" : "1 KG YEM", a, 470, "#ffd54a", 120, 540); bigTxt(EN ? "= 1 KG LOBSTER" : "= 1 KG ISTAKOZ", sm((st.kg - .8) / .3), 610, "#fff", 120, 540); }
  if (st.grow != null) { const a = sm((st.grow - st.growD * .45) / .3); bigTxt(EN ? "300 G" : "300 GRAM", sm(st.grow / .3), 470); bigTxt(EN ? "8 INCHES" : "20 CM", a, 640, "#ffd54a", 160); }
  // dış: LED, sıcak su, buhar
  if (outs.visible) { const col = new THREE.Color(); for (let i = 0; i < LEDN; i++) { const on = ((T * 3 + PR[i][0] * 7) % 1) < .7; col.set(on ? (PR[i][1] < .7 ? 0x5affaa : 0x5ab8ff) : 0x1a2a22); LEDS.setColorAt(i, col); } LEDS.instanceColor.needsUpdate = true;
    if (st.hot) { HOTF.visible = true; const p = HOTF.geometry.attributes.position; for (let i = 0; i < 220; i++) { const r = PR[i + 600], f = (T * .35 + r[0]) % 1; p.setXYZ(i, P_O.x - 7 + f * 17, P_O.y + 3 + (r[1] - .5) * .5, P_O.z + 3 + (r[2] - .5) * .5 + 1.2); } p.needsUpdate = true;
      STEAM.visible = true; const q = STEAM.geometry.attributes.position; for (let i = 0; i < 300; i++) { const r = PR[i + 900], f = (T * .2 + r[0]) % 1; q.setXYZ(i, P_O.x + 18 + (r[1] - .5) * 20 + f * 2, P_O.y + 7.5 + f * 8, P_O.z + 2 + (r[2] - .5) * 10); } q.needsUpdate = true; STEAM.material.opacity = .3; } }
  if (st.nor != null) mapNor(st.nor, sm(st.nor / .3)); if (st.trm != null) mapTr(st.trm, sm(st.trm / .3));
  // halka (tek hücreyi göster)
  if (st.ring != null && hall.visible) { const c = HCP(); const [x, y] = proj(c); const r = 70 + 30 * Math.sin(T * 4); LN.save(); LN.globalAlpha = sm(st.ring / .4); LN.strokeStyle = "#ffd54a"; LN.lineWidth = 8; LN.beginPath(); LN.arc(x, y, r, 0, 7); LN.stroke(); LN.restore(); }
  // ortak tank: kavga
  if (st.fight != null) { const k = clamp(st.fight / (st.fightD * .8)); HERO.visible = HERO2.visible = true; const c = H(P_SH.x, 1.12, P_SH.z);
    const d0 = lerp(3.6, 1.8, ease(k)); HERO.position.copy(c).add(V(.2, 0, d0)); HERO.rotation.set(0, Math.PI / 2, 0); HERO2.position.copy(c).add(V(-.2, 0, -d0)); HERO2.rotation.set(0, -Math.PI / 2, 0);
    [HERO, HERO2].forEach((h, i) => { h.scale.setScalar(1.0); poseLob(h, T, { act: 1.5, raise: .35 * k, spread: .35 * k, snap: k > .7 ? (.5 + .5 * Math.sin(T * 9 + i * 2)) * .4 : 0, ph: i * 2 }); });
    if (k > .75) { const s = sm((k - .75) / .25); HERO.position.z += Math.sin(T * 11) * .06 * s; } }
  if (st.ninety != null) { const c = H(P_SH.x, 1.12, P_SH.z), k = st.ninety / st.ninetyD; SMALL.forEach((m, i) => { m.visible = true; const r = PR[i + 40]; const keep = i === 4;
      const t0 = .1 + i * .07 + (i > 4 ? -.07 : 0), e = keep ? 0 : sm((k - t0) / .12); m.position.set(c.x + ((i % 3) - 1) * 2.4 + (r[0] - .5) * .5, c.y, c.z + (Math.floor(i / 3) - 1.5) * 2.2 + (r[1] - .5) * .4); m.rotation.set(0, r[2] * 6.28 + Math.sin(T + i) * .3, 0); m.scale.setScalar(.6 * (1 - e) + .001); m.material.opacity = 1 - e; });
    bigTxt("%90", sm((k - .55) / .1), 520, "#ffd54a", 240); }
}
function bigTxt(txt, al, y = 560, col = "#fff", size = 220, x = 540) { if (al <= 0) return; LN.save(); LN.globalAlpha = al; LN.textAlign = "center"; LN.font = `${size}px AN`; LN.fillStyle = col; LN.shadowColor = "rgba(0,0,0,.55)"; LN.shadowBlur = 30; LN.fillText(txt, x, y); LN.restore(); LN.textAlign = "left"; }
const _applyBase = apply; apply = (st, T) => { _applyBase(st, T); apply2(st, T); };
