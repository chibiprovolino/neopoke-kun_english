import sys
import re,sys
sys.stdout.reconfigure(encoding="utf-8")
d=open(sys.argv[1],"rb").read()
runs=[]
for m in re.finditer(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\xfc]|[\x20-\x7e]){6,}',d):
    s=m.group()
    try: t=s.decode('shift_jis')
    except: continue
    if sum(ord(c)>0x3000 for c in t)>=4: runs.append((m.start(),t))
print("sjis",len(runs))
for o,t in runs[:30]: print(hex(o),t[:60])
a=[(m.start(),m.group()) for m in re.finditer(rb'[\x20-\x7e]{8,}',d)]
print("ascii",len(a)); [print(hex(o),s[:60]) for o,s in a[:30]]
e=len(d)
while d[e-1]==0xff: e-=1
print("used end",hex(e))
