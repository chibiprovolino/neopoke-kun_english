"""Objects from command lists 0xD2000-0xDD000. Record: [op16][map16][01 00][tiles24][00][n16]; tile block k uses map field of record k+1.
Map formats: [b0 b1 w h] + w*h words (word map, entry = tile | pal<<9 | flips) or + w*h bytes (byte map)."""
import re, struct, os
from PIL import Image, ImageDraw
D = open('../../rom/original.ngc', 'rb').read()
TINT = [(255,255,255),(255,170,170),(170,255,170),(170,170,255),(255,255,150),(255,150,255),(150,255,255),(255,210,140)]*2
def tile(o): return [[((D[o+y*2] | D[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
def u16(o): return struct.unpack_from('<H', D, o)[0]
recs = []
for m in re.finditer(rb'\x01\x00(...)\x00(..)', D, re.S):
    s = m.start()
    if not (0xD2000 <= s < 0xDD000): continue
    a = int.from_bytes(m.group(1), 'little'); n = struct.unpack('<H', m.group(2))[0]
    if not (0x2C0000 <= a < 0x400000 and 0 < n <= 0x200): continue
    recs.append(dict(cmd=s-4, mapf=0xD0000 + u16(s-2), tiles=a-0x200000, n=n))
objs = []
for k, r in enumerate(recs):
    o = dict(r)
    o['map'] = recs[k+1]['mapf'] if k+1 < len(recs) and recs[k+1]['cmd'] - r['cmd'] < 0x20 else None
    objs.append(o)
def decode(o, mp):
    w, h = D[mp+2], D[mp+3]
    if not (0 < w <= 40 and 0 < h <= 40): return None
    words = [u16(mp+4+i*2) for i in range(w*h)]
    bys = list(D[mp+4:mp+4+w*h])
    wbad = sum((e & 0x1ff) >= o['n'] for e in words); bbad = sum(b >= o['n'] for b in bys)
    if wbad <= bbad: return w, h, words, 'word', wbad
    return w, h, bys, 'byte', bbad
def compose(o):
    best = None
    for mp in [o['map'], o['mapf']]:
        if mp is None: continue
        d = decode(o, mp)
        if d and (best is None or d[4] < best[1][4]): best = (mp, d)
    if not best: return None
    mp, (w, h, ents, kind, bad) = best
    o.update(usemap=mp, w=w, h=h, kind=kind, bad=bad)
    img = Image.new('RGB', (w*8, h*8), (40, 0, 40))
    for i, e in enumerate(ents):
        tn = e & 0x1ff; p = (e >> 9) & 15 if kind == 'word' else 0
        if tn >= o['n']: continue
        tl = tile(o['tiles']+tn*16); ti = TINT[p]
        for y in range(8):
            for x in range(8):
                c = tl[7-y if (kind == 'word' and e & 0x4000) else y][7-x if (kind == 'word' and e & 0x8000) else x]
                g = [0, 90, 170, 255][c]
                img.putpixel(((i % w)*8+x, (i//w)*8+y), (g*ti[0]//255, g*ti[1]//255, g*ti[2]//255))
    return img
if __name__ == "__main__":
    out = []
    for o in objs:
        im = compose(o)
        print('cmd %05x tiles %06x n=%3x' % (o['cmd'], o['tiles'], o['n']), ('map %05x %s %dx%d bad=%d' % (o['usemap'], o['kind'], o['w'], o['h'], o['bad'])) if im else 'NOMAP')
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
        S.save('ob2_%02d.png' % page); page += 1
    print(page, 'pages')
