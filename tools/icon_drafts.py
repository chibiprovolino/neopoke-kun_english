"""Swap the profile field labels for icons: python tools/icon_drafts.py [in.json] [out.json]
Default build/tr_drafts.json -> build/tr_drafts_icons.json. Fields are ids 110-347, 7 per profile
(name, age, job, income, hobby, appeal, message). Each field becomes <icon><value><padding>.
These strings use the game's own 8x8 proportional renderer (not the VWF). The VALUE is lettered in the CFC2 font,
whose glyphs sit in blank code slots of the 8x8 font (tools/fields_cfc2.py); the char -> code map is saved under
"_cfc2" in the output for tools/insert.py. The icon's width (tools/icons.py) already includes the 1 px gap.
The renderer only clears what it draws, so every field is padded to the full 64 px with the blank codes 0x19-0x1F (1-7 px)."""
import sys, json, re
sys.path.insert(0, "tools")
from icons import LABEL, load, width, WIDTHS
import fields_cfc2 as fc
FIELD = 64
src = sys.argv[1] if len(sys.argv) > 1 else "build/tr_drafts.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "build/tr_drafts_icons.json"
W = bytearray(open("rom/original.ngc", "rb").read()[WIDTHS:WIDTHS + 0x200])
for lab, rows in load().items(): W[LABEL[lab]] = width(rows)
HEART = "♥"   # 2-byte code 0x12A, the game's own glyph
d = json.load(open(src, encoding="utf-8"))
labels = ["Age", "Job", "Income", "Hobby", "Appeal"]
vals = {}
for i in range(110, 348):
    k = (i - 110) % 7
    if not 1 <= k <= 5 or str(i) not in d: continue
    lab = labels[k - 1]
    m = re.match(re.escape(lab) + r"\s*(.*?)\s*$", d[str(i)])
    if not m: raise SystemExit(f"{i}: {d[str(i)]!r} does not start with {lab}")
    vals[i] = (lab, m.group(1))
cmap = fc.plan(v for _, v in vals.values())
def px(s): return sum(W[0x12A] if c == HEART else fc.SPACE_PX if c == " " else fc.width(c) for c in s)
def enc(s): return "".join(c if c == HEART else fc.SPACE if c == " " else fc.token(cmap[c]) for c in s)
over = []
for i, (lab, val) in vals.items():
    ic = LABEL[lab]
    free = FIELD - W[ic] - px(val)
    padding = "[1F]" * (free // 7) + ("[%02X]" % (0x18 + free % 7) if free % 7 else "") if free > 0 else ""  # 7 px blanks
    d[str(i)] = "[%02X]%s%s" % (ic, enc(val), padding)
    if free < 0: over.append((i, lab, val, -free))
# Mr. Yabou stat labels (ids 69-83) use the same renderer, which only clears the tiles it draws into. Each field is
# as many 8 px tiles as the Japanese label had characters; shorter English labels left the last tiles showing stale
# art from the previous screen. Pad them to the field width with the same blanks.
_rom = open("rom/original.ngc", "rb").read()
_strs = json.load(open("script/strings.json", encoding="utf-8"))
# The same renderer draws the whole Yabou screen (labels 69-83, names 373-378, prompt 379) and the V.OFF shooter text
# windows (intro 407-437 and ending 548-574 in a 104 px window, story 438-547 in a 144 px window; checked in MAME).
# Its space is 8 px, as wide as a kana, so the gaps between English words look enormous: every space after the first word
# of a line becomes a 4 px blank (the dialog font's space), narrowed further (down to 1 px) if the line is still too wide.
# Glyph widths already include a 1 px gap. Leading spaces stay 8 px (they position the line; blanks there are position codes).
# Each line is then padded to the field width so the previous text is wiped, as the Japanese did with trailing spaces.
# A Yabou field is the Japanese text's pixel width rounded up to whole tiles (69 "1576ねんなつ" is 52 px -> 56).
SPACE8 = 4
def _jpw(b):
    x = i = 0
    while i < len(b):
        c = b[i]; i += 1
        if c == 1: c = 0x100 + b[i]; i += 1
        x += W[c]
    return x
def _px(t): return sum(W[int(m[1], 16)] if m[1] else W[ord(m[2])] for m in re.finditer(r"\[([0-9A-F]{2})\]|(.)", t))
def _pad(free): return "[1F]" * (free // 7) + ("[%02X]" % (0x18 + free % 7) if free % 7 else "") if free > 0 else ""
def fit8(t, field):
    out = []; worst = 0
    for line in t.split("\n"):
        line = line.rstrip(" ")
        lead = len(line) - len(line.lstrip(" ")); head, body = line[:lead], line[lead:]
        ns = body.count(" "); sp = SPACE8
        if ns:
            need = SPACE8 - -(-(_px(head + body.replace(" ", "")) + ns * SPACE8 - field) // ns)
            # narrower than a 3 px blank reads as one word in MAME, so lines that need it keep normal gaps and need rewording
            # (the Yabou labels are single words or "Summer 1576", which may go down to 1 px)
            lo = 1 if field < 64 else 3
            sp = min(SPACE8, need) if need >= lo else SPACE8
        line = head + body.replace(" ", "[%02X]" % (0x18 + sp))
        free = field - _px(line); worst = min(worst, free)
        out.append(line + _pad(free))
    return "\n".join(out), -worst
FIELDS = {i: None for i in list(range(69, 84)) + list(range(373, 380))}
FIELDS.update({i: 104 for i in list(range(407, 438)) + list(range(548, 575))})
FIELDS.update({i: 144 for i in range(438, 548)})
for i, field in FIELDS.items():
    if str(i) not in d: continue
    if field is None:
        a = int(_strs[i]["off"], 16); field = -(-_jpw(_rom[a:_rom.index(b"\0", a)]) // 8) * 8
    d[str(i)], ex = fit8(d[str(i)], field)
    if ex > 0: over.append((i, "8x8", d[str(i)], ex))
d["_cfc2"] = cmap
json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(vals)} fields -> {dst} ({len(cmap)} CFC2 letters in {len(fc.SLOTS)} slots)")
for i, lab, val, o in over: print(f"  too wide: {i} {lab} {val!r} by {o} px")
