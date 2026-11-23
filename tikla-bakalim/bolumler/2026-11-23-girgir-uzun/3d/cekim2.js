// ================= GIRGIR çekimleri =================
const G = (o) => base(Object.assign({ tuna: "hide" }, o));
const ON = (f) => shipOnRing(f);
const AIR = (lt, d, o = {}) => { const u = sm(lt / d); camSet(V(lerp(-190, -170, u), lerp(175, 160, u), lerp(150, 130, u)), V(0, -12, 0), 44);
  return G(Object.assign({ xray: .5, seine: 1, ship: ON(1), skiff: ON(0), ham: "seine", hC: V(0, -6, 0), hR: 44, hH: 14, hS: 1.7 }, o)); };
const UNDER = (lt, d, o = {}) => { const u = sm(lt / d); camSet(V(lerp(40, 30, u), lerp(-80, -76, u), lerp(70, 60, u)), V(0, -26, 0), 56);
  return G(Object.assign({ seine: 1, purse: .55, ham: "seine", hC: V(0, -18, 0), hR: 38, hH: 16 }, o)); };
const BALL = (lt, d, o = {}) => { const a = .6 + lt / d * .6; camSet(V(Math.cos(a) * 46, -16, Math.sin(a) * 46), V(0, -20, 0), 50); return G(Object.assign({ ham: "ball", hC: V(0, -20, 0), hR: 16 }, o)); };
const SHIPV = (lt, d, o = {}, mood = "day") => { const u = sm(lt / d); camSet(V(lerp(70, 60, u), lerp(14, 12, u), lerp(46, 40, u)), V(-4, 6, 0), 40); return G(Object.assign({ mood, ship: { p: V(0, 0, 0), h: 0, run: true } }, o)); };
const DECK = (lt, d, o = {}) => { const u = sm(lt / d); camSet(V(lerp(30, 26, u), lerp(24, 22, u), lerp(26, 22, u)), V(-3, 4, 0), 42); return G(Object.assign({ ship: { p: V(0, 0, 0), h: 0 }, crew: 1 }, o)); };
const HARB = (lt, d, mood, dir = 1) => { const u = lt / d; camSet(V(170, 20, 110), V(0, 8, -40), 42);
  return G({ mood, harbor: 1, ship: { p: V(lerp(-60, 60, dir > 0 ? u : 1 - u), 0, -20), h: dir > 0 ? 0 : Math.PI, run: true } }); };
const SONAR = (lt, d, o = {}) => { const u = sm(lt / d); camSet(V(lerp(70, 60, u), -6, lerp(80, 70, u)), V(0, -16, 0), 50); return G(Object.assign({ ship: { p: V(0, 0, 0), h: 0 }, sonar: 1, ham: "ball", hC: V(0, -34, 0), hR: 12 }, o)); };
const RINGV = (lt, d, o = {}) => { seinePt(.02, 1, tmpV); const r = tmpV.clone(); const out = V(r.x, 0, r.z).normalize(); const u = sm(lt / d);
  camSet(r.clone().add(out.clone().multiplyScalar(lerp(-14, -11, u))).add(V(0, 3, 0)).add(V(-out.z, 0, out.x).multiplyScalar(6)), r.clone().add(V(0, 1, 0)), 48);
  return G(Object.assign({ seine: 1, rings: 1, ham: "seine", hC: V(0, -26, 0), hR: 40, hH: 18 }, o)); };
const S2 = {
  hookAir: (lt, d) => AIR(lt, d, { purse: .3 }),
  hookUnder: (lt, d) => UNDER(lt, d, { purse: .7 }),
  harbor: (lt, d) => HARB(lt, d, "night", 1),
  cta: (lt, d) => BALL(lt, d, { cta: lt, ctaD: d }),
  shipHero: (lt, d) => SHIPV(lt, d, {}, "dusk"),
  crew: (lt, d) => DECK(lt, d, { mood: "dusk" }),
  season: (lt, d) => { const u = lt / d; camSet(V(lerp(60, 48, u), 12 + Math.sin(lt) * 2, lerp(44, 38, u)), V(-4, 6, 0), 44); return G({ mood: "grey", amp: 2.4, ship: { p: V(0, 0, 0), h: 0, run: true } }); },
  clock: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(140, 120, u), 26, lerp(30, 10, u)), V(0, 6, -40), 46); return G({ mood: "dusk", harbor: 1, ship: { p: V(-20, 0, -20), h: 0, run: true }, clock: lt }); },
  harborN: (lt, d) => HARB(lt, d, "night", 1),
  dawn: (lt, d) => HARB(lt, d, "dawn", -1),
  school: (lt, d) => BALL(lt, d),
  predator: (lt, d) => { const u = lt / d; const pr = V(lerp(-60, 40, u), -20 + Math.sin(lt * 2) * 2, lerp(8, -4, u)); const r = BALL(lt, d, { pred: pr }); r.predOn = 1; return r; },
  peloton: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-20, 10, u), -14, 52), V(lerp(-10, 20, u), -18, 0), 48); return G({ ham: "stream", hC: V(0, -18, 0), hR: 40, hH: 10 }); },
  feed: (lt, d) => BALL(lt, d, { plank: 1 }),
  search: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-140, -100, u), 90, lerp(80, 60, u)), V(lerp(-20, 10, u), 0, 0), 44); return G({ ship: { p: V(lerp(-30, 10, u), 0, 0), h: 0, run: true } }); },
  sonar: (lt, d) => SONAR(lt, d),
  sonarDepth: (lt, d) => SONAR(lt, d, { echo: lt }),
  bladder: (lt, d) => { camSet(V(1.2, -19.6, lerp(5.2, 4.4, lt / d)), V(0, -20, 0), 40); return G({ bigH: 1, pulseOn: 1 }); },
  echo: (lt, d) => SONAR(lt, d, { echo: lt + 1 }),
  skiff: (lt, d) => { const u = ease(clamp(lt / d)); camSet(V(-150, 140, 120), V(-20, -8, 20), 44); return G({ xray: .5, seine: 1, close: lerp(.01, .12, u), ship: ON(lerp(0, .12, u)), skiff: ON(0), ham: "ball", hC: V(0, -14, 0), hR: 18 }); },
  encircle: (lt, d) => { const u = ease(clamp(lt / (d * .92))); camSet(V(-190, 180, 150), V(0, -12, 0), 44); return G({ xray: .5, seine: 1, close: Math.max(.12, u), ship: ON(Math.max(.12, u)), skiff: ON(0), ham: "ball", hC: V(0, -14, 0), hR: 18 }); },
  floats: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(30, 34, u), -9, lerp(22, 20, u)), V(58, -1, 8), 54); return G({ seine: 1, ham: "seine", hC: V(0, -14, 0), hR: 40, hH: 12 }); },
  lead: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(30, 34, u), -40, lerp(22, 20, u)), V(58, -47, 8), 54); return G({ seine: 1, ham: "seine", hC: V(0, -20, 0), hR: 40, hH: 14 }); },
  wall: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-30, -20, u), -24, lerp(10, 0, u)), V(60, -24, 0), 62); return G({ seine: 1, ham: "seine", hC: V(0, -18, 0), hR: 40, hH: 18 }); },
  kulac: (lt, d) => { camSet(V(0, 10.5, lerp(-36, -38, lt / d)), V(0, 9, -60), 36); return G({ mood: "day", harbor: 1, kulac: sm(lt / .6) }); },
  push: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(10, 20, u), -62, lerp(40, 34, u)), V(40, -46, 20), 52); return G({ seine: 1, ham: "seine", hC: V(0, -26, 0), hR: 40, hH: 20 }); },
  like: (lt, d) => { camSet(V(20, -62, 34), V(40, -46, 20), 52); return G({ seine: 1, ham: "seine", hC: V(0, -26, 0), hR: 40, hH: 20, chip: ["like", fadeIO(lt, d)] }); },
  escape: (lt, d) => { camSet(V(20, -66, 34), V(40, -50, 20), 54); return G({ seine: 1, ham: "seine", hC: V(0, -36, 0), hR: 44, hH: 14 }); },
  rings: (lt, d) => RINGV(lt, d),
  pline: (lt, d) => RINGV(lt, d, { glowLine: 1 }),
  pursing: (lt, d) => { const u = ease(clamp(lt / d)); camSet(V(0, -110, 90), V(0, -36, 0), 52); return G({ seine: 1, rings: 1, purse: u, ham: "seine", hC: V(0, -22, 0), hR: lerp(40, 28, u), hH: lerp(18, 12, u) }); },
  pursed: (lt, d) => { const a = lt / d; camSet(V(Math.cos(a) * 90, -100, Math.sin(a) * 90 + 30), V(0, -34, 0), 52); return G({ seine: 1, rings: 1, purse: 1, ham: "seine", hC: V(0, -20, 0), hR: 28, hH: 12 }); },
  pursedAir: (lt, d) => AIR(lt, d, { purse: 1, hR: 32 }),
  haul: (lt, d) => { const u = sm(lt / d); SN.R = lerp(60, 34, u); camSet(V(-150, 140, 110), V(0, -6, 0), 44); return G({ xray: .5, seine: 1, purse: 1, ship: ON(1), ham: "seine", hC: V(0, -6, 0), hR: lerp(32, 22, u), hH: 8, hS: 1.7 }); },
  pblock: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(12, 9, u), lerp(15, 14, u), lerp(12, 10, u)), V(0, 13, -4), 42); return G({ ship: { p: V(0, 0, -4), h: 0 }, pblock: 1, crew: 1 }); },
  hand: (lt, d) => DECK(lt, d, { crewPull: 1 }),
  brail: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(36, 30, u), lerp(18, 16, u), lerp(32, 28, u)), V(-6, 4, -4), 42); return G({ ship: { p: V(0, 0, 0), h: 0 }, brail: lt, crates: 1, crew: 1 }); },
  market: (lt, d) => { const u = sm(lt / d); camSet(V(lerp(-22, -18, u), 13, lerp(-34, -38, u)), V(-40, 6, -60), 42); return G({ mood: "dawn", harbor: 1, crates: 2, ship: { p: V(-80, 0, -30), h: Math.PI } }); },
  outro: (lt, d) => AIR(lt, d, { purse: .3 }),
  comment: (lt, d) => AIR(lt, d, { purse: .3, chip: ["comment", fadeIO(lt, d)] }),
  sign: (lt, d) => AIR(lt, d, { purse: .3, logo: sm(lt / .4) }),
};
for (const k in S2) S[k] = S2[k];

function apply2(st, T) {
  if (!st.haulR) { if (S2.haul !== undefined && !st.__haul) {} }
  placeHamsi(st, T);
  updateRings(!!st.rings); if (st.rings) pline.material.emissive.set(st.glowLine ? 0xffa000 : 0x3a2400);
  predator.visible = !!st.pred; if (st.pred) { predator.position.copy(st.pred); predator.scale.setScalar(2.6); predator.rotation.set(0, Math.atan2(-(-4 - 8), 100) * 0, Math.sin(T * 6) * .1); }
  plank.visible = !!st.plank; if (st.plank) plank.position.set(0, -20, 0);
  // sonar konisi + darbeler
  sCone.visible = !!st.sonar; pulses.forEach(p => p.visible = false);
  if (st.sonar || st.pulseOn) { const top = st.sonar ? V(0, -2, 0) : V(0, -10, 0), depth = 34;
    if (st.sonar) { sCone.scale.set(14, depth, 14); sCone.position.set(0, top.y - depth / 2, 0); sCone.rotation.set(Math.PI, 0, 0); }
    pulses.forEach((p, k) => { const s = ((T * .6 + k / 3) % 1); p.visible = true; const down = s < .5, f = down ? s * 2 : (1 - s) * 2;
      const y = top.y - f * (st.sonar ? depth : 9); p.position.set(st.sonar ? 0 : 0, st.pulseOn && !st.sonar ? -20 + (1 - f) * 0 + (down ? 2 - f * 2 : 2 - f * 2) : y, 0);
      const r = st.sonar ? 1 + f * 13 : 1.5 + f * 3; p.scale.setScalar(r); p.material.opacity = .7 * (1 - f * .6); p.material.color.set(down ? 0x8affc8 : 0xff7a5a); }); }
  bigH.visible = !!st.bigH; if (st.bigH) { bigH.position.set(0, -20, 0); bigH.scale.setScalar(4.5); bigH.rotation.set(0, -.3, Math.sin(T * 2) * .03); bigH.userData.sac.material.color.setHSL(.52, .9, .7 + .2 * Math.sin(T * 6)); }
  harbor.visible = !!st.harbor;
  // tayfa
  crew.forEach(c => c.visible = false);
  if (st.crew) { crew.forEach((c, i) => { c.visible = true; const lx = -16 + (i % 7) * 4.2, lz = i < 7 ? 3 : -3; c.position.copy(V(lx / 1.7, 2.3, lz / 1.7).applyMatrix4(ship.matrixWorld)); c.rotation.y = i < 7 ? 0 : Math.PI;
    c.children[0].rotation.z = st.crewPull ? Math.sin(T * 4 + i * .5) * .25 : Math.sin(T * 1.5 + i) * .05; }); }
  kulac.visible = !!st.kulac; if (st.kulac) { kulac.position.set(0, 5, -60); kulac.rotation.y = Math.PI / 2; kulac.updateMatrixWorld(true);
    const a = V(0, 2.05, -1.45).applyMatrix4(kulac.matrixWorld), b = V(0, 2.05, 1.45).applyMatrix4(kulac.matrixWorld); spanLine(a.add(V(0, 1.2, 0)), b.add(V(0, 1.2, 0)), st.kulac); }
  pblock.visible = !!st.pblock; if (st.pblock) { pblock.position.set(0, 14, -4); pblock.userData.blk.rotation.y = T * 3; pblock.userData.band.position.y = -15 + Math.sin(T * 3) * .2; }
  brail.visible = st.brail != null; if (st.brail != null) { const k = (st.brail * .5) % 1, up = k < .5 ? k * 2 : (1 - k) * 2; brail.position.set(lerp(-18, -6, up), lerp(-1, 7, up), -6); brail.material.color.set(0xcdd6dc); }
  crates.visible = !!st.crates; if (st.crates === 1) { crates.position.copy(V(-7, 2.4, -1.5).applyMatrix4(ship.matrixWorld)); crates.rotation.y = ship.rotation.y; } else if (st.crates === 2) { crates.position.set(-44, 5.2, -61); crates.rotation.y = 0; }
  if (st.echo != null) { const pn = $("panel"); pn.style.left = "960px"; pn.style.top = "90px"; pn.style.width = "900px"; pn.style.height = "900px"; echogram(st.echo, sm(st.echo / .4)); }
  if (st.clock != null) clockDial(st.clock, sm(st.clock / .3));
  if (!st.haulActive) SN.R = st.__R || SN.R;
}
const _applyBase = apply; apply = (st, T) => { _applyBase(st, T); apply2(st, T); };
