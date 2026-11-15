"""python mapfind.py dump.bin plane row c0 c1 -> ROM positions holding that row of the tilemap (byte or word encodings, any base)"""
import sys, numpy as np
from vram import mapent
R = np.frombuffer(open('../../rom/original.ngc', 'rb').read(), dtype=np.uint8)
def search(seq, word):
    n = len(seq); hits = []
    if word:
        for al in (0, 1):
            W = R[al:al + (len(R)-al)//2*2].view('<u2').astype(np.int32)
            ok = np.ones(len(W)-n, bool)
            for i in range(1, n): ok &= (W[i:len(W)-n+i] - W[:len(W)-n]) == (seq[i]-seq[0])
            hits += [(int(p)*2+al, int(W[p])) for p in np.nonzero(ok)[0]]
    else:
        B = R.astype(np.int32); ok = np.ones(len(B)-n, bool)
        for i in range(1, n): ok &= ((B[i:len(B)-n+i] - B[:len(B)-n]) & 255) == ((seq[i]-seq[0]) & 255)
        hits = [(int(p), int(B[p])) for p in np.nonzero(ok)[0]]
    return hits
def find(v, kind, row, c0, c1):
    ents = [mapent(v, kind, row*32+c) for c in range(c0, c1)]
    out = {}
    out['word'] = [(hex(p), hex(w), hex(ents[0]-w)) for p, w in search(ents, True)][:10]
    out['byte'] = [(hex(p), hex(b), hex(((ents[0] & 0x1ff)-b))) for p, b in search([e & 0x1ff for e in ents], False)][:10]
    return ents, out
if __name__ == "__main__":
    v = open(sys.argv[1], 'rb').read()
    e, o = find(v, sys.argv[2], *map(int, sys.argv[3:6]))
    print(' '.join('%04x' % x for x in e)); print(o)
