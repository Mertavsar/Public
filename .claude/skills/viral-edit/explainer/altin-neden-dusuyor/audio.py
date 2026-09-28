# Müzik yatağı + geçiş/pop efektleri. Zamanlar görüntüden (events.json) gelir:
#  - wipe(): SW-0.2'de başlar, ekranı tam SW'de kapatır, SW+0.2'de açılır
#    -> whoosh'un tepesi SW'ye, yumuşak "tok" açılışa (SW+0.02) oturur
#  - A()/pop(): öğe t0'da belirir -> tık t0+0.03
# Kullanıcı isteği (bu video): müzik "arkadan tatlı tatlı" — seslendirmenin ~17 LU altında.
import json, sys, subprocess, numpy as np
from scipy.signal import butter, sosfilt
sys.path.insert(0, '/home/user/Public/.claude/skills/viral-edit/scripts')
import audiobed as ab
SR = ab.SR
ev = json.load(open('events.json')); dur = ev['dur']
rng = np.random.default_rng(7)

bus = ab.Bus(dur)
WD = 0.46
for t in ev['switches']:
    bus.place(ab.whoosh(rng, dur=WD, amp=0.34), t - 0.88 * WD)       # tepe = ekran kapanışı
    bus.place(ab.boom(rng, dur=0.55, f0=260, f1=120, amp=0.20), t + 0.02)  # açılış
last = -9; n = 0
for t in ev['pops']:
    if t < 0.05 or t - last < 0.35 or any(abs(t - s) < 0.35 for s in ev['switches']):
        continue
    bus.place(ab.tick(rng, amp=0.12), t + 0.03); last = t; n += 1
bus.write('sfx.wav', 80, peak=0.8)
print(f"sfx: {len(ev['switches'])} geçiş + {n} pop")

# yumuşak yatak: 'warm' kip (hi-hat yok, vuruş yumuşak), 92 BPM, tizleri yumuşat
ab.build_music(dur, 'music_raw.wav', bpm=92.0, peak_at=dur * 0.5, warm_at=3.0)
