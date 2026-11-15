"""Find in which dump/plane a ROM word map (screen table) or object tiles appear."""
import glob, os, re, sys, struct
from vram import mapent
import screens
D = screens.D
DUMPS = sorted(glob.glob('o_*/v*.bin'))
_cache = {}
def dump(f):
    if f not in _cache: _cache[f] = open(f, 'rb').read()
    return _cache[f]
def find_screen(rec):
    m, t, w, h, n, fl = screens.rec(rec)
    ents = [struct.unpack_from('<H', D, m+i*2)[0] for i in range(w*h)]
    # pick a distinctive row
    best = []
    for f in DUMPS:
        v = dump(f)
        for k in ('p1', 'p2'):
            ok = 0; base = None
            for i in range(0, w*h, 7):
                e = ents[i]; r, c = divmod(i, w)
                if c >= 32 or r >= 32: continue
                ve = mapent(v, k, r*32+c)
                b = ve - e
                if base is None: base = b
                if b == base: ok += 1
            tot = len(range(0, w*h, 7))
            if ok > tot*0.9: best.append((f, k, base))
    return best
def find_tiles(t0, n):
    """dumps whose VRAM contains tile t0..t0+n raw -> (dump, vram tile index of first)"""
    out = []
    pat = D[t0:t0+16*min(n, 4)]
    for f in DUMPS:
        v = dump(f); i = v.find(pat, 0x2000)
        if i >= 0 and (i-0x2000) % 16 == 0: out.append((f, (i-0x2000)//16))
    return out
if __name__ == "__main__":
    for a in sys.argv[1:]:
        a = int(a, 16)
        if 0x1C0000 <= a < 0x1C0500: r = find_screen(a); print(hex(a), len(r), r[:4])
        else: print(hex(a), find_tiles(a, 4)[:5])
