"""Write the whole V.OFF script in reading order: python tools/voff_dump.py [build/page_lines.json] [script/voff_script.md]
Run tools/merge_page.py and tools/page_lines.py first. Each line is measured the way the game draws it (8x8 renderer,
inner spaces 4 px, leading spaces 8 px) against its window: story 144 px, intro/ending 104 px."""
import json, sys
sys.path.insert(0, "tools")
from icons import WIDTHS
src = sys.argv[1] if len(sys.argv) > 1 else "build/page_lines.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "script/voff_script.md"
W = open("rom/original.ngc", "rb").read()[WIDTHS:WIDTHS + 0x200]
def px(t, gap=4):
    t = t.rstrip(" "); lead = len(t) - len(t.lstrip(" "))
    return lead * 8 + sum(gap if c == " " else W[ord(c)] for c in t[lead:])
L = [l for l in json.load(open(src, encoding="utf-8")) if l.get("part")]
out = ["# V.OFF script", "",
       "All shooter text in reading order, as the build has it now (script/page.json).",
       "Width is measured as the game draws it: inner spaces 4 px (the build narrows the game's 8 px space), leading spaces 8 px.",
       "Windows: Intro and Ending 104 px (from the Japanese, not yet seen on screen), Story 144 px (checked in MAME).",
       "`px` = width / window. **over** = does not fit; *tight* = fits only with 3 px spaces (the build squeezes these automatically).",
       "Known story screens: page 1 = 438-439, page 2 = 440-446, page 3 = 447-452, page 4 = 453-455 (later pages not captured yet).", ""]
part = seg = None; n_over = n_tight = 0
for l in L:
    i = l["ids"][0]; en = l.get("en", l["draft"]); b = l["budget"]; w = px(en); w3 = px(en, 3)
    if l["part"] != part:
        part = l["part"]; out += ["", f"## {part} ({b} px window)", ""]; seg = None
    s = l.get("seg")
    if s and (s[0] == 1 or s[2] != seg):
        seg = s[2]; out += ["", f"> {seg}", ""]
        out += ["| id | Japanese | English | px |", "|---:|---|---|---:|"]
    elif not s and seg != "-":
        seg = "-"; out += ["", "| id | Japanese | English | px |", "|---:|---|---|---:|"]
    flag = ""
    if w > b:
        if w3 <= b: flag = " *tight*"; n_tight += 1
        else: flag = f" **over {w - b}**"; n_over += 1
    cell = lambda t: t.strip().replace("|", "\\|") or "(blank)"
    out.append(f"| {i} | {cell(l['jp'])} | {cell(en)} | {w}/{b}{flag} |")
out.insert(7, f"Summary: {len(L)} lines, {n_over} over, {n_tight} tight.")
open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"{len(L)} lines -> {dst}: {n_over} over, {n_tight} tight")
