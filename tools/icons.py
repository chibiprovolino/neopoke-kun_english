"""Profile field icons (replace the labels Age/Job/Income/Hobby/Appeal on the dating profiles).

The profile fields are NOT drawn by the VWF routine: they use the game's own proportional renderer
(0x2122c3 -> 0x2124d6), which reads the original 8x8 font at file 0xC2018 (16 bytes per code) and a
width table at file 0x128a2 (one byte per code). Codes >= 0x10 are glyphs there;
tiles 0x11-0x15 are blank with width 0 in the original ROM, so they are free. In drafts: [11]..[15].
The renderer is 1-colour (ink/background from the text object). A colour version (raw 2bpp tile + own
palette per icon tile) was tried and dropped; see ROADMAP "Profile icons".

Art: font/icons.png, 5 cells of 8x8 side by side (40x8, or any whole-number upscale of that).
Dark pixels = ink, light = empty. Draw left-aligned; the advance width is
set to (rightmost ink column + 1) + GAP, so the value starts GAP px after the icon.
python tools/icons.py           -> writes font/icons_template.png (zoomed guide with grid, codes, widths)
python tools/icons.py --init    -> (re)writes font/icons.png from the built-in drawings below"""
import os, struct, sys
FONT = 0xC2018; WIDTHS = 0x128a2
CODES = {"Age": 0x11, "Job": 0x12, "Income": 0x13, "Hobby": 0x14, "Appeal": 0x15}
LABEL = CODES
GAP = 1
PNG = "font/icons.png"
DEFAULT = {  # fallback drawings, used when font/icons.png is missing
    "Age":    ["...#....", "..#.#...", "...#....", ".#####..", "#.#.#.#.", "#######.", "#.....#.", "#######."],
    "Job":    ["..###...", ".#...#..", "#######.", "#..#..#.", "###.###.", "#.....#.", "#######.", "........"],
    "Income": ["#.....#.", ".#...#..", "..#.#...", ".#####..", "...#....", ".#####..", "...#....", "...#...."],
    "Hobby":  ["........", ".##.##..", "#..#..#.", "#.....#.", "#.....#.", ".#...#..", "..#.#...", "...#...."],
    "Appeal": ["...#....", "..#.#...", "###.###.", "#.....#.", ".#...#..", ".#.#.#..", "#.#.#.#.", "##...##."],
}

def load():
    """{label: 8 rows of '#'/'.'} from font/icons.png, else DEFAULT."""
    if not os.path.exists(PNG): return DEFAULT
    from PIL import Image
    im = Image.open(PNG).convert("L")
    s = im.width // 40
    assert s >= 1 and im.width == 40 * s and im.height == 8 * s, f"{PNG} must be 40x8 (or a whole upscale), got {im.size}"
    out = {}
    for i, lab in enumerate(CODES):
        out[lab] = ["".join("#" if im.getpixel(((i * 8 + x) * s + s // 2, y * s + s // 2)) < 128 else "." for x in range(8))
                    for y in range(8)]
    return out

def width(rows):
    cols = [x for r in rows for x, p in enumerate(r) if p == "#"]
    return min(8, max(cols) + 1 + GAP) if cols else 3

def apply(d):
    """Write the icons into the game's own 8x8 font and width table (ROM bytearray d)."""
    for lab, rows in load().items():
        c = CODES[lab]
        for y, r in enumerate(rows):
            v = 0
            for x, p in enumerate(r):
                if p == "#": v |= 3 << (14 - 2 * x)
            struct.pack_into("<H", d, FONT + c * 16 + 2 * y, v)
        d[WIDTHS + c] = width(rows)
    return d

def _draw(icons, path, S, guide):
    from PIL import Image, ImageDraw
    pad = 14 if guide else 0
    im = Image.new("RGB", (40 * S, 8 * S + pad), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    for i, (lab, rows) in enumerate(icons.items()):
        for y, r in enumerate(rows):
            for x, p in enumerate(r):
                x0, y0 = (i * 8 + x) * S, y * S
                if p == "#": dr.rectangle([x0, y0, x0 + S - 1, y0 + S - 1], fill=(0, 0, 0))
                elif guide and x == 7: dr.rectangle([x0, y0, x0 + S - 1, y0 + S - 1], fill=(235, 235, 255))
        if guide:
            for k in range(9):
                dr.line([(i * 8 + k) * S, 0, (i * 8 + k) * S, 8 * S], fill=(200, 200, 200) if 0 < k < 8 else (255, 0, 0))
                dr.line([i * 8 * S, k * S, (i + 1) * 8 * S, k * S], fill=(200, 200, 200))
            dr.text((i * 8 * S + 3, 8 * S + 1), f"{lab} [{CODES[lab]:02X}] w{width(rows)}", fill=(200, 0, 0))
    im.save(path)

if __name__ == "__main__":
    if "--init" in sys.argv: _draw(DEFAULT, PNG, 1, False)
    ic = load()
    _draw(ic, "font/icons_template.png", 16, True)
    for lab, rows in ic.items(): print(f"{lab:7s} [{CODES[lab]:02X}] width {width(rows)}")
