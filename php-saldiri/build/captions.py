#!/usr/bin/env python3
"""Altyazı + sahne zamanlaması.

Seslendirme okunuşla yazılır (seslendirme.txt: "pi eyç pi"), ekranda doğru yazım
görünür (altyazi.txt: "PHP"). İki dosya satır satır eşleşir; her satır bir sahnedir.

- vo/captions.json varsa (align.py çıktısı, okunuş metnine göre) satır sınırları
  gerçek sesten alınır.
- Yoksa (ses henüz gelmedi) satır süreleri hece sayısından tahmin edilir (5,2 hece/sn),
  böylece önizleme altyazılı çıkar.
Satır içindeki altyazı kelimeleri satır süresine hece ağırlığıyla dağıtılır.

    python3 build/captions.py   ->  assets/timing.js, vo/timing.json
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
# her satırın animasyon penceresi (index.html'deki iç zaman); sıra serbest: hook sahnesi 70–75'te durur
WIN = [[70, 75], [0, 5], [5, 14], [14, 23], [31, 39], [39, 48], [48, 56], [56, 60.5]]
LEAD, TAIL, GAP, RATE = .25, 1.0, .45, 5.2
MAX_CHARS = 26
OLD_TICKS = [71.2, 72.6, 6.0, 7.2, 9.4, 15.4, 17.6, 19.6, 32.0, 34.6, 40.0, 41.6, 49.0, 51.8, 57.2]
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

words = []
for (a, b), l in zip(spans, shown):
    tot = sum(syl(w) for w in l); t = a
    for w in l:
        d = (b - a) * syl(w) / tot
        k = key(w)
        c = 'red' if k in RED else ('yellow' if re.search(r'\d', w) else 'white')
        words.append(dict(w=w, s=round(t, 3), e=round(t + d, 3), c=c, line_end=False)); t += d
    words[-1]['line_end'] = True

def L(ws): return len(' '.join(x['w'] for x in ws))
def split(ws):
    if L(ws) <= MAX_CHARS or len(ws) == 1:
        return [ws]
    best = min(range(1, len(ws)), key=lambda k: abs(L(ws[:k]) - L(ws[k:])) + (6 if len(ws[k - 1]['w']) <= 3 else 0))
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
# satır i: seslendirme [EDGE[i], EDGE[i+1]] -> animasyon WIN[i]
WARP = [[EDGE[i], EDGE[i + 1], o0, o1] for i, (o0, o1) in enumerate(WIN)]
def to_new(t):
    for n0, n1, o0, o1 in WARP:
        if o0 <= t <= o1: return n0 + (t - o0) / (o1 - o0) * (n1 - n0)
    return dur
open(P('assets', 'timing.js'), 'w').write('window.TIMING = ' + json.dumps(dict(DUR=dur, WARP=WARP, CAPS=CAPS, REAL=real), ensure_ascii=False) + ';\n')
hits = sorted(set([0.05] + [round(s, 3) for s, _ in spans[1:]] + [round(w['s'] + .03, 3) for w in words if w['c'] == 'red']))
json.dump(dict(DUR=dur, ticks=[round(to_new(t), 3) for t in OLD_TICKS], scenes=NEW, hits=hits,
               speech=[[w['s'], w['e']] for w in words]), open(P('vo', 'timing.json'), 'w'), indent=1)
print(f"{'gerçek ses' if real else 'TAHMİNİ'} · süre {dur}s · {len(CAPS)} altyazı · sahneler {NEW}")
