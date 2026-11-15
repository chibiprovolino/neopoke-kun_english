import glob, os, re
from collections import defaultdict
from vram import mapent, sprites, render
from PIL import Image, ImageDraw
ROM = open('../../rom/original.ngc', 'rb').read()
cnt = defaultdict(int); best = {}
for f in glob.glob('o_*/v*.bin'):
    run = os.path.basename(os.path.dirname(f))
    if run.startswith('o_t_'): continue
    v = open(f, 'rb').read(); nf = set()
    cells = [(k, i) for k in ('p1', 'p2') for i in range(1024)]
    for k, i in cells:
        t = mapent(v, k, i) & 0x1ff; b = bytes(v[0x2000+t*16:0x2010+t*16])
        if len(set(b)) > 3 and ROM.find(b) < 0: nf.add(t)
    for s in sprites(v):
        if s[7]:
            b = bytes(v[0x2000+s[1]*16:0x2010+s[1]*16])
            if len(set(b)) > 3 and ROM.find(b) < 0: nf.add(s[1])
    if len(nf) > cnt[run]: cnt[run] = len(nf); best[run] = (f, nf)
# mark not-found tiles in red on the best frame of each run
outs = []
for run in sorted(best, key=lambda r: -cnt[r])[:12]:
    f, nf = best[run]; v = open(f, 'rb').read()
    im = render(v).convert('RGB'); d = ImageDraw.Draw(im)
    s1 = (v[0x32], v[0x33]); s2 = (v[0x34], v[0x35])
    for k, sc in (('p1', s1), ('p2', s2)):
        for i in range(1024):
            if (mapent(v, k, i) & 0x1ff) in nf:
                x = ((i % 32)*8 - sc[0]) % 256; y = ((i//32)*8 - sc[1]) % 256
                if x < 160 and y < 152: d.rectangle([x, y, x+7, y+7], outline=(255, 0, 0))
    outs.append((run, cnt[run], im))
S = Image.new('RGB', (6*164, 2*170), (0, 0, 0)); dd = ImageDraw.Draw(S)
for k, (r, c, im) in enumerate(outs):
    x, y = (k % 6)*164, (k//6)*170; S.paste(im, (x, y+14)); dd.text((x, y), '%s %d' % (r, c), fill=(255, 255, 0))
S.resize((S.width*2, S.height*2), Image.NEAREST).save('notfound.png')
print(sorted(cnt.items(), key=lambda x: -x[1])[:20])
