#!/usr/bin/env bash
# Google Flow videosunu siteye hazır kare dizisine çevirir.
# Kullanım:  ./hazirla.sh flow-videosu.mp4
#
# Hareketli anlar her karede, durağan anlar seyrek tutulur; böylece site hafif kalır.
# PLAN, "kareAralığı:adım" listesidir (24 fps'te kare numarası, 0'dan başlar).
# Varsayılan plan Kuzu Lahmacun'un uzun lahmacunlu 8 sn'lik Flow videosuna göre ayarlıdır:
#   0-26:6     beze duruyor (0–1,1 sn)               → seyrek
#   27-45:1    hamur boydan boya açılıyor (1,1–1,9)  → her kare
#   46-64:1    harç beliriyor (1,9–2,7 sn)           → her kare
#   65-161:6   yavaş pişme (2,7–6,7 sn)              → 6'da 1
#   162-178:1  maydanoz ve limon (6,75–7,4 sn)       → her kare
#   179-191:4  son hâl (7,5–8 sn)                    → seyrek
# Başka bir videoda tüm kareleri almak için: PLAN="0-9999:1" ./hazirla.sh video.mp4
set -euo pipefail

in="${1:?Video dosyasını ver: ./hazirla.sh flow-videosu.mp4}"
out="$(cd "$(dirname "$0")" && pwd)/frames"
fps="${FPS:-24}"
width="${WIDTH:-1280}"
quality="${QUALITY:-6}"    # JPEG kalitesi: 2 en iyi, 31 en kötü
sharpen="${SHARPEN:-0.45}" # Flow 720p verdiği için hafif keskinleştirme; 0 kapatır
plan="${PLAN:-0-26:6,27-45:1,46-64:1,65-161:6,162-178:1,179-191:4}"

command -v ffmpeg >/dev/null || { echo "ffmpeg bulunamadı. Mac: brew install ffmpeg"; exit 1; }
command -v python3 >/dev/null || { echo "python3 bulunamadı."; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

ffmpeg -loglevel error -i "$in" -an \
  -vf "fps=${fps},scale='min(${width},iw)':-2:flags=lanczos,unsharp=5:5:${sharpen}" \
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
