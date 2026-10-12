#!/usr/bin/env python3
"""Descript SRT (sıkılaştırılmış sesin transkripti) -> kelime zamanları: her segmentin kelimeleri o segmentteki
sesli karelere (dB > p98-30) hece ağırlığıyla dağıtılır. Kullanım: wordmap.py vo.srt vo_fast.wav cap_fast.json"""
import re, json, subprocess, sys, numpy as np
srt, wav, out = sys.argv[1:4]
SR = 16000
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True).stdout, np.float32)
hop = 160; n = len(a) // hop
db = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
voiced = db > np.percentile(db, 98) - 30
def ts(x): h, m, s = x.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
blocks = re.split(r"\n\s*\n", open(srt).read().strip()); words = []
def syl(w): return max(1, len(re.findall(r"[aeıioöuüAEIİOÖUÜ]", w))) + 0.3 * len(re.sub(r"\W", "", w)) / 4
for b in blocks:
    L = b.strip().split("\n"); s0, s1 = [ts(x.strip()) for x in L[1].split("-->")]
    ws = " ".join(L[2:]).split()
    i0, i1 = int(s0 * 100), min(n, int(s1 * 100) + 1)
    v = np.where(voiced[i0:i1])[0] + i0
    if len(v) == 0: v = np.arange(i0, i1)
    wt = np.array([syl(w) for w in ws]); cum = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
    for k, w in enumerate(ws):
        a_ = v[min(len(v) - 1, int(cum[k] * len(v)))]; b_ = v[min(len(v) - 1, max(0, int(cum[k + 1] * len(v)) - 1))]
        words.append({"w": w, "s": round(a_ / 100, 3), "e": round((b_ + 1) / 100, 3)})
json.dump(words, open(out, "w"), ensure_ascii=False, indent=0)
ok = sum(voiced[min(n - 1, int(w["s"] * 100))] for w in words); print(len(words), "kelime;", ok, "başlangıç sesli kareye denk")
