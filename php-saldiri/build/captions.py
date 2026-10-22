#!/usr/bin/env python3
"""Altyazı + sahne zamanlaması.

Seslendirme okunuşla yazılır (seslendirme.txt: "pi eyç pi"), ekranda doğru yazım
görünür (altyazi.txt: "PHP"). İki dosya satır satır eşleşir; her satır bir sahnedir.

- vo/captions.json varsa (align.py çıktısı, okunuş metnine göre) satır sınırları
  gerçek sesten alınır.
- Yoksa (ses henüz gelmedi) satır süreleri hece sayısından tahmin edilir (5,2 hece/sn),
  böylece önizleme altyazılı çıkar.
Satır içindeki altyazı kelimeleri satır süresine hece ağırlığıyla dağıtılır.

    python3 build/captions.py   ->  assets/timing.js, vo/timing.json (+ gerçek seste vo/son.wav)
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
# her satırın animasyon penceresi (index.html'deki iç zaman); sıra serbest: hook sahnesi 70–75'te durur
WIN = [[70, 75], [0, 5], [5, 14], [14, 23], [31, 39], [39, 48], [48, 56], [56, 60.5]]
LEAD, TAIL, GAP, RATE = .25, 1.0, .45, 5.2
MAX_CHARS = 26
NOBREAK = {('rank', 'math'), ('math', "pro'ya"), ('ele', 'geçirilebilir'), ('takip', 'et')}   # birlikte kalsın
# animasyon anı <-> kelime: (satır, ekrandaki kelime, kelimeye göre kayma sn, animasyon zamanı)
ANCHORS = [
    (0, 'açık', 0, 71.2), (0, 'şifren', -.1, 72.2), (0, 'korumuyor.', 0, 73.0),
    (1, 'Sitelerin', 0, .3), (1, 'motoru', 0, 1.5),
    (2, "Ekim'de", 0, 6.4), (2, 'iki', 0, 7.2), (2, 'Adı:', 0, 9.3), (2, 'PHP2Shell.', 0, 9.4),
    (3, 'şifre', 0, 15.4), (3, 'sunucunda', 0, 16.4), (3, 'çalıştırabiliyor.', 0, 18.6), (3, 'ele', -.15, 20.3),
    (4, 'saldırılar,', 0, 32.0), (4, 'güncelleme', 0, 34.6), (4, 'saatler', 0, 35.6),
    (5, 'Aynı', 0, 39.6), (5, 'WordPress', 0, 40.6), (5, 'gizli', 0, 41.6),
    (6, 'Hosting', 0, 48.8), (6, 'Güncellemeden', 0, 51.8),
    (7, 'videoyu', 0, 56.4), (7, 'takip', 0, 57.6),
]
OLD_TICKS = [71.2, 72.6, 6.4, 7.2, 9.4, 15.4, 16.4, 18.6, 32.0, 34.6, 40.6, 41.6, 48.8, 51.8, 57.6]
RED = {'açık', 'korumuyor', 'php2shell', 'geçirilebilir', 'saatler', 'kapı', 'güncel'}
# okunuşu hecesiz/farklı olan yazımlar için hece ağırlığı
WEIGHT = {'hackerlara': 4, 'php': 3, "php'de": 4, "php'yi": 4, 'php2shell': 5, '21': 4, "21": 4, "ekim'de": 3, "5'ten": 2, "8'e": 2,
          '6': 2, 'cloudflare': 2, "wordpress'in": 4, 'wordpress': 3, 'rank': 1, 'math': 1, "pro'ya": 2}
VOW = set('aeıioöuüAEIİOÖUÜ')

def key(w):
    return re.sub(r'[^\w\']', '', w.lower().replace('İ', 'i').replace('I', 'ı'))

def syl(w):
    k = key(w)
    if k in WEIGHT:
        return WEIGHT[k]
    if re.search(r'\d', k):
        return 2
    return max(1, sum(c in VOW for c in w))

spoken = [l.split() for l in open(P('seslendirme.txt'), encoding='utf-8').read().strip().split('\n')]
shown = [l.split() for l in open(P('altyazi.txt'), encoding='utf-8').read().strip().split('\n')]
assert len(spoken) == len(shown) == len(WIN)

cap = P('vo', 'captions.json')
if os.path.exists(cap):
    W = json.load(open(cap))
    assert len(W) == sum(map(len, spoken)), 'hizalama ile okunuş metni kelime sayısı tutmuyor'
    spans, i = [], 0
    for l in spoken:
        spans.append((W[i]['s'], W[i + len(l) - 1]['e'])); i += len(l)
    real = True
else:
    spans, t = [], .3
    for l in spoken:
        d = sum(syl(w) for w in l) / RATE
        spans.append((t, t + d)); t += d + GAP
    real = False

def groups(l):
    """Okunuş kelimelerini ekrandaki tek kelimeye denk gelen öbeklere ayır:
    "pi eyç pi tu şel." -> PHP2Shell., "pi eyç pi" -> PHP, "Yirmi bir" -> 21."""
    g, i = [], 0
    while i < len(l):
        k = [key(w) for w in l[i:i + 5]]
        n = 5 if k[:2] == ['pi', 'eyç'] and k[3:5] == ['tu', 'şel'] else \
            3 if k[:2] == ['pi', 'eyç'] else 2 if k[:2] == ['yirmi', 'bir'] else 1
        g.append(n); i += n
    return g

def color(w):
    return 'red' if key(w) in RED else ('yellow' if re.search(r'\d', w) else 'white')

words = []
if real:   # kelime zamanları gerçek sesten
    i = 0
    for li, (sp, l) in enumerate(zip(spoken, shown)):
        g = groups(sp)
        assert len(g) == len(l), f'okunuş/yazım eşleşmedi: {sp} | {l}'
        for n, w in zip(g, l):
            words.append(dict(w=w, s=round(W[i]['s'], 3), e=round(W[i + n - 1]['e'], 3), c=color(w), line_end=False, line=li)); i += n
        words[-1]['line_end'] = True
else:      # tahmini: satır süresi hece ağırlığıyla dağıtılır
    for li, ((a, b), l) in enumerate(zip(spans, shown)):
        tot = sum(syl(w) for w in l); t = a
        for w in l:
            d = (b - a) * syl(w) / tot
            words.append(dict(w=w, s=round(t, 3), e=round(t + d, 3), c=color(w), line_end=False, line=li)); t += d
        words[-1]['line_end'] = True

def L(ws): return len(' '.join(x['w'] for x in ws))
def split(ws):
    if L(ws) <= MAX_CHARS or len(ws) == 1:
        return [ws]
    best = min(range(1, len(ws)), key=lambda k: abs(L(ws[:k]) - L(ws[k:])) + (6 if len(ws[k - 1]['w']) <= 3 else 0)
               + (60 if (key(ws[k - 1]['w']), key(ws[k]['w'])) in NOBREAK else 0))
    return split(ws[:best]) + split(ws[best:])
phr, cur = [], []
for w in words:
    cur.append(w)
    if w['line_end'] or re.search(r'[.,:;?!]$', w['w']):
        phr.append(cur); cur = []
caps = []
for ph in phr:
    if caps and L(ph) <= 6 and L(caps[-1]) + L(ph) + 1 <= MAX_CHARS + 4:
        caps[-1] = caps[-1] + ph
    else:
        caps.append(ph)
caps = [c for ph in caps for c in split(ph)]
# geriye eklenemeyen tek kısa öbek ("Adı:") bir sonrakiyle birlikte görünsün
k = 0
while k < len(caps) - 1:
    if L(caps[k]) <= 6 and L(caps[k]) + L(caps[k + 1]) + 1 <= MAX_CHARS + 4:
        caps[k:k + 2] = [caps[k] + caps[k + 1]]
    k += 1
dur = round(spans[-1][1] + TAIL + 2.2, 2)          # sondaki soru/takip ekranı biraz kalsın
CAPS = []
for k, c in enumerate(caps):
    t1 = caps[k + 1][0]['s'] if k + 1 < len(caps) else dur - .3
    CAPS.append(dict(t0=c[0]['s'], t1=round(min(t1, c[-1]['e'] + .9), 3), words=[{x: w[x] for x in 'wsec'} for w in c]))
NEW = [0.0] + [round(max(s - LEAD, 0), 3) for s, _ in spans[1:]]
EDGE = NEW + [dur]
# satır i: seslendirme [EDGE[i], EDGE[i+1]] -> animasyon WIN[i]; aradaki çapalar
# animasyonun önemli anını kelimenin başladığı ana kilitler
WARP = []
for i, (o0, o1) in enumerate(WIN):
    knots = [[EDGE[i], o0]]
    for li, wd, off, old in ANCHORS:
        if li != i: continue
        w = next(x for x in words if x['line'] == li and x['w'] == wd)
        n = round(w['s'] + off, 3)
        if knots[-1][0] < n < EDGE[i + 1] and knots[-1][1] < old < o1:
            knots.append([n, old])
    knots.append([EDGE[i + 1], o1])
    WARP.append(knots)
def to_new(t):
    for knots in WARP:
        if knots[0][1] <= t <= knots[-1][1]:
            for (n0, a), (n1, b) in zip(knots, knots[1:]):
                if a <= t <= b: return n0 + (t - a) / (b - a) * (n1 - n0)
    return dur
open(P('assets', 'timing.js'), 'w').write('window.TIMING = ' + json.dumps(dict(DUR=dur, WARP=WARP, CAPS=CAPS, REAL=real), ensure_ascii=False) + ';\n')
# efekt sesleri (animasyon zamanı -> ses zamanı); soundtrack.py sentezler
SFX_OLD = [(70.15, 'glitch'), (71.2, 'clunk'), (71.3, 'alarm'), (72.9, 'zip'), (73.0, 'stamp'),
           (.25, 'glitch'), (1.5, 'sweep'),
           (5.25, 'glitch'), (7.6, 'sweep'), (9.4, 'stamp'),
           (14.25, 'glitch'), (15.5, 'zip'), (18.6, 'alarm'), (20.3, 'stamp'),
           (31.25, 'glitch'), (32.0, 'pop'), (34.6, 'pop'), (35.6, 'stamp'),
           (39.25, 'glitch'), (39.6, 'pop'), (40.9, 'pop'), (41.6, 'clunk'),
           (48.25, 'glitch'), (48.8, 'pop'), (51.8, 'pop'),
           (56.2, 'glitch'), (56.4, 'pop'), (57.6, 'pop'), (58.0, 'ding')]
SFX_OLD += [(.3 + i * .08, 'blip') for i in range(0, 12, 2)]                      # siteler belirir
SFX_OLD += [(16.4 + k * .55 + 1.4, 'blip') for k in range(5)]                      # paketler sunucuya varır
SFX_OLD += [(72.3 + k * .0625, 'key') for k in range(8)]                           # şifre noktaları
for a0, b0, n in [(5.5, 6.3, 22), (6.4, 6.9, 21), (7.2, 7.6, 21), (7.8, 8.2, 19), (8.3, 8.7, 19)]:
    SFX_OLD += [(a0 + (b0 - a0) * k / n, 'key') for k in range(0, n, 2)]            # terminal yazımı
sfx = sorted([round(to_new(t), 3), k] for t, k in SFX_OLD if to_new(t) < dur)

hits = sorted(set([0.05] + [round(s, 3) for s, _ in spans[1:]] + [round(w['s'] + .03, 3) for w in words if w['c'] == 'red']))
json.dump(dict(DUR=dur, ticks=[round(to_new(t), 3) for t in OLD_TICKS], scenes=NEW, hits=hits, sfx=sfx,
               speech=[[w['s'], w['e']] for w in words]), open(P('vo', 'timing.json'), 'w'), indent=1)
print(f"{'gerçek ses' if real else 'TAHMİNİ'} · süre {dur}s · {len(CAPS)} altyazı · sahneler {NEW}")

# gerçek seste kelimeye denk gelmeyen kısa sesleri (tık, yutkunma) sustur -> vo/son.wav
if real:
    import sys, wave
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from vo_analyze import load, frames, regions
    x, sr = load(P('vo', 'temiz.wav'))
    db, v, h = frames(x, sr)
    mids = [(w['s'] + w['e']) / 2 for w in W]
    ons = [(w['s'], w['e']) for w in W]
    muted = []
    for r in regions(db, v, h):
        core = [m for m in mids if r['a'] - .05 <= m <= r['b'] + .05]
        overlap = sum(max(0, min(r['b'], e) - max(r['a'], s)) for s, e in ons)
        if not core and (overlap < .5 * (r['b'] - r['a']) or r['b'] - r['a'] < .14):
            a, b = int(max(0, r['a'] - .03) * sr), int(min(len(x) / sr, r['b'] + .05) * sr)
            f = min(int(.01 * sr), (b - a) // 2)
            env = np.zeros(b - a); env[:f] = np.linspace(1, 0, f); env[-f:] = np.linspace(0, 1, f)
            x[a:b] *= env
            muted.append((round(r['a'], 2), round(r['b'], 2)))
    w = wave.open(P('vo', 'son.wav'), 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
    print('susturulan:', muted)
    for c in CAPS[:40]:
        print(f"  {c['t0']:6.2f}-{c['t1']:6.2f}  {' '.join(w['w'] for w in c['words'])}")
