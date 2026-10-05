#!/bin/bash
# YouTube Hub — macOS: bu dosyaya çift tıkla. Panel tarayıcıda açılır.
# Bu pencere açık kaldığı sürece panel çalışır.
cd "$(dirname "$0")/.." || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 bulunamadı. Kurulum penceresi açılacak; kurduktan sonra bu dosyaya yeniden çift tıkla."
  xcode-select --install 2>/dev/null
  read -n 1 -s -r -p "Kapatmak için bir tuşa bas..."
  exit 1
fi
# Son güncellemeleri al (yerel değişiklik varsa dokunmaz).
git pull --ff-only -q 2>/dev/null || true
python3 youtube-hub/hub.py serve
