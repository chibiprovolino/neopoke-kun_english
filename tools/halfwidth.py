"""Half-width text: two 4px glyphs per 8px tile. Builds a pair set that fits the free tile slots,
then encodes each line with a DP that re-aligns pairs around spaces to avoid gaps."""
import re,collections
from halffont import G,pair_tile
CODE=re.compile(r'\[[0-9A-F]{2}\]|\{[0-9A-F]{3}\}')

def segments(line):
    """split a line into control tokens and visible runs"""
    out=[];p=0
    for m in CODE.finditer(line):
        if m.start()>p: out.append(("t",line[p:m.start()]))
        out.append(("c",m.group())); p=m.end()
    if p<len(line): out.append(("t",line[p:]))
    return out

def dp(text,have):
    """min-gap tiling of text with pair tiles. Returns list of 2-char strings, gaps."""
    n=len(text); INF=10**9
    best=[(INF,None)]*(n+1); best[0]=(0,None)
    for i in range(n):
        c,_=best[i]
        if c==INF: continue
        if i+1<n and text[i:i+2] in have and c<best[i+2][0]: best[i+2]=(c,(i,text[i:i+2]))
        # single char padded with a space = a gap (free if the next char is a space we then skip)
        if i+1<n and text[i+1]==" " and (text[i]+" ") in have and c<best[i+2][0]: best[i+2]=(c,(i,text[i]+" "))
        if (text[i]+" ") in have and c+1<best[i+1][0]: best[i+1]=(c+1,(i,text[i]+" "))
        if (" "+text[i]) in have and c+1<best[i+1][0]: best[i+1]=(c+1,(i," "+text[i]))
    if best[n][0]==INF: return None,INF
    tiles=[];k=n
    while k>0:
        i,t=best[k][1]; tiles.append(t); k=i
    return tiles[::-1],best[n][0]

def visible_runs(texts):
    for t in texts:
        for line in t.split("\n"):
            for kind,s in segments(line):
                if kind=="t": yield s

def choose_pairs(texts,slots):
    runs=list(visible_runs(texts))
    chars=sorted({ch for r in runs for ch in r})
    missing=[ch for ch in chars if ch not in G]
    if missing: raise ValueError(f"no half-width glyph for {missing}")
    base={ch+" " for ch in chars}          # every char always has a fallback tile
    if len(base)>slots: raise ValueError("not enough slots even for single glyphs")
    want=collections.Counter()
    for r in runs:
        v=r+(" " if len(r)%2 else "")
        for k in range(0,len(v),2): want[v[k:k+2]]+=1
        for k in range(1,len(r)-1,2): want[r[k:k+2]]+=1   # odd alignment too
    have=set(base)
    for _ in range(4):
        extra=[p for p,_ in want.most_common() if p not in base][:slots-len(base)]
        have=base|set(extra)
        used=collections.Counter()
        for r in runs:
            tiles,_=dp(r,have)
            for t in tiles: used[t]+=1
        # reward pairs actually used, keep exploring others
        want=collections.Counter({p:c*3 for p,c in used.items()})+want
    gaps=sum(dp(r,have)[1] for r in runs)
    return sorted(have),gaps

def encode_line(line,code_of):
    """returns list of tile codes / control bytes for one line"""
    out=[]
    for kind,s in segments(line):
        if kind=="c": out.append(s)
        else:
            tiles,_=dp(s,set(code_of))
            out+= [code_of[t] for t in tiles]
    return out
