import sys
from PIL import Image,ImageDraw
d=open(sys.argv[1],"rb").read()
base=int(sys.argv[2],16); n=int(sys.argv[3]); out=sys.argv[4]; S=3; C=16; cw=8*S+6; ch=16*S+14
img=Image.new("RGB",(34+C*cw,20+((n+C-1)//C)*ch),(200,220,255)); dr=ImageDraw.Draw(img)
def tile(t,ox,oy):
    b=d[base+t*16:base+t*16+16]
    for y in range(8):
        w=b[2*y]|b[2*y+1]<<8
        for x in range(8):
            v=[255,170,85,0][(w>>(14-2*x))&3]
            dr.rectangle([ox+x*S,oy+y*S,ox+x*S+S-1,oy+y*S+S-1],fill=(v,v,v))
for k in range(n):
    r,c=divmod(k,C); ox=34+c*cw; oy=20+r*ch
    if c==0: dr.text((2,oy+16),"%02X"%(k),fill=(255,0,0))
    if r==0: dr.text((ox+8,4),"%X"%c,fill=(255,0,0))
    t=(k//32)*64+k%32
    tile(t,ox,oy); tile(t+32,ox,oy+8*S)
img.save(out)
