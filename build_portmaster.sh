#!/usr/bin/env bash
set -euo pipefail
VERSION="${1:-1.2.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/mutube/licenses" "$ROOT/outputs"

cp "$ROOT/port/mutube/MuTube.sh" "$STAGE/"
cp "$ROOT/port/mutube/port.json" "$ROOT/port/mutube/README.md" \
   "$ROOT/port/mutube/gameinfo.xml" "$ROOT/port/mutube/screenshot.png" \
   "$STAGE/mutube/"
cp -a "$ROOT/port/mutube/licenses/." "$STAGE/mutube/licenses/"
rsync -a "$ROOT/" "$STAGE/mutube/" --exclude '.git/' --exclude 'outputs/' \
  --exclude 'downloads/' --exclude 'port/' --exclude '__pycache__/' --exclude '*.pyc' \
  --exclude 'yt-dlp' --exclude 'ffmpeg' --exclude 'log.txt' --exclude 'yt_settings.json' \
  --exclude '.gitignore' --exclude 'mux_launch.sh' \
  --exclude 'build_portmaster.ps1' --exclude 'build_portmaster.sh' --exclude 'build_muxapp.ps1' \
  --exclude 'build_muxapp.sh' --exclude 'build_muxapp.bat'
(cd "$STAGE" && zip -qr "$ROOT/outputs/MuTube-PortMaster-$VERSION.zip" .)
echo "Created $ROOT/outputs/MuTube-PortMaster-$VERSION.zip"
