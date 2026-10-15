"""Cümle düzeyi senkron (bölme yok): her cümle tek parça, tek tempo.
Sınırlar: Descript blok başı/sonu (kesin) + blok içi cümle ayrımı için en uzun sessizlik. Pay: baş -0.10, son +0.18.
Tempo: hızlanma ≤1.15, yavaşlama ≥0.92; sığmayan cümle sonrakini ≤0.45 sn ileri iter. Hepsi rubberband (perde korunur)."""
import json, re, difflib, subprocess, numpy as np
W = json.load(open('w/words.json')); C = json.load(open('w/cues.json'))
VID = 437.9; SR = 44100
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
# Descript blokları
blk = []
for b in re.split(r'\n\s*\n', open('w/vo_desc.srt').read().strip()):
    L_ = b.split('\n'); a, e = L_[1].split(' --> ')
    ts = lambda x: int(x[:2]) * 3600 + int(x[3:5]) * 60 + float(x[6:].replace(',', '.'))
    blk.append((ts(a), ts(e), len(' '.join(L_[2:]).split())))
bstart, bend = {}, {}; wi = 0
for a, e, n in blk:
    bstart[wi] = a; bend[wi + n - 1] = e; wi += n
S = []; st = 0
for i, w in enumerate(W):
    if re.search(r'[.!?]["”]?$', w['w']) or i == len(W) - 1:
        S.append([st, i]); st = i + 1
ci = 0; anch = {}; anch_ci = {}
for k, (a, b) in enumerate(S):
    q = norm(' '.join(x['w'] for x in W[a:b + 1]))[:12]; best = (0, None)
    for j in range(ci, min(len(C), ci + 8)):
        t = norm(C[j]['t'])
        for off in range(0, min(7, max(1, len(t) - len(q) + 1))):
            r = difflib.SequenceMatcher(None, q, t[off:off + len(q)]).ratio() - 0.005 * off
            if r > best[0]: best = (r, j)
    if best[0] >= 0.74: anch[k] = C[best[1]]['s']; anch_ci[k] = best[1]; ci = best[1] + 1
_v = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'w/vo.wav', '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
fr = 160; nf = len(_v) // fr
en = 20 * np.log10(np.sqrt((_v[:nf * fr].reshape(nf, fr) ** 2).mean(1)) + 1e-9); voiced = en > -46
def longest_gap(lo, hi):
    best = None; st_ = None
    for i in range(int(lo * 100), int(hi * 100)):
        if not voiced[i]: st_ = i if st_ is None else st_
        else:
            if st_ is not None and (best is None or i - st_ > best[1] - best[0]): best = (st_, i)
            st_ = None
    return best
SB = []
for k, (a, b) in enumerate(S):
    s0 = bstart.get(a); s1 = bend.get(b)
    SB.append([s0, s1])
joined = set()
for k in range(len(S) - 1):
    if SB[k][1] is None or SB[k + 1][0] is None:           # blok içi sınır: en uzun sessizlik
        est = (W[S[k][1]]['e'] + W[S[k + 1][0]]['s']) / 2
        lo = max(est - 0.8, (SB[k][0] or W[S[k][0]]['s']) + 0.3); hi = min(est + 0.8, W[S[k + 1][1]]['e'] - 0.2)
        g = longest_gap(lo, hi)
        if g and g[1] - g[0] >= 12:
            if SB[k][1] is None: SB[k][1] = g[0] / 100
            if SB[k + 1][0] is None: SB[k + 1][0] = g[1] / 100
        else:
            joined.add(k + 1)
            if SB[k][1] is None: SB[k][1] = W[S[k][1]]['e']
            if SB[k + 1][0] is None: SB[k + 1][0] = W[S[k + 1][0]]['s']
SB[-1][1] = SB[-1][1] or W[-1]['e']
for k in joined: anch.pop(k, None)
keys = sorted(anch)
print('cümle', len(S), 'çapa', len(keys), 'birleşik', len(joined))
vo = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'w/vo.wav', '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
def rb(x, tempo):
    if abs(tempo - 1) < 0.015: return x
    x.astype(np.float32).tofile('w/_i.f32')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'w/_i.f32', '-af',
                    f'atempo={tempo:.4f}', '-f', 'f32le', 'w/_o.f32'], check=True)
    return np.fromfile('w/_o.f32', np.float32)
out = np.zeros(int((VID + 2) * SR), np.float32); prev_end = 0.0; rep = []; caps = []
for n, k in enumerate(keys):
    k2 = keys[n + 1] if n + 1 < len(keys) else len(S)
    T0 = max(anch[k], prev_end + 0.12); T1 = anch[k2] if k2 < len(S) else VID - 0.4
    s0 = SB[k][0] - 0.10; s1 = SB[k2 - 1][1] + 0.18       # grup tek parça: iç boşluklar doğal
    s1 = min(s1, (SB[k2][0] - 0.06) if k2 < len(S) else s1)
    seg = vo[int(s0 * SR):int(s1 * SR)].copy(); r = int(0.02 * SR)
    seg[:r] *= np.linspace(0, 1, r); seg[-r:] *= np.linspace(1, 0, r)
    L = s1 - s0; D = T1 - T0
    # iç altyazı satırları: tek tempoyu bunlara en iyi oturacak şekilde seç (en küçük kareler)
    inner = []; ga, gb = S[k][0], S[k2 - 1][1]; c_lo = anch_ci.get(k, -1); c_hi = anch_ci.get(k2, len(C)); wpos = ga + 1; num = den = 0.0
    for j in range(c_lo + 1, c_hi):
        q = norm(C[j]['t'])[:8]
        if len(q) < 4: continue
        bb = (0, None)
        for wi in range(wpos, min(gb + 1, wpos + 25)):
            r = difflib.SequenceMatcher(None, q, norm(' '.join(x['w'] for x in W[wi:wi + 4]))[:len(q)]).ratio()
            if r > bb[0]: bb = (r, wi)
        if bb[0] >= 0.78:
            dv = W[bb[1]]['s'] - (s0 + 0.10); dT = C[j]['s'] - T0
            if dv > 0.3 and dT > 0.3: num += dv * dT; den += dv * dv; wpos = bb[1] + 1; inner.append((bb[1], C[j]['s']))
    t_fit = (den / num) if num > 0 else None              # v/t = T  ->  t = Σdv²/Σdv·dT
    if L > D - 0.15:
        tempo = min(L / max(D - 0.15, 0.3), 1.15)
    else:
        tempo = max(L / max(D - 0.4, 0.3), 0.92) if L < D - 0.4 else 1.0
    if t_fit:
        tempo = min(max(t_fit, 0.92, L / max(D - 0.05, 0.3)), 1.15)
    o = rb(seg, tempo)
    # satır geçişi seste doğal bir nefese denk geliyorsa o nefesi uzat (kelime bölünmez, hız değişmez)
    cuts = []                                              # (o içindeki örnek, eklenecek sessizlik sn)
    for wi, Tc in inner:
        lo, hi = W[wi - 1]['e'] - 0.15, W[wi]['s'] + 0.15
        gg = longest_gap(lo, hi)
        if not gg or gg[1] - gg[0] < 8: continue
        mid_v = (gg[0] + gg[1]) / 200                       # nefesin ortası (orijinal ses zamanı)
        pos_o = (mid_v - s0) / tempo; natural = T0 + pos_o + sum(c[1] for c in cuts) + (gg[1] - gg[0]) / 200 / tempo
        add = min(Tc - natural - 0.02, 1.2)
        if add > 0.08: cuts.append((int(pos_o * SR), add))
    tot = sum(c[1] for c in cuts); room = (T1 - 0.1) - (T0 + len(o) / SR)
    if cuts and tot > max(room, 0):
        f_ = max(room, 0) / tot; cuts = [(p_, a__ * f_) for p_, a__ in cuts]
    parts = []; last = 0
    for p_, a__ in cuts:
        parts += [o[last:p_], np.zeros(int(a__ * SR), np.float32)]; last = p_
    parts.append(o[last:]); o = np.concatenate(parts)
    a_ = int(T0 * SR); e = min(len(out), a_ + len(o)); out[a_:e] += o[:e - a_]
    prev_end = T0 + len(o) / SR - 0.18
    ins = cuts
    for m in range(k, k2):
        for x in W[S[m][0]:S[m][1] + 1]:
            sh = lambda v: T0 + (v - s0) / tempo + sum(a__ for p_, a__ in ins if p_ / SR <= (v - s0) / tempo)
            caps.append({'w': x['w'], 's': round(sh(x['s']), 3), 'e': round(sh(x['e']), 3)})
    rep.append((round(anch[k], 2), round(T0 - anch[k], 2), round(tempo, 3), ' '.join(x['w'] for x in W[S[k][0]:S[k2 - 1][1] + 1])[:55]))
out[:int(VID * SR)].tofile('w/vo_sync3.f32'); json.dump(caps, open('w/caps_sync3.json', 'w'), ensure_ascii=False)
t = np.array([x[2] for x in rep]); dl = np.array([x[1] for x in rep])
print('tempo min', t.min(), 'max', t.max(), ' >1.05:', (t > 1.05).sum(), ' gecikme>0.1:', (dl > 0.1).sum(), 'max gecikme', dl.max())

