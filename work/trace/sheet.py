"""Contact sheet of a run's snapshots: python sheet.py <name> [scale]"""
import sys, glob, os
from PIL import Image, ImageDraw
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", sys.argv[1])
sc = int(sys.argv[2]) if len(sys.argv) > 2 else 2
fr = [l.split()[0] for l in open(d + "/log.txt") if l.strip().endswith("snap")]
ps = sorted(glob.glob(d + "/0*.png"))
ims = [Image.open(p).convert("RGB") for p in ps]
w, h = ims[0].size; cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
S = Image.new("RGB", (cols * (w * sc + 4), rows * (h * sc + 14)), (40, 40, 40)); D = ImageDraw.Draw(S)
for i, im in enumerate(ims):
    x, y = (i % cols) * (w * sc + 4), (i // cols) * (h * sc + 14)
    S.paste(im.resize((w * sc, h * sc), Image.NEAREST), (x, y + 12)); D.text((x + 2, y), fr[i] if i < len(fr) else "?", fill=(255, 255, 0))
S.save(d + "/sheet.png"); print(d + "/sheet.png", S.size)
