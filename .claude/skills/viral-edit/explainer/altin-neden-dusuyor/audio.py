# Ses: seslendirme (sıkıştırılmış) + kesintisiz müzik yatağı + geçiş/pop efektleri -> master -14 LUFS
import json, sys, subprocess, numpy as np
sys.path.insert(0, '/home/user/Public/.claude/skills/viral-edit/scripts')
import audiobed as ab
ev = json.load(open('events.json'))
dur = ev['dur']
rng = np.random.default_rng(7)
bus = ab.Bus(dur)
for t in ev['switches']:                     # sahne geçişi: whoosh + yumuşak vuruş
    bus.place(ab.whoosh(rng, dur=0.38, amp=0.30), t - 0.30)
    bus.place(ab.boom(rng, dur=0.7, amp=0.30), t - 0.01)
last = -9
for t in ev['pops']:                         # öğe girişleri: tık (seyreltilmiş)
    if t - last < 0.35 or any(abs(t - s) < 0.3 for s in ev['switches']): continue
    bus.place(ab.tick(rng, amp=0.13), t); last = t
bus.write('sfx.wav', 80, peak=0.8)
ab.build_music(dur, 'music.wav', bpm=100.0, peak_at=dur * 0.4)
