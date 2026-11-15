import glob, json, re, os
from collections import defaultdict
from vram import mapent, sprites
import screens, objs
ROM = screens.D
# hash of all 16-byte windows at every offset is big (2M); use dict of tile bytes -> offsets only for needed tiles
need = {}
src = defaultdict(set)
for f in glob.glob('o_*/v*.bin'):
    v = open(f, 'rb').read()
    used = set()
    for k in ('p1', 'p2'):
        for i in range(1024): used.add(mapent(v, k, i) & 0x1ff)
    for s in sprites(v):
        if s[7]: used.add(s[1])
    for t in used:
        b = bytes(v[0x2000+t*16:0x2010+t*16])
        if len(set(b)) <= 2: continue  # skip blank/flat
        need.setdefault(b, set()).add(os.path.basename(os.path.dirname(f)))
print('distinct tiles', len(need))
found = {}
for b in need:
    i = ROM.find(b); offs = []
    while i >= 0 and len(offs) < 3: offs.append(i); i = ROM.find(b, i+1)
    found[b] = offs
ranges = []
for b, offs in found.items():
    if len(offs) == 1: ranges.append((offs[0], offs[0]+16, 'dump:'+','.join(sorted(need[b]))[:40]))
nf = [b for b, o in found.items() if not o]
print('unique-found', len(ranges), 'notfound', len(nf), 'multi', sum(1 for o in found.values() if len(o) > 1))
for r in screens.recs[:59]:
    m, t, w, h, n, fl = screens.rec(r); ranges.append((t, t+n*16, 'screen:%06x' % r))
for o in objs.objs: ranges.append((o['tiles'], o['tiles']+o['n']*16, 'obj:%05x' % o['cmd']))
ranges.sort()
merged = []
for a, b, tag in ranges:
    if merged and a <= merged[-1][1] + 32:
        merged[-1][1] = max(merged[-1][1], b); merged[-1][2].add(tag.split(':')[0])
    else: merged.append([a, b, {tag.split(':')[0]}])
json.dump([[a, b, sorted(t)] for a, b, t in merged], open('ranges.json', 'w'))
tot = sum(b-a for a, b, t in merged); print('merged', len(merged), 'bytes', hex(tot))
for a, b, t in merged: print('%06x-%06x %6x %s' % (a, b, b-a, ','.join(sorted(t))))
