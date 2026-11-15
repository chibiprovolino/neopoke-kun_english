import sys, glob, re
from vram import render
from PIL import Image, ImageDraw
import os; IDX = os.environ.get("IDX", "0,3,6,9,12,16,20,26,32,39").split(","); names = sys.argv[2:]
out = sys.argv[1]
rows = []
for n in names:
    fs = sorted(glob.glob('o_%s/v*.bin' % n), key=lambda f: int(re.findall(r'v(\d+)', f)[0]))
    idx = [int(x) for x in IDX]
    rows.append((n, [fs[i] for i in idx if i < len(fs)]))
S = Image.new('RGB', (len(IDX)*162+40, len(rows)*154), (255, 0, 255)); d = ImageDraw.Draw(S)
for r, (n, fs) in enumerate(rows):
    d.text((0, r*154+60), n, fill=(0, 0, 0))
    for c, f in enumerate(fs): S.paste(render(open(f, 'rb').read()), (40+c*162, r*154))
S.save(out); print(S.size)
