"""CFC2 lettering for the dating-profile stat fields only (age, job, income, hobby, appeal values).

Those fields are drawn by the game's 8x8 proportional renderer (font at file 0xC2018, widths at 0x128a2), which every
other 8x8 text shares. So the game's own glyphs stay where they are and the CFC2 letters go into code slots that are
blank in the original font; the field strings are encoded with those slot codes (tools/icon_drafts.py does that and
stores the char -> code map under "_cfc2" in its output; tools/insert.py passes the map to apply())."""
import json, os, struct
FONT = 0xC2018; WIDTHS = 0x128a2
HERE = os.path.dirname(os.path.abspath(__file__))
# blank in the original 8x8 font. Left alone on purpose: 0x1BF 0x1CE 0x1CF 0x1E0 0x1FF (likely HUD blanks).
SLOTS = [0x16, 0x17, 0x18, 0x12B, 0x12C, 0x12D] + list(range(0x157, 0x180)) + list(range(0x18A, 0x190)) \
        + list(range(0x19A, 0x1A0)) + [0x1DD, 0x1DE, 0x1DF]
SPACE = "[1C]"; SPACE_PX = 4      # a space inside a value: the game's own 4 px blank
KEEP = {"♥"}                      # drawn with the game's own glyph


def glyphs():
    return json.load(open(os.path.join(HERE, "..", "font", "cfc2_vwf.json"), encoding="utf-8"))["glyphs"]


def plan(values):
    """values: iterable of field values -> {char: code} for every character that needs a CFC2 slot."""
    chars = sorted({c for v in values for c in v if c != " " and c not in KEEP})
    g = glyphs()
    missing = [c for c in chars if c not in g]
    if missing: raise SystemExit(f"fields_cfc2: no CFC2 glyph for {missing}")
    if len(chars) > len(SLOTS):
        raise SystemExit(f"fields_cfc2: the stat fields use {len(chars)} different characters, only {len(SLOTS)} blank slots")
    return dict(zip(chars, SLOTS))


def width(ch):
    return max(1, min(8, glyphs()[ch]["w"]))


def token(code):
    return "[%02X]" % code if code < 0x100 else "{%03X}" % code


def apply(d, cmap):
    g = glyphs()
    for ch, c in cmap.items():
        assert bytes(d[FONT + c * 16:FONT + c * 16 + 16]) == bytes(16), "slot %X is not blank" % c
        for y, r in enumerate(g[ch]["rows"][:8]):
            v = 0
            for x, p in enumerate(r[:8]):
                if p == "#": v |= 3 << (14 - 2 * x)
            struct.pack_into("<H", d, FONT + c * 16 + 2 * y, v)
        d[WIDTHS + c] = width(ch)
    return d
