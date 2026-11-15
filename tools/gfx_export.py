"""Write editable templates of the graphics text to gfx/ : python tools/gfx_export.py [--original]
Each PNG is indexed with exactly the 4 colours the game uses (0 = transparent/background). Paint with those
4 colours only, keep the size, save as PNG. tools/insert.py then uses your file instead of the draft.
Default: templates show the current draft; --original shows the Japanese art. *_ref.png = 4x zoom, not used by the build."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gfx_patch as g
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PAL = {"title_logo": [0, 0, 0, 40, 60, 140, 120, 220, 255, 255, 255, 255],   # bg, outline, line-1 fill, main fill
       "menu_icon_text": [255, 190, 60, 255, 220, 120, 230, 120, 60, 20, 30, 70],
       "profile_date_label": [0, 0, 0, 220, 60, 60, 180, 170, 150, 255, 250, 215],  # 3 = paper, 1 = red text
       "profile_kore": [0, 0, 0, 220, 60, 60, 180, 170, 150, 255, 250, 215],        # 2 = grey text, 1 = red arrow
       "exit_icon": [170, 50, 150, 120, 40, 120, 240, 150, 240, 255, 255, 255]}

def rd(d, o):
    return [[((d[o+y*2] | d[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]

def save(name, px):
    h, w = len(px), len(px[0])
    im = Image.new("P", (w, h)); im.putpalette(PAL[name] + [0] * (768 - 12))
    for y in range(h):
        for x in range(w): im.putpixel((x, y), px[y][x])
    os.makedirs(os.path.join(ROOT, "gfx"), exist_ok=True)
    f = os.path.join(ROOT, "gfx", name + ".png")
    if os.path.exists(f) and "--force" not in sys.argv:
        print("kept existing", f, "(use --force to overwrite)")
    else:
        im.save(f); print("wrote", f)
    im.resize((w*4, h*4), Image.NEAREST).save(os.path.join(ROOT, "gfx", name + "_ref.png"))

d = bytearray(open(os.path.join(ROOT, "rom", "original.ngc"), "rb").read())
if "--original" not in sys.argv:
    art = g.ART; g.ART = os.path.join(ROOT, "_none_"); g.apply(d); g.ART = art
logo = [[0]*144 for _ in range(40)]
for i, t in enumerate(d[g.LOGO_MAP:g.LOGO_MAP+90]):
    for y, r in enumerate(rd(d, g.LOGO_TILES + t*16)): logo[(i//18)*8+y][(i%18)*8:(i%18)*8+8] = r
save("title_logo", logo)
icon = [sum((rd(d, g.ICON_TILES + (12+t)*16)[y] for t in range(4)), []) for y in range(1, 8)]
save("menu_icon_text", icon)
o = 0x1E3843
L, R = rd(d, o), rd(d, o + 16)
save("exit_icon", [L[y] + R[y] for y in range(8)])
for name, (o, n) in g.STRIPS.items():
    tiles = [rd(d, o + t * 16) for t in range(n)]
    save(name, [sum((tl[y] for tl in tiles), []) for y in range(8)])
