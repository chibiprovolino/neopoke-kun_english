"""Export the script for another agent/tool.
  python tools/export_script.py [build/reviews] > out
Writes script/export.json: one entry per unique line. Reviews (from ArtifactData list out_dir) are merged in if present."""
import json,glob,os,sys
lines=json.load(open("review/lines.json",encoding="utf-8"))
rev={}
for f in glob.glob("build/reviews/**/*.json",recursive=True):
    r=json.load(open(f,encoding="utf-8")); r=r.get("data",r)
    rev[os.path.splitext(os.path.basename(f))[0]]=r
out={"format":"neopoke-script/1",
 "rules":["Edit only 'en' (and 'note' if you want to leave a remark). Keep 'key' unchanged.",
          "\n is a line break. Codes like [1C] are screen positions: keep them where they are.",
          "Use plain ASCII and the heart ♥ only.",
          "Each line of 'en' should be at most 'maxw' characters (40 if half-width font is on), and at most 'lines' lines.",
          "'status': leave as is, or set to 'approved' / 'flagged' / 'edited'."],
 "lines":[]}
for l in lines:
    r=rev.get(l["key"],{})
    out["lines"].append({"key":l["key"],"scene":l["cat"],"maxw":l["maxw"],"lines":l["lines"],
        "jp":l["jp"],"draft":l["draft"],"en":r.get("text",l["draft"]),
        "status":r.get("status","english" if l["english_already"] else "todo"),"note":r.get("note","")})
json.dump(out,open("script/export.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(out["lines"]),"lines exported to script/export.json")
