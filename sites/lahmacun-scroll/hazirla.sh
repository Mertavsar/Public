#!/usr/bin/env bash
# Google Flow videosunu siteye hazır kare dizisine çevirir.
# Kullanım:  ./hazirla.sh flow-videosu.mp4
# İsteğe bağlı: FPS=30 WIDTH=1920 ./hazirla.sh flow-videosu.mp4
set -euo pipefail

in="${1:?Video dosyasını ver: ./hazirla.sh flow-videosu.mp4}"
out="$(cd "$(dirname "$0")" && pwd)/frames"
fps="${FPS:-24}"
width="${WIDTH:-1600}"

command -v ffmpeg >/dev/null || { echo "ffmpeg bulunamadı. Mac: brew install ffmpeg"; exit 1; }

mkdir -p "$out"
rm -f "$out"/*.jpg "$out"/manifest.json

ffmpeg -loglevel error -i "$in" -an \
  -vf "fps=${fps},scale='min(${width},iw)':-2" \
  -q:v 4 "$out/%04d.jpg"

count=$(find "$out" -name '*.jpg' | wc -l | tr -d ' ')
printf '{ "count": %s, "path": "frames/", "pad": 4, "ext": "jpg" }\n' "$count" > "$out/manifest.json"

size=$(du -sh "$out" | cut -f1)
echo "Hazır: ${count} kare, ${size} → ${out}"
