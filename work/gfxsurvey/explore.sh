# explore.sh name "seq lua table body" start step count  -> dumps + sheet name.png
N=$1; SEQ=$2; S=$3; ST=$4; C=$5
D=""; for i in $(seq 0 $((C-1))); do D="$D$((S+i*ST)),"; done
cat > x_$N.lua <<EOL
seq={{2300,"Button A"},{2600,"Button B"},$SEQ}
dumps={$D}
stop=$((S+C*ST))
poke={{2250,function(sp) for a=0x4500,0x4557 do sp:write_u8(a,0xff) end end}}
${EXTRA}
EOL
bash run.sh ../../rom/original.ngc x_$N.lua o_$N >/dev/null 2>&1
python - "$N" <<'EOP'
import sys,glob,re
from vram import render
from PIL import Image, ImageDraw
n=sys.argv[1]; fs=sorted(glob.glob('o_%s/v*.bin'%n),key=lambda f:int(re.findall(r'v(\d+)',f)[0]))
ims=[render(open(f,'rb').read()) for f in fs]
cols=6; rows=(len(ims)+cols-1)//cols
s=Image.new('RGB',(cols*324,rows*318),(255,0,255)); d=ImageDraw.Draw(s)
for i,(f,im) in enumerate(zip(fs,ims)):
    x,y=(i%cols)*324,(i//cols)*318; s.paste(im.resize((320,304),0),(x,y+12)); d.text((x,y),f.split('v')[-1][:-4],fill=(0,0,0))
s.save('sh_%s.png'%n); print(len(ims))
EOP
