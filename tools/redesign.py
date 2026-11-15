"""Prototype of the "seen it once" progression (alternative to the plain translation patch).
  python tools/redesign.py <in.ngc> <out.ngc>
Works on the original ROM or on a translated build (the VWF block must end below 0x1F7800).

What it changes
  1. Counter A only grows when a scene is seen for the first time (+GAIN), and the pickers offer unseen scenes first.
  2. Leaving the minigame menu while happy (mood below 0) always sends Poke-kun to work; work uses up some of the happiness.
  3. The clock is replaced by a calendar of 12 dates x 7 times of day that moves one step on every menu exit.
  4. Unlock thresholds are evenly spaced, record requirements are scaled to the new score, and scene conditions are loosened
     (narrow mood bands, follow-up events can start alone, visitors need no particular room event, more bathroom visits).
  5. The staff roll shows on 1 menu exit in 4 once counter A is 100.
New saved bytes live in 0x4544-0x4557, which the game saves but never uses."""
import sys, struct

# ---- tuning -------------------------------------------------------------------------------------------------
GAIN = 5                       # counter A per new scene (194 scenes -> 970 of the 1000 cap)
A_STEP, A_FIRST = 24, 5        # game n needs counter A >= A_FIRST + A_STEP*(n-1)   (game 30: 701 = 141 scenes)
B_STEP, B_FIRST = 1, 1         # game n needs counter B >= B_FIRST + B_STEP*(n-1)   (game 30: 30)
MINA_SCALE = 0.6               # record "counter A needed" values are multiplied by this
WORK = [(-81, 8, 30), (-61, 6, 25), (-41, 5, 20), (-21, 4, 15), (0, 3, 8)]   # five brackets: (mood below this, counter B gained, mood added)
IDLE_DRIFT = 0                 # mood added by the idle default event (the game's value is 2)
# Loosening after the play test: the automated player never reached about 60 scenes with the conditions as shipped.
ROOM_EDGE = {34: 8, 35: 9, 67: 16, 68: 17}     # room mood bands: the game's edges at +-34/35 and +-67/68 move to +-8/9 and +-16/17
OTHER_EDGE = {67: 8, 68: 9}                    # visitor and megaphone mood bands: +-67/68 move to +-8/9
FOLLOWUP_CHANCE = 40           # room records that could only start as a follow-up (chance 0) can now also start alone (x/256 per check)
DROP_ROOM_PREREQ = True        # visitors no longer need one particular room event to have been the last one
SEASONAL_ANY_MOOD = (65, 66, 67, 68)   # room records for Christmas, New Year, Halloween and blossom: any mood
BATHROOM = {182: 255}          # room record -> chance: he goes to the bathroom more often by day (visitors 70-89 only call then)
BATHROOM_VISITORS_ANY_HOUR = True   # visitors 70-89: the bathroom events are daytime only, so their night-time records could never match
BATHROOM_VISITORS_ANY_STATE = True  # visitors 70-89 also call while he is in the room (the automated player met only 3-5 of the 20 otherwise)
STAFF_A, STAFF_MASK = 100, 0x03   # staff roll: needs counter A >= STAFF_A, shows when (random & STAFF_MASK) == 0
DATES = [(1, 3), (2, 10), (3, 20), (4, 5), (5, 10), (6, 20), (8, 1), (9, 20), (10, 28), (11, 15), (12, 5), (12, 22)]
TIMES = [(10, 0), (12, 30), (16, 30), (18, 30), (19, 30), (22, 0), (2, 0)]
# ---- addresses ----------------------------------------------------------------------------------------------
ORG = 0x1F7800                 # file offset of the new code and tables (free up to the save area at 0x1F8000)
SEEN_ROOM, SEEN_WIG, SEEN_MEGA, CAL = 0x4544, 0x454F, 0x4552, 0x4554   # RAM, all inside the saved block
MET = 0x4558                   # the game's own "visitor met" bits
CPU = lambda f: f + 0x200000
TABLES = [("room", 0x40000, 1, 202, 0x11, SEEN_ROOM), ("visitor", 0x42000, 1, 263, 0x13, MET),
          ("wiggle", 0x45000, 1, 17, 0x16, SEEN_WIG), ("megaphone", 0x46000, 0, 40, 0x10, SEEN_MEGA)]


def s8(b): return b - 256 if b > 127 else b
def u8(v): return v & 0xFF
def i32(v): return list(struct.pack("<I", v))
def a16(v): return [v & 0xFF, v >> 8]
def a24(v): return [v & 0xFF, (v >> 8) & 0xFF, v >> 16]


class Asm:
    """Just enough TLCS-900 to write the routines below. Every encoding was copied from the game's own code."""
    def __init__(self, org): self.org, self.b, self.lab, self.fix = org, [], {}, []
    def emit(self, *bs): self.b.extend(bs)
    def L(self, n): self.lab[n] = len(self.b)
    def here(self): return self.org + len(self.b)
    def rel(self, ops, n): self.b.extend(list(ops) + [0]); self.fix.append((len(self.b) - 1, n))
    def jr(self, cc, n): self.rel([{"Z": 0x66, "C": 0x67, "T": 0x68, "NZ": 0x6E}[cc]], n)
    def djnz(self, r, n): self.rel({"C": [0xCB, 0x1C], "B": [0xCA, 0x1C], "BC": [0xD9, 0x1C], "WA": [0xD8, 0x1C]}[r], n)
    def call(self, a): self.emit(0x1D, *a24(a))
    def jp(self, a): self.emit(0x1B, *a24(a))
    def done(self):
        for pos, n in self.fix:
            d = self.lab[n] - (pos + 1); assert -128 <= d <= 127, n; self.b[pos] = d & 0xFF
        return bytes(self.b)


def build_code():
    a = Asm(CPU(ORG)); sub = {}
    def S(n): sub[n] = a.here()
    # BT: is bit A of the bitmap at XIX clear?  -> Z if clear.  Uses A, XHL, XIX.
    S("BT")
    a.emit(0xEB, 0xA8, 0xC9, 0x8F, 0xDB, 0xEF, 0x03, 0xC9, 0xCC, 0x07, 0xEB, 0x84)   # ld XHL,0 / ld L,A / srl 3,HL / and A,7 / add XIX,XHL
    a.call(0x200D56); a.emit(0x0E)                                                   # bit A,(XIX) / ret
    # BS: set bit A of the bitmap at XIX.  Uses A, W, XHL, XIX.
    S("BS")
    a.emit(0xEB, 0xA8, 0xC9, 0x8F, 0xDB, 0xEF, 0x03, 0xC9, 0xCC, 0x07, 0xEB, 0x84)
    a.emit(0x84, 0x20); a.call(0x200D1A); a.emit(0xB4, 0x40, 0x0E)                   # ld W,(XIX) / set A,W / ld (XIX),W / ret
    # AWARD: A = scene number, XIX = bitmap. First time: mark it and add GAIN to counter A.
    S("AWARD")
    a.emit(0xC9, 0x8C, 0x3C); a.call(sub["BT"]); a.emit(0x5C, 0xB0, 0xFE)            # ld D,A / push XIX / call BT / pop XIX / ret NZ
    a.emit(0xCC, 0x89); a.call(sub["BS"])                                            # ld A,D / call BS
    S("ADD")
    a.emit(0x30, *a16(GAIN), 0xD1, 0x20, 0x45, 0x88, 0x0E)                           # ld WA,GAIN / add (0x4520),WA / ret
    # per-table award stubs, called with XIY = the chosen record (they replace "ld WA,(XIY+0x0d) / add (0x4520),WA")
    for name, off, lo, hi, key, bitmap in TABLES:
        S("AW_" + name)
        a.emit(0x8D, key, 0x21, 0x44, *i32(bitmap))                                  # ld A,(XIY+key) / ld XIX,bitmap
        if name == "visitor":                                                        # the game sets the met bit itself, later
            a.call(sub["BT"]); a.emit(0xB0, 0xFE); a.jp(sub["ADD"])                  # call BT / ret NZ / jp ADD
        else:
            a.jp(sub["AWARD"])
    # per-table filters: keep only the unseen candidates if there are any, then redo the game's "is the list empty" test
    for name, off, lo, hi, key, bitmap in TABLES:
        S("FI_" + name); p = name[0]
        if name != "visitor":       # byte list at 0x6202, count at 0x6201
            a.emit(0x44, *i32(0x6202), 0x45, *i32(0x6202), 0xC1, 0x01, 0x62, 0x23, 0x22, 0x00, 0xCB, 0xD8)   # XIX=XIY=list / ld C,(count) / ld B,0 / cp C,0
            a.jr("Z", p + "done")
            a.L(p + "loop")
            a.emit(0xC5, 0xF0, 0x21, 0xC9, 0x88)                                     # ld A,(XIX+) / ld W,A
            a.emit(0xEB, 0xA8, 0xC9, 0x8F, 0xDB, 0xEE, 0x05, 0x42, *i32(CPU(off)), 0xEA, 0x83, 0x8B, key, 0x21)   # XHL = record / ld A,(XHL+key)
            a.emit(0x3C, 0x44, *i32(bitmap)); a.call(sub["BT"]); a.emit(0x5C)        # push XIX / ld XIX,bitmap / call BT / pop XIX
            a.jr("NZ", p + "next")
            a.emit(0xF5, 0xF4, 0x40, 0xCA, 0x61)                                     # ld (XIY+),W / inc 1,B
            a.L(p + "next"); a.djnz("C", p + "loop")
            a.emit(0xCA, 0xD8); a.jr("Z", p + "done")                                # cp B,0
            a.emit(0xF1, 0x01, 0x62, 0x42)                                           # ld (0x6201),B
            a.L(p + "done"); a.emit(0xC1, 0x01, 0x62, 0x3F, 0x00, 0x0E)              # cp (0x6201),0 / ret
        else:                       # word list at 0x6204, count at 0x6202; 0x6200 is free here and counts the kept ones
            a.emit(0x44, *i32(0x6204), 0x45, *i32(0x6204), 0xD1, 0x02, 0x62, 0x21, 0xF1, 0x00, 0x62, 0x02, 0x00, 0x00)   # XIX=XIY=list / ld BC,(count) / ld (0x6200),0
            a.emit(0xD1, 0x02, 0x62, 0x3F, 0x00, 0x00); a.jr("Z", p + "done")        # cp (0x6202),0
            a.L(p + "loop")
            a.emit(0xD5, 0xF1, 0x20, 0x28)                                           # ld WA,(XIX+) / push WA
            a.emit(0xEB, 0xA8, 0xD8, 0x8B, 0xDB, 0xEE, 0x05, 0x42, *i32(CPU(off)), 0xEA, 0x83, 0x8B, key, 0x21)   # XHL = record / ld A,(XHL+key)
            a.emit(0x3C, 0x44, *i32(bitmap)); a.call(sub["BT"]); a.emit(0x5C, 0x48)  # ... / pop XIX / pop WA
            a.jr("NZ", p + "next")
            a.emit(0xF5, 0xF5, 0x50, 0xD1, 0x00, 0x62, 0x61)                         # ld (XIY+),WA / incw 1,(0x6200)
            a.L(p + "next"); a.djnz("BC", p + "loop")
            a.emit(0xD1, 0x00, 0x62, 0x3F, 0x00, 0x00); a.jr("Z", p + "done")        # cp (0x6200),0
            a.emit(0xD1, 0x00, 0x62, 0x20, 0xF1, 0x02, 0x62, 0x50)                   # ld WA,(0x6200) / ld (0x6202),WA
            a.L(p + "done"); a.emit(0xD1, 0x02, 0x62, 0x3F, 0x00, 0x00, 0x0E)        # cp (0x6202),0 / ret
    # CALADV: next calendar step on every menu exit, then the routine the hook replaced
    S("CALADV")
    a.emit(0xC1, *a16(CAL), 0x21, 0xC9, 0x61, 0xC9, 0xCF, len(DATES) * len(TIMES))   # ld A,(CAL) / inc 1,A / cp A,84
    a.jr("C", "calok"); a.emit(0x21, 0x00)                                           # ld A,0
    a.L("calok"); a.emit(0xF1, *a16(CAL), 0x41); a.jp(0x2057E0)                      # ld (CAL),A / jp 0x2057e0
    # STAFFRNG: the random number for the staff roll, forced to "no" when he is happy, so a staff roll never replaces a work session
    S("STAFFRNG")
    a.call(0x200DF2); a.emit(0xC1, 0x22, 0x45, 0x20, 0xC8, 0xCC, 0x80, 0xB0, 0xF6, 0x21, 0x01, 0x0E)   # call rng / ld W,(mood) / and W,0x80 / ret Z / ld A,1 / ret
    # INIT: new game -> clear the new saved bytes (and do the instruction the hook replaced)
    S("INIT")
    a.emit(0xF1, 0x6C, 0x45, 0x00, 0x00, 0x30, 0x14, 0x00, 0x42, *i32(0x4544))       # ld (0x456c),0 / ld WA,20 / ld XDE,0x4544
    a.L("iloop"); a.emit(0xF5, 0xE8, 0x00, 0x00); a.djnz("WA", "iloop"); a.emit(0x0E)   # ld (XDE+),0 / djnz WA / ret
    code = a.done()
    # calendar table: 256 entries of month, day, hour, minute (index = step mod 84, so a stray value is harmless)
    S("CALTAB")
    n = len(DATES) * len(TIMES)
    tab = b"".join(bytes(DATES[(i % n) // len(TIMES)] + TIMES[(i % n) % len(TIMES)]) for i in range(256))
    return code + tab, sub


def clock_code(caltab):
    """Replaces the body of 0x205acc (read the BIOS clock into 0x43a0..0x43a3): month, day, hour, minute from the calendar."""
    b = [0xE8, 0xA8, 0xC1, *a16(CAL), 0x21, 0xD8, 0xEE, 0x02, 0x44, *i32(caltab), 0xE8, 0x84]   # ld XWA,0 / ld A,(CAL) / sll 2,WA / ld XIX,tab / add XIX,XWA
    for k in range(4): b += [0xC5, 0xF0, 0x21, 0xF1, *a16(0x43A0 + k), 0x41]                    # ld A,(XIX+) / ld (0x43a0+k),A
    return bytes(b + [0x0E])


def put(d, off, old, new, what):
    old, new = bytes(old), bytes(new)
    assert d[off:off + len(old)] == old, "unexpected bytes at %06x (%s): %s" % (off, what, d[off:off + len(old)].hex(" "))
    assert len(new) == len(old), what
    d[off:off + len(new)] = new


def apply(d):
    code, sub = build_code()
    assert all(b == 0xFF for b in d[ORG:0x1F8000]), "the area for the new code is not free"
    assert len(code) <= 0x1F8000 - ORG
    d[ORG:ORG + len(code)] = code
    call = lambda n: [0x1D, *a24(sub[n])]
    # --- hooks: filters (replace the "is the list empty" compare) and awards (replace the counter A add)
    put(d, 0x5549, [0xC1, 0x01, 0x62, 0x3F, 0x00], call("FI_room") + [0], "room filter")
    put(d, 0x59D1, [0xC1, 0x01, 0x62, 0x3F, 0x00], call("FI_wiggle") + [0], "wiggle filter")
    put(d, 0x542C, [0xC1, 0x01, 0x62, 0x3F, 0x00], call("FI_megaphone") + [0], "megaphone filter")
    put(d, 0x584B, [0xD1, 0x02, 0x62, 0x3F, 0x00, 0x00], call("FI_visitor") + [0, 0], "visitor filter")
    add = [0x9D, 0x0D, 0x20, 0xD1, 0x20, 0x45, 0x88]
    for off, n in ((0x5578, "room"), (0x587E, "visitor"), (0x59FC, "wiggle"), (0x5457, "megaphone")):
        put(d, off, add, call("AW_" + n) + [0, 0, 0], n + " award")
    put(d, 0x58A1, [0xD8, 0xA9], [0xD8, 0xA8], "no counter A for an empty doorbell ring")
    # --- calendar
    c = clock_code(sub["CALTAB"]); assert len(c) <= 0x5B02 - 0x5ACC
    assert d[0x5ACC:0x5AD1] == bytes([0x44, 0x9F, 0x43, 0x00, 0x00])
    d[0x5ACC:0x5ACC + len(c)] = c
    put(d, 0x14081, [0x1D, 0xE0, 0x57, 0x20], call("CALADV"), "calendar step on menu exit")
    put(d, 0x18EE, [0xF1, 0x6C, 0x45, 0x00, 0x00], call("INIT") + [0], "new-game init")
    # --- staff roll
    put(d, 0x14085, [0xD1, 0x20, 0x45, 0x3F, 0xF4, 0x01], [0xD1, 0x20, 0x45, 0x3F, *a16(STAFF_A)], "staff roll threshold")
    put(d, 0x14091, [0xC9, 0xCC, 0x0F], [0xC9, 0xCC, STAFF_MASK], "staff roll chance")
    put(d, 0x1408D, [0x1D, 0xF2, 0x0D, 0x20], call("STAFFRNG"), "staff roll only when not happy")
    # --- work on menu exit: always when happy, pay by bracket, mood back to -20..-1
    assert d[0x150B8:0x150C2] == bytes.fromhex("af07c305d703eb010000")
    assert len(WORK) == 5
    wt = b"".join(bytes([u8(m), 0x0F]) for m, _, _ in WORK)
    d[0x150B8:0x150C2] = wt
    scene = [0x0E, 0x0B, 0x08, 0x05, 0x05]
    gains = b"".join(bytes([g, 0, u8(md), scene[i]]) for i, (_, g, md) in enumerate(WORK))
    d[0x150CC:0x150E0] = gains; d[0x150E0:0x150F4] = gains
    # --- unlock thresholds (31 pairs; entry 0 mirrors game 1)
    assert struct.unpack_from("<2H", d, 0x16C0A + 120) == (1000, 250)
    for i in range(31):
        n = max(i, 1) - 1
        struct.pack_into("<2H", d, 0x16C0A + 4 * i, A_FIRST + A_STEP * n, B_FIRST + B_STEP * n)
    # --- records
    for name, off, lo, hi, key, bitmap in TABLES:
        edge = ROOM_EDGE if name == "room" else OTHER_EDGE
        for i in range(lo, hi):
            r = off + i * 32
            for k in (8, 9):
                v = s8(d[r + k])
                if abs(v) in edge: d[r + k] = u8(edge[abs(v)] * (1 if v > 0 else -1))
            a = struct.unpack_from("<H", d, r + 11)[0]
            struct.pack_into("<H", d, r + 11, int(round(a * MINA_SCALE / 5.0)) * 5)
            if name == "room" and d[r + 15] == 0: d[r + 15] = FOLLOWUP_CHANCE
            if name == "visitor" and DROP_ROOM_PREREQ: d[r + 27] = 0
            if name == "visitor" and s8(d[r + 8]) > s8(d[r + 9]): d[r + 8], d[r + 9] = d[r + 9], d[r + 8]      # two records have their mood bounds the wrong way round and can never match
            if name == "visitor" and BATHROOM_VISITORS_ANY_HOUR and d[r + 19] >= 70: d[r + 4:r + 8] = bytes([0, 0, 23, 59])
            if name == "visitor" and BATHROOM_VISITORS_ANY_STATE and d[r + 19] >= 70: d[r + 21:r + 26] = bytes(5)
    put(d, 0x55CA, [0xC1, 0x22, 0x45, 0x3F, 0x22], [0xC1, 0x22, 0x45, 0x3F, ROOM_EDGE[34]], "mood edge for the unhappy default events")
    if BATHROOM_VISITORS_ANY_STATE:        # the visitor check also has a hard-coded "ids 70 and up only in the bathroom" test
        put(d, 0x5980, [0xD8, 0xCF, 0x46, 0x00], [0xD8, 0xCF, 0xFF, 0x00], "bathroom visitors in any state")
    for i in SEASONAL_ANY_MOOD: d[0x40000 + i * 32 + 8] = u8(-100); d[0x40000 + i * 32 + 9] = 100
    for i, c in BATHROOM.items():
        d[0x40000 + i * 32 + 15] = c; d[0x40000 + i * 32 + 8] = u8(-100); d[0x40000 + i * 32 + 9] = 100
    for i in range(1, 9):                      # the default events are added to counter A directly: no points
        struct.pack_into("<H", d, 0x40000 + i * 32 + 13, 0)
    for i in range(5, 9):
        assert d[0x40000 + i * 32 + 10] == 2; d[0x40000 + i * 32 + 10] = IDLE_DRIFT
    return sub, len(code)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    d = bytearray(open(src, "rb").read())
    sub, n = apply(d)
    open(dst, "wb").write(d)
    print("%s -> %s: %d bytes of code and tables at %06x" % (src, dst, n, ORG))
    print(" ".join("%s=%06x" % kv for kv in sub.items()))
