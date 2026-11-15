"""One horizontal strip per run: python strip.py <name> ... -> out/<name>/strip.png"""
import sys, glob, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
for name in sys.argv[1:]:
    d = os.path.join(here, "out", name)
    ps = sorted(glob.glob(d + "/0*.png"))
    if not ps: print("no shots", name); continue
    ims = [Image.open(p).convert("RGB") for p in ps]; w, h = ims[0].size
    S = Image.new("RGB", (w * len(ims), h))
    for i, im in enumerate(ims): S.paste(im, (i * w, 0))
    S.save(d + "/strip.png")
