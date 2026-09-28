#!/usr/bin/env python3
"""
Gömülü yazı / filigran / çizimi VİDEO ONARIM MODELİYLE (ProPainter) siler.

NEDEN: detext.py ve dewatermark.py her kareyi tek başına Telea ile dolduruyor.
Küçük filigranda iş görüyor ama iki satırlık altyazı bandı hayvanın üstünden
geçince (ay balığı klibi) dolgu köşeli, lekeli, bulanık yamalar bıraktı.
Kullanıcı: "blurlar berbat olmuş". ProPainter silinen pikseli komşu karelerden
optik akışla taşıyor (kamera / hayvan hareket ettikçe yazının arkası başka
karede görünüyor), kalan boşluğu transformer dolduruyor — sonuç gerçek doku.

    python3 vinpaint.py ham.mp4 temiz.mp4 --until 36 \
        --band 610,790 \                                   # değişen altyazı
        --switch 5.0 --box-a 420,570,0,170 --box-b 770,905,430,576 \  # köşe değiştiren logo
        --extra 14.9,16.6,300,615,0,265                    # kırmızı ok (t0,t1,y0,y1,x0,x1)

Maskeler detext.text_mask ve dewatermark.build_mask ile aynı; yalnızca dolgu
değişti. Kaynak sahne kesimlerinden bölünüp her sahne ayrı işleniyor (akış
kesimin öbür yanından piksel taşımasın). Sadece maskeli satırlar (ROI)
modele veriliyor — tam kare CPU'da gereksiz yavaş.

KURULUM (bir kez, ~5 dk): scripts/setup_propainter.sh
CPU'da (4 çekirdek) ≈ 1.7 sn/kare → 36 sn'lik klip ~35 dk: arka planda çalıştır. Önce --only t0,t1 ile tek sahnede dene, BAK.
"""
import argparse, os, shutil, subprocess, sys, tempfile, time
from collections import deque
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dewatermark import probe, build_mask
from detext import text_mask

PP = os.environ.get("PROPAINTER_DIR", os.path.expanduser("~/.cache/propainter"))


def frames_of(src, W, H, t_end=None):
    cmd = ["ffmpeg", "-v", "error", "-i", src]
    if t_end:
        cmd += ["-t", f"{t_end}"]
    dec = subprocess.Popen(cmd + ["-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    dec.wait()


def scene_cuts(src, thr, t_end):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", src, "-t", f"{t_end}", "-vf",
                          f"select='gt(scene,{thr})',metadata=print:file=-", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stdout
    import re
    return sorted(float(m) for m in re.findall(r"pts_time:([0-9.]+)", out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--until", type=float, default=1e9, help="kapanış kartı başlangıcı; sonrası dokunulmaz")
    # değişen altyazı (detext)
    ap.add_argument("--band", help="altyazı bandı y0,y1 (yoksa altyazı maskesi yok)")
    ap.add_argument("--band-at", action="append", default=[],
                    help="t0,t1,y0,y1: o aralıkta bandı daralt. Ay balığı klibinde balığın gözündeki "
                         "beyaz halka bantta kalınca yazı sanılıp silindi; göz bandın dışında bırakıldı")
    ap.add_argument("--hl-hue", default="118,150")
    ap.add_argument("--white-min", type=int, default=195)
    ap.add_argument("--grow", type=int, default=11, help="harf + gölge genişletme (model 4 px daha ekler)")
    ap.add_argument("--extra", action="append", default=[], help="kırmızı çizim t0,t1,y0,y1,x0,x1")
    # sabit / köşe değiştiren logo (dewatermark)
    ap.add_argument("--box-a", help="logo kutusu y0,y1,x0,x1")
    ap.add_argument("--box-b", help="--switch sonrası logo kutusu")
    ap.add_argument("--switch", type=float, default=1e9)
    ap.add_argument("--wm-grow", type=int, default=9)
    ap.add_argument("--halo-min", type=int, default=140)
    # işleme
    ap.add_argument("--scene-thr", type=float, default=0.30)
    ap.add_argument("--max-chunk", type=int, default=150, help="uzun sahneyi bu kadar karede böl")
    ap.add_argument("--margin", type=int, default=64, help="ROI'ye maskenin üstü/altından eklenen bağlam")
    # CPU ölçümü (30 kare, 576x280 ROI): tam çözünürlük 6.3 sn/kare; 0.5 ölçek +
    # neighbor 20 → 1.7 sn/kare, dolgu gözle aynı (su/deri dokusu zaten yumuşak).
    ap.add_argument("--scale", type=float, default=0.5, help="modelin işleme ölçeği (1.0 = tam, 4x yavaş)")
    ap.add_argument("--neighbor", type=int, default=20)
    ap.add_argument("--raft-iter", type=int, default=12)
    ap.add_argument("--only", help="t0,t1: sadece bu aralığı işle (deneme)")
    ap.add_argument("--work", help="kalıcı çalışma klasörü (kesilirse aynı komutla devam)")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(os.path.join(PP, "inference_propainter.py")):
        sys.exit(f"ProPainter yok: {PP}. Önce scripts/setup_propainter.sh çalıştır.")

    W, H, fps = probe(a.src)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                "csv=p=0", a.src], capture_output=True, text=True).stdout)
    t_end = min(a.until, dur)
    # Uzun iş (35+ dk) konteyner yeniden başlayınca yarıda kaldı: --work ile
    # kalıcı klasör verilirse biten sahneler done.txt'ye yazılır, aynı komut
    # tekrar çalışınca kaldığı yerden devam eder.
    work = a.work or tempfile.mkdtemp(prefix="vinpaint_")
    os.makedirs(work, exist_ok=True)
    frp, donep = os.path.join(work, "fr.npy"), os.path.join(work, "done.txt")
    resume = os.path.exists(frp) and os.path.exists(donep)
    done = {tuple(int(v) for v in l.split()) for l in open(donep)} if resume else set()

    # ---- logo maskeleri (zamana göre sabit) ----
    mA = mB = None
    if a.box_a:
        sfps = min(fps, 10.0)
        F = np.stack(list(frames_of(a.src, W, H, t_end)))[::max(1, round(fps / sfps))]
        sw = int(min(a.switch, t_end) * sfps)
        mA = build_mask(F[:max(sw, 1)], [int(v) for v in a.box_a.split(",")], W, H, a.wm_grow, a.halo_min)
        if a.box_b:
            mB = build_mask(F[sw:], [int(v) for v in a.box_b.split(",")], W, H, a.wm_grow, a.halo_min)
        del F

    def logo_mask(t):
        if mA is None:
            return None
        if mB is None or t < a.switch - 0.25:
            return mA
        return mA | mB if t < a.switch + 0.25 else mB

    band = [int(v) for v in a.band.split(",")] if a.band else None
    hue = [int(v) for v in a.hl_hue.split(",")]
    extras = [[float(v) for v in e.split(",")] for e in a.extra]

    band_at = [[float(v) for v in b.split(",")] for b in a.band_at]

    def raw_mask(f, t):
        m = np.zeros((H, W), np.uint8)
        if band:
            by0, by1 = band
            for t0, t1, y0, y1 in band_at:
                if t0 <= t <= t1:
                    by0, by1 = int(y0), int(y1)
            tm, hlm = text_mask(f, by0, by1, hue, a.white_min, a.grow)
            m |= tm | hlm
        for t0, t1, y0, y1, x0, x1 in extras:
            if t0 <= t <= t1:
                hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
                red = ((hsv[..., 0] < 12) | (hsv[..., 0] > 168)) & (hsv[..., 1] > 90) & (hsv[..., 2] > 60)
                r = np.zeros_like(m)
                r[int(y0):int(y1), int(x0):int(x1)] = red[int(y0):int(y1), int(x0):int(x1)] * 255
                m |= cv2.dilate(r, np.ones((11, 11), np.uint8))
        return m

    # ---- kareleri diske, maskeleri belleğe ----
    n = int(round(t_end * fps))
    fr = np.load(frp, mmap_mode="r+") if resume else \
        np.lib.format.open_memmap(frp, "w+", np.uint8, (n, H, W, 3))
    if resume:
        print(f"devam: {len(done)} sahne zaten bitmiş ({work})")
    raw = np.zeros((n, H, W), np.uint8)
    for i, f in enumerate(frames_of(a.src, W, H, t_end)):
        if i >= n:
            break
        if not resume:
            fr[i] = f
        raw[i] = raw_mask(f, i / fps)  # maske hep ORİJİNAL kareden
    n = min(n, i + 1)
    # yazı belirip kaybolurken (fade) yarı saydam harf eşiğin altında kalıyor:
    # komşu karelerin maskesi de eklenir (detext ile aynı pencere)
    back, ahead = 6, 10
    masks = np.zeros_like(raw)
    for i in range(n):
        masks[i] = raw[max(0, i - back):min(n, i + ahead + 1)].max(0)
        lm = logo_mask(i / fps)
        if lm is not None:
            masks[i] |= lm
    del raw

    def roi_of(m):
        """maskeli satırlar + bağlam, yüksekliği 8'in katı (model 8'e yuvarlıyor)"""
        rows = np.nonzero(m.max(axis=(0, 2)))[0]
        y0 = max(0, rows.min() - a.margin)
        y1 = min(H, rows.max() + a.margin)
        h = -(-(y1 - y0) // 8) * 8
        y0 = max(0, min(y0, H - h))
        return y0, min(H, y0 + h)

    if not masks[:n].any():
        sys.exit("maske boş — silinecek bir şey bulunamadı")
    print(f"{n} kare")

    # ---- sahnelere böl ----
    cuts = [0] + [int(round(c * fps)) for c in scene_cuts(a.src, a.scene_thr, t_end)] + [n]
    cuts = sorted(set(c for c in cuts if 0 <= c <= n))
    chunks = []
    for s, e in zip(cuts[:-1], cuts[1:]):
        k = max(1, -(-(e - s) // a.max_chunk))
        step = -(-(e - s) // k)
        chunks += [(b, min(e, b + step)) for b in range(s, e, step)]
    if a.only:
        o0, o1 = (int(round(float(v) * fps)) for v in a.only.split(","))
        chunks = [(max(s, o0), min(e, o1)) for s, e in chunks if e > o0 and s < o1]

    out = fr  # yerinde güncelle
    t_all = time.time()
    for ci, (s, e) in enumerate(chunks):
        if e - s < 2 or not masks[s:e].any() or (s, e) in done:
            continue
        ry0, ry1 = roi_of(masks[s:e])  # sahne başına: ok/logo yalnız kendi sahnesinde büyütsün
        d = os.path.join(work, f"c{ci:03d}"); fd = os.path.join(d, "frames"); md = os.path.join(d, "masks")
        shutil.rmtree(d, ignore_errors=True); os.makedirs(fd); os.makedirs(md)
        for j in range(s, e):
            cv2.imwrite(os.path.join(fd, f"{j - s:04d}.png"), fr[j, ry0:ry1])
            cv2.imwrite(os.path.join(md, f"{j - s:04d}.png"), masks[j, ry0:ry1])
        t0 = time.time()
        r = subprocess.run([sys.executable, "inference_propainter.py", "-i", fd, "-m", md,
                            "-o", os.path.join(d, "res"), "--save_frames",
                            "--raft_iter", str(a.raft_iter), "--resize_ratio", str(a.scale),
                            "--neighbor_length", str(a.neighbor)],
                           cwd=PP, capture_output=True, text=True)
        rd = os.path.join(d, "res", "frames", "frames")
        if r.returncode or not os.path.isdir(rd):
            print(r.stdout[-2000:], r.stderr[-3000:]); sys.exit(f"ProPainter hata: kare {s}-{e}")
        for j in range(s, e):
            p = cv2.imread(os.path.join(rd, f"{j - s:04d}.png"))
            if p.shape[:2] != (ry1 - ry0, W):
                p = cv2.resize(p, (W, ry1 - ry0), interpolation=cv2.INTER_CUBIC)
            m = cv2.dilate(masks[j, ry0:ry1], np.ones((13, 13), np.uint8))
            al = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2)[..., None]
            roi = out[j, ry0:ry1].astype(np.float32)
            out[j, ry0:ry1] = (p * al + roi * (1 - al)).round().astype(np.uint8)
        fr.flush()
        with open(donep, "a") as fh:
            fh.write(f"{s} {e}\n")
        if not a.keep:
            shutil.rmtree(d)
        print(f"sahne {s / fps:6.2f}-{e / fps:6.2f} s ({e - s} kare, y {ry0}-{ry1}) {time.time() - t0:5.0f} sn", flush=True)
    print(f"model toplam {time.time() - t_all:.0f} sn")

    # ---- yaz: işlenen kareler + (varsa) kapanış kartı olduğu gibi ----
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-i", a.src, "-map", "0:v",
                            "-map", "1:a?", "-c:v", "libx264", "-crf", "12", "-preset", "slow",
                            "-pix_fmt", "yuv420p", "-c:a", "copy", a.out], stdin=subprocess.PIPE)
    for i, f in enumerate(frames_of(a.src, W, H)):
        enc.stdin.write((out[i] if i < n else f).tobytes())
    enc.stdin.close(); enc.wait()
    if not a.keep:
        shutil.rmtree(work)
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
