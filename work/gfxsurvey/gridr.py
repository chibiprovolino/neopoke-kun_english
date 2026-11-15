import sys, glob
from PIL import Image, ImageDraw
def grid(path, out, sc=2, crop=None):
    im = Image.open(path).convert('RGB')  # already 2x (16 px per tile)
    if crop: im = im.crop(crop)
    im = im.resize((im.width*sc//2*2//2, im.height*sc//2*2//2)) if False else im
    d = ImageDraw.Draw(im); T = 16
    for x in range(0, im.width, T): d.line([(x, 0), (x, im.height)], fill=(255, 0, 0) if (x//T) % 5 == 0 else (90, 0, 0))
    for y in range(0, im.height, T): d.line([(0, y), (im.width, y)], fill=(255, 0, 0) if (y//T) % 5 == 0 else (90, 0, 0))
    big = im.resize((im.width*2, im.height*2), Image.NEAREST); d = ImageDraw.Draw(big)
    for c in range(0, im.width//T, 5): d.text((c*T*2+2, 2), str(c), fill=(255, 255, 0))
    for r in range(0, im.height//T, 5): d.text((2, r*T*2+2), str(r), fill=(0, 255, 255))
    big.save(out)
names = sys.argv[1:]
for n in names:
    f = glob.glob('screens/%s_*' % n)[0]; grid(f, 'grid_%s.png' % n)
