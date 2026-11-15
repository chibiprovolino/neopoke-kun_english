"""python sweep.py start end parity [cols] [rows_px] [scale] -> sweep_<start>_<p>.png sheets; each column = rows_px*2 bytes of consecutive 2bpp rows"""
import sys
from PIL import Image, ImageDraw
D = open('../../rom/original.ngc', 'rb').read()
s, e, par = int(sys.argv[1], 16), int(sys.argv[2], 16), int(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 128
H = int(sys.argv[5]) if len(sys.argv) > 5 else 512
sc = int(sys.argv[6]) if len(sys.argv) > 6 else 1
per = cols*H*2
o = s + par
while o < e:
    im = Image.new('L', (cols*9, H+10), 128); d = ImageDraw.Draw(im)
    for c in range(cols):
        base = o + c*H*2
        if c % 16 == 0: d.text((c*9, H), '%x' % base, fill=255)
        for y in range(H):
            p = base + y*2
            if p+1 >= len(D): break
            w = D[p] | D[p+1] << 8
            for x in range(8): im.putpixel((c*9+x, y), [0, 90, 170, 255][(w >> (14-2*x)) & 3])
    if sc > 1: im = im.resize((im.width*sc, im.height*sc), Image.NEAREST)
    im.save('sw_%06x_%d.png' % (o-par, par)); print('sw_%06x_%d.png' % (o-par, par))
    o += per
