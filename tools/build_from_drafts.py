import json,sys; sys.path.insert(0,"script"); from drafts import D
a=json.load(open("script/strings.json",encoding="utf-8"))
by={}
for o in a: by.setdefault(o["jp"],[]).append(o["id"])
out={}
for jp,ids in by.items():
    if ids[0] in D:
        for i in ids: out[str(i)]=D[ids[0]]
json.dump(out,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False)
