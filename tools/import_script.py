"""Validate a file in neopoke-script/1 format and turn it into review-page writes.
  python tools/import_script.py incoming.json
Prints problems, writes build/import_batches/batch_NN.json (each <=50 docs) for Claude to push to the page."""
import json,sys,os,re
src=json.load(open(sys.argv[1],encoding="utf-8"))
assert src.get("format")=="neopoke-script/1","wrong format"
base={l["key"]:l for l in json.load(open("review/lines.json",encoding="utf-8"))}
probs=[];docs=[]
for e in src["lines"]:
    k=e.get("key")
    if k not in base: probs.append(f"{k}: unknown key"); continue
    b=base[k]; en=e.get("en","")
    if e.get("jp",b["jp"])!=b["jp"]: probs.append(f"{k}: Japanese text was changed (ignored)")
    if re.search(r'[^\x20-\x7e\n♥！-～]',re.sub(r'\[[0-9A-F]{2}\]','',en)): probs.append(f"{k}: non-ASCII characters")
    if re.findall(r'\[[0-9A-F]{2}\]',en)!=re.findall(r'\[[0-9A-F]{2}\]',b["jp"]): probs.append(f"{k}: position codes differ from Japanese")
    if en==b["draft"] and e.get("status") in (None,"todo","english") and not e.get("note"): continue
    st=e.get("status") if e.get("status") in ("approved","flagged","edited") else "edited"
    docs.append({"op":"set","collection":"rev","doc_id":k,"data":{"text":en,"status":st,"note":e.get("note",""),"ids":b["ids"],"updatedAt":"imported"}})
os.makedirs("build/import_batches",exist_ok=True)
for f in os.listdir("build/import_batches"): os.remove("build/import_batches/"+f)
for n in range(0,len(docs),50):
    json.dump(docs[n:n+50],open(f"build/import_batches/batch_{n//50:02d}.json","w",encoding="utf-8"),ensure_ascii=False)
print(len(docs),"changed lines;",len(probs),"warnings"); print("\n".join(probs[:100]))
