#!/bin/bash
# HELP: MuTube
# ICON: mutube
# GRID: MuTube


# --- 1. Get Resolution from MUOS ---
if [ -f /opt/muos/script/var/func.sh ]; then
  . /opt/muos/script/var/func.sh
  WIDTH=$(GET_VAR device mux/width)
  HEIGHT=$(GET_VAR device mux/height)
else
  # Fallback
  WIDTH=640
  HEIGHT=480
fi

# --- 2. Push Resolution to Python ---
# We export these so youtube.py can read them
export APP_SCREEN_WIDTH="$WIDTH"
export APP_SCREEN_HEIGHT="$HEIGHT"

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
$ESUDO python3 youtube.py

# Cleanup
printf "\033c" > /dev/tty0
