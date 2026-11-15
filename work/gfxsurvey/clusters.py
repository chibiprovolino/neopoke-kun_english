import glob, json, os
from collections import defaultdict
from vram import mapent, sprites
ROM = open('../../rom/original.ngc', 'rb').read()
per = defaultdict(set)
for f in glob.glob('o_*/v*.bin'):
    run = os.path.basename(os.path.dirname(f)); v = open(f, 'rb').read()
    used = set()
    for k in ('p1', 'p2'):
        for i in range(1024): used.add(mapent(v, k, i) & 0x1ff)
    for s in sprites(v):
        if s[7]: used.add(s[1])
    for t in used:
        b = bytes(v[0x2000+t*16:0x2010+t*16])
        if len(set(b)) <= 3: continue
        per[run].add(b)
cache = {}
def loc(b):
    if b not in cache:
        i = ROM.find(b); j = ROM.find(b, i+1) if i >= 0 else -1
        cache[b] = i if i >= 0 and j < 0 else None
    return cache[b]
allcl = {}
for run in sorted(per):
    offs = sorted(o for o in (loc(b) for b in per[run]) if o is not None and o >= 0xC4100)
    cl = []
    for o in offs:
        if cl and o - cl[-1][1] < 0x400: cl[-1][1] = o+16; cl[-1][2] += 1
        else: cl.append([o, o+16, 1])
    cl = [c for c in cl if c[2] >= 3]
    allcl[run] = cl
    print(run, ' '.join('%06x-%06x(%d)' % tuple(c) for c in cl))
json.dump(allcl, open('clusters.json', 'w'))
