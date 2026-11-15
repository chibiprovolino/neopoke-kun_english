import json,re,sys; sys.path.insert(0,"script"); from drafts import D
a=json.load(open("script/strings.json",encoding="utf-8"))
def vis(s): return re.sub(r'\[[0-9A-F]{2}\]','',re.sub(r'\{1C0\}\{1C1\}\{1C2\}','ロード',s))
def cat(i):
    for lo,hi,n in [(0,30,"Minigame menu"),(30,106,"HUD & labels"),(106,110,"Save / load"),(110,348,"Dating profiles"),(348,373,"Rock-paper-scissors date"),(373,384,"Mr. Yabou"),(384,406,"D&DQ"),(406,438,"Shooter intro"),(438,548,"Shooter story"),(548,575,"Shooter ending"),(575,637,"Staff credits"),(637,667,"Minigame instructions")]:
        if lo<=i<hi: return n
groups={};order=[]
for o in a:
    j=o["jp"]
    if not j.strip(): continue
    if j not in groups: groups[j]={"key":"s%03d"%o["id"],"ids":[],"jp":j,"cat":cat(o["id"])}; order.append(j)
    groups[j]["ids"].append(o["id"])
out=[]
for j in order:
    g=groups[j]; first=g["ids"][0]
    g["draft"]=D.get(first,j)
    g["english_already"]=first not in D
    g["maxw"]=max(len(vis(l)) for l in j.split("\n"))
    g["lines"]=len(j.split("\n"))
    out.append(g)
json.dump(out,open("review/lines.json","w",encoding="utf-8"),ensure_ascii=False)
print(len(out),sum(1 for g in out if not g["english_already"]))
