"""Screenshot any string in the save-prompt box (a preview, not its real screen).
usage: python tools/tour/show.py <rom> <id> [<id> ...]
Makes a temp ROM whose save-prompt pointer (0xcc280) points at the string, runs routes/save.lua,
and leaves build/tour/show_<id>/."""
import os, sys, json, struct, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); import run_tour, idmap
S = json.load(open(os.path.join(ROOT, 'script', 'strings.json'), encoding='utf8'))
rom = bytearray(open(sys.argv[1], 'rb').read())
os.makedirs(run_tour.OUT, exist_ok=True)
for a in sys.argv[2:]:
    i = int(a); r = bytearray(rom)
    tgt = struct.unpack_from('<I', rom, int(S[i]['refs'][0], 16))[0]
    struct.pack_into('<I', r, 0xcc280, tgt)
    tmp = os.path.join(run_tour.OUT, f'show_{i}.ngc'); open(tmp, 'wb').write(r)
    idm = os.path.join(run_tour.OUT, 'idmap.lua'); idmap.build(tmp, idm)
    route = os.path.join(run_tour.OUT, f'show_{i}.lua')
    src = open(os.path.join(HERE, 'routes', 'save.lua')).read().replace('stop=4700', 'stop=2420').replace('name="save"', f'name="show_{i}"')
    open(route, 'w').write(src)
    name, shots = run_tour.run_route(tmp, route, idm)
    os.remove(tmp); os.remove(route)
    print(i, [s['file'] for s in shots if i in s['ids']])
