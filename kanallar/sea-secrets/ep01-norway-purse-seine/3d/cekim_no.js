// ================= NORWAY çekimleri (dikey 1080×1920) =================
ship.traverse(o => { if (o.isMesh && o.material && o.material.color && o.material.color.getHex() === 0x1d3f7a) o.material = o.material.clone(); });
// ---- 60 katlı bina (ağ derinliği karşılaştırması) ----
const tower = new THREE.Group(); { const H = 48, W = 9;
  const body = new THREE.Mesh(new THREE.BoxGeometry(W, H, W), new THREE.MeshStandardMaterial({ color: 0xbfe9ff, transparent: true, opacity: .32, roughness: .1, metalness: .2, depthWrite: false })); body.position.y = H / 2; tower.add(body);
  const p = []; for (let i = 0; i <= 60; i++) { const y = i * H / 60; for (const [a, b] of [[[-1, -1], [1, -1]], [[1, -1], [1, 1]], [[1, 1], [-1, 1]], [[-1, 1], [-1, -1]]]) p.push(a[0] * W / 2, y, a[1] * W / 2, b[0] * W / 2, y, b[1] * W / 2); }
  for (const [x, z] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) p.push(x * W / 2, 0, z * W / 2, x * W / 2, H, z * W / 2);
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3));
  tower.add(new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .75 })));
  const ant = new THREE.Mesh(new THREE.CylinderGeometry(.15, .15, 5, 6), new THREE.MeshBasicMaterial({ color: 0xffffff })); ant.position.y = H + 2.5; tower.add(ant); }
tower.visible = false; scene.add(tower);
// ---- pompa hortumu ----
const hoseMat = new THREE.MeshStandardMaterial({ color: 0xd8e4ea, transparent: true, opacity: .35, roughness: .15, side: THREE.DoubleSide, depthWrite: false });
const hose = new THREE.Mesh(new THREE.BufferGeometry(), hoseMat); hose.frustumCulled = false; scene.add(hose); let hoseCurve = null;
const hoseRib = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshStandardMaterial({ color: 0x1a1d20, roughness: .6 })); hoseRib.frustumCulled = false; scene.add(hoseRib);
function setHose(a, b) { const mid = a.clone().lerp(b, .5); mid.y = Math.max(a.y, b.y) + 3; const c1 = a.clone().lerp(mid, .6); c1.y += 2;
  hoseCurve = new THREE.CatmullRomCurve3([a, c1, mid, b.clone().add(V(0, 6, 0)), b]); hose.geometry.dispose(); hose.geometry = new THREE.TubeGeometry(hoseCurve, 120, 1.3, 16);
  const ribs = []; hoseRib.geometry.dispose(); hoseRib.geometry = new THREE.TubeGeometry(hoseCurve, 120, 1.34, 16); hoseRib.material.wireframe = true; }
// ---- tank + olimpik havuz dioraması (metre ölçeğinde, ayrı konumda) ----
const P_TK = V(900, 0, 900);
const dio = new THREE.Group(); dio.position.copy(P_TK); scene.add(dio);
const steel = new THREE.MeshStandardMaterial({ color: 0x8a96a0, metalness: .6, roughness: .35 });
const coldW = new THREE.MeshStandardMaterial({ color: 0x30b4ec, transparent: true, opacity: .75, roughness: .05, metalness: .1, emissive: 0x0b3346, depthWrite: false });
const poolW = new THREE.MeshStandardMaterial({ color: 0x1d8fd6, transparent: true, opacity: .9, roughness: .05, emissive: 0x06304a });
{ const slab = new THREE.Mesh(new THREE.BoxGeometry(66, 3, 112), new THREE.MeshStandardMaterial({ color: 0x5d666d, roughness: .9 })); slab.position.set(0, -1.5, 0); dio.add(slab); }
// havuz: 50×25×2 m, şerit ipleri
const pool = new THREE.Group(); pool.position.set(0, 0, -28); dio.add(pool);
{ const tile = new THREE.Mesh(new THREE.BoxGeometry(52, .2, 27), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .6 })); tile.position.y = .1; pool.add(tile);
  const pw = new THREE.Mesh(new THREE.BoxGeometry(50, 1, 25), poolW); pw.position.y = 0; pool.add(pw); pool.userData.w = pw;
  const wm = new THREE.MeshStandardMaterial({ color: 0xf4f6f7, roughness: .5 }); for (const [sx, sz, px, pz] of [[51.2, .6, 0, 12.8], [51.2, .6, 0, -12.8], [.6, 26.2, 25.3, 0], [.6, 26.2, -25.3, 0]]) { const m = new THREE.Mesh(new THREE.BoxGeometry(sx, 2.4, sz), wm); m.position.set(px, 1.2, pz); pool.add(m); }
  for (let i = 1; i < 10; i++) { const r = new THREE.Mesh(new THREE.CylinderGeometry(.12, .12, 50, 6), new THREE.MeshStandardMaterial({ color: i % 2 ? 0xe3141b : 0xffd21a })); r.rotation.z = Math.PI / 2; r.position.set(0, 0, -12.5 + i * 2.5); pool.add(r); pool.userData.ropes = (pool.userData.ropes || []).concat(r); } }
// 4 tank: her biri 10×8×8.6 m (toplam ≈ 2.755 m³), ön yüzleri kesik (cam)
const tanks = new THREE.Group(); tanks.position.set(0, 0, 30); dio.add(tanks); const tankW = [];
for (let i = 0; i < 4; i++) { const t = new THREE.Group(); t.position.set((i % 2 - .5) * 9.5, 0, (Math.floor(i / 2) - .5) * 9); tanks.add(t);
  const th = .4, w = 8, d = 7.2, h = 12;
  for (const [sx, sy, sz, px, py, pz] of [[w, th, d, 0, 0, 0], [th, h, d, -w / 2, h / 2, 0], [th, h, d, w / 2, h / 2, 0], [w, h, th, 0, h / 2, -d / 2]]) { const m = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), steel); m.position.set(px, py, pz); t.add(m); }
  const gl = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshStandardMaterial({ color: 0xe8f6ff, transparent: true, opacity: .12, roughness: 0, depthWrite: false })); gl.position.set(0, h / 2, d / 2); t.add(gl);
  const rim = new THREE.Mesh(new THREE.BoxGeometry(w + .4, .3, .3), steel); rim.position.set(0, h, d / 2); t.add(rim);
  const wt = new THREE.Mesh(new THREE.BoxGeometry(w - .8, 1, d - .8), coldW); t.add(wt); tankW.push(wt); }
const frost = new THREE.Points((() => { const g = new THREE.BufferGeometry(), p = []; for (let i = 0; i < 700; i++) p.push((rnd() - .5) * 20, rnd() * 9, (rnd() - .5) * 18); g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); return g; })(),
  new THREE.PointsMaterial({ color: 0xffffff, size: .25, transparent: true, opacity: .7 })); tanks.add(frost);
dio.visible = false; dio.position.y = 2.5;
function tankLevel(k) { tankW.forEach(w => { const h = Math.max(.01, k * 12); w.scale.y = h; w.position.y = .2 + h / 2; }); }

const G = (o) => base(Object.assign({ tuna: "hide" }, o));
const ON = (f) => shipOnRing(f);
const AIRP = [V(-120, 250, 95), V(-110, 236, 88)];
const AIR = (lt, d, o = {}) => { const u = sm(lt / d); camSet(AIRP[0].clone().lerp(AIRP[1], u), V(-6, -10, 6), 50);
  return G(Object.assign({ xray: .5, seine: 1, ship: ON(1), skiff: ON(0), ham: "seine", hC: V(0, -6, 0), hR: 44, hH: 14, hS: 1.7 }, o)); };
const UNDER = (lt, d, o = {}) => { const u = sm(lt / d); camSet(V(lerp(30, 24, u), lerp(-60, -56, u), lerp(62, 54, u)), V(0, -24, 0), 62);
  return G(Object.assign({ seine: 1, purse: .55, ham: "seine", hC: V(0, -18, 0), hR: 38, hH: 16 }, o)); };
const BALL = (lt, d, o = {}) => { const a = .6 + lt / d * .6; camSet(V(Math.cos(a) * 52, -16, Math.sin(a) * 52), V(0, -20, 0), 52); return G(Object.assign({ ham: "ball", hC: V(0, -20, 0), hR: 16 }, o)); };
const SONAR = (lt, d, o = {}) => { const u = sm(lt / d); camSet(V(lerp(80, 70, u), -14, lerp(92, 82, u)), V(0, -20, 0), 56); return G(Object.assign({ ship: { p: V(0, 0, 0), h: 0 }, sonar: 1, ham: "ball", hC: V(0, -34, 0), hR: 12 }, o)); };
const RINGV = (lt, d, o = {}) => { seinePt(.02, 1, tmpV); const r = tmpV.clone(); const out = V(r.x, 0, r.z).normalize(); const u = sm(lt / d);
  camSet(r.clone().add(out.clone().multiplyScalar(lerp(-10, -8, u))).add(V(0, 3, 0)).add(V(-out.z, 0, out.x).multiplyScalar(4)), r.clone().add(V(0, 1, 0)), 52);
  return G(Object.assign({ seine: 1, rings: 1, ham: "seine", hC: V(0, -26, 0), hR: 40, hH: 18 }, o)); };
const NETSIDE = (lt, d, o = {}) => { const u = ease(clamp(lt / d)); camSet(V(lerp(30, 32, u), lerp(-8, -40, u), lerp(24, 22, u)), V(58, lerp(-1, -46, u), 8), 56); return G(Object.assign({ seine: 1, ham: "seine", hC: V(0, -16, 0), hR: 40, hH: 14 }, o)); };
const PUMP = (lt, d, o = {}) => { SN.R = 30; const u = sm(lt / d); camSet(V(lerp(-70, -62, u), lerp(70, 62, u), lerp(110, 100, u)), V(-14, -4, 18), 50);
  return G(Object.assign({ xray: .5, seine: 1, purse: 1, haulR: 30, ship: ON(1), ham: "seine", hC: V(0, -6, 0), hR: 20, hH: 7, hS: 1.7, hose: 1 }, o)); };
const TANK = (lt, d, o = {}) => { const u = sm(lt / d); camSet(P_TK.clone().add(V(lerp(16, 12, u), lerp(24, 22, u), lerp(68, 64, u))), P_TK.clone().add(V(0, 7, 30)), 50); return G(Object.assign({ dio: 1, lvl: 1, ham: "tank" }, o)); };
const S2 = {
  hookAir: (lt, d) => AIR(lt, d, { purse: .3 }),
  hookUnder: (lt, d) => UNDER(lt, d, { purse: .7 }),
  begin: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-90, -70, u), 40, lerp(80, 70, u)), V(lerp(-20, 0, u), 4, 0), 50); return G({ ship: { p: V(lerp(-30, 0, u), 0, 0), h: 0, run: true } }); },
  cta: (lt, d) => BALL(lt, d, { cta: lt, ctaD: d }),
  sonar: (lt, d) => SONAR(lt, d),
  echo: (lt, d) => SONAR(lt, d, { echo: lt + .2 }),
  skiff: (lt, d) => { const u = ease(clamp(lt / d)); camSet(V(-120, 240, 110), V(-14, -8, 14), 50); return G({ xray: .5, seine: 1, close: lerp(.01, .15, u), ship: ON(lerp(0, .15, u)), skiff: ON(0), ham: "ball", hC: V(0, -14, 0), hR: 18, hS: 1.6 }); },
  encircle: (lt, d) => { const u = ease(clamp(lt / (d * .92))); camSet(V(-125, 262, 100), V(-6, -10, 6), 50); return G({ xray: .5, seine: 1, close: Math.max(.15, u), ship: ON(Math.max(.15, u)), skiff: ON(0), ham: "ball", hC: V(0, -14, 0), hR: 18, hS: 1.6 }); },
  tower: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-112, -106, u), -24, lerp(66, 60, u)), V(-68, -24, 10), 62); return G({ seine: 1, ham: "seine", hC: V(0, -18, 0), hR: 40, hH: 16, tower: sm((lt - .2) / .8) }); },
  floats: (lt, d) => NETSIDE(lt, d),
  clever: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(10, 20, u), -64, lerp(42, 36, u)), V(40, -46, 20), 56); return G({ seine: 1, ham: "seine", hC: V(0, -26, 0), hR: 40, hH: 20 }); },
  like: (lt, d) => { camSet(V(20, -64, 36), V(40, -46, 20), 56); return G({ seine: 1, ham: "seine", hC: V(0, -26, 0), hR: 40, hH: 20, chip: ["like", fadeIO(lt, d)] }); },
  escape: (lt, d) => { const u = sm(lt / d); camSet(V(20, lerp(-68, -72, u), 36), V(40, -50, 20), 58); return G({ seine: 1, ham: "seine", hC: V(0, -38, 0), hR: 44, hH: 14 }); },
  secret: (lt, d) => RINGV(lt, d),
  rings: (lt, d) => RINGV(lt, d, { glowLine: 1 }),
  pull: (lt, d) => { const u = ease(clamp(lt / d)); camSet(V(0, -118, 110), V(0, -36, 0), 56); return G({ seine: 1, rings: 1, glowLine: 1, purse: u, ham: "seine", hC: V(0, -22, 0), hR: lerp(40, 28, u), hH: lerp(18, 12, u) }); },
  trapped: (lt, d) => { const a = lt / d; camSet(V(Math.cos(a) * 105, -104, Math.sin(a) * 105 + 30), V(0, -34, 0), 56); return G({ seine: 1, rings: 1, purse: 1, ham: "seine", hC: V(0, -20, 0), hR: 28, hH: 12 }); },
  pump: (lt, d) => lt < d * .55 ? PUMP(lt, d * .55) : TANK(lt - d * .55, d * .45, { lvl: .7 + .3 * sm((lt - d * .55) / (d * .45)) }),
  pool: (lt, d) => { const u = sm(lt / d), k = sm((lt - d * .3) / (d * .55)); camSet(P_TK.clone().add(V(lerp(26, 20, u), lerp(60, 56, u), lerp(96, 90, u))), P_TK.clone().add(V(0, 0, -4)), 50);
    return G({ dio: 1, lvl: k * .907, poolLvl: 1 - k, ham: "hide" }); },
  plate: (lt, d) => { const u = sm(lt / d); const s = .28 + u * .12; const p = hoseCurveAt(s); camSet(p.clone().add(V(-9, 4, 12)), p, 48);
    return G({ xray: .5, seine: 1, purse: 1, haulR: 30, ship: ON(1), ham: "seine", hC: V(0, -6, 0), hR: 20, hH: 7, hS: 1.7, hose: 1 }); },
  next: (lt, d) => AIR(lt, d, { purse: .3 }),
  comment: (lt, d) => AIR(lt, d, { purse: .3, chip: ["comment", fadeIO(lt, d)] }),
  loop: (lt, d) => { const u = ease(clamp(lt / d)); camSet(V(-140, 285, 110).lerp(AIRP[0], u), V(-6, -10, 6), 50);
    return G({ xray: .5, seine: 1, purse: lerp(.05, .3, u), ship: ON(1), skiff: ON(0), ham: "seine", hC: V(0, -6, 0), hR: 44, hH: 14, hS: 1.7 }); },
};
for (const k in S2) S[k] = S2[k];
function hoseCurveAt(s) { SN.R = 30; return hosePts(SN.R).curve.getPointAt(s); }
function hosePts(R) { const sh = shipOnRing(1); const a = V(-2, 2.6, 4).applyAxisAngle(up, sh.h).add(sh.p); const b = V(sh.p.x, 0, sh.p.z).multiplyScalar(.45); b.y = -3;
  if (!hoseCurve || hosePts._k !== R) { setHose(a, b); hosePts._k = R; } return { curve: hoseCurve }; }

function apply2(st, T) {
  hose.visible = !!st.hose; hoseRib.visible = false; if (st.hose) hosePts(SN.R);
  placeHamsi2(st, T);
  updateRings(!!st.rings); if (st.rings) pline.material.emissive.set(st.glowLine ? 0xffa000 : 0x3a2400);
  predator.visible = false; plank.visible = false; bigH.visible = false; harbor.visible = false; kulac.visible = false; brail.visible = false; crates.visible = false; pblock.visible = false; crew.forEach(c => c.visible = false);
  sCone.visible = !!st.sonar; pulses.forEach(p => p.visible = false);
  if (st.sonar) { const top = V(0, -2, 0), depth = 34; sCone.scale.set(14, depth, 14); sCone.position.set(0, top.y - depth / 2, 0); sCone.rotation.set(Math.PI, 0, 0);
    pulses.forEach((p, k) => { const s = ((T * .6 + k / 3) % 1); p.visible = true; const down = s < .5, f = down ? s * 2 : (1 - s) * 2;
      p.position.set(0, top.y - f * depth, 0); p.scale.setScalar(1 + f * 13); p.material.opacity = .7 * (1 - f * .6); p.material.color.set(down ? 0x8affc8 : 0xff7a5a); }); }
  tower.visible = !!st.tower; if (st.tower) { tower.position.set(-76, -48, 14); tower.children.forEach(c => { if (c.material) c.material.opacity = (c.isLineSegments ? .75 : .32) * st.tower; }); }
  dio.visible = !!st.dio; if (st.dio) { tankLevel(st.lvl ?? 1); const pl = st.poolLvl ?? 1, pw = pool.userData.w; pw.scale.y = Math.max(.01, pl * 2); pw.position.y = pw.scale.y / 2 + .2;
    pool.userData.ropes.forEach(r => r.position.y = pw.position.y + pw.scale.y / 2); frost.position.y = Math.sin(T) * .2; }
  if (st.echo != null) { const pn = $("panel"); pn.style.left = "190px"; pn.style.top = "150px"; pn.style.width = "700px"; pn.style.height = "700px"; echogram(st.echo, sm(st.echo / .4)); }
}
function placeHamsi2(st, T) {
  if (st.ham === "pipe" || st.ham === "tank" || st.hose) {
    if (st.ham !== "tank") placeHamsi(Object.assign({}, st, { hN: 1100 }), T);
    const C = P_TK.clone().add(V(0, 2.5, 30));
    if (st.ham === "tank") { for (let i = 0; i < NH; i++) if (i >= 600) { dummy.position.set(0, -900, 0); dummy.scale.setScalar(0); dummy.updateMatrix(); HAM.setMatrixAt(i, dummy.matrix); } }
    for (let i = (st.ham === "tank" ? 0 : 1100); i < (st.ham === "tank" ? 600 : NH); i++) { const f = HI[i]; let p, d;
      if (st.ham === "tank") { const k = i % 4, tc = tanks.children[k].position.clone().add(C); const ang = f.th + T * .5 * f.sp, rr = f.r * 2.9; const lv = (st.lvl ?? 1) * 12;
        p = V(tc.x + Math.cos(ang) * rr, C.y + .6 + f.y * Math.max(.5, lv - 1.2), tc.z + Math.sin(ang) * rr * .85); d = V(-Math.sin(ang), 0, Math.cos(ang)); }
      else { const s = (f.u + T * .35) % 1; p = hoseCurve.getPointAt(s).add(V((f.r - .5) * 1.4, (f.v - .5) * 1.4, (f.y - .5) * 1.4)); d = hoseCurve.getTangentAt(s); }
      d.normalize(); m4.lookAt(V(0, 0, 0), d, up); q.setFromRotationMatrix(m4); q.multiply(qq.setFromAxisAngle(up, Math.PI / 2 + Math.sin(T * 10 * f.sp + f.ph) * .16));
      dummy.position.copy(p); dummy.quaternion.copy(q); dummy.scale.setScalar(st.ham === "tank" ? 1.1 : .9); dummy.updateMatrix(); HAM.setMatrixAt(i, dummy.matrix); }
    HAM.instanceMatrix.needsUpdate = true; return; }
  placeHamsi(st, T);
}
const _applyBase = apply; apply = (st, T) => { if (st.haulR) SN.R = st.haulR; _applyBase(st, T); apply2(st, T); };
