"""Give the review page the real fonts: python tools/review_fonts.py   (run after tools/mklines.py)
Writes review/font.json = {"f8": {...}, "cfc2": {...}, "big": {...}}, each {char: [advance px, bitmap]} with
bitmap = rows of '#'/'.' (8x8 for f8 and cfc2, 16x16 for big), and adds to every line of review/lines.json:
  "font":   "big" (script/font_plan.BIG), "cfc2" (dating-profile stat values) or "f8" (everything else)
  "budget": width limit in px: big = the window; cfc2 = 56 (64 px field minus the 8 px icon);
            f8 = Japanese line length x 12 for dialog text, x 8 for the minigame menu and HUD labels."""
import json, re, sys
sys.path.insert(0, "tools"); sys.path.insert(0, "script")
import vwf, fields_cfc2
from font_plan import BIG, BIG_WINDOW
d = bytearray(open("rom/original.ngc", "rb").read())
CH = [chr(c) for c in range(0x20, 0x7F)]


def bits8(c):
    out = ""
    for y in range(8):
        w = d[vwf.F8 + c * 16 + 2 * y] | d[vwf.F8 + c * 16 + 2 * y + 1] << 8
        out += "".join("#" if (w >> (14 - 2 * x)) & 3 else "." for x in range(8))
    return out


w8 = vwf.widths8(d)
f8 = {ch: [w8[ord(ch)], bits8(ord(ch))] for ch in CH}
f8["♥"] = [w8[0x12A], bits8(0x12A)]
g = fields_cfc2.glyphs()
cfc2 = {ch: [fields_cfc2.width(ch), "".join((r + "........")[:8] for r in (g[ch]["rows"] + ["........"] * 8)[:8])] for ch in CH if ch in g and ch != " "}
cfc2[" "] = [fields_cfc2.SPACE_PX, "." * 64]
cfc2["♥"] = f8["♥"]
wb, _ = vwf.metrics(d)
big = {}
for ch in CH + ["♥"]:
    c = 0x12A if ch == "♥" else ord(ch)
    P = vwf.glyph_px(d, c); b = vwf.ink(P)
    if b and c < vwf.NCOPY: P = [row[b[0]:] + [0] * b[0] for row in P]
    big[ch] = [wb[c], "".join("#" if p else "." for row in P for p in row)]
json.dump({"f8": f8, "cfc2": cfc2, "big": big}, open("review/font.json", "w", encoding="utf-8"), ensure_ascii=False)

lines = json.load(open("review/lines.json", encoding="utf-8"))
n = {"big": 0, "cfc2": 0, "f8": 0}
for l in lines:
    i = l["ids"][0]
    if i in BIG: l["font"] = "big"; l["budget"] = BIG_WINDOW[i]
    elif 110 <= i < 348 and (i - 110) % 7 in (1, 2, 3, 4, 5): l["font"] = "cfc2"; l["budget"] = 56
    else:
        l["font"] = "f8"
        l["budget"] = l["maxw"] * (8 if l["cat"] in ("Minigame menu", "HUD & labels") or l["english_already"] else 12)
    n[l["font"]] += 1
json.dump(lines, open("review/lines.json", "w", encoding="utf-8"), ensure_ascii=False)
print("review/font.json and review/lines.json updated:", n)
