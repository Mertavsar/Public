#!/usr/bin/env python3
"""
Aynı kurgunun farklı AÇILIŞ YAZISIYLA sürümlerini üretir — hook A/B testi için.

Neden: kanalın tutunma oranı %48.6, yani yarısı ilk saniyelerde kaydırıyor.
Bugüne kadarki her hook kararı teoriden geldi (YouTube'un genel tavsiyesi,
referans videodan ölçüm). Aynı videonun iki farklı açılışla yayınlanması
HİÇ denenmedi. Ölçmeden hangi kalıbın bu kitlede çalıştığı bilinemez.

Ucuz olmasının sebebi: görüntü, ses ve altyazı değişmiyor. Sadece banner
katmanı yeniden çiziliyor ve birleştirme tekrarlanıyor — tam kurgunun
beşte biri kadar iş.

    python3 variants.py --work _build --out-dir . --base kirpi \
        --hook "BU DİKEN|BİNLERCE LİRA" \
        --hook "BU DİKENLER|NEDEN TOPLANIYOR?" \
        --hook "ÇÖPE ATTIĞIN ŞEY|BİNLERCE LİRA"

`--work`, `build.py`nin bıraktığı klasör (content.mp4 + mix.wav + spec.resolved.json).

Test yöntemi: sürümleri AYNI ANDA yayınlama — biri Shorts'a biri Reels'e,
ya da iki gün arayla. 2. saniyedeki tutunma eğrisini karşılaştır ve sonucu
`reference/performance-log.md`ye yaz. Tek değişken değişsin: sadece yazı.
"""

import argparse, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    p = subprocess.run(cmd)
    if p.returncode:
        raise SystemExit(f"BAŞARISIZ: {' '.join(cmd[:5])} …")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="build.py'nin bıraktığı klasör")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--base", required=True, help="çıktı adı öneki")
    ap.add_argument("--hook", action="append", required=True,
                    help="açılış yazısı; | satır kırar. Birden fazla ver.")
    ap.add_argument("--fx", default=None, help="parlama/sarsıntı ifadeleri (fx.txt)")
    a = ap.parse_args()

    content = f"{a.work}/content.mp4"
    mix = f"{a.work}/mix.wav"
    spec_path = f"{a.work}/spec.resolved.json"
    for f in (content, mix, spec_path):
        if not os.path.exists(f):
            raise SystemExit(f"{f} yok — önce build.py çalıştır.")
    spec = json.load(open(spec_path, encoding="utf-8"))
    if not spec.get("banners"):
        raise SystemExit("spec'te banner yok; A/B testi açılış yazısı üzerine.")

    dur = spec["duration"]
    if a.fx and os.path.exists(a.fx):
        flash, sx, sy = open(a.fx).read().splitlines()[:3]
    else:
        flash, sx, sy = "0", "14", "24"

    outs = []
    for i, hook in enumerate(a.hook):
        tag = chr(ord("A") + i)
        s = dict(spec)
        s["banners"] = [dict(spec["banners"][0], text=hook)]
        sp = f"{a.work}/spec.{tag}.json"
        json.dump(s, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        ov = f"{a.work}/overlay.{tag}.mov"
        print(f"\n--- {tag}: {hook.replace('|', ' / ')}")
        run([sys.executable, f"{HERE}/overlay.py", "--spec", sp, "--out", ov])
        out = os.path.join(a.out_dir, f"{a.base}_{tag}.mp4")
        fc = (f"[0:v]scale=1108:1968:flags=bicubic,crop=1080:1920:x='{sx}':y='{sy}',"
              f"eq=brightness='{flash}':eval=frame,eq=contrast=1.04:saturation=1.06,"
              f"setsar=1[bg];[bg][1:v]overlay=0:0:format=auto[v]")
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", content, "-i", ov,
             "-i", mix, "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
             "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
             "-maxrate", "7000k", "-bufsize", "14000k", "-pix_fmt", "yuv420p",
             "-profile:v", "high", "-level", "4.0", "-r", "30",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart", out])
        mb = os.path.getsize(out) / 1048576
        print(f"    -> {out}  ({mb:.1f} MiB)")
        outs.append((tag, hook, out))

    print("\n" + "=" * 60)
    print("TEST YÖNTEMİ")
    print("  1. Sürümleri aynı anda yayınlama — biri Shorts, biri Reels;")
    print("     ya da iki gün arayla aynı saatte.")
    print("  2. 2-3 gün sonra Studio'dan 2. saniyedeki tutunma yüzdesini al.")
    print("  3. reference/performance-log.md'ye yaz. Tek değişken: açılış yazısı.")
    print("  4. Beş testten sonra hangi kalıbın tuttuğu görünür.")
    for tag, hook, out in outs:
        print(f"  {tag}: {hook.replace('|', ' / ')}")


if __name__ == "__main__":
    main()
