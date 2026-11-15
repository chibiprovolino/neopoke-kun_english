"""Neo Poke-kun VWF patch: replaces the 12px-pitch dialog renderer with a 1px variable-width renderer.
Two fonts, both the game's own, chosen per string:
  font 0 (default): the 8x8 font (file 0xC2018, widths at 0x128a2), read in place, drawn on rows 4-11 of the 16-row line.
  font 1: the big dialog font (16x16 cells, 2bpp, file 0xC4006, 64 bytes/code in tile order TL,TR,BL,BR).
          Codes 0x00-0x7F come from left-aligned copies (COPY), widths = ink width + GAP;
          codes >= 0x80 (kana, kanji, heart...) come straight from the ROM, unshifted, at the original 12px pitch.
In text: [10][F1] switches to the big font, [10][F0] back to 8x8 (lasts to the end of the string);
         [10][xx] with xx < F0 moves to pixel xx from the line start.
Hook: 0x212428 (after the text byte is read)."""
import struct
# All VWF data must stay below 0x1F8000: the game saves into flash block 0x20 (file 0x1F8000-0x1F9FFF) and erases it when full.
CODE=0x1F5000; WID=0x1F5200; COPY=0x1F5400; NCH=0x200
SAVE_AREA=0x1F8000
F8=0xC2018; W8=0x128a2          # the game's 8x8 font and its width table
W8V=0x1F7400; SPACE8=4          # copy of that table for dialog text: same widths, but a 4 px space (the game's is 8)
# The game's 8x8 widths give every letter its ink width + 1 px, except "o" (no gap: "ol" read as "d", e.g. "Golem")
# and D G K O S V v (2 px gap). FIX8 evens them out; applied to the ROM table (all 8x8 renderers) and the dialog copy.
FIX8={ord(c):w for c,w in zip("oDGKOSVv",(5,5,5,6,5,4,5,5))}
def fix8(w):
    """-> the 8x8 width table (bytes-like, indexed by code) with FIX8 applied, as a bytearray."""
    w=bytearray(w)
    for c,v in FIX8.items(): w[c]=v
    return w
ROMFONT=0xC4006; NCOPY=0x80
GAP=1; SPACE=5; PITCH=12
BIG="[10][F1]"                  # put at the start of a string to draw it in the big font
CPU=lambda f:f+0x200000
def imm32(v): return list(struct.pack("<I",v))

def glyph_px(d,c):
    g=d[ROMFONT+c*64:ROMFONT+c*64+64]; P=[[0]*16 for _ in range(16)]
    for t in range(4):
        for y in range(8):
            w=g[t*16+y*2]|g[t*16+y*2+1]<<8
            for x in range(8): P[(t>>1)*8+y][(t&1)*8+x]=(w>>(14-2*x))&3
    return P
def pack(P):
    out=bytearray()
    for t in range(4):
        for y in range(8):
            w=0
            for x in range(8): w|=P[(t>>1)*8+y][(t&1)*8+x]<<(14-2*x)
            out+=struct.pack("<H",w)
    return bytes(out)
def ink(P):
    xs=[x for r in P for x in range(16) if r[x]]
    return (min(xs),max(xs)) if xs else None

def build_code():
    a=[];lab={};fix=[];fixj=[]
    def emit(*b): a.extend(b)
    def L(n): lab[n]=len(a)
    def jr(op,n): a.extend([op,0]); fix.append((len(a)-1,n))
    def jp(n): a.extend([0x1b,0,0,0]); fixj.append((len(a)-3,n))
    def rows(tag):
        emit(0x27,0x08)                            # ld L,8
        L("row"+tag)
        emit(0xd5,0xf1,0x21)                       # ld BC,(XIX+)
        emit(0xe9,0xee,0x00)                       # sll 16,XBC      pixels to the high word
        emit(0xc9,0xd8)                            # cp A,0
        jr(0x66,"ns"+tag)                          # jr Z
        emit(0xe9,0xff)                            # srl A,XBC
        L("ns"+tag)
        emit(0x9a,0x20,0xe9)                       # or (XDE+0x20),BC   spill into next column
        emit(0xd7,0xe6,0x89)                       # ld BC,QBC
        emit(0xd5,0xe9,0xe9)                       # or (XDE+),BC       this column
        emit(0xcf,0x1c,0); fix.append((len(a)-1,"row"+tag)) # djnz L,row
    # object byte +0x38: bits 0-2 = sub-pixel, bits 4-5 = font (0 = 8x8, 1 = big dialog font)
    # code 0x10 xx (XWA = text ptr after the 0x10, BC = code): xx >= 0xF0 selects font xx-0xF0, else move to pixel xx
    emit(0xd9,0xcf,0x10,0x00)                      # cp BC,0x0010
    jr(0x6e,"glyph")                               # jr NZ
    emit(0xc5,0xe0,0x23)                           # ld C,(XWA+)
    emit(0xbe,0x2c,0x60)                           # ld (XIZ+0x2c),XWA  consume it
    emit(0xcb,0xcf,0xf0)                           # cp C,0xF0
    jr(0x67,"move")                                # jr C
    emit(0xcb,0x89)                                # ld A,C
    emit(0xc9,0xee,0x04)                           # sll 4,A         font bits
    emit(0x8e,0x38,0x23)                           # ld C,(XIZ+0x38)
    emit(0xcb,0xcc,0x0f)                           # and C,0x0F
    emit(0xcb,0xe1)                                # or A,C
    emit(0xbe,0x38,0x41)                           # ld (XIZ+0x38),A
    emit(0x0e)                                     # ret
    L("move")
    emit(0x8e,0x38,0x21)                           # ld A,(XIZ+0x38)
    emit(0xc9,0xcc,0xf0)                           # and A,0xF0      keep font
    emit(0xcb,0x88)                                # ld W,C
    emit(0xc8,0xcc,0x07)                           # and W,7
    emit(0xc8,0xe1)                                # or A,W
    emit(0xbe,0x38,0x41)                           # ld (XIZ+0x38),A sub-pixel
    emit(0xcb,0xcc,0xf8)                           # and C,0xf8
    emit(0xd9,0xee,0x02)                           # sll 2,BC        (X/8)*0x20
    emit(0x3a)                                     # push XDE
    emit(0x9e,0x20,0x22)                           # ld DE,(XIZ+0x20) line start
    emit(0xd9,0x82)                                # add DE,BC
    emit(0xbe,0x24,0x52)                           # ld (XIZ+0x24),DE
    emit(0x5a)                                     # pop XDE
    emit(0x0e)                                     # ret
    L("glyph")
    emit(0x3a); emit(0x3b)                         # push XDE ; push XHL
    emit(0x8e,0x38,0x21)                           # ld A,(XIZ+0x38)
    emit(0xc9,0xcc,0x30)                           # and A,0x30
    jr(0x6e,"big")                                 # jr NZ
    # --- 8x8 font: the game's own glyphs and width table, rows 4-11 of the 16-row line
    emit(0x45,*imm32(CPU(W8V)))                    # ld XIY,8x8 widths (copy with the narrow space)
    emit(0xc3,0x07,0xf4,0xe4,0x26)                 # ld H,(XIY+BC)   width
    emit(0x44,*imm32(CPU(F8)))                     # ld XIX,8x8 font (ROM)
    emit(0xd9,0xee,0x04)                           # sll 4,BC        16 bytes/glyph
    emit(0xf3,0x07,0xf0,0xe4,0x34)                 # lda XIX,XIX+BC
    emit(0xae,0x24,0x22)                           # ld XDE,(XIZ+0x24)
    emit(0xda,0xc8,0x08,0x00)                      # add DE,0x0008   row 4
    emit(0x8e,0x38,0x21)                           # ld A,(XIZ+0x38)
    emit(0xc9,0xcc,0x07)                           # and A,7
    emit(0xc9,0x81)                                # add A,A         2 bits/pixel
    rows("s")
    L("adv0")
    emit(0xae,0x24,0x22)                           # ld XDE,(XIZ+0x24)
    emit(0x8e,0x38,0x21)                           # ld A,(XIZ+0x38)
    emit(0xc9,0xcc,0x07)                           # and A,7
    emit(0xce,0x81)                                # add A,H
    L("adv")
    emit(0xc9,0xcf,0x08)                           # cp A,8
    jr(0x67,"done")                                # jr C
    emit(0xc9,0xca,0x08)                           # sub A,8
    emit(0xda,0xc8,0x20,0x00)                      # add DE,0x0020
    jr(0x68,"adv")                                 # jr T
    L("done")
    emit(0x8e,0x38,0x27)                           # ld L,(XIZ+0x38)
    emit(0xcf,0xcc,0xf0)                           # and L,0xF0      keep font
    emit(0xcf,0xe1)                                # or A,L
    emit(0xbe,0x38,0x41)                           # ld (XIZ+0x38),A
    emit(0xbe,0x24,0x62)                           # ld (XIZ+0x24),XDE
    emit(0x5b); emit(0x5a)                         # pop XHL ; pop XDE
    emit(0x0e)                                     # ret
    # --- big dialog font: 16x16, 4 tiles TL,TR,BL,BR -> column offsets 0x00,0x20,0x10,0x30
    L("big")
    emit(0x45,*imm32(CPU(WID)))                    # ld XIY,widths
    emit(0xc3,0x07,0xf4,0xe4,0x26)                 # ld H,(XIY+BC)   width
    emit(0x44,*imm32(CPU(COPY)))                   # ld XIX,left-aligned copies
    emit(0xd9,0xcf,NCOPY,0x00)                     # cp BC,NCOPY
    jr(0x67,"low")                                 # jr C
    emit(0x44,*imm32(CPU(ROMFONT)))                # ld XIX,ROM dialog font
    L("low")
    emit(0xd9,0xee,0x06)                           # sll 6,BC        64 bytes/glyph
    emit(0xf3,0x07,0xf0,0xe4,0x34)                 # lda XIX,XIX+BC
    emit(0xae,0x24,0x22)                           # ld XDE,(XIZ+0x24)  column start, row 0
    emit(0x8e,0x38,0x21)                           # ld A,(XIZ+0x38)
    emit(0xc9,0xcc,0x07)                           # and A,7
    emit(0xc9,0x81)                                # add A,A
    for t,adj in enumerate([None,0x10,-0x20,0x10]):
        if adj is not None:
            if adj>0: emit(0xda,0xc8,adj,0x00)     # add DE,adj
            else: emit(0xda,0xca,-adj,0x00)        # sub DE,-adj
        rows("b%d"%t)
    jp("adv0")
    for pos,n in fix:
        r=lab[n]-(pos+1); assert -128<=r<128,n; a[pos]=r&0xff
    for pos,n in fixj:
        v=CPU(CODE)+lab[n]; a[pos:pos+3]=[v&0xff,(v>>8)&0xff,v>>16]
    return bytes(a)

def metrics(d):
    """Big font: -> (widths[NCH], copies bytes for codes < NCOPY)."""
    wid=bytearray([PITCH]*NCH); cp=bytearray()
    for c in range(NCOPY):
        P=glyph_px(d,c); b=ink(P)
        if c==0x20: wid[c]=SPACE
        elif 0x19<=c<=0x1F: wid[c]=c-0x18; P=[[0]*16 for _ in range(16)]   # 1-7 px blanks, as in the 8x8 font
        elif b is None: wid[c]=0 if c<0x20 else SPACE
        else:
            l,r=b; P=[row[l:]+[0]*l for row in P]; wid[c]=r-l+1+GAP
        cp+=pack(P)
    return wid,bytes(cp)

def widths8(d):
    """8x8 font advance widths used for dialog text: the game's own, except the space."""
    w=fix8(d[W8:W8+NCH]); w[0x20]=SPACE8
    return bytes(w)

def apply(d):
    code=build_code(); wid,cp=metrics(d)
    assert CODE+len(code)<=WID and WID+NCH<=COPY and COPY+len(cp)<=SAVE_AREA
    d[CODE:CODE+len(code)]=code; d[WID:WID+NCH]=wid; d[COPY:COPY+len(cp)]=cp
    for c,v in FIX8.items(): d[W8+c]=v
    assert COPY+len(cp)<=W8V and W8V+NCH<=SAVE_AREA; d[W8V:W8V+NCH]=widths8(d)
    # hook at 0x212428: jp VWF   (keep ld (XIZ+0x2c),XWA before it)
    j=CPU(CODE); d[0x12428:0x1242c]=bytes([0x1b,j&0xff,(j>>8)&0xff,j>>16])
    assert d[0x123ea:0x123ee]==bytes([0x8e,0x38,0x3d,0x08]); d[0x123ea:0x123ee]=b"\0\0\0\0"   # no 12px toggle
    assert d[0x123d9:0x123dd]==bytes([0xbe,0x38,0x00,0x08]); d[0x123dc]=0                      # string start: sub-pixel 0, font 0
    assert d[0x1241a:0x1241e]==bytes([0xbe,0x38,0x00,0x00]); d[0x1241a:0x1241e]=bytes([0x8e,0x38,0x3c,0xf0])  # newline: and (XIZ+0x38),0xF0 (keep font)
    return d
if __name__=="__main__":
    open("work/dis/vwf.bin","wb").write(build_code())
