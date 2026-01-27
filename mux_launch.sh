#!/bin/bash
# HELP: MuTube
# ICON: mutube
# GRID: MuTube

. /opt/muos/script/var/func.sh

# Define global variables
SCREEN_WIDTH=$(GET_VAR device mux/width)
SCREEN_HEIGHT=$(GET_VAR device mux/height)

if [ "$SCREEN_WIDTH" == "720" ] && [ "$SCREEN_HEIGHT" == "480" ]; then
  # RG34XX SP / Plus / H
  APP_FILE="yt_32.py"
elif [ "$SCREEN_WIDTH" == "640" ] && [ "$SCREEN_HEIGHT" == "480" ]; then
  # RG35XX SP / OG / Plus
  APP_FILE="yt_43.py"
else
  # Fallback for default screens (e.g. 720x720)
  APP_FILE="yt_11.py"
fi

# ---  Directory Setup ---
DIR="$(dirname "$0")"
DATADIR="$DIR/data"

# --- 1. PortMaster Detection ---
XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source $controlfolder/control.txt
get_controls
[ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"


# --- 2. Exports & Library Setup ---
export LD_LIBRARY_PATH="$controlfolder/libs:$controlfolder/utils/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$controlfolder/exlibs:$controlfolder/pylibs:$controlfolder/libs:$PYTHONPATH"
export PYSDL2_DLL_PATH="$controlfolder/libs"
export PATH="$DATADIR:$PATH"

# --- 3. Move into the directory ---
cd "$DATADIR"

> "$DATADIR/log.txt" && exec > >(tee "$DATADIR/log.txt") 2>&1

# [TEXT FIX] Force system to look for fonts in the game folder
export XDG_DATA_DIRS="$DIR:$controlfolder:$XDG_DATA_DIRS"

# Terminal settings
$ESUDO chmod 666 /dev/tty0
export TERM=linux
printf "\033c" > /dev/tty0

# Logging
echo "Starting YouTube..."
echo "PortMaster found at: $controlfolder"
echo "Running in directory: $(pwd)"

# Launch the application
$ESUDO python3 "$APP_FILE"

# Cleanup
printf "\033c" > /dev/tty0
