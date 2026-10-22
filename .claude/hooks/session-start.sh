#!/bin/bash
# OpenMontage'ı bulut oturumunda hazır eder (yapay zekâ destekli video üretim sistemi).
# - Depoya kopyalanmaz (AGPL-3.0); oturum başında $HOME altına sığ klonlanır.
# - Python bağımlılıkları .venv'e, Remotion bağımlılıkları npm ile kurulur.
# - Remotion kendi tarayıcısını remotion.media'dan indirmek ister; bu alan adı ağ
#   politikasında kapalı. Ortamdaki Playwright Chromium (headless shell) kullanılır.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

OM_DIR="${OPENMONTAGE_DIR:-$(dirname "${CLAUDE_PROJECT_DIR:-$PWD}")/calesthio/openmontage}"
OM_URL="https://github.com/calesthio/openmontage"
BROWSER="/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"

if [ ! -d "$OM_DIR/.git" ]; then
  mkdir -p "$(dirname "$OM_DIR")"
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 "$OM_URL" "$OM_DIR"
fi

cd "$OM_DIR"
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q -r requirements-dev.txt
(cd remotion-composer && npm install --no-audit --no-fund --silent)
[ -f .env ] || cp .env.example .env

# Remotion: yerel Chromium'u kullan (ağdan indirme yok)
if [ -x "$BROWSER" ] && ! grep -q setBrowserExecutable remotion-composer/remotion.config.ts 2>/dev/null; then
  cat >> remotion-composer/remotion.config.ts <<TS
import { Config } from '@remotion/cli/config';
Config.setBrowserExecutable('$BROWSER');
TS
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export OPENMONTAGE_DIR=\"$OM_DIR\"" >> "$CLAUDE_ENV_FILE"
  echo "export REMOTION_BROWSER_EXECUTABLE=\"$BROWSER\"" >> "$CLAUDE_ENV_FILE"
fi
echo "OpenMontage hazır: $OM_DIR"
