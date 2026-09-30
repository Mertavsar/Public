#!/usr/bin/env python3
"""
Tam kare (1080x1920) dikey kaynaktan plan listesiyle kurgu + kare başına
kaynaktaki yazı kutusunun kurgudaki yeri (boxmap). build.py'nin yapamadığı:
geri sarma (rewind) planı ve plan içi zoom'da kutu konumunu dönüştürmek.

plans.json:
[
 {"o0":0.0,"o1":0.7,"src":27.0,"slow":1.0},
 {"o0":0.7,"o1":1.2,"rewind":[27.0,0.8]},              // kaynağı geriye sar
 {"o0":4.1,"o1":5.3,"src":4.6,"slow":1.0,"z0":1.0,"z1":1.12,"cx":0.45,"cy":0.55}
]
slow>1 ağır çekim (kaynaktan (o1-o0)/slow sn çekilir).

    python3 cutter.py ham.mp4 plans.json content.mp4 --boxtrack boxtrack.json --boxmap boxmap.json
"""
import argparse, json, subprocess
import numpy as np, cv2

W, H, FPS = 1080, 1920, 30


def frames(src, idx):
    """kaynaktan istenen kare indekslerini (sıralı, tekrarlı olabilir) getir"""
    need = sorted(set(idx))
    a, b = need[0], need[-1]
    d = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a / FPS:.4f}", "-i", src, "-frames:v",
                          str(b - a + 1), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                         stdout=subprocess.PIPE)
    got = {}
    for k in range(a, b + 1):
        buf = d.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        if k in need:
            got[k] = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    d.stdout.close(); d.wait()
    last = got[max(got)]
    return [got.get(k, last) for k in idx]


def rewind_fx(f, u):
    """geri sarma görünümü: kanal kayması + yatay tarama çizgileri + hafif soluk"""
    g = f.copy()
    s = int(10 + 14 * np.sin(np.pi * u))
    g[..., 2] = np.roll(f[..., 2], s, 1)
    g[..., 0] = np.roll(f[..., 0], -s, 1)
    g[::4] = (g[::4] * 0.72).astype(np.uint8)
    band = int((u * 5 % 1) * H)
    g[band:band + 60] = np.clip(g[band:band + 60].astype(int) + 45, 0, 255).astype(np.uint8)
    return cv2.addWeighted(g, 0.88, np.full_like(g, 30), 0.12, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("plans"); ap.add_argument("out")
    ap.add_argument("--boxtrack"); ap.add_argument("--boxmap")
    a = ap.parse_args()
    plans = json.load(open(a.plans))
    track = json.load(open(a.boxtrack)) if a.boxtrack else None
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf",
                            "14", "-preset", "medium", "-pix_fmt", "yuv420p", a.out],
                           stdin=subprocess.PIPE)
    boxmap, total = [], 0
    for p in plans:
        n = int(round(p["o1"] * FPS)) - int(round(p["o0"] * FPS))
        if "rewind" in p:
            s0, s1 = p["rewind"]
            idx = [int(round((s0 + (s1 - s0) * k / max(1, n - 1)) * FPS)) for k in range(n)]
            wts = [0.0] * n
        else:
            # ağır çekimde kare tekrarı takılıyor: ara konumda iki kareyi harmanla
            pos = [p["src"] * FPS + k / p.get("slow", 1.0) for k in range(n)]
            idx = [int(q) for q in pos]
            wts = [q - int(q) for q in pos]
        fr = frames(a.src, idx + [i + 1 for i in idx])
        fr, nxt = fr[:n], fr[n:]
        fr = [f if w < 0.05 else cv2.addWeighted(f, 1 - w, g, w, 0) for f, g, w in zip(fr, nxt, wts)]
        z0, z1 = p.get("z0", 1.0), p.get("z1", 1.0)
        cx, cy = p.get("cx", 0.5) * W, p.get("cy", 0.5) * H
        for k, (si, f) in enumerate(zip(idx, fr)):
            u = k / max(1, n - 1)
            z = z0 + (z1 - z0) * (3 * u * u - 2 * u * u * u)     # yumuşak zoom
            if abs(z - 1) > 1e-3:
                M = np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]])
                f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            else:
                M = None
            if "rewind" in p:
                f = rewind_fx(f, u)
            enc.stdin.write(np.ascontiguousarray(f).tobytes())
            if track:
                y0, y1, x0, x1 = track[min(si, len(track) - 1)]
                if M is not None:
                    x0, y0 = z * x0 + cx * (1 - z), z * y0 + cy * (1 - z)
                    x1, y1 = z * x1 + cx * (1 - z), z * y1 + cy * (1 - z)
                boxmap.append([int(y0) - 2, int(y1) + 2, int(x0) - 2, int(x1) + 2])
        total += n
    enc.stdin.close(); enc.wait()
    if a.boxmap:
        json.dump(boxmap, open(a.boxmap, "w"))
    print(f"{len(plans)} plan · {total} kare ({total / FPS:.2f} sn) -> {a.out}")


if __name__ == "__main__":
    main()
