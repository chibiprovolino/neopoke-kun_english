import sys
from PIL import Image,ImageDraw
d=open(sys.argv[1],"rb").read()
start=int(sys.argv[2],16); n=int(sys.argv[3]); out=sys.argv[4]; S=4; C=int(sys.argv[5]) if len(sys.argv)>5 else 16; cell=8*S+4
img=Image.new("RGB",(30+C*cell,20+((n+C-1)//C)*cell),(200,220,255))
dr=ImageDraw.Draw(img)
for c in range(C): dr.text((30+c*cell+10,4),"%X"%c,fill=(255,0,0))
for t in range(n):
    r,c=divmod(t,C)
    if c==0: dr.text((2,20+r*cell+10),"%03X"%(r*C),fill=(255,0,0))
    b=d[start+t*16:start+t*16+16]
    for y in range(8):
        w=b[2*y]|b[2*y+1]<<8
        for x in range(8):
            v=[255,170,85,0][(w>>(14-2*x))&3]
            dr.rectangle([30+c*cell+x*S,20+r*cell+y*S,30+c*cell+x*S+S-1,20+r*cell+y*S+S-1],fill=(v,v,v))
img.save(out)
