"""Measure every dialog line with the font it will really use: python tools/check_fit.py [build/tr_revised.json] [out.txt]
Big-font strings (start with [10][F1]) are checked against script/font_plan.BIG_WINDOW; every other line (8x8 font) against
its Japanese line at 12 px per character, a conservative stand-in for the window (real windows may be wider).
Profile stat fields (8x8 renderer, checked by tools/icon_drafts.py) are skipped."""
import json, re, sys
sys.path.insert(0, "tools"); sys.path.insert(0, "script")
import vwf
from font_plan import BIG_WINDOW
src = sys.argv[1] if len(sys.argv) > 1 else "build/tr_revised.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "build/fit.txt"
d = bytearray(open("rom/original.ngc", "rb").read())
wbig, _ = vwf.metrics(d); w8 = vwf.widths8(d)
S = json.load(open("script/strings.json", encoding="utf-8")); tr = json.load(open(src, encoding="utf-8"))
FW = {chr(0xFF01 + k): 0x21 + k for k in range(94)}   # full-width forms: HUD letters, not dialog text


def lines(s):
    """-> list of (pixel width, visible text) per line."""
    big = False; out = []; x = 0; vis = ""; i = 0
    s = s.replace("ロード", "{1C0}{1C1}{1C2}")
    while i < len(s):
        m = re.match(r'\[([0-9A-F]{2})\]|\{([0-9A-F]{3})\}', s[i:])
        if m:
            c = int(m.group(1) or m.group(2), 16); i += m.end()
            if c == 0x10:
                m2 = re.match(r'\[([0-9A-F]{2})\]', s[i:]); v = int(m2.group(1), 16); i += m2.end()
                if v >= 0xF0: big = v == 0xF1
                else: x = v; vis += " "
                continue
        else:
            ch = s[i]; i += 1
            if ch == "\n": out.append((x, vis)); x = 0; vis = ""; continue
            vis += ch; c = 0x12A if ch == "♥" else ord(ch)
            if c >= 0x200: return None
        x += (wbig if big else w8)[c]
    out.append((x, vis)); return out


rows = []; n = 0
for o in S:
    i = o["id"]
    if str(i) not in tr or (110 <= i < 348 and (i - 110) % 7 in (1, 2, 3, 4, 5)): continue
    L = lines(tr[str(i)])
    if L is None: continue
    jl = o["jp"].split("\n")
    for k, (px, vis) in enumerate(L):
        n += 1
        lim = BIG_WINDOW[i] if i in BIG_WINDOW else (len(re.sub(r'\[[0-9A-F]{2}\]', '', jl[k])) * 12 if k < len(jl) else 0)
        if px > lim: rows.append((i, k, px, lim, vis))
with open(dst, "w", encoding="utf-8") as f:
    f.write("Lines wider than their limit (big font: the window; 8x8 font: the Japanese line at 12 px/char).\nid line  px / limit  text\n")
    for i, k, px, lim, vis in rows: f.write("%4d %d  %4d / %3d  %s\n" % (i, k, px, lim, vis))
print(f"{len(rows)} of {n} lines over their limit, in {len({r[0] for r in rows})} strings -> {dst}; wider than the 160 px screen: {sum(1 for r in rows if r[2] > 160)}")
