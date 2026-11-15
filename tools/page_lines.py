"""Refresh the Script Desk's lines.json: python tools/page_lines.py [script/page.json] [out lines.json]
Adds to every line of review/lines.json:
  en      the current English (script/page.json), shown when the page has no save for the line
  font    "r8" for strings drawn by the game's own 8x8 renderer (Yabou screen, D&DQ monster names, V.OFF text windows):
          same glyphs and widths as "f8", but inner spaces are 4 px blanks and leading spaces stay 8 px (see tools/icon_drafts.py)
  budget  that renderer's real field width (Yabou: Japanese width rounded up to tiles; V.OFF story 144 px, intro/ending 104 px;
          monster names 32 px, assumed: the battle screen was never captured)
  part    for V.OFF lines: "Intro", "Story" or "Ending" (the page's V.OFF script view lists them in order)
  seg     sentence grouping from the page.json notes ("Segment 1/2 of: ...") when there is one
Default output: build/page_lines.json (publish it as lines.json)."""
import json, re, sys
src = sys.argv[1] if len(sys.argv) > 1 else "script/page.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "build/page_lines.json"
sys.path.insert(0, "tools")
from icons import WIDTHS
rom = open("rom/original.ngc", "rb").read(); import vwf; W = vwf.fix8(rom[WIDTHS:WIDTHS + 0x200])
S = json.load(open("script/strings.json", encoding="utf-8"))
L = json.load(open("review/lines.json", encoding="utf-8"))
P = {l["key"]: l for l in json.load(open(src, encoding="utf-8"))["lines"]}
def jpw(i):
    a = int(S[i]["off"], 16); b = rom[a:rom.index(b"\0", a)]; x = k = 0
    while k < len(b):
        c = b[k]; k += 1
        if c == 1: c = 0x100 + b[k]; k += 1
        x += W[c]
    return -(-x // 8) * 8
R8 = {i: jpw(i) for i in list(range(69, 84)) + list(range(373, 380))}
R8.update({i: 32 for i in range(384, 394)})
R8.update({i: 104 for i in list(range(407, 438)) + list(range(548, 575))})
R8.update({i: 144 for i in range(438, 548)})
for l in L:
    p = P.get(l["key"])
    if p: l["en"] = p["en"]
    i = l["ids"][0]
    if i in R8: l["font"] = "r8"; l["budget"] = R8[i]
    if 407 <= i < 575: l["part"] = "Intro" if i < 438 else "Story" if i < 548 else "Ending"
    m = p and re.search(r"Segment (\d+)/(\d+) of: (.*?)(?:\s*\||;\s*(?:Assistant|User|Claude)\b|$)", p.get("note", ""))
    if m: l["seg"] = [int(m[1]), int(m[2]), m[3].strip()]
json.dump(L, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(L)} lines -> {dst}; {sum(1 for l in L if l.get('font') == 'r8')} on the 8x8 renderer, {sum(1 for l in L if 'seg' in l)} with a sentence group")
