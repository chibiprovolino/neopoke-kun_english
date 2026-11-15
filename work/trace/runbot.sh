#!/bin/bash
# usage: BOT_STOP=.. BOT_SEED=.. bash runbot.sh <name> [absolute rom path]
: "${MAME_DIR:?set MAME_DIR to your MAME folder, e.g. export MAME_DIR=/c/mame}"
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
name=$1; rom=${2:-$ROOT/build/proto_fastunlock_jp.ngc}
d="$HERE/out/$name"; rm -rf "$d"; mkdir -p "$d/mame"
export BOT_OUT="$(cygpath -w "$d")"
cd "$d/mame" && "$MAME_DIR/mame.exe" ngpc -cart "$(cygpath -w "$rom")" -rompath "$(cygpath -w "$MAME_DIR/roms")" -autoboot_script "$(cygpath -w "$HERE/bot.lua")" \
 -nothrottle -sound none -video none -skip_gameinfo -cfg_directory cfg -nvram_directory nvram >/dev/null 2>&1
tail -3 "$d/bot.txt"
