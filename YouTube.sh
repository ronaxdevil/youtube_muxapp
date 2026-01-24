#!/bin/bash
# YouTube App - PortMaster Launch Script

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
export PATH="$GAMEDIR:$PATH"

# --- 3. Directory Setup ---
GAMEDIR="/$directory/MUOS/application/Youtube/youtube"

# --- 4. Move into the directory ---
cd "$GAMEDIR"

> "$GAMEDIR/log.txt" && exec > >(tee "$GAMEDIR/log.txt") 2>&1

# [TEXT FIX] Force system to look for fonts in the game folder
export XDG_DATA_DIRS="$GAMEDIR:$controlfolder:$XDG_DATA_DIRS"

# Terminal settings
$ESUDO chmod 666 /dev/tty0
export TERM=linux
printf "\033c" > /dev/tty0

# Logging
echo "Starting YouTube..."
echo "PortMaster found at: $controlfolder"
echo "Running in directory: $(pwd)"

# YouTube uygulamasını başlat
$ESUDO python3 youtube.py

# Cleanup
printf "\033c" > /dev/tty0
