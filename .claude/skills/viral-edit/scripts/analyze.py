#!/usr/bin/env python3
"""
Bir videoyu ölçer. "Şu videodaki gibi olsun" denince tahminle taklit etme —
önce bununla ölç, çıkan sayıları `reference/style-profile.md`'ye yaz.

    python3 analyze.py referans.mp4
    python3 analyze.py referans.mp4 --scene 0.30 --json profil.json

Ölçtükleri
----------
- Çözünürlük, fps, süre
- Kesim sayısı ve sıklığı, plan süresi dağılımı (sahne değişimiyle)
- Integrated loudness (LUFS), tepe, sessizlik oranı
- Konuşma hızı (hece/s) — seslendirme varsa
- Kadraj doluluğu: görüntü tam ekran mı, kenarlarda bant var mı

Kesim tespiti `select='gt(scene,N)'` ile. Varsayılan 0.20 ölçümle seçildi:
kesim sayısı bilinen 25 planlık bir videoda 0.30 sadece 12'sini gördü (planlar
aynı mekânda, sahne farkı düşük), 0.20 ise 28 buldu — gerçeğe en yakını.
Çok hareketli/mekân değiştiren bir referansta 0.30'a çıkar. Çıkan plan sayısı
gözle saydığınla tutmuyorsa `--scene` ile oyna.
"""

import argparse, json, re, subprocess, sys
import numpy as np


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate:format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = d["stream"][0] if "stream" in d else d["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return (int(st["width"]), int(st["height"]),
            float(num) / float(den), float(d["format"]["duration"]))


def cuts(path, thr):
    err = subprocess.run(
        ["ffmpeg", "-nostdin", "-i", path, "-filter_complex",
         f"select='gt(scene,{thr})',metadata=print:file=-", "-f", "null", "-"],
        capture_output=True, text=True).stdout
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", err)]


def loudness(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    def grab(key):
        for l in err.splitlines()[::-1]:
            if key in l:
                try:
                    return float(l.split()[-2])
                except (ValueError, IndexError):
                    return None
        return None
    return grab("I:"), grab("Peak:")


def speech(path):
    """Sessizlik oranı ve hece hızı. Ses yoksa (None, None)."""
    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    try:
        import align as A
    except ImportError:
        return None, None
    try:
        x = A.load_audio(path)
    except subprocess.CalledProcessError:
        return None, None
    if len(x) < A.SR:
        return None, None
    db = A.envelope(x)
    blocks, _ = A.speech_blocks(db)
    dur = len(x) / A.SR
    voiced = sum(b - a for a, b in blocks)
    return 1.0 - voiced / dur, len(A.syllable_peaks(x)) / dur


def letterbox(path, dur, n=6):
    """Kenarlarda siyah bant var mı — referans tam ekran mı kullanıyor?"""
    bars = []
    for k in range(n):
        t = dur * (k + 0.5) / n
        err = subprocess.run(["ffmpeg", "-nostdin", "-ss", str(t), "-i", path,
                              "-frames:v", "2", "-vf", "cropdetect=24:2:0",
                              "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", err)
        if m:
            bars.append(tuple(int(v) for v in m[-1]))
    return bars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--scene", type=float, default=0.20)
    ap.add_argument("--json")
    a = ap.parse_args()

    w, h, fps, dur = probe(a.video)
    t = cuts(a.video, a.scene)
    shots = np.diff([0.0] + t + [dur]) if t else np.array([dur])
    I, pk = loudness(a.video)
    sil, syl = speech(a.video)
    bars = letterbox(a.video, dur)

    print(f"{a.video}")
    print(f"  {w}x{h} · {fps:.2f} fps · {dur:.2f}s · en-boy {w/h:.4f}"
          f"{'  (9:16)' if abs(w/h - 0.5625) < 0.005 else '  ⚠ 9:16 DEĞİL'}")
    print(f"\nRİTİM")
    print(f"  {len(t)} kesim · saniyede {len(t)/dur:.2f}")
    print(f"  plan: ort {shots.mean():.2f}s · medyan {np.median(shots):.2f}s · "
          f"en kısa {shots.min():.2f}s · en uzun {shots.max():.2f}s")
    if shots.max() > 3.0:
        print(f"  ⚠ {int((shots > 3.0).sum())} plan 3 saniyeyi aşıyor (SKILL.md 0b)")
    print(f"\nSES")
    print(f"  {I if I is None else f'{I:.1f}'} LUFS · tepe "
          f"{pk if pk is None else f'{pk:+.1f}'} dBFS")
    if sil is not None:
        print(f"  sessizlik %{sil*100:.0f} · konuşma {syl:.2f} hece/s")
        if sil > 0.15:
            print("  ⚠ sessizlik yüksek — referans stilde altta kesintisiz müzik var")
    print(f"\nKADRAJ")
    if bars and len(set(bars)) == 1 and bars[0][:2] == (w, h):
        print(f"  tam ekran, bant yok")
    elif bars:
        print(f"  cropdetect: {sorted(set(bars))}  ⚠ bant olabilir")
    else:
        print("  ölçülemedi")

    if a.json:
        json.dump({"w": w, "h": h, "fps": fps, "dur": dur, "cuts": t,
                   "shot_mean": float(shots.mean()), "shot_median": float(np.median(shots)),
                   "lufs": I, "peak": pk, "silence": sil, "syl_per_s": syl},
                  open(a.json, "w"), indent=1)
        print(f"\n-> {a.json}")


if __name__ == "__main__":
    main()
