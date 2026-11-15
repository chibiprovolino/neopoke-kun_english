"""Extract the graphics text from your ROM as editable PNGs: python tools/gfx_extract.py [rom/original.ngc] [name ...] [--force]

Writes gfx/<png> for every item, in the format the build reads back:
  * gfx_patch items (title_logo, menu_icon_text, profile_date_label, profile_kore): 4-colour indexed PNGs.
    Paint with palette entries 0-3 only. tools/gfx_patch.py imports them (and draws draft lettering when a PNG is missing).
  * gfx_import items (every gfx/<name>.json with "cells" and "map"): RGB PNGs using only the colours listed in the
    item's JSON palette. tools/gfx_import.py imports them; unchanged cells keep their original tiles.
Keep each PNG's size. Existing files are kept unless --force is given.
original(d, name) returns (mode, rows): mode "P" -> rows of indices, mode "RGB" -> rows of (r, g, b)."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
GFX = os.path.join(HERE, "..", "gfx")

# gfx_patch items and where their pixels come from (constants mirror tools/gfx_patch.py)
LOGO_TILES, LOGO_MAP, LOGO_W, LOGO_H = 0xF99E2, 0xDE1B2, 18, 5
ICON_TILES = 0x11F1F0
STRIPS = {"profile_date_label": (0x1E1430, 9), "profile_kore": (0x1E1260, 3)}
PATCH_ITEMS = ["title_logo", "menu_icon_text"] + list(STRIPS)


def tile(d, o):
    return [[((d[o + y * 2] | d[o + y * 2 + 1] << 8) >> (14 - 2 * x)) & 3 for x in range(8)] for y in range(8)]


def _patch_item(d, name):
    if name == "title_logo":
        px = [[0] * (LOGO_W * 8) for _ in range(LOGO_H * 8)]
        for i, t in enumerate(d[LOGO_MAP:LOGO_MAP + LOGO_W * LOGO_H]):
            for y, r in enumerate(tile(d, LOGO_TILES + t * 16)):
                px[(i // LOGO_W) * 8 + y][(i % LOGO_W) * 8:(i % LOGO_W) * 8 + 8] = r
        return px
    if name == "menu_icon_text":       # pixel rows 1-7 of tiles 12-15
        return [sum((tile(d, ICON_TILES + (12 + t) * 16)[y] for t in range(4)), []) for y in range(1, 8)]
    o, n = STRIPS[name]
    tiles = [tile(d, o + t * 16) for t in range(n)]
    return [sum((tl[y] for tl in tiles), []) for y in range(8)]


def import_items():
    out = []
    for f in sorted(os.listdir(GFX)):
        if f.endswith(".json"):
            m = json.load(open(os.path.join(GFX, f), encoding="utf-8"))
            if "cells" in m and "map" in m:
                out.append(f[:-5])
    return out


def _import_item(d, name):
    import gfx_import as gi
    meta = json.load(open(os.path.join(GFX, name + ".json"), encoding="utf-8"))
    mp = gi.Map(d, meta)
    T0 = int(meta["tiles"]["rom"], 16)
    r = meta["rect_in_map"]; x0, y0, rw, rh = r["x"], r["y"], r["w"], r["h"]
    idx = meta["palette"]["png_index_map"]
    zero = tuple(idx[0]["rgb"])
    col = {(e["palette"], e["colour"]): tuple(e["rgb"]) for e in idx if e["index"] != 0}
    W, H = meta["size_px"]
    px = [[zero] * W for _ in range(H)]
    for k in range(rw * rh):
        t, p, h, v = mp.get((y0 + k // rw) * mp.w + x0 + k % rw)
        if p is None:
            p = meta["cells"][k][1]
        rows = gi.flip(gi.tile_get(d, T0 + t * 16), h, v)
        cx, cy = (k % rw) * 8, (k // rw) * 8
        for y in range(8):
            for x in range(8):
                c = rows[y][x]
                px[cy + y][cx + x] = zero if c == 0 else col.get((p, c), zero)
    return px


RAW_ITEMS = ["garou_name_terry_hud", "garou_name_andy_hud"]   # tiles loaded by code, no map: cells in tile order


def _raw_item(d, name):
    meta = json.load(open(os.path.join(GFX, name + ".json"), encoding="utf-8"))
    T0, N = int(meta["tiles"]["rom"], 16), meta["tiles"]["count"]
    col = {e["index"]: tuple(e.get("rgb", (255, 0, 255))) for e in meta["palette"]["png_index_map"]}
    W, H = meta["size_px"]
    px = [[col[0]] * W for _ in range(H)]
    for k in range(N):
        cx, cy = (k % (W // 8)) * 8, (k // (W // 8)) * 8
        for y, r in enumerate(tile(d, T0 + k * 16)):
            for x, c in enumerate(r):
                px[cy + y][cx + x] = col[c]
    return px


def items():
    return PATCH_ITEMS + import_items() + RAW_ITEMS


def original(d, name):
    if name in PATCH_ITEMS:
        return "P", _patch_item(d, name)
    if name in RAW_ITEMS:
        return "RGB", _raw_item(d, name)
    return "RGB", _import_item(d, name)


def png_name(name):
    if name in PATCH_ITEMS:
        return name + ".png"
    return json.load(open(os.path.join(GFX, name + ".json"), encoding="utf-8"))["png"]


# display colours for the indexed items (bg, 1, 2, 3); only the indices matter to the build
PAL = {"title_logo": [0, 0, 0, 40, 60, 140, 120, 220, 255, 255, 255, 255],
       "menu_icon_text": [255, 190, 60, 255, 220, 120, 230, 120, 60, 20, 30, 70],
       "profile_date_label": [0, 0, 0, 220, 60, 60, 180, 170, 150, 255, 250, 215],
       "profile_kore": [0, 0, 0, 220, 60, 60, 180, 170, 150, 255, 250, 215]}


def save(d, name, force=False):
    from PIL import Image
    f = os.path.join(GFX, png_name(name))
    if os.path.exists(f) and not force:
        return "kept existing " + f
    mode, px = original(d, name)
    W, H = len(px[0]), len(px)
    if mode == "P":
        im = Image.new("P", (W, H)); im.putpalette(PAL[name] + [0] * (768 - 12))
    else:
        im = Image.new("RGB", (W, H))
    for y in range(H):
        for x in range(W):
            im.putpixel((x, y), px[y][x])
    im.save(f)
    return "wrote " + f


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rom = args[0] if args and args[0].endswith(".ngc") else os.path.join(HERE, "..", "rom", "original.ngc")
    names = [a for a in args if not a.endswith(".ngc")] or items()
    d = open(rom, "rb").read()
    for n in names:
        print(save(d, n, "--force" in sys.argv))
