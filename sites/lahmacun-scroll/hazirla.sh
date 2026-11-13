#!/usr/bin/env bash
# Google Flow sahnelerini siteye hazır kare paketlerine çevirir.
# Kullanım:  ./hazirla.sh sahne1.mp4 sahne2.mp4 sahne3.mp4   (tek video da olur)
# Birden fazla video verilirse önce uç uca birleştirilir (her sahnenin son karesi
# sonrakinin ilk karesi olduğu için birleşim görünmez).
#
# Kareler görüntü değişimine göre seçilir: art arda iki seçili kare arasındaki fark hep
# aynı küçük miktarda kalır (alev ve hamurun havada dönüşü her karede, duran el seyrek).
#   HEDEF     seçilecek yaklaşık kare sayısı (varsayılan 330)
#   ENSEYREK  iki seçili kare arasında en fazla kaç kaynak kare olabileceği (varsayılan 5)
#
# Çıktı iki set:
#   frames/        bilgisayar: tam kare 1280x720, 2x2'lik paketlerde (paket-N.jpg)
#   frames-mobil/  telefon: yalnızca telefonun gösterdiği orta bölge (genişliğin %6–74'ü),
#                  640 px, 2x2'lik paketlerde; kare başı ~1/3 boyut
# Her sette ayrıca bütün karelerin küçük hâli 8x6'lık önizleme paketlerinde (onizleme-N.jpg):
# site önce bunları indirir, kaydırma ilk saniyeden her karede doğru görüntüyü gösterir.
# Paketler hem dosya sayısını hem istek sayısını 4'e böler; yavaş sunucuda ilk giriş hızlanır.
# manifest.json'a her kaynak karenin birikimli görüntü değişimi ("cum") de yazılır; site
# kaydırma hızını görüntünün değişim hızına göre dengeler.
set -euo pipefail

[ $# -ge 1 ] || { echo "Video dosyasını ver: ./hazirla.sh sahne1.mp4 [sahne2.mp4 ...]"; exit 1; }
root="$(cd "$(dirname "$0")" && pwd)"
out="$root/frames"
mob="$root/frames-mobil"
fps="${FPS:-24}"
width="${WIDTH:-1280}"
quality="${QUALITY:-6}"     # JPEG kalitesi: 2 en iyi, 31 en kötü
sharpen="${SHARPEN:-0.45}"  # Flow 720p verdiği için hafif keskinleştirme; 0 kapatır
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

# near-lossless intermediates; the only real compression happens once, in the packs
ffmpeg -loglevel error -i "$in" -an \
  -vf "fps=${fps},scale='min(${width},iw)':-2:flags=lanczos,unsharp=5:5:${sharpen}" \
  -q:v 2 "$tmp/k_%05d.jpg"

mkdir -p "$tmp/sel" "$out" "$mob"
rm -f "$out"/*.jpg "$out"/manifest.json "$mob"/*.jpg "$mob"/manifest.json

python3 - "$tmp" "$hedef" "$enseyrek" <<'PY'
import json, os, shutil, sys
import numpy as np
from PIL import Image
src, hedef, enseyrek = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
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
    shutil.copy(os.path.join(src, names[i]), os.path.join(src, "sel", f"{n:04d}.jpg"))
steps = np.diff(cum[picked])
base = {
    "count": len(picked), "width": 1280, "height": 720,
    "times": [round(i / (total - 1), 5) for i in picked],
    "cum": [round(float(c / cum[-1]), 5) for c in cum],
}
json.dump(base, open(os.path.join(src, "base.json"), "w"), separators=(",", ":"))
print(f"{total} kareden {len(picked)} tanesi seçildi; kare başı değişim ort. {steps.mean():.2f}, en çok {steps.max():.2f}")
PY

sel="$tmp/sel/%04d.jpg"
# desktop: full frames in 2x2 packs, plus 8x6 preview sheets
ffmpeg -loglevel error -framerate 24 -i "$sel" -vf "tile=2x2" -q:v "$quality" "$out/paket-%d.jpg"
ffmpeg -loglevel error -framerate 24 -i "$sel" -vf "scale=320:180:flags=lanczos,tile=8x6" -q:v 7 "$out/onizleme-%d.jpg"
# phone: only the middle the phone shows, at the size the screen needs
ffmpeg -loglevel error -framerate 24 -i "$sel" -vf "crop=iw*0.68:ih:iw*0.06:0,scale=640:-2:flags=lanczos,tile=2x2" -q:v 6 "$mob/paket-%d.jpg"
ffmpeg -loglevel error -framerate 24 -i "$sel" -vf "crop=iw*0.68:ih:iw*0.06:0,scale=320:-2:flags=lanczos,tile=8x6" -q:v 9 "$mob/onizleme-%d.jpg"

python3 - "$tmp" "$out" "$mob" <<'PY'
import json, os, sys
from PIL import Image
tmp, out, mob = sys.argv[1:4]
base = json.load(open(os.path.join(tmp, "base.json")))
def write(folder, name, crop):
    pw, ph = Image.open(os.path.join(folder, "paket-1.jpg")).size
    vw, vh = Image.open(os.path.join(folder, "onizleme-1.jpg")).size
    m = dict(base)
    m["pack"] = {"path": f"{name}/paket-%d.jpg", "packs": len([f for f in os.listdir(folder) if f.startswith("paket-")]),
                 "cols": 2, "rows": 2, "w": pw // 2, "h": ph // 2}
    m["preview"] = {"path": f"{name}/onizleme-%d.jpg", "sheets": len([f for f in os.listdir(folder) if f.startswith("onizleme-")]),
                    "cols": 8, "rows": 6, "w": vw // 8, "h": vh // 6}
    if crop: m["crop"] = crop
    json.dump(m, open(os.path.join(folder, "manifest.json"), "w"), separators=(",", ":"))
    print(f"{name}: {m['pack']['packs']} paket ({m['pack']['w']}x{m['pack']['h']} kare), {m['preview']['sheets']} önizleme")
write(out, "frames", None)
write(mob, "frames-mobil", {"x": 0.06, "w": 0.68})
PY

echo "Bilgisayar: $(du -sh "$out" | cut -f1) → $out"
echo "Telefon:    $(du -sh "$mob" | cut -f1) → $mob"
