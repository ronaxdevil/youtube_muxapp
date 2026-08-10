# MuTube

MuTube is a controller-friendly YouTube browser, downloader, and offline video player for muOS and PortMaster-compatible Linux handhelds.

It is built with Python 3, PySDL2, and SDL2. Online browsing, search, stream resolution, and downloads use yt-dlp. Playback uses MPV when available and falls back to ffplay. FFmpeg merges separate high-quality video and audio streams.

## Features

- Home feed, normal text search, and genre search including Live.
- 360p, 480p, 720p, and 1080p; 720p is the default.
- Downloaded-video playback, file details, deletion, and Media move/copy actions.
- MPV seek bar while seeking with D-pad or shoulder buttons.
- Circular loader while starting videos; B cancels loading or downloading.
- First-run yt-dlp and FFmpeg install prompt; Settings can update either tool.
- MPV preferred with automatic ffplay fallback.
- CFW-aware Media export and thumbnail artwork placement.

## Controls

| Button | Action |
|---|---|
| D-pad | Navigate lists and menus |
| A | Select / play |
| Hold A | Quality or local-file action menu |
| B | Back / cancel loading or downloading |
| X | Text search |
| START | Download selected online video |
| L1/R1 or Left/Right while playing | Seek backward/forward |
| Y while playing | Pause/resume in MPV |

## First launch

Release packages do not include yt-dlp or FFmpeg. On first launch choose **Download now** to install them to `data/`. MuTube restores execute permission for FFmpeg because FAT SD cards do not preserve it. Internet access is required, and YouTube rate limits or account checks may still prevent a request.

## Media export

Settings → **Media layout** supports Automatic detection plus muOS, EmulationStation (Batocera/Knulli/ROCKNIX), Onion/Garlic/MinUI, and ArkOS. A moved/copied video goes to the layout's `Media` ROM folder. Its JPG thumbnail is placed with the same filename stem in:

- muOS: `MUOS/info/catalogue/Media/box`
- Batocera, Knulli, ROCKNIX, ArkOS: `Media/images`
- OnionOS, GarlicOS, MinUI: `Media/Imgs`

On muOS, **Media destination** selects MMC or SD Card and falls back to MMC if needed.

## Build packages

Generated archives go to `outputs/` and are ignored by Git.

### Windows

Double-click `build_muxapp.bat` for a muOS `.muxapp`, or `build_portmaster.bat` for a PortMaster ZIP. To set a version:

```bat
build_muxapp.bat 1.2.0
build_portmaster.bat 1.2.0
```

The batch launchers use a process-only PowerShell execution-policy bypass.

### Linux

```sh
chmod +x build_muxapp.sh build_portmaster.sh
./build_muxapp.sh 1.2.0
./build_portmaster.sh 1.2.0
```

The Linux PortMaster build needs `rsync` and `zip`.

## PortMaster ZIP layout

```text
MuTube.sh
mutube/
  data/
  conf/
  downloads/
  licenses/
  port.json
  README.md
  gameinfo.xml
  screenshot.png
```

The launcher loads PortMaster controls, CFW-specific settings, resolution, dependency paths, and font paths. Replace the included placeholder screenshot with a real 640×480 MuTube screen before an upstream PortMaster catalogue submission.

## Project files

- `data/youtube.py` — application UI, playback, downloads, and settings.
- `mux_launch.sh` — muOS launcher.
- `port/mutube/` — PortMaster metadata and launcher.
- `build_muxapp.*` — muOS package builders.
- `build_portmaster.*` — PortMaster package builders.
