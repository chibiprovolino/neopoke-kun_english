# render NGP 2bpp tiles: each tile 16 bytes, row = 2 bytes little-endian word, pixel 0 is leftmost in high bits
import sys
from PIL import Image
d=open(sys.argv[1],"rb").read()
start=int(sys.argv[2],16); n=int(sys.argv[3]); out=sys.argv[4]; cols=int(sys.argv[5]) if len(sys.argv)>5 else 32
img=Image.new("L",(cols*8,((n+cols-1)//cols)*8))
pal=[255,170,85,0]
for t in range(n):
    b=d[start+t*16:start+t*16+16]
    if len(b)<16: break
    for y in range(8):
        w=b[y*2]|(b[y*2+1]<<8)
        for x in range(8):
            v=(w>>(14-2*x))&3
            img.putpixel(((t%cols)*8+x,(t//cols)*8+y),pal[v])
img=img.resize((img.width*int(sys.argv[6]),img.height*int(sys.argv[6]))) if len(sys.argv)>6 else img
img.save(out)
