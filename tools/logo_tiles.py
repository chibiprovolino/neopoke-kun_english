"""Tile guide for the title logo (144x40 = 18x5 tiles of 8x8; at most 58 different non-empty tiles).

    python tools/logo_tiles.py [logo.png]        (default: gfxdone/title_logo.png)

Writes next to the input:
  title_logo_tiles.png  8x zoom with the tile grid. Each tile shows its number (row-col) and is tinted:
                          grey   = empty (free, doesn't count)
                          green  = repeats another tile exactly (free after the first copy)
                          yellow = differs from another tile by only a few pixels: make them identical to save one
                          orange = very few ink pixels: erase it (or match a neighbour) to save one
  title_logo_grid.png   transparent 8x grid only (1152x320), to put on a layer over an 8x zoom of the logo.
It also prints the count and the cheapest tiles to merge or erase.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

LIMIT, Z, TW, TH = 58, 8, 18, 5
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "gfxdone", "title_logo.png")
out = os.path.dirname(os.path.abspath(src))
im = Image.open(src).convert("RGB")
assert im.size == (TW * 8, TH * 8), f"logo must be {TW*8}x{TH*8}, got {im.size}"
px = im.load()
# background = colour 0: for an indexed file the first palette entry, else the most common colour
raw = Image.open(src)
if raw.mode == "P":
    bg = tuple(raw.getpalette()[:3])
else:
    bg = max(set(im.getdata()), key=list(im.getdata()).count)

tiles = {}
for ty in range(TH):
    for tx in range(TW):
        tiles[(tx, ty)] = tuple(px[tx * 8 + x, ty * 8 + y] for y in range(8) for x in range(8))

empty = {k for k, t in tiles.items() if set(t) == {bg}}
first, dup = {}, set()
for k in sorted(tiles, key=lambda k: (k[1], k[0])):
    if k in empty: continue
    t = tiles[k]
    if t in first: dup.add(k)
    else: first[t] = k
uniq = list(first.values())
need = len(uniq) - LIMIT


def diff(a, b): return sum(1 for p, q in zip(tiles[a], tiles[b]) if p != q)


pairs = sorted((diff(a, b), a, b) for i, a in enumerate(uniq) for b in uniq[i + 1:])
ink = {k: sum(1 for p in tiles[k] if p != bg) for k in uniq}
sparse = sorted((n, k) for k, n in ink.items())

# suggestions: cheapest pixel edits, each tile used once
near, used = [], set()
for d, a, b in pairs:
    if len(near) >= max(need, 0) + 6: break
    if a in used or b in used: continue
    near.append((d, a, b)); used |= {a, b}
few = [(n, k) for n, k in sparse if n <= 6][:max(need, 0) + 6]

name = lambda k: f"r{k[1]+1}c{k[0]+1}"
print(f"{len(uniq)} different non-empty tiles, limit {LIMIT}: " + (f"remove {need}" if need > 0 else "OK"))
print("closest pairs (pixels that differ):", ", ".join(f"{name(a)}~{name(b)} {d}" for d, a, b in near))
print("tiles with least ink:", ", ".join(f"{name(k)} {n}px" for n, k in few))

# --- guide image ---
W, H = TW * 8 * Z, TH * 8 * Z
g = im.resize((W, H), Image.NEAREST).convert("RGBA")
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
yel = {a for _, a, b in near} | {b for _, a, b in near}
ora = {k for _, k in few}
for (tx, ty) in tiles:
    k = (tx, ty); box = [tx * 64, ty * 64, tx * 64 + 63, ty * 64 + 63]
    c = ((128, 128, 128, 90) if k in empty else (0, 200, 0, 90) if k in dup else
         (255, 220, 0, 110) if k in yel else (255, 120, 0, 110) if k in ora else None)
    if c: d.rectangle(box, fill=c)
g = Image.alpha_composite(g, ov)
d = ImageDraw.Draw(g)
try: font = ImageFont.truetype("arial.ttf", 11)
except OSError: font = ImageFont.load_default()
for tx in range(TW + 1): d.line([(tx * 64, 0), (tx * 64, H)], fill=(255, 0, 0, 255))
for ty in range(TH + 1): d.line([(0, ty * 64), (W, ty * 64)], fill=(255, 0, 0, 255))
for (tx, ty) in tiles:
    t = name((tx, ty)); x, y = tx * 64 + 2, ty * 64 + 1
    d.text((x + 1, y + 1), t, fill=(0, 0, 0, 255), font=font); d.text((x, y), t, fill=(255, 64, 64, 255), font=font)
# legend strip
leg = Image.new("RGBA", (W, 56), (30, 30, 30, 255)); ld = ImageDraw.Draw(leg)
items = [((128, 128, 128), "empty"), ((0, 200, 0), "exact repeat"), ((255, 220, 0), "near-duplicate pair"), ((255, 120, 0), "little ink")]
for i, (c, s) in enumerate(items):
    ld.rectangle([8 + i * 200, 8, 24 + i * 200, 24], fill=c); ld.text((30 + i * 200, 10), s, fill="white", font=font)
ld.text((8, 34), f"{len(uniq)} different tiles, limit {LIMIT}" + (f" -> remove {need}" if need > 0 else " -> OK") +
        "   pairs: " + ", ".join(f"{name(a)}~{name(b)} ({dd}px)" for dd, a, b in near[:6]), fill="white", font=font)
full = Image.new("RGBA", (W, H + 56)); full.paste(g, (0, 0)); full.paste(leg, (0, H))
full.save(os.path.join(out, "title_logo_tiles.png"))

grid = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(grid)
for tx in range(TW + 1): gd.line([(min(tx * 64, W - 1), 0), (min(tx * 64, W - 1), H)], fill=(255, 0, 0, 255))
for ty in range(TH + 1): gd.line([(0, min(ty * 64, H - 1)), (W, min(ty * 64, H - 1))], fill=(255, 0, 0, 255))
grid.save(os.path.join(out, "title_logo_grid.png"))
im.resize((W, H), Image.NEAREST).save(os.path.join(out, "title_logo_x8.png"))
print("wrote title_logo_tiles.png, title_logo_grid.png, title_logo_x8.png in", out)
