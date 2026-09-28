#!/usr/bin/env bash
# vinpaint.py için ProPainter (video onarım modeli) kurulumu. Bir kez çalıştır.
# Ağ notu: huggingface ve download.pytorch.org kapalı; pypi ve github
# release indirmeleri açık. torch pypi'den (CUDA paketleriyle ~3 GB) geliyor,
# GPU yoksa CPU'da çalışıyor.
set -euo pipefail
DIR="${PROPAINTER_DIR:-$HOME/.cache/propainter}"
python3 -c "import torch, torchvision" 2>/dev/null || pip install -q torch torchvision
pip install -q einops timm scipy scikit-image addict yapf av imageio-ffmpeg matplotlib opencv-python-headless
if [ ! -f "$DIR/inference_propainter.py" ]; then
  rm -rf "$DIR"; git clone -q --depth 1 https://github.com/sczhou/ProPainter.git "$DIR"
fi
for w in ProPainter.pth recurrent_flow_completion.pth raft-things.pth; do
  [ -s "$DIR/weights/$w" ] || curl -sSL -o "$DIR/weights/$w" \
    "https://github.com/sczhou/ProPainter/releases/download/v0.1.0/$w"
done
ls -la "$DIR/weights"
echo "hazır: $DIR"
