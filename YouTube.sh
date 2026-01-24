#!/bin/bash

# YouTube App - PortMaster Launch Script

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source $controlfolder/control.txt

export LD_LIBRARY_PATH="$controlfolder/libs:$controlfolder/utils/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$controlfolder/exlibs:$controlfolder/pylibs:$controlfolder/libs:$PYTHONPATH"
export PYSDL2_DLL_PATH="$controlfolder/libs"

# yt-dlp için PATH ekle (pip install ile kurulan)
export PATH="$HOME/.local/bin:/home/ark/.local/bin:$PATH"

# YouTube App dizini
GAMEDIR="/roms/ports/youtube"

cd $GAMEDIR

# Terminal ayarları
$ESUDO chmod 666 /dev/tty0
export TERM=linux
printf "\033c" > /dev/tty0

# YouTube uygulamasını başlat
$ESUDO python3 youtube.py > "$GAMEDIR/log.txt" 2>&1

# Temizlik
printf "\033c" > /dev/tty0
