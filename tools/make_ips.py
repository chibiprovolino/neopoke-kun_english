"""Make an IPS patch from the original ROM to a build: python tools/make_ips.py <build.ngc> <out.ips> [rom/original.ngc]
Writes plain records (<= 65535 bytes each) and RLE records for long runs of one byte, then applies the patch back to the
original and checks the result is byte-identical to the build. Same-size ROMs only (IPS cannot shrink a file)."""
import sys, hashlib, zlib
build, out = sys.argv[1], sys.argv[2]
orig = sys.argv[3] if len(sys.argv) > 3 else "rom/original.ngc"
a, b = open(orig, "rb").read(), open(build, "rb").read()
assert len(a) == len(b), "ROM sizes differ"
EOF_MARK = 0x454F46                                   # an offset equal to "EOF" would end the patch early
def apply(src, ips):
    d = bytearray(src); assert ips[:5] == b"PATCH"; i = 5
    while ips[i:i + 3] != b"EOF":
        o = int.from_bytes(ips[i:i + 3], "big"); n = int.from_bytes(ips[i + 3:i + 5], "big"); i += 5
        if n: d[o:o + n] = ips[i:i + n]; i += n
        else: r = int.from_bytes(ips[i:i + 2], "big"); d[o:o + r] = ips[i + 2:i + 3] * r; i += 3
    return bytes(d)
recs = []; i = 0; n = len(a)
while i < n:
    if a[i] == b[i]: i += 1; continue
    j = i                                             # extend the changed run, bridging gaps of up to 5 equal bytes (a record costs 5)
    while j < n and (a[j] != b[j] or any(a[k] != b[k] for k in range(j, min(j + 6, n)))): j += 1
    recs.append((i, j)); i = j
ips = bytearray(b"PATCH")
for s, e in recs:
    p = s
    while p < e:
        if p == EOF_MARK: p -= 1                      # never start a record at "EOF" (cannot happen in a 2 MB ROM)
        r = p                                         # RLE for runs of 9+ identical bytes
        while r < e and b[r] == b[p] and r - p < 0xFFFF: r += 1
        if r - p >= 9:
            ips += p.to_bytes(3, "big") + b"\0\0" + (r - p).to_bytes(2, "big") + b[p:p + 1]; p = r; continue
        q = p                                         # plain record up to the next long run or 65535 bytes
        while q < e and q - p < 0xFFFF:
            r = q
            while r < e and b[r] == b[q] and r - q < 9: r += 1
            if r - q >= 9: break
            q += 1
        ips += p.to_bytes(3, "big") + (q - p).to_bytes(2, "big") + b[p:q]; p = q
ips += b"EOF"
assert apply(a, bytes(ips)) == b, "round trip failed"
open(out, "wb").write(ips)
print(f"{out}: {len(ips)} bytes, {len(recs)} changed ranges; applies to {orig} "
      f"(CRC32 {zlib.crc32(a):08X}) -> {build} (CRC32 {zlib.crc32(b):08X}, SHA-1 {hashlib.sha1(b).hexdigest()[:12]}...) - round trip OK")
