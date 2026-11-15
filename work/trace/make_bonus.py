"""Test ROM for the staff roll: python work/trace/make_bonus.py [rom/original.ngc] [work/trace/bonus.ngc]
Sets file 0x14093 to 0 (the 1-in-16 mask of the staff-roll roll), so every menu exit with counter A >= 500 plays the staff roll."""
import sys
src = sys.argv[1] if len(sys.argv) > 1 else "rom/original.ngc"
dst = sys.argv[2] if len(sys.argv) > 2 else "work/trace/bonus.ngc"
d = bytearray(open(src, "rb").read())
assert d[0x14091:0x14094] == bytes([0xC9, 0xCC, 0x0F]), "unexpected bytes at 0x14091"
d[0x14093] = 0
open(dst, "wb").write(d)
print("wrote", dst)
