"""Sprite frames (tables 0xDE8B4-0xF2EC5): [tiles*8 u16][tile ptr u32][x s8][y s8][rows u8][code0]{[code][dx s8]}...
Each row holds (0x50-code)/5 raw 16-byte tiles side by side; dx = horizontal shift relative to the previous row."""
D = open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'rom', 'original.ngc'), 'rb').read()
s8 = lambda v: v-256 if v > 127 else v
def tryparse(o):
    size = D[o] | D[o+1] << 8
    if D[o+5] != 0 or not (0x2f <= D[o+4] <= 0x3a): return None
    p = (D[o+2] | D[o+3] << 8 | D[o+4] << 16)-0x200000; n = D[o+8]
    if not 1 <= n <= 24: return None
    codes = [D[o+9]]+[D[o+10+2*k] for k in range(n-1)]
    if any(c % 5 or not 0x28 <= c <= 0x4b for c in codes): return None
    if sum((0x50-c)//5*8 for c in codes) != size: return None
    return dict(off=o, tiles=p, n=size//8, x=s8(D[o+6]), y=s8(D[o+7]), rows=[(0x50-c)//5 for c in codes],
                dx=[0]+[s8(D[o+11+2*k]) for k in range(n-1)], end=o+8+2*n)
def frames():
    fr = []; o = 0xd0000
    while o < 0xf8000:
        f = tryparse(o)
        if f: fr.append(f); o = f['end']
        else: o += 1
    return fr
def cells(f):
    """-> list of (tile index, px x, px y), x normalised to >= 0"""
    out = []; x = 0; t = 0
    for r, (k, d) in enumerate(zip(f['rows'], f['dx'])):
        x += d
        for u in range(k): out.append((t, x+u*8, r*8)); t += 1
    m = min(c[1] for c in out)
    return [(t, x-m, y) for t, x, y in out]
def tile(o): return [[((D[o+y*2] | D[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
def image(f, shades=(40, 110, 180, 255)):
    from PIL import Image
    cs = cells(f); W = max(c[1] for c in cs)+8; H = max(c[2] for c in cs)+8
    im = Image.new('L', (W, H), 40)
    for t, x, y in cs:
        tl = tile(f['tiles']+t*16)
        for yy in range(8):
            for xx in range(8):
                if tl[yy][xx]: im.putpixel((x+xx, y+yy), shades[tl[yy][xx]])
    return im
if __name__ == '__main__':
    import sys
    from PIL import Image, ImageDraw
    out = sys.argv[1]; fr = frames(); seen = set(); u = []
    for f in fr:
        k = (f['tiles'], tuple(f['rows']), tuple(f['dx']))
        if k not in seen: seen.add(k); u.append(f)
    print(len(fr), 'frames', len(u), 'unique')
    page = 0; i = 0
    while i < len(u):
        Sh = Image.new('RGB', (1300, 1300), (20, 20, 70)); d = ImageDraw.Draw(Sh); x = y = rowh = 0
        while i < len(u):
            im = image(u[i]); im = im.resize((im.width*2, im.height*2), Image.NEAREST)
            w = max(im.width, 38)
            if x+w > 1300: x = 0; y += rowh+14; rowh = 0
            if y+im.height+14 > 1300: break
            d.text((x, y), '%05x' % u[i]['off'], fill=(255, 255, 0)); Sh.paste(im, (x, y+11)); x += w+4; rowh = max(rowh, im.height); i += 1
        Sh.save('%s/spr%02d.png' % (out, page)); page += 1
    print(page, 'pages')

def rect_frames(lo=0xd0000, hi=0xf8000):
    """format A: [tile ptr u32][x s8][y s8][w][h][tiles*8 u16] (w*h tiles in reading order)
       format B: [x s8][y s8][w][h][tiles*8 u16][tile ptr u32][w*h bytes: tile index per cell]"""
    out = []; o = lo
    while o < hi:
        if D[o+3] == 0 and 0x2f <= D[o+2] <= 0x3a:
            w, h = D[o+6], D[o+7]; size = D[o+8] | D[o+9] << 8
            if 1 <= w <= 20 and 1 <= h <= 19 and size == w*h*8:
                p = (D[o] | D[o+1] << 8 | D[o+2] << 16)-0x200000
                out.append(dict(off=o, fmt='A', tiles=p, n=w*h, w=w, h=h, map=list(range(w*h)))); o += 10; continue
        if D[o+9] == 0 and 0x2f <= D[o+8] <= 0x3a:
            w, h = D[o+2], D[o+3]; size = D[o+4] | D[o+5] << 8
            if 1 <= w <= 20 and 1 <= h <= 19 and size % 8 == 0 and 0 < size <= w*h*8:
                m = list(D[o+10:o+10+w*h])
                if max(m)+1 == size//8 and w*h >= 4:
                    p = (D[o+6] | D[o+7] << 8 | D[o+8] << 16)-0x200000
                    out.append(dict(off=o, fmt='B', tiles=p, n=size//8, w=w, h=h, map=m)); o += 10+w*h; continue
        o += 1
    return out
def rect_image(f, shades=(40, 110, 180, 255)):
    from PIL import Image
    im = Image.new('L', (f['w']*8, f['h']*8), 40)
    for i, t in enumerate(f['map']):
        tl = tile(f['tiles']+t*16)
        for yy in range(8):
            for xx in range(8):
                if tl[yy][xx]: im.putpixel(((i % f['w'])*8+xx, (i//f['w'])*8+yy), shades[tl[yy][xx]])
    return im
