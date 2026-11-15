"""VRAM dump (0x8000-0xBFFF) helpers for the graphics-text survey."""
import sys
from PIL import Image
PALBASE = {'spr': 0x200, 'p1': 0x280, 'p2': 0x300}
MAPBASE = {'p1': 0x1000, 'p2': 0x1800}
def rgb(w): return ((w & 15) * 17, ((w >> 4) & 15) * 17, ((w >> 8) & 15) * 17)
def palw(v, kind, p): b = PALBASE[kind] + p * 8; return [v[b+c*2] | v[b+c*2+1] << 8 for c in range(4)]
def tile(v, t):
    o = 0x2000 + t * 16
    return [[((v[o+y*2] | v[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
def tbytes(v, t): return bytes(v[0x2000+t*16:0x2010+t*16])
def mapent(v, kind, i): o = MAPBASE[kind] + i*2; return v[o] | v[o+1] << 8
def plane(v, kind):
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    for i in range(1024):
        e = mapent(v, kind, i); t = e & 0x1ff; p = (e >> 9) & 15
        pal = [rgb(w) for w in palw(v, kind, p)]; tl = tile(v, t)
        for y in range(8):
            for x in range(8):
                c = tl[7-y if e & 0x4000 else y][7-x if e & 0x8000 else x]
                if c: img.putpixel(((i % 32)*8+x, (i//32)*8+y), pal[c]+(255,))
    return img
def sprites(v):
    """-> list of (k, tile, x, y, pal, hflip, vflip, prio) with chaining resolved."""
    out = []; px = py = 0
    for k in range(64):
        o = 0x800 + k*4; b1 = v[o+1]; t = v[o] | (b1 & 1) << 8
        x, y = v[o+2], v[o+3]
        if b1 & 4: x = (px + x) & 255
        if b1 & 2: y = (py + y) & 255
        px, py = x, y
        out.append((k, t, x, y, v[0xC00+k] & 15, bool(b1 & 0x80), bool(b1 & 0x40), (b1 >> 3) & 3))
    return out
def render(v, full=False):
    import PIL.ImageChops as C
    out = Image.new("RGBA", (256, 256), rgb(v[0x3e0] | v[0x3e1] << 8) + (255,))
    s1 = (v[0x32], v[0x33]); s2 = (v[0x34], v[0x35])
    p1 = C.offset(plane(v, 'p1'), -s1[0], -s1[1]); p2 = C.offset(plane(v, 'p2'), -s2[0], -s2[1])
    a, b = (p1, p2) if v[0x30] & 0x80 else (p2, p1)
    out.alpha_composite(a); out.alpha_composite(b)
    for k, t, x, y, p, hf, vf, pr in sprites(v):
        if not pr: continue
        pal = [rgb(w) for w in palw(v, 'spr', p)]; tl = tile(v, t)
        for yy in range(8):
            for xx in range(8):
                c = tl[7-yy if vf else yy][7-xx if hf else xx]
                if c: out.putpixel(((x+xx) & 255, (y+yy) & 255), pal[c]+(255,))
    return out if full else out.crop((0, 0, 160, 152))
if __name__ == "__main__":
    v = open(sys.argv[1], "rb").read()
    r = render(v); r.resize((r.width*3, r.height*3), Image.NEAREST).save(sys.argv[2])
