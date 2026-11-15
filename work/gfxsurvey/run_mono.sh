# usage: run.sh <rom> <cfg.lua> <outdir>
: "${MAME_DIR:?set MAME_DIR to your MAME folder, e.g. export MAME_DIR=/c/mame}"
X=1; R=$(cygpath -w "$(realpath $1)"); C=$(cygpath -w "$(realpath $2)"); mkdir -p $3; O=$(cygpath -w "$(realpath $3)")
rm -rf $3; mkdir -p $3
cd "$MAME_DIR" && CFG="$C" OUT="$O" ./mame.exe ngp -cart "$R" -autoboot_script "$(cygpath -w $(realpath $OLDPWD/drv.lua))" -nothrottle -sound none -video none -artpath x -cfg_directory "$O\cfg" -nvram_directory "$O\nvram" -snapshot_directory "$O\snap" -skip_gameinfo -nonvram_save > "$O/log.txt" 2>&1
