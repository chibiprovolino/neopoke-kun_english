"""Merge review docs (saved by ArtifactData list out_dir=build/reviews) into build/translations.json.
Only 'approved' lines are used; everything else keeps the Japanese."""
import json,glob,os
out={}
for f in glob.glob("build/reviews/**/*.json",recursive=True):
    r=json.load(open(f,encoding="utf-8")); r=r.get("data",r)
    if r.get("status")=="approved":
        for i in r["ids"]: out[str(i)]=r["text"]
json.dump(out,open("build/translations.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(out),"strings approved")
