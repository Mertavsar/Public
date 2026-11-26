// ================= NORWAY (dikey) ek modeller + çekimler =================
MOODS.night = { top: 0x0b1530, hor: 0x2a3a66, deep: 0x07223a, sunc: 0x9fb4ff, sun: V(.3, .25, -.6), amp: .8, exp: .9, fog: 0x1c2a4a };
MOODS.dawn = { top: 0x3a5d93, hor: 0xffc48a, deep: 0x0d4a6a, sunc: 0xffd6a0, sun: V(.9, .12, -.3), amp: .7, exp: 1.05, fog: 0xe8c8a8 };
MOODS.grey = { top: 0x56687a, hor: 0xb9c3cc, deep: 0x123a50, sunc: 0xdfe6ec, sun: V(-.3, .6, .2), amp: 2.2, exp: 1.0, fog: 0xa7b2bc };
SN.R = 60; SN.D = 48;

// ---- hamsi sürüsü ----
const hamsiG = (() => {
  const P = [], C = [], push = (a, b, c, ca, cb, cc) => { P.push(...a, ...b, ...c); C.push(...ca, ...cb, ...cc); };
  const NS = 30, NK = 10, L0 = -.9, L1 = 1.0, R = u => .02 + .2 * Math.pow(Math.sin(Math.PI * Math.pow(u, .75)), .9);
  const pt = (u, k) => { const th = k / NK * Math.PI * 2, r = R(u); return [lerp(L0, L1, u), Math.sin(th) * r * 1.05, Math.cos(th) * r * .55]; };
  const col = p => { const h = p[1]; if (h > .05) { const s = Math.sin(p[0] * 34 + Math.abs(p[2]) * 40 + Math.sin(p[0] * 9) * 2); return s > .25 ? [.03, .08, .1] : [.1, .4, .38]; } return h > .0 ? [.7, .82, .8] : [.96, .97, .98]; };
  for (let i = 0; i < NS; i++) for (let k = 0; k < NK; k++) { const a = pt(i / NS, k), b = pt((i + 1) / NS, k), c = pt((i + 1) / NS, k + 1), d = pt(i / NS, k + 1);
    push(a, b, c, col(a), col(b), col(c)); push(a, c, d, col(a), col(c), col(d)); }
  const fin = [.55, .7, .75], t = (a, b, c) => push(a, b, c, fin, fin, fin);
  t([-.88, 0, 0], [-1.22, .3, 0], [-1.05, 0, 0]); t([-.88, 0, 0], [-1.05, 0, 0], [-1.22, -.3, 0]);
  t([.05, .2, 0], [-.18, .19, 0], [-.05, .38, 0]); t([-.45, -.12, 0], [-.62, -.1, 0], [-.52, -.26, 0]);
  const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(P, 3)); g.setAttribute("color", new THREE.Float32BufferAttribute(C, 3)); g.computeVertexNormals(); return g; })();
const NH = 1800, HAM = new THREE.InstancedMesh(hamsiG, new THREE.MeshStandardMaterial({ color: 0xffffff, vertexColors: true, metalness: .88, roughness: .15, emissive: 0x0e2a34, envMapIntensity: 2.0 }), NH);
HAM.frustumCulled = false; scene.add(HAM);
const HI = []; for (let i = 0; i < NH; i++) HI.push({ th: rnd() * 6.283, r: Math.sqrt(rnd()), y: rnd(), ph: rnd() * 6.283, sp: .7 + rnd() * .6, u: rnd(), v: rnd() });
const predator = new THREE.Mesh(tuna.geometry, new THREE.MeshStandardMaterial({ vertexColors: true, metalness: .55, roughness: .3 })); predator.visible = false; scene.add(predator);
const plank = new THREE.Points((() => { const g = new THREE.BufferGeometry(), p = []; for (let i = 0; i < 1500; i++) p.push((rnd() - .5) * 120, (rnd() - .5) * 60, (rnd() - .5) * 120); g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); return g; })(),
  new THREE.PointsMaterial({ color: 0xcff6d8, size: .35, transparent: true, opacity: .8 })); plank.visible = false; scene.add(plank);
const qq = new THREE.Quaternion();
function placeHamsi(st, T) {
  const m = st.ham || "hide", C = st.hC || V(0, -20, 0), R = st.hR || 14, H = st.hH || 6, sc = st.hS || 1;
  for (let i = 0; i < NH; i++) {
    const f = HI[i]; let p, d;
    if (m === "hide" || i >= (st.hN || NH)) { dummy.position.set(0, -900, 0); dummy.scale.setScalar(0); dummy.updateMatrix(); HAM.setMatrixAt(i, dummy.matrix); continue; }
    if (m === "seine") {                                     // gırgır içinde dönen sürü (büzüldükçe dibe yakın sıkışır)
      const ang = f.th + T * .3 * f.sp, rr = f.r * R; p = V(C.x + Math.cos(ang) * rr, C.y - f.y * H + Math.sin(T * 1.2 + f.ph) * .5, C.z + Math.sin(ang) * rr); d = V(-Math.sin(ang), 0, Math.cos(ang));
    } else if (m === "ball") {                               // yemi top: yırtıcıdan kaçar
      const ang = f.th + T * .45 * f.sp, el = (f.v - .5) * Math.PI;
      p = V(Math.cos(ang) * Math.cos(el), Math.sin(el) * .8, Math.sin(ang) * Math.cos(el)).multiplyScalar(R * (.35 + .65 * f.r)).add(C);
      d = V(-Math.sin(ang), 0, Math.cos(ang));
      if (st.pred) { const off = p.clone().sub(st.pred); const dist = off.length(); if (dist < 16) { p.add(off.normalize().multiplyScalar((16 - dist) * 1.1)); } }
    } else if (m === "stream") {                             // peloton: aynı yöne akan uzun sürü
      const s = (f.u + T * .05 * f.sp) % 1; p = V(lerp(-R * 2, R * 2, s), C.y + (f.y - .5) * H, C.z + (f.r - .5) * R * .9); d = V(1, 0, 0);
    }
    d.normalize(); const wig = Math.sin(T * 10 * f.sp + f.ph) * .16;
    m4.lookAt(V(0, 0, 0), d, up); q.setFromRotationMatrix(m4); q.multiply(qq.setFromAxisAngle(up, Math.PI / 2 + wig));
    dummy.position.copy(p); dummy.quaternion.copy(q); dummy.scale.setScalar(sc * (.85 + f.v * .3)); dummy.updateMatrix(); HAM.setMatrixAt(i, dummy.matrix);
  }
  HAM.instanceMatrix.needsUpdate = true;
}

// ---- kurşun yaka ----
const LEADS = new THREE.InstancedMesh(new THREE.CylinderGeometry(.45, .45, 1.1, 10), new THREE.MeshStandardMaterial({ color: 0x3a3f44, metalness: .6, roughness: .45 }), 120); LEADS.frustumCulled = false; scene.add(LEADS);
function updateLeads(on) { LEADS.visible = on; if (!on) return; for (let i = 0; i < 120; i++) { seinePt(i / 120, 1, tmpV); dummy.position.copy(tmpV); dummy.rotation.set(0, -(SN.a0 + i / 120 * SN.close * 6.283), Math.PI / 2); dummy.scale.setScalar(1); dummy.updateMatrix(); LEADS.setMatrixAt(i, dummy.matrix); } LEADS.instanceMatrix.needsUpdate = true; }
// ---- halkalar + büzme halatı ----
const NR = 36, RINGS = new THREE.InstancedMesh(new THREE.TorusGeometry(.9, .16, 8, 18), new THREE.MeshStandardMaterial({ color: 0xb8c0c6, metalness: .9, roughness: .25 }), NR); RINGS.frustumCulled = false; scene.add(RINGS);
const pline = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshStandardMaterial({ color: 0xffb21a, roughness: .6, emissive: 0x3a2400 })); pline.frustumCulled = false; scene.add(pline);
function updateRings(on) {
  RINGS.visible = pline.visible = on; if (!on) return; const pts = [];
  for (let i = 0; i < NR; i++) { seinePt(i / NR, 1, tmpV); tmpV.y -= 1.2; pts.push(tmpV.clone()); dummy.position.copy(tmpV); dummy.rotation.set(Math.PI / 2, 0, i / NR * Math.PI * 2); dummy.scale.setScalar(1); dummy.updateMatrix(); RINGS.setMatrixAt(i, dummy.matrix); }
  RINGS.instanceMatrix.needsUpdate = true; pts.push(pts[0].clone());
  pline.geometry.dispose(); pline.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false), 200, .28, 6);
}

// ---- sonar konisi + darbe halkaları ----
const sCone = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 40, 1, true), new THREE.MeshBasicMaterial({ color: 0x5affaa, transparent: true, opacity: .16, depthWrite: false, side: THREE.DoubleSide, fog: false })); sCone.visible = false; scene.add(sCone);
const pulses = [0, 1, 2].map(() => { const m = new THREE.Mesh(new THREE.RingGeometry(.92, 1, 64), new THREE.MeshBasicMaterial({ color: 0x8affc8, transparent: true, depthWrite: false, side: THREE.DoubleSide, fog: false })); m.rotation.x = -Math.PI / 2; m.visible = false; scene.add(m); return m; });
// yüzme kesesi yakın planı: büyük tek hamsi + parlayan kese
const bigH = new THREE.Group(); { const b = new THREE.Mesh(hamsiG, new THREE.MeshPhysicalMaterial({ color: 0xffffff, vertexColors: true, metalness: .6, roughness: .2, transparent: true, opacity: .55, side: THREE.DoubleSide })); bigH.add(b);
  const sac = new THREE.Mesh(new THREE.SphereGeometry(.16, 20, 12), new THREE.MeshBasicMaterial({ color: 0xbff7ff })); sac.scale.set(2.2, .7, .7); sac.position.set(.05, .03, 0); bigH.add(sac); bigH.userData.sac = sac; }
bigH.visible = false; scene.add(bigH);

// ---- liman + fener ----
const harbor = new THREE.Group(); scene.add(harbor);
{ const stone = new THREE.MeshStandardMaterial({ color: 0x6f6a64, roughness: 1 });
  const bw = new THREE.Mesh(new THREE.BoxGeometry(260, 8, 18), stone); bw.position.set(-40, 1, -60); harbor.add(bw);
  const tw = new THREE.Mesh(new THREE.CylinderGeometry(4, 5, 22, 16), new THREE.MeshStandardMaterial({ color: 0xe3141b })); tw.position.set(85, 15, -60); harbor.add(tw);
  for (const y of [8, 16]) { const b = new THREE.Mesh(new THREE.CylinderGeometry(4.05, 4.2, 3, 16), new THREE.MeshStandardMaterial({ color: 0xffffff })); b.position.set(85, y, -60); harbor.add(b); }
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(2.4, 16, 10), new THREE.MeshBasicMaterial({ color: 0xfff2b0 })); lamp.position.set(85, 28, -60); harbor.add(lamp);
  const town = new THREE.Points((() => { const g = new THREE.BufferGeometry(), p = []; for (let i = 0; i < 900; i++) p.push(-500 + rnd() * 1000, 2 + rnd() * 40 * rnd(), -260 - rnd() * 260); g.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); return g; })(),
    new THREE.PointsMaterial({ color: 0xffd48a, size: 2.2, sizeAttenuation: true, fog: false })); harbor.add(town);
  const hill = new THREE.Mesh(new THREE.SphereGeometry(500, 32, 12, 0, Math.PI * 2, 0, Math.PI / 2), new THREE.MeshStandardMaterial({ color: 0x1f2a22, roughness: 1 })); hill.scale.set(2.2, .22, .6); hill.position.set(0, -5, -560); harbor.add(hill); }
harbor.position.set(0, 0, 0);

// ---- tayfa (turuncu tulumlu figürler) ----
function makeCrew(col = 0xff7a1a, arms = 0) { const g = new THREE.Group(); const suit = new THREE.MeshStandardMaterial({ color: col, roughness: .6 });
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(.42, 1.1, 4, 10), suit); body.position.y = 1.55; g.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(.3, 12, 10), new THREE.MeshStandardMaterial({ color: 0xc89878 })); head.position.y = 2.7; g.add(head);
  for (const s of [-.22, .22]) { const l = new THREE.Mesh(new THREE.CapsuleGeometry(.16, .8, 4, 8), suit); l.position.set(0, .55, s); g.add(l); }
  for (const s of [-1, 1]) { const a = new THREE.Mesh(new THREE.CapsuleGeometry(.12, .8, 4, 8), suit); a.position.set(0, 2.05, s * .55); a.rotation.x = s * (arms ? Math.PI / 2 : .25); if (arms) a.position.z = s * .95; g.add(a); }
  return g; }
const crew = []; for (let i = 0; i < 14; i++) { const c = makeCrew(i % 3 ? 0xff7a1a : 0xffd21a); scene.add(c); crew.push(c); }
const kulac = makeCrew(0xff7a1a, 1); kulac.scale.setScalar(3); scene.add(kulac);
// ---- hidrolik makara + ağ bandı ----
const pblock = new THREE.Group(); { const blk = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 1.4, 24), new THREE.MeshStandardMaterial({ color: 0xd9a21a, metalness: .3 })); blk.rotation.x = Math.PI / 2; pblock.add(blk); pblock.userData.blk = blk;
  const band = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 30, 1, 60), new THREE.MeshStandardMaterial({ color: 0x2c5f74, roughness: 1, side: THREE.DoubleSide, transparent: true, opacity: .9 })); band.position.set(1.6, -15, 0); pblock.add(band); pblock.userData.band = band; }
scene.add(pblock);
// ---- kepçe + kasalar ----
const brail = new THREE.Group(); { const bag = new THREE.Mesh(new THREE.SphereGeometry(2.4, 18, 12), new THREE.MeshStandardMaterial({ color: 0xdfe8ee, metalness: .85, roughness: .2 })); bag.scale.set(1, 1.2, 1); brail.add(bag);
  const net = new THREE.Mesh(new THREE.SphereGeometry(2.55, 16, 10), new THREE.MeshBasicMaterial({ color: 0x2c5f74, wireframe: true })); net.scale.set(1, 1.2, 1); brail.add(net);
  const rope = new THREE.Mesh(new THREE.CylinderGeometry(.08, .08, 12, 6), new THREE.MeshStandardMaterial({ color: 0x2a2d30 })); rope.position.y = 8.5; brail.add(rope); } scene.add(brail);
const crates = new THREE.Group(); { const cm = new THREE.MeshStandardMaterial({ color: 0x2b7ad9, roughness: .6 }), fm = new THREE.MeshStandardMaterial({ color: 0xdfe7ec, metalness: .8, roughness: .25 }), im = new THREE.MeshStandardMaterial({ color: 0xf4fbff, roughness: .2, transparent: true, opacity: .85 });
  for (let i = 0; i < 24; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(1.6, .5, 1), cm); c.position.set((i % 4) * 1.7, Math.floor(i / 8) * .55, Math.floor((i % 8) / 4) * 1.1); crates.add(c);
    const f = new THREE.Mesh(new THREE.BoxGeometry(1.45, .08, .88), fm); f.position.copy(c.position).add(V(0, .26, 0)); crates.add(f);
    const ic = new THREE.Mesh(new THREE.BoxGeometry(1.4, .06, .8), im); ic.position.copy(c.position).add(V(0, .31, 0)); ic.visible = i % 2 === 0; crates.add(ic); } }
scene.add(crates);

// ---- 2D: derinlik ekranı (yankı) + saat ----
function echogram(t, a) {
  const c = $("panel"); c.style.opacity = a; const g = PANEL; g.clearRect(0, 0, 900, 900); if (a <= 0) return;
  g.fillStyle = "#06121c"; g.beginPath(); g.roundRect(0, 0, 900, 900, 34); g.fill(); g.strokeStyle = "#2b3a46"; g.lineWidth = 12; g.stroke();
  const x0 = 70, y0 = 80, W = 780, H = 760; g.save(); g.beginPath(); g.rect(x0, y0, W, H); g.clip();
  const sh = t * 140; for (let x = 0; x < W; x += 4) { const X = x0 + x, wx = (x + sh) * .01;
    const bed = y0 + H * (.82 + .05 * Math.sin(wx * 1.3) + .02 * Math.sin(wx * 4.1)); const gr = g.createLinearGradient(0, bed, 0, y0 + H); gr.addColorStop(0, "#c98a3a"); gr.addColorStop(1, "#4a2b12"); g.fillStyle = gr; g.fillRect(X, bed, 4, y0 + H - bed);
    const sc = Math.exp(-Math.pow((x - W * .62 + Math.sin(t) * 10) / 120, 2)); if (sc > .05 && t > .4) { const yc = y0 + H * .42, hh = H * .16 * sc; for (let k = 0; k < 6; k++) { g.fillStyle = `rgba(255,${60 + k * 30},40,${.5 * sc * clamp((t - .4) * 2)})`; g.fillRect(X, yc - hh / 2 + Math.sin(x * .3 + k) * 8 + k * 4, 4, hh / 6); } } }
  g.restore(); g.strokeStyle = "rgba(120,200,255,.25)"; g.lineWidth = 2; g.fillStyle = "#8fc9ff"; g.font = "28px PS";
  for (let k = 0; k <= 4; k++) { const y = y0 + H * k / 4; g.beginPath(); g.moveTo(x0, y); g.lineTo(x0 + W, y); g.stroke(); g.fillText(`${k * 20} m`, 12, y + 10); }
}
function clockDial(t, a) {
  LN.save(); LN.globalAlpha = a; const cx = 1480, cy = 400, R = 210;
  LN.fillStyle = "rgba(10,18,30,.72)"; LN.beginPath(); LN.arc(cx, cy, R + 24, 0, 7); LN.fill();
  const ang = h => (h % 12) / 12 * Math.PI * 2 - Math.PI / 2;
  const p = clamp(t / 1.6), from = ang(15), span = (18 / 12) * Math.PI * 2 * p;   // 15:00 → 09:00 (18 saat, 1,5 tur)
  LN.strokeStyle = "#ffd54a"; LN.lineWidth = 22; LN.lineCap = "round"; LN.beginPath(); LN.arc(cx, cy, R - 6, from, from + Math.min(span, Math.PI * 2 - .01)); LN.stroke();
  if (span > Math.PI * 2) { LN.strokeStyle = "#e3141b"; LN.beginPath(); LN.arc(cx, cy, R - 34, from, from + span - Math.PI * 2); LN.stroke(); }
  LN.fillStyle = "#fff"; LN.font = "40px AN"; LN.textAlign = "center"; LN.textBaseline = "middle";
  for (let h = 1; h <= 12; h++) { const a2 = ang(h); LN.fillText(String(h), cx + Math.cos(a2) * (R - 66), cy + Math.sin(a2) * (R - 66)); }
  const hh = 15 + 18 * p, a3 = ang(hh); LN.strokeStyle = "#fff"; LN.lineWidth = 10; LN.beginPath(); LN.moveTo(cx, cy); LN.lineTo(cx + Math.cos(a3) * (R - 100), cy + Math.sin(a3) * (R - 100)); LN.stroke();
  LN.font = "64px AN"; LN.fillStyle = "#ffd54a"; LN.fillText(p < .5 ? "15:00" : "09:00", cx, cy + R + 80); LN.restore(); LN.textAlign = "left"; LN.textBaseline = "alphabetic";
}
function spanLine(a, b, alpha) { if (alpha <= 0) return; const [x1, y1] = proj(a), [x2, y2] = proj(b); LN.save(); LN.globalAlpha = alpha; LN.strokeStyle = "#ffd54a"; LN.lineWidth = 6;
  LN.beginPath(); LN.moveTo(x1, y1); LN.lineTo(x2, y2); LN.stroke(); for (const [x, y] of [[x1, y1], [x2, y2]]) { LN.beginPath(); LN.moveTo(x, y - 26); LN.lineTo(x, y + 26); LN.stroke(); } LN.restore(); }

