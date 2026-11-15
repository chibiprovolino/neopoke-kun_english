"""Turn the revised script into build translations: python tools/build_from_revised.py [script/revised.json] [build/tr_revised.json]
script/revised.json is a file in neopoke-script/1 format (see tools/export_script.py); its 'en' is used for every id of the line.
Then the font plan (script/font_plan.py) is applied: strings listed in BIG are replaced by their big-font wording."""
import json, sys
sys.path.insert(0, "tools"); sys.path.insert(0, "script")
from vwf import BIG as BIGCODE
from font_plan import BIG
src = sys.argv[1] if len(sys.argv) > 1 else "script/revised.json"
dst = sys.argv[2] if len(sys.argv) > 2 else "build/tr_revised.json"
rev = json.load(open(src, encoding="utf-8"))
assert rev.get("format") == "neopoke-script/1"
L = json.load(open("review/lines.json", encoding="utf-8"))      # made from your ROM by tools/setup.py
ids = {l["key"]: l["ids"] for l in L}
jp = {l["key"]: l["jp"] for l in L}                                 # the script files carry no Japanese text
out = {}
for l in rev["lines"]:
    if l.get("status") == "english" and l["en"] == jp[l["key"]]: continue     # already English in the ROM
    for i in ids[l["key"]]: out[str(i)] = l["en"]
for i, text in BIG.items():
    out[str(i)] = BIGCODE + text
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(out)} strings -> {dst} ({len(BIG)} in the big font)")
