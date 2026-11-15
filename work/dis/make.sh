#!/bin/bash
# Disassemble the code area of your ROM: bash work/dis/make.sh [rom]   -> work/dis/code.asm
# A linear dump of file 0x000000-0x0BFFFF at CPU 0x200000, so data regions also show up as instructions.
# One slice of any build: bash work/gfxharness/dis.sh <fileoff hex> <len hex> [rom]
: "${MAME_DIR:?set MAME_DIR to your MAME folder (unidasm.exe ships with MAME), e.g. export MAME_DIR=/c/mame}"
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
rom=${1:-$ROOT/rom/original.ngc}
head -c $((0xC0000)) "$rom" > "$HERE/code.bin"
"$MAME_DIR/unidasm.exe" -arch tlcs900 -basepc 200000 "$(cygpath -w "$HERE/code.bin")" > "$HERE/code.asm"
wc -l "$HERE/code.asm"
