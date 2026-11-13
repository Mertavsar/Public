#!/usr/bin/env bash
# Google Flow sahnelerini siteye hazır kare dizisine çevirir.
# Kullanım:  ./hazirla.sh sahne1.mp4 sahne2.mp4 sahne3.mp4   (tek video da olur)
# Birden fazla video verilirse önce uç uca birleştirilir (her sahnenin son karesi
# sonrakinin ilk karesi olduğu için birleşim görünmez).
#
# Kareler görüntü değişimine göre seçilir: art arda iki seçili kare arasındaki fark hep
# aynı küçük miktarda kalır. Alevin çıktığı, hamurun havada döndüğü anlarda her kare
# alınır; elin durduğu anlarda seyrek alınır. Böylece kaydırma her yerde aynı akıcılıkta olur.
#   HEDEF   seçilecek yaklaşık kare sayısı (varsayılan 330)
#   ENSEYREK  iki seçili kare arasında en fazla kaç kaynak kare olabileceği (varsayılan 5)
# manifest.json'a ayrıca her kaynak karenin birikimli görüntü değişimi ("cum") yazılır;
# site bununla kaydırma hızını görüntünün değişim hızına göre dengeler.
set -euo pipefail

[ $# -ge 1 ] || { echo "Video dosyasını ver: ./hazirla.sh sahne1.mp4 [sahne2.mp4 ...]"; exit 1; }
out="$(cd "$(dirname "$0")" && pwd)/frames"
fps="${FPS:-24}"
width="${WIDTH:-1280}"
quality="${QUALITY:-6}"    # JPEG kalitesi: 2 en iyi, 31 en kötü
sharpen="${SHARPEN:-0.45}" # Flow 720p verdiği için hafif keskinleştirme; 0 kapatır
hedef="${HEDEF:-330}"
enseyrek="${ENSEYREK:-5}"

command -v ffmpeg >/dev/null || { echo "ffmpeg bulunamadı. Mac: brew install ffmpeg"; exit 1; }
command -v python3 >/dev/null || { echo "python3 bulunamadı."; exit 1; }
python3 -c "import numpy, PIL" 2>/dev/null || { echo "python3 için numpy ve Pillow gerekli: pip install numpy pillow"; exit 1; }

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

python3 - "$tmp" "$out" "$hedef" "$enseyrek" <<'PY'
import json, os, shutil, sys
import numpy as np
from PIL import Image
src, out, hedef, enseyrek = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
names = sorted(f for f in os.listdir(src) if f.startswith("k_") and f.endswith(".jpg"))
total = len(names)
small = np.stack([np.asarray(Image.open(os.path.join(src, f)).convert("L").resize((160, 90)), np.float32) for f in names])
d = np.abs(np.diff(small, axis=0)).mean(axis=(1, 2))           # change between frame i and i+1
cum = np.concatenate([[0.0], np.cumsum(d)])

def pick(theta):
    keep, acc, last = [0], 0.0, 0
    for i in range(1, total):
        acc += d[i - 1]
        if acc >= theta or i - last >= enseyrek:
            keep.append(i); acc, last = 0.0, i
    if keep[-1] != total - 1: keep.append(total - 1)
    return keep

lo, hi = 0.01, float(cum[-1])                                     # bisect the step size to hit HEDEF
for _ in range(40):
    mid = (lo + hi) / 2
    if len(pick(mid)) > hedef: lo = mid
    else: hi = mid
picked = pick(hi)
for n, i in enumerate(picked, 1):
    shutil.copy(os.path.join(src, names[i]), os.path.join(out, f"{n:04d}.jpg"))
steps = np.diff(cum[picked])
manifest = {
    "count": len(picked), "path": "frames/", "pad": 4, "ext": "jpg",
    "times": [round(i / (total - 1), 5) for i in picked],
    "cum": [round(float(c / cum[-1]), 5) for c in cum],
}
with open(os.path.join(out, "manifest.json"), "w") as fh:
    json.dump(manifest, fh, separators=(",", ":"))
print(f"{total} kareden {len(picked)} tanesi seçildi; kare başı değişim ort. {steps.mean():.2f}, en çok {steps.max():.2f}")
PY

echo "Hazır: $(du -sh "$out" | cut -f1) → $out"
