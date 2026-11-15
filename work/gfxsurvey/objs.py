"""Compose every object from the command lists at 0xD2000-0xDD000: [op16][map lo16][01 00][tiles 24][00][n16]."""
import re, struct, os
from PIL import Image, ImageDraw
D = open('../../rom/original.ngc', 'rb').read()
TINT = [(255,255,255),(255,170,170),(170,255,170),(170,170,255),(255,255,150),(255,150,255),(150,255,255),(255,210,140)]*2
def tile(o): return [[((D[o+y*2] | D[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
def u16(o): return struct.unpack_from('<H', D, o)[0]
objs = []
for m in re.finditer(rb'\x01\x00(...)\x00(..)', D, re.S):
    s = m.start()
    if not (0xD2000 <= s < 0xDD000): continue
    a = int.from_bytes(m.group(1), 'little'); n = struct.unpack('<H', m.group(2))[0]
    if not (0x2C0000 <= a < 0x400000 and 0 < n <= 0x200): continue
    mp = 0xC0000 + 0x10000 + u16(s-2)
    objs.append(dict(cmd=s-4, op=u16(s-4), map=mp, tiles=a-0x200000, n=n))
def compose(o):
    mp = o['map']; w, h = D[mp+2], D[mp+3]
    if not (0 < w <= 32 and 0 < h <= 32): return None
    img = Image.new('RGB', (w*8, h*8), (40, 0, 40)); bad = 0
    for i in range(w*h):
        e = u16(mp+4+i*2); tn = e & 0x1ff; p = (e >> 9) & 15
        if tn >= o['n']: bad += 1; continue
        tl = tile(o['tiles']+tn*16); ti = TINT[p]
        for y in range(8):
            for x in range(8):
                c = tl[7-y if e & 0x4000 else y][7-x if e & 0x8000 else x]
                g = [0, 90, 170, 255][c]
                img.putpixel(((i % w)*8+x, (i//w)*8+y), (g*ti[0]//255, g*ti[1]//255, g*ti[2]//255))
    o['w'], o['h'], o['bad'] = w, h, bad
    return img
if __name__ == "__main__":
    os.makedirs('objs', exist_ok=True)
    out = []
    for o in objs:
        im = compose(o)
        print('cmd %05x op %04x map %05x tiles %06x n=%3x' % (o['cmd'], o['op'], o['map'], o['tiles'], o['n']), ('%dx%d bad=%d' % (o['w'], o['h'], o['bad'])) if im else 'NOMAP')
        if im: out.append((o, im.resize((im.width*2, im.height*2), Image.NEAREST)))
    page = 0; i = 0
    while i < len(out):
        S = Image.new('RGB', (1300, 1300), (20, 20, 60)); d = ImageDraw.Draw(S)
        x = y = rowh = 0
        while i < len(out):
            o, im = out[i]
            if x + im.width > 1300: x = 0; y += rowh + 14; rowh = 0
            if y + im.height + 14 > 1300: break
            d.text((x, y), '%05x' % o['cmd'], fill=(255, 255, 0)); S.paste(im, (x, y+12))
            x += max(im.width, 40) + 6; rowh = max(rowh, im.height); i += 1
        S.save('obj%02d.png' % page); page += 1
    print(page, 'pages')
