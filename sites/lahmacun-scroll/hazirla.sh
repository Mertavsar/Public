#!/usr/bin/env bash
# Google Flow videosunu siteye hazır kare dizisine çevirir.
# Kullanım:  ./hazirla.sh flow-videosu.mp4
#
# Hareketli anlar her karede, durağan anlar seyrek tutulur; böylece site hafif kalır.
# PLAN, "kareAralığı:adım" listesidir (24 fps'te kare numarası, 0'dan başlar).
# Varsayılan plan Kuzu Lahmacun'un 8 sn'lik Flow videosuna göre ayarlıdır:
#   0-20:5     beze duruyor (0–0,9 sn)             → seyrek
#   21-44:1    hamur açılıyor (0,9–1,8 sn)         → her kare
#   45-73:2    harç yayılıyor (1,9–3,0 sn)         → 2'de 1
#   74-106:4   neredeyse durağan (3,1–4,4 sn)      → 4'te 1
#   107-130:1  pişiyor (4,5–5,4 sn)                → her kare
#   131-191:3  buhar, limon, maydanoz (5,5–8 sn)   → 3'te 1
# Başka bir videoda tüm kareleri almak için: PLAN="0-9999:1" ./hazirla.sh video.mp4
set -euo pipefail

in="${1:?Video dosyasını ver: ./hazirla.sh flow-videosu.mp4}"
out="$(cd "$(dirname "$0")" && pwd)/frames"
fps="${FPS:-24}"
width="${WIDTH:-1280}"
quality="${QUALITY:-10}"   # JPEG kalitesi: 2 en iyi, 31 en kötü
plan="${PLAN:-0-20:5,21-44:1,45-73:2,74-106:4,107-130:1,131-191:3}"

command -v ffmpeg >/dev/null || { echo "ffmpeg bulunamadı. Mac: brew install ffmpeg"; exit 1; }
command -v python3 >/dev/null || { echo "python3 bulunamadı."; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

ffmpeg -loglevel error -i "$in" -an \
  -vf "fps=${fps},scale='min(${width},iw)':-2" \
  -q:v "$quality" "$tmp/%05d.jpg"

mkdir -p "$out"
rm -f "$out"/*.jpg "$out"/manifest.json

python3 - "$tmp" "$out" "$plan" <<'PY'
import json, os, shutil, sys
src, out, plan = sys.argv[1], sys.argv[2], sys.argv[3]
total = len([f for f in os.listdir(src) if f.endswith(".jpg")])
keep = set()
for part in plan.split(","):
    rng, step = part.split(":")
    a, b = (int(x) for x in rng.split("-"))
    keep.update(range(a, min(b, total - 1) + 1, int(step)))
keep.update({0, total - 1})
picked = sorted(i for i in keep if i < total)
for n, i in enumerate(picked, 1):
    shutil.copy(os.path.join(src, f"{i + 1:05d}.jpg"), os.path.join(out, f"{n:04d}.jpg"))
times = [round(i / (total - 1), 5) for i in picked]
with open(os.path.join(out, "manifest.json"), "w") as fh:
    json.dump({"count": len(picked), "path": "frames/", "pad": 4, "ext": "jpg", "times": times}, fh)
print(f"{total} kareden {len(picked)} tanesi seçildi")
PY

echo "Hazır: $(du -sh "$out" | cut -f1) → $out"
