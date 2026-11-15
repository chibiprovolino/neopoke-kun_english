"""Render every record of the screen table at 0x1C0000 (greyscale, palette nibble shown as tint)."""
import struct, os
from PIL import Image, ImageDraw
D = open('../../rom/original.ngc', 'rb').read()
def u16(o): return struct.unpack_from('<H', D, o)[0]
def u32(o): return struct.unpack_from('<I', D, o)[0]
ptrs = []
o = 0x1C0000
while True:
    p = u32(o)
    if not (0x3C0000 <= p < 0x3C0600): break
    ptrs.append(p - 0x200000); o += 4
recs = sorted(set(ptrs))
TINT = [(255,255,255),(255,180,180),(180,255,180),(180,180,255),(255,255,160),(255,160,255),(160,255,255),(255,210,150)]*2
def tile(o):
    return [[((D[o+y*2] | D[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
def rec(r):
    m, t = u32(r) - 0x200000, u32(r+4) - 0x200000
    w, h, n, fl = u16(r+8), u16(r+10), u16(r+12), u16(r+14)
    return m, t, w, h, n, fl
if __name__ == "__main__":
    os.makedirs('screens', exist_ok=True)
    print('pointer list', len(ptrs), 'records', len(recs))
    for i, r in enumerate(recs):
        m, t, w, h, n, fl = rec(r)
        print('%2d rec %06x map %06x tiles %06x %dx%d n=%03x fl=%04x' % (i, r, m, t, w, h, n, fl), 'idx', [k for k, p in enumerate(ptrs) if p == r])
        if not (0 < w <= 256 and 0 < h <= 256 and 0 <= m < len(D) and 0 <= t < len(D)): continue
        img = Image.new('RGB', (w*8, h*8))
        for i2 in range(w*h):
            e = u16(m + i2*2); tn = e & 0x1ff; p = (e >> 9) & 15
            if tn >= n: continue
            tl = tile(t + tn * 16)
            if tl is None: continue
            for y in range(8):
                for x in range(8):
                    c = tl[7-y if e & 0x4000 else y][7-x if e & 0x8000 else x]
                    g = [0, 90, 170, 255][c]; ti = TINT[p]
                    img.putpixel(((i2 % w)*8+x, (i2//w)*8+y), (g*ti[0]//255, g*ti[1]//255, g*ti[2]//255))
        img.resize((w*16, h*16), Image.NEAREST).save('screens/s%02d_%06x.png' % (i, t))
