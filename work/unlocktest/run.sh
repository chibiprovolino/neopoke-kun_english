#!/bin/bash
# usage: UT_A=.. UT_B=.. bash run.sh <name> [rom]
: "${MAME_DIR:?set MAME_DIR to your MAME folder, e.g. export MAME_DIR=/c/mame}"
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
name=$1; rom=${2:-$ROOT/rom/original.ngc}
d="$HERE/out/$name"; rm -rf "$d"; mkdir -p "$d/mame"
export UT_OUT="$(cygpath -w "$d")"
cd "$d/mame" && "$MAME_DIR/mame.exe" ngpc -cart "$(cygpath -w "$rom")" -rompath "$(cygpath -w "$MAME_DIR/roms")" -autoboot_script "$(cygpath -w "$HERE/t.lua")" \
 -nothrottle -sound none -skip_gameinfo -window -nomaximize -snapshot_directory "$UT_OUT" -snapname '%i' -cfg_directory cfg -nvram_directory nvram >/dev/null 2>&1
cat "$d/log.txt"
