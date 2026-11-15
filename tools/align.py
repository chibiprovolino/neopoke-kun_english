import sys
d=open(sys.argv[1],"rb").read()
for off in range(0,16,2):
    s=0
    for t in range(64,256):
        b=d[0xc2000+off+t*16:0xc2000+off+t*16+16]
        if b[14:16]==b'\0\0' and b[0:2]==b'\0\0' and b!=b'\0'*16: s+=1
    print(off,s)
