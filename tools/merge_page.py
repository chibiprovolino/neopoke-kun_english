"""Take the Script Desk page's saved lines into the script: python tools/merge_page.py <export.json | db dir> [script/page.json]
<export.json> is the file the page's Export button saves (review/index.html opened outside Claude).
<db dir> is the page's `rev` collection as one JSON file per line key (ArtifactData list with out_dir writes <dir>/rev/<key>.json).
The saved text, status and note of each line overwrite that line in script/page.json (neopoke-script/1 format, read by tools/build.py).
Lines the page never saved are left as they are."""
import json, glob, os, sys
src = sys.argv[1]; dst = sys.argv[2] if len(sys.argv) > 2 else "script/page.json"
r = json.load(open(dst, encoding="utf-8"))
if os.path.isfile(src):
    page = json.load(open(src, encoding="utf-8"))["rev"]
else:
    page = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(src, "rev", "*.json"))}
n = 0
for l in r["lines"]:
    d = page.get(l["key"])
    if not d: continue
    new = dict(l, en=d["text"], status=d.get("status", l["status"]), note=d.get("note", l["note"]))
    if new != l: l.update(new); n += 1
json.dump(r, open(dst, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(f"{n} lines updated from the page -> {dst}")
