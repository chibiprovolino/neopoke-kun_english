"""Build a Lua table mapping CPU address ranges of every string in a built ROM to string ids."""
import json, struct, sys
def build(rom_path, out_path, strings='script/strings.json'):
    rom = open(rom_path, 'rb').read()
    S = json.load(open(strings, encoding='utf8'))
    rng = {}
    for s in S:
        for r in s['refs']:
            a = struct.unpack_from('<I', rom, int(r, 16))[0]
            f = a - 0x200000
            if not (0 <= f < len(rom)): continue
            e = rom.index(b'\0', f)
            rng.setdefault((a, a + (e - f) + 1), set()).add(s['id'])
    with open(out_path, 'w') as o:
        o.write('return {\n')
        for (a, b), ids in sorted(rng.items()):
            o.write('{%d,%d,{%s}},\n' % (a, b, ','.join(map(str, sorted(ids)))))
        o.write('}\n')
    lo = min(a for a, b in rng); hi = max(b for a, b in rng)
    return lo, hi
if __name__ == '__main__':
    print(build(sys.argv[1], sys.argv[2]))
