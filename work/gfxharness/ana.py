import sys
v=open(sys.argv[1],'rb').read()
print('scroll',v[0x32:0x36].hex(),'ctl30',hex(v[0x30]))
for name,mo in (('P1',0x1000),('P2',0x1800)):
    print(name)
    for r in range(32):
        row=[(v[mo+(r*32+c)*2]|v[mo+(r*32+c)*2+1]<<8) for c in range(32)]
        if any(row): print('%2d '%r+' '.join('%04x'%x if x else '....' for x in row))
print('sprites')
for k in range(64):
    o=0x800+k*4
    if v[o+1]&0x18: print(k,'t%03x f%02x x%d y%d p%d'%(v[o]|(v[o+1]&1)<<8,v[o+1],v[o+2],v[o+3],v[0xC00+k]))
