# MuTube

MuTube is a muOS YouTube browser and offline video player.

## Building a muxapp

Windows: double-click `build_muxapp.bat`. It starts the PowerShell builder with
the temporary execution-policy setting that some Windows systems require. To
choose a version, run `build_muxapp.bat 1.2.0` from Command Prompt.

Linux: run `chmod +x build_muxapp.sh` once, then `./build_muxapp.sh 1.2.0`.

Build output is placed in `outputs/`, which is intentionally ignored by Git.
The release package excludes downloaded content, logs, Python cache, yt-dlp,
and FFmpeg. MuTube downloads yt-dlp and FFmpeg to the device on first launch
after you approve the prompt.

## Download controls

Hold **A** on a local download for Play, Delete, Details, Move to Media, or
Copy to Media. Settings chooses MMC or SD Card as the Media target. If the SD
card is not available, MuTube uses MMC safely.
