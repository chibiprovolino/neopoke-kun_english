import sys
v=open(sys.argv[1],'rb').read(); rom=open('../../rom/original.ngc','rb').read()
for t in [int(x,16) for x in sys.argv[2:]]:
    b=v[0x2000+t*16:0x2010+t*16]; i=rom.find(b); print(hex(t),b.hex(),hex(i))
