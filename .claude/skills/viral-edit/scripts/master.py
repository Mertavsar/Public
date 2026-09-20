"""
Miksi hedef ses seviyesine çıkarır ve GERÇEKTEN kırpılmayı önler.

Neden ayrı bir script: `volume=XdB,alimiter=...` zinciri güvenilir değil.
alimiter keskin transientleri (darbe sesleri) kaçırıyor; sinyal tavanı aşıyor ve
16-bit PCM'e yazılırken sert kırpılıyor. Bir videoda 459 kırpılma platosu oluştu,
baştan sona duyulur distorsiyon yarattı.

Burada kazanç envanteri ileriye bakan (look-ahead) bir zarftan hesaplanır, tavan
asla aşılmaz ve çıktı 24-bit yazılır.

AAC AŞMASI: kayıplı kodlayıcı, WAV'daki tepeden ~3.5 dB daha yükseğe çıkabilir.
Bu yüzden tavan -3.5 dBFS seçilir; AAC çıkışı o zaman ~-0.3 dBFS'te temiz kalır.
Ölçüldü: tavan -1.2 -> AAC +1.96 dBFS (kırpık), tavan -3.5 -> AAC -0.28 (temiz).

Kullanım
--------
    python3 master.py mix_raw.wav mix.wav -14.0 -3.5

Ardından her seferinde kod çözülmüş AAC'nin tepesini ölç; 0 dBFS'i aşan örnek
olmamalı.
"""

import numpy as np, subprocess, sys, os
SR=48000
src, dst = sys.argv[1], sys.argv[2]
target_lufs = float(sys.argv[3]) if len(sys.argv)>3 else -14.0
ceiling_db  = float(sys.argv[4]) if len(sys.argv)>4 else -1.2

raw=subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","2","-ar",str(SR),"-f","f32le","-"],
                   capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).reshape(-1,2).astype(np.float64).T   # 2 x N

def lufs(y):
    p=subprocess.Popen(["ffmpeg","-hide_banner","-f","f32le","-ar",str(SR),"-ac","2","-i","-",
                        "-af","ebur128","-f","null","-"],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    _,err=p.communicate(y.T.astype(np.float32).tobytes())
    for l in err.decode().splitlines()[::-1]:
        if "I:" in l and "LUFS" in l: return float(l.split()[1])
    return None

def limit(y, ceil, look_ms=3.0, rel_ms=80.0):
    """Look-ahead tepe limiter: kazanç zarfi once ileriye bakarak dusurulur,
    sonra yavas biraklir. ffmpeg alimiter keskin transientleri kaciriyordu."""
    L=int(SR*look_ms/1000); R=int(SR*rel_ms/1000)
    peak=np.maximum(np.abs(y[0]),np.abs(y[1]))
    need=np.minimum(1.0, ceil/np.maximum(peak,1e-12))
    # ileriye bakis: her noktada onumuzdeki L ornegin en dusuk kazancini al
    pad=np.concatenate([need, np.ones(L)])
    win=np.lib.stride_tricks.sliding_window_view(pad, L+1)
    g=win.min(axis=1)[:len(need)]
    # yumusak birakma (tek kutuplu)
    a=np.exp(-1.0/max(R,1))
    out=np.empty_like(g); cur=1.0
    for i,v in enumerate(g):
        cur = v if v < cur else a*cur + (1-a)*v
        out[i]=cur
    # kisa atak yumusatmasi (tikirti olmasin)
    k=np.hanning(int(SR*0.0015)*2+1); k/=k.sum()
    out=np.convolve(out,k,mode="same")
    out=np.minimum(out,g)          # yumusatma tavani asmasin
    return y*out

ceil=10**(ceiling_db/20)
cur=lufs(x); print(f"giris: {cur:.1f} LUFS, tepe {20*np.log10(np.abs(x).max()):+.2f} dBFS")
gain=10**((target_lufs-cur)/20)
y=limit(x*gain, ceil)
got=lufs(y); pk=20*np.log10(np.abs(y).max())
# limitleme sonrasi ses biraz dustuyse kucuk bir telafi (tekrar limitli)
if got is not None and target_lufs-got > 0.25:
    y=limit(y*10**((target_lufs-got)/20), ceil); got=lufs(y); pk=20*np.log10(np.abs(y).max())
print(f"cikis: {got:.1f} LUFS, tepe {pk:+.2f} dBFS, >tavan ornek: {(np.abs(y)>ceil+1e-6).sum()}")
subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","2","-i","-",
                "-c:a","pcm_s24le",dst],input=y.T.astype(np.float32).tobytes(),check=True)
print("->",dst)
