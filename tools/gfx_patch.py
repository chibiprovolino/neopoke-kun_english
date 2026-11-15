"""Graphics-text patches (things drawn as tiles, not by the script routine). See script/graphics_text.md.
apply(d) edits the ROM bytearray in place; called from tools/insert.py just before vwf.apply(d).
All edits are in place (same size), so no free space is used.
The English wording below is a DRAFT for the human to approve: change the strings in DRAFT and rebuild."""
import json, os

DRAFT = {
    # title logo, line 1 (orig. ガンバレ = "Go for it!") and line 2 (orig. ねおぽけくん(仮))
    "title_top": "GANBARE!",
    "title_main": "NEOPOKE-KUN",
    "title_tag": "(TEMP)",          # orig. (仮) "provisional"; drawn small after/under the main line
    "menu_icon": "SOON",            # orig. 予定地 "planned site" on the purple minigame menu icons
}

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = json.load(open(os.path.join(HERE, "..", "font", "cfc2_vwf.json")))["glyphs"]

# --- ROM locations (file offsets) ---
LOGO_TILES = 0xF99E2   # 2bpp tiles, loaded to VRAM tile 0x100+n; n=0x3A is the blank tile
LOGO_MAP = 0xDE1B2     # 18x5 bytes (header "12 05" at 0xDE1B0), each byte = tile n
LOGO_W, LOGO_H = 18, 5
LOGO_MAXT = 0x3A       # tiles 0x00-0x39 usable, 0x3A must stay blank
ICON_TILES = 0x11F1F0  # 4x4 tiles of the menu "予定地" icon; text is in tiles 12-15, pixel rows 1-7


def text_pixels(s, scale=1):
    """-> (width, rows) bitmap of s in the CFC2 font, 7 px tall * scale."""
    cols = []
    for ch in s:
        g = FONT.get(ch) or FONT[" "]
        for x in range(g["w"]):
            cols.append([g["rows"][y][x] == "#" for y in range(7)])
    w = len(cols)
    bm = [[cols[x // scale][y // scale] for x in range(w * scale)] for y in range(7 * scale)]
    return w * scale, bm


def tile_bytes(px, tx, ty):
    out = bytearray()
    for y in range(8):
        w = 0
        for x in range(8):
            w |= (px[ty * 8 + y][tx * 8 + x] & 3) << (14 - 2 * x)
        out += bytes([w & 255, w >> 8])
    return bytes(out)


def stamp(px, bm, ox, oy, fill, outline=None):
    h = len(bm); w = len(bm[0]) if h else 0
    H = len(px); W = len(px[0])
    if outline is not None:
        for y in range(h):
            for x in range(w):
                if bm[y][x]:
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            X, Y = ox + x + dx, oy + y + dy
                            if 0 <= X < W and 0 <= Y < H and px[Y][X] == 0:
                                px[Y][X] = outline
    for y in range(h):
        for x in range(w):
            if bm[y][x] and 0 <= ox + x < W and 0 <= oy + y < H:
                px[oy + y][ox + x] = fill


# --- hand-drawn art: if gfx/<name>.png exists (4-colour indexed PNG, made by tools/gfx_export.py), it replaces the draft ---
ART = os.path.join(HERE, "..", "gfx")


def load_art(name, w, h):
    f = os.path.join(ART, name + ".png")
    if not os.path.exists(f):
        return None
    from PIL import Image
    im = Image.open(f)
    if im.mode != "P" or im.size != (w, h):
        raise SystemExit(f"gfx_patch: {f} must be a {w}x{h} indexed PNG (keep the template's 4-colour palette)")
    px = [[im.getpixel((x, y)) for x in range(w)] for y in range(h)]
    if max(max(r) for r in px) > 3:
        raise SystemExit(f"gfx_patch: {f} uses colours beyond the first 4 palette entries")
    return px


def build_logo():
    W, H = LOGO_W * 8, LOGO_H * 8
    art = load_art("title_logo", W, H)
    px = art or [[0] * W for _ in range(H)]
    if art:
        return cut_logo(px)
    # colours as in the original: 1 = outline, 2 = line-1 fill, 3 = main fill
    tw, tb = text_pixels(DRAFT["title_top"], 2)
    stamp(px, tb, 2, 1, 2, 1)
    mw, mb = text_pixels(DRAFT["title_main"], 2)
    mx = max(1, (W - mw) // 2)
    stamp(px, mb, mx, 17, 3, 1)
    gw, gb = text_pixels(DRAFT["title_tag"], 1)
    stamp(px, gb, W - gw - 2, 33, 3, 1)
    return cut_logo(px)


def cut_logo(px):
    # cut into tiles, dedupe
    blank = bytes(16)
    tiles, idx, tmap = [], {}, []
    for ty in range(LOGO_H):
        for tx in range(LOGO_W):
            b = tile_bytes(px, tx, ty)
            if b == blank:
                tmap.append(LOGO_MAXT); continue
            if b not in idx:
                idx[b] = len(tiles); tiles.append(b)
            tmap.append(idx[b])
    if len(tiles) > LOGO_MAXT:
        raise SystemExit(f"gfx_patch: title logo needs {len(tiles)} tiles, only {LOGO_MAXT} available")
    return tiles, tmap


def patch_logo(d):
    tiles, tmap = build_logo()
    for n in range(LOGO_MAXT):
        d[LOGO_TILES + n * 16:LOGO_TILES + n * 16 + 16] = tiles[n] if n < len(tiles) else bytes(16)
    d[LOGO_MAP:LOGO_MAP + LOGO_W * LOGO_H] = bytes(tmap)
    return len(tiles)


def patch_icon(d):
    # read the 32x8 bottom tile row, keep pixel row 0 (grass dots), redraw rows 1-7
    px = [[0] * 32 for _ in range(8)]
    for t in range(4):
        o = ICON_TILES + (12 + t) * 16
        for y in range(8):
            w = d[o + y * 2] | d[o + y * 2 + 1] << 8
            for x in range(8):
                px[y][t * 8 + x] = (w >> (14 - 2 * x)) & 3
    art = load_art("menu_icon_text", 32, 7)
    if art:
        px[1:8] = art
    else:
        for y in range(1, 8):
            px[y] = [0] * 32
        w, bm = text_pixels(DRAFT["menu_icon"], 1)
        if w > 32:
            raise SystemExit("gfx_patch: menu icon text wider than 32 px")
        stamp(px, bm, (32 - w) // 2, 1, 3)
    for t in range(4):
        o = ICON_TILES + (12 + t) * 16
        d[o:o + 16] = tile_bytes(px, t, 0)


EXIT_TILES = (0x1E0BE0, 0x1E0BF0)   # menu EXIT button: kanji 退 above the word EXIT (VRAM tiles 0x16, 0x17)
EXIT_BOTTOM = (0x1E0C80, 0x1E0C90)  # row 0 of these holds the kanji's last stroke; rows 2-7 are "EXIT"
# DRAFT replacement for 退: a back arrow (12x7, index 3 on the button's index-2 background)
EXIT_ARROW = ["...#........",
              "..##........",
              ".###########",
              "############",
              ".###########",
              "..##........",
              "...#........"]


EXIT_COPIES = (0, 0x1E3843 - 0x1E0BE0)  # the same tiles also sit (unaligned) at 0x1E3843; patch both


def patch_exit(d):
    for k in EXIT_COPIES:
        _patch_exit(d, k)


def _patch_exit(d, k):
    def rd(o):
        return [[((d[o+y*2] | d[o+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]
    L, R = rd(EXIT_TILES[0] + k), rd(EXIT_TILES[1] + k)
    BL, BR = rd(EXIT_BOTTOM[0] + k), rd(EXIT_BOTTOM[1] + k)
    for y in range(8):
        for x in range(8):
            L[y][x] = 2
        for x in range(6):
            R[y][x] = 2
    BL[0] = [1] + [3] * 7; BR[0] = [3] * 7 + [1]      # keep the button's bottom edge, drop the stroke
    art = load_art("exit_icon", 16, 8)
    if art:
        for y in range(8):
            L[y] = art[y][:8]; R[y] = art[y][8:14] + R[y][6:]
        rows = []
    else:
        rows = EXIT_ARROW
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c == "#":
                (L if x + 1 < 8 else R)[y][(x + 1) % 8] = 3
    for o, px in zip(EXIT_TILES + EXIT_BOTTOM, (L, R, BL, BR)):
        o += k
        d[o:o+16] = tile_bytes(px, 0, 0)


# Plain tile strips, only replaced when you supply gfx/<name>.png (no text draft): name -> (first tile offset, width in tiles)
STRIPS = {
    "profile_date_label": (0x1E1430, 9),  # profile screen, row under the photo: "DATE/" + メッセージ (pixel rows 0-5)
    "profile_kore": (0x1E1260, 3),        # profile screen, これ ("this") beside the arrow at the top right
}


def patch_strips(d):
    done = []
    for name, (o, n) in STRIPS.items():
        art = load_art(name, n * 8, 8)
        if not art:
            continue
        for t in range(n):
            d[o + t * 16:o + t * 16 + 16] = tile_bytes(art, t, 0)
        done.append(name)
    return done


def apply(d):
    n = patch_logo(d)
    patch_icon(d)
    # patch_exit(d) is off: the "kanji" above EXIT is really a pictogram of a man leaving through a door; the user keeps it as is.
    strips = patch_strips(d)
    print(f"gfx_patch: title logo {n}/{LOGO_MAXT} tiles, menu icon text redrawn, strips from PNG: {strips or 'none'}")
