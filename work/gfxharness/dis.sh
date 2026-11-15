# dis.sh <fileoff hex> <len hex> [rom]
: "${MAME_DIR:?set MAME_DIR to your MAME folder, e.g. export MAME_DIR=/c/mame}"
R=${3:-rom/original.ngc}; S=work/gfx/slice.bin
python -c "import sys;d=open('$R','rb').read();open('$S','wb').write(d[0x$1:0x$1+0x$2])"
P=$(pwd); cd "$MAME_DIR" && ./unidasm.exe -arch tlcs900 -basepc $(printf '%x' $((0x$1+0x200000))) "$(cygpath -w $P/$S)" | cut -c1-70
