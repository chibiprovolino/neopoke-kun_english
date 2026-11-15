import sys
d=open(sys.argv[1],"rb").read()
def score(t):
    b=d[t:t+16]
    if b==b'\0'*16 or b==b'\xff'*16: return 0
    cols=set();rows=[]
    for y in range(8):
        w=b[2*y]|b[2*y+1]<<8
        px=[(w>>(14-2*x))&3 for x in range(8)]
        cols|=set(px); rows.append(px)
    if len(cols)!=2 or 0 not in cols: return 0
    # blank last row or last column typical of fonts
    return 1 if all(r[7]==0 for r in rows) or all(p==0 for p in rows[7]) else 0
blk=0x1000
res=[]
for s in range(0,len(d),blk):
    sc=sum(score(t) for t in range(s,s+blk,16))
    res.append((sc,s))
for sc,s in sorted(res,reverse=True)[:25]: print(hex(s),sc)
