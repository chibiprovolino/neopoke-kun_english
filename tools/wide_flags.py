"""Work out the Script Desk's "Too wide" flags: python tools/wide_flags.py <db dir> <out batch.json>
Needs build/tr_page.json (tools/build_from_revised.py) and build/fit_page.txt (tools/check_fit.py) from the current page text.
<db dir>/wide/*.json is the page's current `wide` collection (ArtifactData list with out_dir).
Writes an ArtifactData batch (set new/changed flags, delete flags for lines that now fit) and prints a summary."""
import json, os, glob, re, subprocess, sys, datetime
db, dst = sys.argv[1], sys.argv[2]
out = subprocess.run([sys.executable, "tools/icon_drafts.py", "build/tr_page.json", "build/tr_page_icons.json"],
                     capture_output=True, text=True, encoding="utf-8").stdout
L = json.load(open("review/lines.json", encoding="utf-8")); key = {i: l["key"] for l in L for i in l["ids"]}
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
new = {}
for m in re.finditer(r"too wide: (\d+) (\S+) (.*) by (\d+) px", out):
    i, o = int(m[1]), int(m[4])
    if m[2] in ("Age", "Job", "Income", "Hobby", "Appeal"): new[key[i]] = f"stat value is {o} px over the 64 px field"
    elif 438 <= i < 548: new[key[i]] = (f"{o} px wider than the 144 px story window (V.OFF), even with 4 px spaces; squeezing the spaces "
                                       "under 3 px makes the words run together. Checked on screen in MAME")
    elif 407 <= i < 575: new[key[i]] = f"{o} px wider than the 88 px readable part of the intro/ending window (the picture covers the rest), even with 4 px spaces"
    elif 384 <= i < 394: new[key[i]] = f"{o} px wider than the 32 px name field (assumed same rule as the Yabou fields; battle screen not captured)"
    else: new[key[i]] = f"{o} px wider than its {m[2]} field"
for r in open("build/fit_page.txt", encoding="utf-8").read().splitlines()[2:]:
    i, k, px, _, lim, *t = r.split()
    new[key[int(i)]] = f"line {int(k) + 1} is {px} px vs {lim} (Japanese width); probably fits, check on screen"
old = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(db, "wide", "*.json"))}
ver = {}   # versions are not in the files; ArtifactData lists them. Pass them via <db dir>/wide_versions.json if not all 1.
vf = os.path.join(db, "wide_versions.json")
if os.path.exists(vf): ver = json.load(open(vf))
fdir = os.path.join(os.path.dirname(os.path.abspath(dst)), "wide_docs"); os.makedirs(fdir, exist_ok=True)
W = []
for k in sorted(set(old) | set(new)):
    if k not in new: W.append({"op": "delete", "collection": "wide", "doc_id": k, "if_version": ver.get(k, 1)}); continue
    if k in old and old[k]["msg"] == new[k]: continue
    fp = os.path.join(fdir, k + ".json").replace("\\", "/"); json.dump({"msg": new[k], "at": now}, open(fp, "w", encoding="utf-8"), ensure_ascii=False)
    e = {"op": "set", "collection": "wide", "doc_id": k, "file_path": fp}
    if k in old: e["if_version"] = ver.get(k, 1)
    W.append(e)
json.dump(W, open(dst, "w"), indent=0)
print(f"{len(new)} lines too wide; {len(W)} writes -> {dst}")
for k in sorted(new): print(f"  {k}: {new[k]}")
