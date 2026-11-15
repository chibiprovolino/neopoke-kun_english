# render NGPC VRAM dump (0x8000-0xBFFF) : python render.py v.bin out.png
import sys
from PIL import Image
def col(v,base,pal,c):
    w=v[base+pal*8+c*2]|(v[base+pal*8+c*2+1]<<8)
    return ((w&15)*17,((w>>4)&15)*17,((w>>8)&15)*17)
def tile(v,t):
    o=0x2000+t*16; return [[((v[o+y*2]|(v[o+y*2+1]<<8))>>(14-2*x))&3 for x in range(8)] for y in range(8)]
def plane(v,mapo,palo):
    img=Image.new("RGBA",(256,256),(0,0,0,0))
    for i in range(1024):
        e=v[mapo+i*2]|(v[mapo+i*2+1]<<8); t=e&0x1ff; p=(e>>9)&15
        tl=tile(v,t)
        for y in range(8):
            for x in range(8):
                xx=7-x if e&0x8000 else x; yy=7-y if e&0x4000 else y
                c=tl[yy][xx]
                if c: img.putpixel(((i%32)*8+x,(i//32)*8+y),col(v,palo,p,c)+(255,))
    return img
def render(v,full=False):
    bg=col(v,0x3e0-0x8000+0x8000-0x8000+0x3e0-0x3e0+0x3e0,0,0) if False else (40,40,40)
    p1=plane(v,0x1000,0x300); p2=plane(v,0x1800,0x380)
    s1=(v[0x32],v[0x33]); s2=(v[0x34],v[0x35])
    def scr(p,s):
        q=Image.new("RGBA",(256,256))
        for dx in (0,-256):
            for dy in (0,-256): q.paste(p,(dx-s[0]+(256 if s[0] else 0)-(256 if s[0] else 0),dy-s[1]),p) if False else None
        import PIL.ImageChops as C
        return C.offset(p,-s[0],-s[1])
    out=Image.new("RGBA",(256,256),bg+(255,))
    front_p1 = not (v[0x30]&0x80)
    a,b=(scr(p2,s2),scr(p1,s1)) if front_p1 else (scr(p1,s1),scr(p2,s2))
    out.alpha_composite(a); out.alpha_composite(b)
    # sprites
    for k in range(64):
        o=0x800+k*4; t=v[o]|((v[o+1]&1)<<8); fl=v[o+1]
        if not (fl&0x18): continue
        x=v[o+2]; y=v[o+3]; p=v[0xC00+k]&15
        tl=tile(v,t)
        for yy in range(8):
            for xx in range(8):
                c=tl[7-yy if fl&0x40 else yy][7-xx if fl&0x80 else xx]
                if c: out.putpixel(((x+xx)&255,(y+yy)&255),col(v,0x280,p,c)+(255,))
    return out if full else out.crop((0,0,160,152))
if __name__=="__main__":
    v=open(sys.argv[1],"rb").read()
    r=render(v,len(sys.argv)>3); r=r.resize((r.width*3,r.height*3),Image.NEAREST); r.save(sys.argv[2])
