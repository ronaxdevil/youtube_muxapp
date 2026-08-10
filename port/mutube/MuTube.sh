#!/bin/bash
# PortMaster launcher for MuTube
XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}
if [ -d "/opt/system/Tools/PortMaster" ]; then controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster" ]; then controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster" ]; then controlfolder="$XDG_DATA_HOME/PortMaster"
else controlfolder="/roms/ports/PortMaster"; fi

source "$controlfolder/control.txt"
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
get_controls

GAMEDIR="/$directory/ports/mutube"
mkdir -p "$GAMEDIR/conf" "$GAMEDIR/downloads"
cd "$GAMEDIR/data" || exit 1
> "$GAMEDIR/log.txt" && exec > >(tee "$GAMEDIR/log.txt") 2>&1

# Obtain the current CFW framebuffer size and make it available to MuTube.
# Most PortMaster control files provide SCREEN_WIDTH/SCREEN_HEIGHT; fbset is a
# safe fallback on CFWs that do not.
WIDTH="${SCREEN_WIDTH:-${APP_SCREEN_WIDTH:-}}"
HEIGHT="${SCREEN_HEIGHT:-${APP_SCREEN_HEIGHT:-}}"
if [ -z "$WIDTH" ] || [ -z "$HEIGHT" ]; then
  if command -v fbset >/dev/null 2>&1; then
    set -- $(fbset -s 2>/dev/null | awk '/geometry/ {print $2, $3; exit}')
    WIDTH="${WIDTH:-${1:-640}}"
    HEIGHT="${HEIGHT:-${2:-480}}"
  else
    WIDTH="${WIDTH:-640}"
    HEIGHT="${HEIGHT:-480}"
  fi
fi
export APP_SCREEN_WIDTH="$WIDTH"
export APP_SCREEN_HEIGHT="$HEIGHT"

# Keep downloads, settings and thumbnails outside the application data folder.
export XDG_DATA_HOME="$GAMEDIR/conf"
export MUTUBE_DOWNLOAD_DIR="$GAMEDIR/downloads"
export MUTUBE_CFW_NAME="$CFW_NAME"
export PATH="$GAMEDIR/data:$PATH"
export LD_LIBRARY_PATH="$controlfolder/libs:$controlfolder/utils/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$controlfolder/exlibs:$controlfolder/pylibs:$controlfolder/libs:$PYTHONPATH"
export PYSDL2_DLL_PATH="$controlfolder/libs"
export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"
# Let SDL/fontconfig find the app's bundled font on CFWs with sparse font paths.
export XDG_DATA_DIRS="$GAMEDIR:$controlfolder:${XDG_DATA_DIRS:-}"

# yt-dlp installs FFmpeg here. FAT filesystems do not retain execute bits.
[ -f "$GAMEDIR/data/ffmpeg" ] && chmod +x "$GAMEDIR/data/ffmpeg"

python3 youtube.py
pm_finish
