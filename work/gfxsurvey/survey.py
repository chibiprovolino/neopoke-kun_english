"""python survey.py dump.bin -> tile->ROM blocks and plane maps"""
import sys, re
from vram import *
ROM = open('../../rom/original.ngc', 'rb').read()
def find_all(b, lim=4):
    r = []; i = ROM.find(b)
    while i >= 0 and len(r) < lim: r.append(i); i = ROM.find(b, i+1)
    return r
def blocks(v, used):
    res = {}
    for t in sorted(used):
        b = tbytes(v, t)
        if b == bytes(16): continue
        res[t] = find_all(b)
    # group runs
    out = []; cur = None
    for t in sorted(res):
        offs = res[t]
        if cur and t == cur[1]+1 and any(o == cur[3]+16 for o in offs):
            cur[1] = t; cur[3] += 16
        else:
            if cur: out.append(cur)
            cur = [t, t, offs[0] if offs else None, offs[0] if offs else None, len(offs)]
            if not offs: cur = [t, t, None, None, 0]
        if cur[2] is None: out.append(cur); cur = None
    if cur: out.append(cur)
    return out
if __name__ == "__main__":
    v = open(sys.argv[1], 'rb').read()
    used = {}
    for k in ('p1', 'p2'):
        print(k, 'scroll', v[0x32+(k=='p2')*2:0x34+(k=='p2')*2].hex())
        for r in range(32):
            row = [mapent(v, k, r*32+c) for c in range(32)]
            for e in row: used.setdefault(e & 0x1ff, set()).add(k+':%d' % ((e>>9)&15))
            if any(e & 0x1ff for e in row): print('%2d ' % r + ' '.join('%04x' % e if e & 0x1ff else '....' for e in row))
    for s in sprites(v):
        if s[7]: used.setdefault(s[1], set()).add('spr:%d' % s[4])
    print('palettes')
    for kind in ('spr', 'p1', 'p2'):
        print(kind, ' '.join('%d:' % p + ','.join('%03x' % w for w in palw(v, kind, p)) for p in range(16)))
    print('tile blocks (vram first-last -> rom, nmatches)')
    for b in blocks(v, used):
        print('  %03x-%03x  %s  n=%d  %s' % (b[0], b[1], hex(b[2]) if b[2] is not None else 'NOT FOUND', b[4], sorted(used.get(b[0], ()))))
