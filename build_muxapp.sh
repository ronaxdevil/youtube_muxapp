#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.2.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$ROOT/outputs"
STAGE="$(mktemp -d)"
APP="$STAGE/MuTube"
ARCHIVE="$OUTPUT/MuTube-${VERSION}.muxapp"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$APP" "$OUTPUT"
if command -v rsync >/dev/null 2>&1; then
  rsync -a "$ROOT/" "$APP/" --exclude '.git/' --exclude 'outputs/' \
    --exclude 'downloads/' --exclude '__pycache__/' --exclude '*.pyc' \
    --exclude 'yt-dlp' --exclude 'ffmpeg' --exclude 'log.txt' \
    --exclude 'yt_settings.json'
else
  tar -C "$ROOT" --exclude='./.git' --exclude='./outputs' \
    --exclude='./downloads' --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='./data/yt-dlp' --exclude='./data/ffmpeg' \
    --exclude='./data/log.txt' --exclude='./data/yt_settings.json' \
    -cf - . | tar -C "$APP" -xf -
fi
rm -f "$ARCHIVE"
(cd "$STAGE" && zip -qr "$ARCHIVE" MuTube)
echo "Created $ARCHIVE"
