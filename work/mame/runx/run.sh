# usage: run.sh rom outdir
: "${MAME_DIR:?set MAME_DIR to your MAME folder, e.g. export MAME_DIR=/c/mame}"
H=$(pwd); R=$(cygpath -w "$1"); rm -rf "$2" nvram; cd "$MAME_DIR" && ./mame.exe ngpc -cart "$R" -nothrottle -video none -sound none -skip_gameinfo -noartwork_crop -artpath x -snapshot_directory "$(cygpath -w $H/$2)" -cfg_directory "$(cygpath -w $H/cfg)" -nvram_directory "$(cygpath -w $H/nvram)" -autoboot_script "$(cygpath -w $H/inp.lua)" >/dev/null 2>&1
cd "$H"; python -c "
from PIL import Image;import glob,sys
fs=sorted(glob.glob('$2/**/*.png',recursive=True));im=[Image.open(f).convert('RGB') for f in fs]
w,h=im[0].size;o=Image.new('RGB',(w*len(im),h))
for i,x in enumerate(im):o.paste(x,(i*w,0))
o.resize((o.width*3,h*3),0).save('$2.png')"
