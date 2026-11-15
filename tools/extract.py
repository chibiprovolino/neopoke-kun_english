import sys,struct,json,collections
sys.path.insert(0,"tools"); from table import T
d=open(sys.argv[1],"rb").read()
S,E=0xccd80,0xcfb68
refs=collections.defaultdict(list)
for i in range(0,len(d)-4):
    v=d[i]|d[i+1]<<8|d[i+2]<<16
    if 0x200000+S<=v<0x200000+E and d[i+3]==0: refs[v-0x200000].append(i)
def dec(b):
    s="";i=0
    while i<len(b):
        c=b[i]
        if c==1: c=0x100+b[i+1]; i+=2
        else: i+=1
        if c in T: s+=T[c]
        elif c==0x0d: s+="\n"
        else: s+="[%02X]"%c
    return s
out=[];i=S
while i<E:
    j=i
    while d[j]!=0: j+= 2 if d[j]==1 else 1
    out.append({"id":len(out),"off":hex(i),"len":j-i,"refs":[hex(r) for r in refs.get(i,[])],"jp":dec(d[i:j]),"en":""})
    i=j+1
json.dump(out,open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(out),"strings;", sum(1 for o in out if not o["refs"]),"unreferenced")
