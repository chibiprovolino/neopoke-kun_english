"""Build a patched ROM: python tools/insert.py rom/original.ngc translations.json out.ngc
translations.json: {"<string id>": "english text", ...} (ids from script/strings.json). Missing ids keep Japanese."""
import sys,json,re,struct
sys.path.insert(0,"tools"); from table import T
R={v:k for k,v in T.items() if len(v)==1}
d=bytearray(open(sys.argv[1],"rb").read())
S=json.load(open("script/strings.json",encoding="utf-8"))
tr=json.load(open(sys.argv[2],encoding="utf-8"))
def enc(s):
    s=s.replace("ロード","{1C0}{1C1}{1C2}")
    out=bytearray();i=0
    while i<len(s):
        m=re.match(r'\[([0-9A-F]{2})\]|\{([0-9A-F]{3})\}',s[i:])
        if m:
            if m.group(1): out.append(int(m.group(1),16))
            else: c=int(m.group(2),16); out+=bytes([1,c-0x100])
            i+=m.end(); continue
        ch=s[i]; i+=1
        if ch=="\n": out.append(0x0d); continue
        c=R.get(ch)
        if c is None: raise ValueError(f"no glyph for {ch!r} in {s!r}")
        out+= bytes([c]) if c<0x100 else bytes([1,c-0x100])
    return bytes(out)+b"\0"
# free space at end of ROM
import vwf
FREE=0x1ea300; END=vwf.CODE   # text goes below the VWF block; nothing may be placed at 0x1F8000+ (save area)
assert all(b==0xff for b in d[FREE:END]), "free space not empty"
cur=FREE; moved=0
for o in S:
    i=str(o["id"])
    if i not in tr: continue
    b=enc(tr[i]); off=int(o["off"],16)
    if len(b)<=o["len"]+1:
        d[off:off+len(b)]=b; continue
    if cur+len(b)>END: raise SystemExit("out of free space")
    d[cur:cur+len(b)]=b
    for r in o["refs"]:
        struct.pack_into("<I",d,int(r,16),0x200000+cur)
    cur+=len(b); moved+=1
import gfx_patch; gfx_patch.apply(d)   # graphics text: title logo, menu icons, profile labels (tools/gfx_patch.py)
import gfx_import; gfx_import.apply(d, log=lambda s: None if s.endswith("unchanged") else print("gfx_import:", s))   # survey items in gfx/*.json; some tile blocks move to 0x1B0000-0x1B2C7F
vwf.apply(d)
import icons; icons.apply(d)   # profile field icons at codes 0x11-0x15 in the game's own font (tools/icons.py)
import fields_cfc2; fields_cfc2.apply(d, tr.get("_cfc2", {}))   # CFC2 letters for the profile stat values, in blank 8x8 slots
assert all(b==0xff for b in d[vwf.SAVE_AREA:]), "patch data in the save area / system block"
open(sys.argv[3],"wb").write(d)
print(f"patched {len(tr)} strings, {moved} relocated, free space used {cur-FREE} of {END-FREE} bytes")
