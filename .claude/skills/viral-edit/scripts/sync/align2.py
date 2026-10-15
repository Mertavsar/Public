import json, re, difflib, subprocess, numpy as np
W = json.load(open('w/words.json')); C = json.load(open('w/cues.json'))
VID = 437.9; SR = 44100
norm = lambda s: re.sub(r'[^a-z]', '', s.lower())
# cümleler
S = []; st = 0
for i, w in enumerate(W):
    if re.search(r'[.!?]["”]?$', w['w']) or i == len(W) - 1:
        S.append([st, i]); st = i + 1
# cümle -> altyazı parçası (cümlenin ilk kelimeleri parçanın başında)
ci = 0; anch = {}; anch_ci = {}
for k, (a, b) in enumerate(S):
    q = norm(' '.join(x['w'] for x in W[a:b + 1]))[:12]
    best = (0, None)
    for j in range(ci, min(len(C), ci + 8)):
        t = norm(C[j]['t'])
        for off in range(0, max(1, len(t) - len(q) + 1)):
            r = difflib.SequenceMatcher(None, q, t[off:off + len(q)]).ratio() - 0.02 * off / 4
            if r > best[0]: best = (r, j)
            if off > 6: break
    if best[0] >= 0.74:
        anch[k] = C[best[1]]['s']; anch_ci[k] = best[1]; ci = best[1] + 1
print('cümle', len(S), 'çapalı', len(anch))
keys = sorted(anch)
# cümle sınırlarını gerçek sessizliğe oturt (10 ms çerçeve)
_v = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'w/vo.wav', '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
fr = 160; nf = len(_v) // fr
en = 20 * np.log10(np.sqrt((_v[:nf * fr].reshape(nf, fr) ** 2).mean(1)) + 1e-9)
voiced = en > -38
def onset(t):
    i0, i1 = int((t - 0.45) * 100), int((t + 0.30) * 100)
    for i in range(max(i0, 8), min(i1, nf)):
        if voiced[i] and not voiced[i - 8:i].any(): return i / 100
    return t
def offset(t):
    i0, i1 = int((t - 0.45) * 100), int((t + 0.35) * 100)
    for i in range(min(i1, nf - 9), max(i0, 1), -1):
        if voiced[i] and not voiced[i + 1:i + 9].any(): return (i + 1) / 100
    return t
# ardışık iki cümle arasındaki EN UZUN sessizliği bul (kelime tahmini ±1 sn kayabilir)
def runs(i0, i1):
    out = []; st = None
    for i in range(max(i0, 0), min(i1, nf)):
        if not voiced[i]:
            st = i if st is None else st
        elif st is not None:
            out.append((st, i)); st = None
    if st is not None: out.append((st, min(i1, nf)))
    return out
SB = [[onset(W[a]['s']), offset(W[b]['e'])] for a, b in S]
joined = set()
for k in range(len(S) - 1):
    est = (W[S[k][1]]['e'] + W[S[k + 1][0]]['s']) / 2
    lo = max(est - 0.8, SB[k][0] + 0.25); hi = min(est + 0.8, W[S[k + 1][1]]['e'] - 0.2)
    rr = [r for r in runs(int(lo * 100), int(hi * 100)) if r[1] - r[0] >= 14]
    if rr:
        r = max(rr, key=lambda r: (r[1] - r[0]) - 0.15 * abs((r[0] + r[1]) / 200 - est))
        SB[k][1] = r[0] / 100; SB[k + 1][0] = r[1] / 100
    else:
        joined.add(k + 1)
for k in range(len(S)):
    if SB[k][1] <= SB[k][0] + 0.12: SB[k] = [W[S[k][0]]['s'], W[S[k][1]]['e']]
for k in joined: anch.pop(k, None)
keys = sorted(anch)
print('nefeste birleşik cümle', len(joined), [' '.join(x['w'] for x in W[S[k][0]:S[k][1]+1])[:30] for k in sorted(joined)])

# ilk cümle mutlaka çapalı
vo = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'w/vo.wav', '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
out = np.zeros(int((VID + 1) * SR), np.float32); rep = []; caps = []; prev_end = 0.0
for n, k in enumerate(keys):
    k2 = keys[n + 1] if n + 1 < len(keys) else len(S)
    T0 = anch[k]; T1 = anch[k2] if k2 < len(S) else VID - 0.5
    # grup: k..k2-1 cümleleri, iç boşluklar en fazla 0.5 sn
    pieces = []
    for m in range(k, k2):
        a, b = S[m]; s0 = SB[m][0] - 0.03; s1 = SB[m][1] + 0.05
        pieces.append((s0, s1, a, b))
    segs = []; L = 0; lay = []
    for p, (s0, s1, a, b) in enumerate(pieces):
        seg = vo[int(s0 * SR):int(s1 * SR)].copy(); r = int(0.01 * SR)
        seg[:r] *= np.linspace(0, 1, r); seg[-r:] *= np.linspace(1, 0, r)
        if p:
            gap = min(max(pieces[p][0] - pieces[p - 1][1], 0.15), 0.5); segs.append(np.zeros(int(gap * SR), np.float32)); L += gap
        lay.append((L, a, b, s0)); segs.append(seg); L += s1 - s0
    D = T1 - T0
    ga, gb = S[k][0], S[k2 - 1][1]
    c_lo = anch_ci.get(k, -1); c_hi = anch_ci[k2] if k2 in anch_ci else len(C)
    pts = []; wpos = ga + 1
    for j in range(c_lo + 1, c_hi):
        q = norm(C[j]['t'])[:8]
        if len(q) < 3: continue
        best = (0, None)
        for wi in range(wpos, min(gb + 1, wpos + 25)):
            t = norm(' '.join(x['w'] for x in W[wi:wi + 4]))[:len(q)]
            r = difflib.SequenceMatcher(None, q, t).ratio()
            if r > best[0]: best = (r, wi)
        if best[0] >= 0.75 and C[j]['s'] > T0 + 0.3 and C[j]['s'] < T1 - 0.2:
            pts.append((best[1], C[j]['s'])); wpos = best[1] + 1
    # VO zaman ekseninde grup (iç boşluklar kırpılmış): parçaları birleştir
    g = np.concatenate(segs)
    def vpos(wi):                                          # kelimenin grup içindeki ses konumu
        for (off, a, b, s0) in lay:
            if a <= wi <= b: return off + W[wi]['s'] - 0.03 - s0
        return None
    P = [(0.0, T0)] + [(vpos(wi), Tc) for wi, Tc in pts if vpos(wi) is not None]
    P = [p for i, p in enumerate(P) if i == 0 or (p[0] > P[i - 1][0] + 0.2 and p[1] > P[i - 1][1] + 0.2)]
    if L > (D - 0.1) * 1.12:
        borrow = min(L / 1.12 - (D - 0.1), max(T0 - prev_end - 0.15, 0), 0.4)
        T0 -= borrow; D += borrow; P[0] = (0.0, T0)
    def stretch(x, tempo):
        if abs(tempo - 1) < 0.01 or len(x) < 400: return x
        x.tofile('w/_i.f32')
        af = f'atempo={min(tempo, 2.0):.4f}' if tempo > 1 else f'rubberband=tempo={tempo:.4f}:pitch=1.0'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'w/_i.f32', '-af', af, '-f', 'f32le', 'w/_o.f32'], check=True)
        return np.fromfile('w/_o.f32', np.float32)
    pieces_out = []; tmap = []; cur = T0
    for i, (v0, Tp) in enumerate(P):
        v1 = P[i + 1][0] if i + 1 < len(P) else L
        seg = g[int(v0 * SR):int(v1 * SR)]
        if i + 1 < len(P):
            tgt = P[i + 1][1] - max(cur, Tp); tp = min(max((v1 - v0) / max(tgt, 0.2), 0.85), 1.35)
        else:
            Dl = T1 - max(cur, Tp); Ll = v1 - v0
            tp = Ll / max(Dl - 0.1, 0.3) if Ll > Dl - 0.1 else max(Ll / max(Dl - 0.35, 0.3), 0.90)
        st_ = max(cur, Tp); o = stretch(seg.copy(), tp)
        tmap.append((v0, v1, st_, tp)); pieces_out.append((st_, o)); cur = st_ + len(o) / SR
    for st_, o in pieces_out:
        a_ = int((st_ + 0.03) * SR); e = min(len(out), a_ + len(o)); out[a_:e] += o[:e - a_]
    prev_end = cur + 0.03; tempo = L / max(cur - T0, 0.01)
    def newt(v):
        for v0, v1, st_, tp in tmap:
            if v0 <= v <= v1 + 1e-6: return st_ + 0.03 + (v - v0) / tp
        return tmap[-1][2] + 0.03 + (v - tmap[-1][0]) / tmap[-1][3]
    for (off, a, b, s0) in lay:                            # kelime zamanlarını yeni sese taşı
        for x in W[a:b + 1]:
            caps.append({'w': x['w'], 's': round(newt(off + x['s'] - s0), 3), 'e': round(newt(off + x['e'] - s0), 3)})
    rep.append((round(T0, 2), round(D, 2), round(L, 2), round(tempo, 2), ' '.join(x['w'] for x in W[S[k][0]:S[k2 - 1][1] + 1])[:60]))
out[:int(VID * SR)].tofile('w/vo_sync.f32')
json.dump(rep, open('w/rep.json', 'w'), ensure_ascii=False, indent=0); json.dump(caps, open('w/caps_sync.json', 'w'), ensure_ascii=False)
t = np.array([r[3] for r in rep])
print('grup', len(rep), 'tempo min', t.min(), 'max', t.max(), 'ort', round(t.mean(), 3), ' >1.2:', (t > 1.2).sum(), ' 0.9:', (t <= 0.905).sum())
for r in rep:
    if r[3] > 1.15: print('  HIZ', r)
missing = [' '.join(x['w'] for x in W[S[k][0]:S[k][1] + 1])[:50] for k in range(len(S)) if k not in anch]
print('çapasız cümleler:', missing)
