import re, struct, os
from PIL import Image, ImageDraw
D = open('../../rom/original.ngc', 'rb').read()
def tile(o): return [[((D[o+y*2] | D[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
hits = {}
for m in re.finditer(rb'\x01\x00(...)\x00(..)', D, re.S):
    a = int.from_bytes(m.group(1), 'little'); n = struct.unpack('<H', m.group(2))[0]
    if 0x2C0000 <= a < 0x400000 and 0 < n <= 0x200 and 0xD2000 <= m.start() < 0xDD000:
        hits.setdefault((a-0x200000, n), []).append(m.start())
blocks = sorted(hits)
def strip(a, n, cols=16, sc=2):
    rows = (n+cols-1)//cols
    im = Image.new('L', (cols*9, rows*9), 40)
    for k in range(n):
        tl = tile(a+k*16)
        for y in range(8):
            for x in range(8): im.putpixel(((k % cols)*9+x, (k//cols)*9+y), [0, 100, 180, 255][tl[y][x]])
    return im.resize((im.width*sc, im.height*sc), Image.NEAREST)
if __name__ == "__main__":
    ims = [(a, n, strip(a, n)) for a, n in blocks]
    # pack into sheets ~1300x1300
    sheets = []; cur = []; h = 0
    for a, n, im in ims:
        if h + im.height + 14 > 1400 and cur: sheets.append(cur); cur = []; h = 0
        cur.append((a, n, im)); h += im.height + 14
    sheets.append(cur)
    # two columns per sheet
    allc = [x for s in sheets for x in s]
    page = 0; i = 0
    while i < len(allc):
        S = Image.new('RGB', (2*300, 1400), (60, 0, 60)); d = ImageDraw.Draw(S)
        for col in range(2):
            y = 0
            while i < len(allc) and y + allc[i][2].height + 14 <= 1400:
                a, n, im = allc[i]; d.text((col*300, y), '%06x n=%x' % (a, n), fill=(255, 255, 0)); S.paste(im, (col*300, y+12)); y += im.height+14; i += 1
        S.save('blk%02d.png' % page); page += 1
    print(page, 'pages', len(blocks))
