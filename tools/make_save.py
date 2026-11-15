"""Put a saved game with every minigame unlocked into a build: python tools/make_save.py <in.ngc> <out.ngc>
The game saves into its own cartridge flash at file 0x1F8000-0x1F9FFF: 32 slots of 256 bytes. A slot is 0x00, the 77 saved
bytes (RAM 0x4520-0x456C), then a checksum = sum of the first 78 bytes; the rest stays 0xFF (routines 0x20181a save,
0x201894 load: it takes the highest slot with byte 0 = 0 and a good checksum). Slot 0 is written here, the other 31 stay blank,
so the game's next save goes to slot 1 and later ones keep the newest.
Saved state: games 1-30 unlocked and cleared (flag bytes 0x4526-0x4543 = 0xF8: high nibble F = unlocked, bit 3 = cleared,
rank bits 0-2 = 0), counter A 1000 and counter B 255 (the maximums: all visitors and events become available), mood 0.
All 30 cleared bits make routine 0x216b60 show the hidden menu page E (Love Love Profile catalog), and the visitor-met bits
0x4558-0x4563 are all set so every profile in it is unlocked. The fast-unlock patch's seen bits and calendar (0x4544-0x4557) and the
staff-roll state (0x4568-0x456C) stay zero, as on a new game. Note: with every visitor marked met, the fast-unlock patch's
unseen-first picker treats all visitors as already seen.
An emulator that keeps its own save file (.ngf, .sav, MAME nvram) uses that instead of the cartridge copy: delete it first."""
import sys
src, dst = sys.argv[1], sys.argv[2]
d = bytearray(open(src, "rb").read())
BASE = 0x1F8000
if any(b != 0xFF for b in d[BASE:BASE + 0x2000]): raise SystemExit("the save area 0x1F8000-0x1F9FFF is not blank in " + src)
ram = bytearray(77)                                   # RAM 0x4520 + i
ram[0:2] = (1000).to_bytes(2, "little")               # counter A
ram[2] = 0                                            # mood
ram[3:5] = (255).to_bytes(2, "little")                # counter B
for g in range(1, 31): ram[0x4525 + g - 0x4520] = 0xF8   # unlocked + cleared
for a in range(0x4558, 0x4564): ram[a - 0x4520] = 0xFF        # every visitor met = every profile unlocked
slot = bytes([0]) + bytes(ram)
slot += bytes([sum(slot) & 0xFF])
d[BASE:BASE + len(slot)] = slot
open(dst, "wb").write(d)
print(f"{src} -> {dst}: save slot 0 with games 1-30 unlocked + cleared, page E with all profiles, counter A 1000, counter B 255")
