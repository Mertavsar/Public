#!/usr/bin/env python3
"""Tek komutla: temiz plaka -> derinlik -> ses -> video.

  python3 pipeline.py urun.jpg cikti/ --ar 9:16 4:5

Ara dosyalar cikti dizinine yazilir; segment adimindan sonra
mask_debug.png dosyasina bakmadan sonuca guvenmeyin.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(*args):
    cmd = [sys.executable] + [str(a) for a in args]
    print("»", " ".join(os.path.basename(str(a)) for a in cmd[1:]))
    subprocess.run(cmd, check=True, cwd=HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="urun gorseli")
    ap.add_argument("outdir", help="cikti dizini")
    ap.add_argument("--ar", nargs="+", default=["9:16"],
                    choices=["9:16", "4:5", "1:1"])
    ap.add_argument("--cta", default="HEMEN SİPARİŞ VER")
    ap.add_argument("--kicker", default="KOLEKSİYONA EKLE")
    ap.add_argument("--no-clean", action="store_true",
                    help="poster grafik katmani yoksa temizleme adimini atla")
    a = ap.parse_args()

    src = os.path.abspath(a.src)
    out = os.path.abspath(a.outdir)
    os.makedirs(out, exist_ok=True)
    j = lambda n: os.path.join(out, n)

    clean = src
    if not a.no_clean:
        run(os.path.join(HERE, "clean_plate.py"), src, j("clean.png"))
        clean = j("clean.png")

    run(os.path.join(HERE, "segment.py"), clean, out + os.sep)
    run(os.path.join(HERE, "make_audio.py"), j("soundtrack.wav"))

    for ar in a.ar:
        tag = ar.replace(":", "x")
        run(os.path.join(HERE, "make_video.py"), src, j(f"reklam_{tag}.mp4"),
            "--clean", clean, "--depth", j("depth.png"),
            "--plate", j("bgplate.png"), "--ar", ar,
            "--audio", j("soundtrack.wav"), "--cta", a.cta, "--kicker", a.kicker)

    print("\nbitti ->", out)
    print("KONTROL: mask_debug.png maskeleri dogru mu?")


if __name__ == "__main__":
    main()
