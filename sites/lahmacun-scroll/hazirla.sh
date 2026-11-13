#!/usr/bin/env bash
# Google Flow sahnelerini siteye hazır kare dizisine çevirir.
# Kullanım:  ./hazirla.sh sahne1.mp4 sahne2.mp4 sahne3.mp4   (tek video da olur)
# Birden fazla video verilirse önce uç uca birleştirilir (her sahnenin son karesi
# sonrakinin ilk karesi olduğu için birleşim görünmez).
#
# Hareketli anlar sık, durağan anlar seyrek tutulur; böylece site hafif kalır.
# PLAN, "kareAralığı:adım" listesidir (birleşik videoda 24 fps'te kare numarası, 0'dan).
# Varsayılan plan Kuzu Lahmacun'un üç sahnelik videosuna göre ayarlıdır (her sahne 190 kare):
#   Sahne 1  0-83:3      un serpme, beze (0–3,5 sn)
#            84-120:1    hamurun havada açılıp inişi (3,5–5 sn)   → her kare
#            121-189:2   el hamuru düzeltir
#   Sahne 2  190-201:4   açılmış hamur
#            202-310:2   tuz, biber, domates, sarımsak yağıyor
#            311-335:1   kıyma katmanı geliyor                      → her kare
#            336-379:2   maydanoz
#   Sahne 3  380-416:2   el harcı bastırır
#            417-475:4   durgun
#            476-536:2   fırın alevi
#            537-569:3   pişmiş lahmacun
set -euo pipefail

[ $# -ge 1 ] || { echo "Video dosyasını ver: ./hazirla.sh sahne1.mp4 [sahne2.mp4 ...]"; exit 1; }
out="$(cd "$(dirname "$0")" && pwd)/frames"
fps="${FPS:-24}"
width="${WIDTH:-1280}"
quality="${QUALITY:-6}"    # JPEG kalitesi: 2 en iyi, 31 en kötü
sharpen="${SHARPEN:-0.45}" # Flow 720p verdiği için hafif keskinleştirme; 0 kapatır
plan="${PLAN:-0-83:3,84-120:1,121-189:2,190-201:4,202-310:2,311-335:1,336-379:2,380-416:2,417-475:4,476-536:2,537-569:3}"

command -v ffmpeg >/dev/null || { echo "ffmpeg bulunamadı. Mac: brew install ffmpeg"; exit 1; }
command -v python3 >/dev/null || { echo "python3 bulunamadı."; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if [ $# -gt 1 ]; then
  inputs=(); filt=""
  for i in $(seq 0 $(($# - 1))); do inputs+=(-i "${@:$((i + 1)):1}"); filt+="[$i:v]"; done
  ffmpeg -loglevel error "${inputs[@]}" -filter_complex "${filt}concat=n=$#:v=1:a=0,fps=${fps}[v]" \
    -map "[v]" -c:v libx264 -crf 14 -preset medium -pix_fmt yuv420p "$tmp/birlesik.mp4"
  in="$tmp/birlesik.mp4"
else
  in="$1"
fi

ffmpeg -loglevel error -i "$in" -an \
  -vf "fps=${fps},scale='min(${width},iw)':-2:flags=lanczos,unsharp=5:5:${sharpen}" \
  -q:v "$quality" "$tmp/k_%05d.jpg"

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
    shutil.copy(os.path.join(src, f"k_{i + 1:05d}.jpg"), os.path.join(out, f"{n:04d}.jpg"))
times = [round(i / (total - 1), 5) for i in picked]
with open(os.path.join(out, "manifest.json"), "w") as fh:
    json.dump({"count": len(picked), "path": "frames/", "pad": 4, "ext": "jpg", "times": times}, fh)
print(f"{total} kareden {len(picked)} tanesi seçildi")
PY

echo "Hazır: $(du -sh "$out" | cut -f1) → $out"
