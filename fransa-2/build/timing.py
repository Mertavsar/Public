#!/usr/bin/env python3
"""Hizalanmış seslendirmeden videonun zamanlamasını üretir.

Girdi : vo/temiz.wav, vo/captions.json (align.py), seslendirme.txt
Çıktı : assets/timing.js  (sahne zaman eşlemesi + altyazı parçaları)
        vo/son.wav        (kelimeye denk gelmeyen ses bölgeleri susturulmuş)
        vo/timing.json    (soundtrack.py için)

Sahne eşlemesi: metnin her satırı bir sahneye karşılık gelir. Sahne, satırın
ilk kelimesinden LEAD saniye önce başlar; animasyonun iç zamanları sahne
süresine doğrusal olarak uzar/kısalır (index.html'deki warp()).
"""
import json, os, re, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vo_analyze import load, frames, regions  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

OLD = [0, 5.2, 12.6, 20.8, 29.6, 38.4, 45.6, 52.6, 56.0]     # index.html sahne başları
OLD_END = 59.6
OLD_TICKS = [2.2, 8.1, 8.9, 13.5, 16.5, 17.3, 18.1, 22.0, 30.5, 32.6, 34.7, 38.8, 41.2, 46.4, 47.9, 49.4, 53.6, 54.2, 57.0]
LEAD, TAIL = .25, 1.1
MAX_CHARS = 28
DISPLAY = {"Limoj'da": "Limoges'da"}                          # okunuş -> yazım

words = json.load(open(P('vo', 'captions.json')))
# align.py'nin sayı listesinde "yüz" yok; sayı öbekleri bütün kalsın ve sarı olsun
NUM = set('bir iki üç dört beş altı yedi sekiz dokuz on yirmi otuz kırk elli altmış yetmiş seksen doksan yüz bin milyon'.split())
for i, w in enumerate(words):
    core = re.sub(r"[^\wçğıöşüÇĞİÖŞÜ]", '', w['w'].lower())
    if core in NUM and w['c'] == 'white' and core != 'bir':
        w['c'] = 'yellow'
    if core == 'bir' and i + 1 < len(words) and re.sub(r'[^\w]', '', words[i + 1]['w'].lower()) in NUM:
        w['c'] = 'yellow'
lines = [l.split() for l in open(P('seslendirme.txt'), encoding='utf-8').read().strip().split('\n')]
assert sum(map(len, lines)) == len(words), 'metin ve hizalama kelime sayısı tutmuyor'
assert len(lines) == len(OLD), 'her satır bir sahneye karşılık gelmeli'

# satır başları
idx, starts = 0, []
for l in lines:
    starts.append(words[idx]['s']); idx += len(l)
dur = round(words[-1]['e'] + TAIL, 2)
NEW = [0.0] + [round(max(s - LEAD, 0), 3) for s in starts[1:]]
warp = [[n, o] for n, o in zip(NEW, OLD)] + [[dur, OLD_END]]

def to_new(t_old):
    for (n0, o0), (n1, o1) in zip(warp, warp[1:]):
        if o0 <= t_old <= o1:
            return n0 + (t_old - o0) / (o1 - o0) * (n1 - n0)
    return dur

# altyazı parçaları: önce noktalama ve satır sonlarında öbeklere ayır; öbek uzunsa
# dengeli ikiye böl. Sayı kelimeleri (sarı) arasından asla bölme: "beş yüz elli bin".
def L(ws):
    return len(' '.join(w['w'] for w in ws))

def split(ws):
    if L(ws) <= MAX_CHARS or len(ws) == 1:
        return [ws]
    best = None
    for k in range(1, len(ws)):
        if ws[k - 1]['c'] == 'yellow' and ws[k]['c'] == 'yellow':
            continue
        cost = abs(L(ws[:k]) - L(ws[k:])) + (6 if len(ws[k - 1]['w']) <= 3 else 0)   # tek kalan kısa kelime
        cost += 40 if sum(w['w'].count('"') for w in ws[:k]) % 2 else 0                # tırnağı bölme
        if best is None or cost < best[0]:
            best = (cost, k)
    if best is None:
        return [ws]
    return split(ws[:best[1]]) + split(ws[best[1]:])

phrases, cur, line_end = [], [], set(np.cumsum([len(l) for l in lines]) - 1)
for i, w in enumerate(words):
    cur.append(dict(w=DISPLAY.get(w['w'], w['w']), s=round(w['s'], 3), e=round(w['e'], 3), c=w['c']))
    if i in line_end or re.search(r'[.,:;?!]$', w['w']):
        phrases.append(cur); cur = []
if cur:
    phrases.append(cur)
caps = []
# çok kısa öbekleri (tek kısa kelime: "var.", "yok,", "dedi.") bir öncekine ekle
for ph in phrases:
    if caps and (L(ph) <= 5 or L(caps[-1]) <= 5) and L(caps[-1]) + L(ph) + 1 <= MAX_CHARS + 4:
        caps[-1] = caps[-1] + ph
    else:
        caps.append(ph)
caps = [c for ph in caps for c in split(ph)]
CAPS = []
for k, c in enumerate(caps):
    t0 = c[0]['s']
    t1 = caps[k + 1][0]['s'] if k + 1 < len(caps) else dur - .2
    t1 = min(t1, c[-1]['e'] + .9)                                # uzun sessizlikte ekranda asılı kalmasın
    CAPS.append(dict(t0=round(t0, 3), t1=round(t1, 3), words=c))

open(P('assets', 'timing.js'), 'w').write('window.TIMING = ' + json.dumps(dict(DUR=dur, WARP=warp, CAPS=CAPS), ensure_ascii=False) + ';\n')

# kelimesiz bölgeleri sustur (hırıltı, tık, yutkunma)
x, sr = load(P('vo', 'temiz.wav'))
db, v, h = frames(x, sr)
mids = [(w['s'] + w['e']) / 2 for w in words]
ons = [(w['s'], w['e']) for w in words]
muted = []
for r in regions(db, v, h):
    core = [m for m in mids if r['a'] - .05 <= m <= r['b'] + .05]
    overlap = sum(max(0, min(r['b'], e) - max(r['a'], s)) for s, e in ons)
    if not core and (overlap < .5 * (r['b'] - r['a']) or r['b'] - r['a'] < .14):   # kelimesiz kısa tık/burun sesi
        a, b = int(max(0, r['a'] - .03) * sr), int(min(len(x) / sr, r['b'] + .05) * sr)
        f = min(int(.01 * sr), (b - a) // 2)
        env = np.zeros(b - a); env[:f] = np.linspace(1, 0, f); env[-f:] = np.linspace(0, 1, f)
        x[a:b] *= env
        muted.append((round(r['a'], 2), round(r['b'], 2)))
w = wave.open(P('vo', 'son.wav'), 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()); w.close()

json.dump(dict(DUR=dur, ticks=[round(to_new(t), 3) for t in OLD_TICKS], scenes=NEW,
               speech=[[w['s'], w['e']] for w in words]), open(P('vo', 'timing.json'), 'w'), indent=1)
print(f'süre {dur}s · {len(CAPS)} altyazı parçası · susturulan: {muted}')
print('sahne başları:', NEW)
for c in CAPS[:6]:
    print(f"  {c['t0']:6.2f}-{c['t1']:6.2f}  {' '.join(w['w'] for w in c['words'])}")
