#!/bin/bash
# usage: ST_SEQ=.. ST_CODE=0x3f5000 bash run.sh <name> <rom> [keep]   (keep = reuse the nvram of a previous run of the same name)
: "${MAME_DIR:?set MAME_DIR to your MAME folder, e.g. export MAME_DIR=/c/mame}"
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
name=$1; rom=$2
d="$HERE/out/$name"; [ "$3" = keep ] || rm -rf "$d"; mkdir -p "$d/mame"; rm -f "$d"/*.png
export ST_OUT="$(cygpath -w "$d")"
cd "$d/mame" && "$MAME_DIR/mame.exe" ngpc -cart "$(cygpath -w "$rom")" -rompath "$(cygpath -w "$MAME_DIR/roms")" -autoboot_script "$(cygpath -w "$HERE/t.lua")" \
 -nothrottle -sound none -skip_gameinfo -window -nomaximize -snapshot_directory "$ST_OUT" -snapname '%i' -cfg_directory cfg -nvram_directory nvram >/dev/null 2>&1
cat "$d/log.txt"
