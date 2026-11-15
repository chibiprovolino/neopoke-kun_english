"""Re-import graphics-text PNGs exported by the survey (gfx/<name>.png + gfx/<name>.json) into a ROM image.
NOT wired into tools/insert.py yet (see script/graphics_text.md, "Re-import plan").

    python tools/gfx_import.py <in.ngc> <out.ngc> [name ...] [--dry-run]

With no names, every gfx/*.json that has a "cells" list is processed (i.e. the survey items, not the
older title_logo / menu_icon_text / exit_icon / profile_* files, which tools/gfx_patch.py handles).

How it works, per item:
  * Each 8x8 cell of the PNG is matched by colour (RGB) against the item's palette(s) in the JSON, so it does
    not matter whether the editor saved the PNG indexed or as RGB. Colour 0 = transparent.
  * A cell whose pixels did not change keeps its tile (an unedited PNG rebuilds the ROM byte for byte).
  * A changed cell reuses an identical tile already in the block, or takes a free tile: one that no cell of the
    whole map uses any more (tiles shared with the rest of the screen are never overwritten).
  * The new tile bytes are written in place in the tile block, and the map cell (word or byte map) is rewritten.
    Everything stays the same size: no free space is used and nothing is repointed.
  * If the drawing needs more distinct tiles than the block can give, the item is skipped with an error.
    (Then: simplify the art, or relocate the tile block to free space, which needs the loader pointer changed:
    the screen-table record (+4) or the object command's tile pointer; both are listed in the JSON.)
Limitations (on purpose, keep it simple): no flipped-tile matching for new tiles, and palette numbers can only
change on word maps (byte maps get their palette from the game code)."""
import json, os, struct, sys
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
GFX = os.path.join(ROOT, 'gfx')


def tile_get(d, off):
    return tuple(tuple(((d[off+y*2] | d[off+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)) for y in range(8))


def tile_bytes(px):
    out = bytearray()
    for row in px:
        w = 0
        for x, c in enumerate(row): w |= (c & 3) << (14-2*x)
        out += bytes((w & 255, w >> 8))
    return bytes(out)


def flip(px, h, v):
    rows = list(px)[::-1] if v else list(px)
    return tuple(tuple(r[::-1]) if h else tuple(r) for r in rows)


def load_item(name):
    meta = json.load(open(os.path.join(GFX, name + '.json'), encoding='utf-8'))
    im = Image.open(os.path.join(GFX, meta['png'])).convert('RGB')
    if list(im.size) != meta['size_px']:
        raise ValueError('%s: PNG is %dx%d, must stay %dx%d' % (name, *im.size, *meta['size_px']))
    return meta, im


class Map:
    """Read/write access to the item's whole map in the ROM (screen word map, object word map or object byte map)."""
    def __init__(self, d, meta):
        m = meta['map']; self.d = d
        self.fmt, self.w, self.h = m['format'], m['width'], m['height']
        self.base = int(m['rom'], 16) + (4 if m.get('header') else 0)

    def get(self, i):
        if self.fmt == 'byte': return self.d[self.base+i], None, 0, 0
        e = struct.unpack_from('<H', self.d, self.base+i*2)[0]
        return e & 0x1ff, (e >> 9) & 15, e >> 15 & 1, e >> 14 & 1

    def put(self, i, t, p, h, v):
        if self.fmt == 'byte':
            self.d[self.base+i] = t
        else:
            old = struct.unpack_from('<H', self.d, self.base+i*2)[0]
            e = (t & 0x1ff) | (p & 15) << 9 | (old & 0x2000) | (v & 1) << 14 | (h & 1) << 15
            struct.pack_into('<H', self.d, self.base+i*2, e)


# Tile blocks moved to free space and enlarged, so the redrawn art has room: screen record -> (new file offset, new tile count).
# The record (+4 tile pointer, +12 tile count) is rewritten; the old block is left in place, unused.
# The VRAM range base..base+count-1 must be unused on that screen (checked on VRAM dumps in work/gfxsurvey):
#   catalog  base 0x001: original 81 tiles to 0x051, nothing visible above it -> 140 tiles, to 0x08C
#   doki     base 0x100: original 134 to 0x185, HUD font from 0x1B0 -> 170 tiles, to 0x1A9
#   voff     base 0x138: original 196 to 0x1FB, 0x1FC-0x1FF blank -> 200 tiles, to 0x1FF (VRAM end)
GROW = {0x1c0424: (0x1B0000, 140), 0x1c0384: (0x1B1000, 170), 0x1c0444: (0x1B2000, 200)}


def block(d, meta):
    """Tile block (file offset, count) for this item, moving/enlarging it first if it is listed in GROW."""
    T0, N = int(meta['tiles']['rom'], 16), meta['tiles']['count']
    rec = meta['map'].get('record_rom')
    if not rec or int(rec, 16) not in GROW:
        return T0, N
    rec = int(rec, 16); new, cnt = GROW[rec]
    if struct.unpack_from('<I', d, rec+4)[0] == new + 0x200000:
        return new, struct.unpack_from('<H', d, rec+12)[0]
    if any(b != 0xff for b in d[new:new+cnt*16]):
        raise ValueError('%s: free space at 0x%x is not free' % (meta['name'], new))
    d[new:new+N*16] = d[T0:T0+N*16]; d[new+N*16:new+cnt*16] = bytes((cnt-N)*16)
    struct.pack_into('<I', d, rec+4, new + 0x200000); struct.pack_into('<H', d, rec+12, cnt)
    return new, cnt


def import_item(d, name, log=print):
    meta, im = load_item(name)
    mp = Map(d, meta)
    T0, N = block(d, meta)
    r = meta['rect_in_map']; x0, y0, rw, rh = r['x'], r['y'], r['w'], r['h']
    idx = meta['palette']['png_index_map']
    rgb2 = {}                     # rgb -> list of (palette, colour)
    for e in idx:
        if e['index'] == 0: continue
        rgb2.setdefault(tuple(e['rgb']), []).append((e['palette'], e['colour']))
    zero = tuple(idx[0]['rgb'])
    cells = [(y0+cy)*mp.w + x0+cx for cy in range(rh) for cx in range(rw)]
    inside = set(cells)
    # 1. wanted pixels (colour indices) + palette per cell
    want = []
    for k, i in enumerate(cells):
        cx, cy = (k % rw)*8, (k//rw)*8
        t, p, h, v = mp.get(i)
        if p is None: p = meta['cells'][k][1]
        # choose one palette for the whole cell: one that has every colour used (a colour may exist in several palettes)
        cols = {im.getpixel((cx+x, cy+y)) for y in range(8) for x in range(8)} - {zero}
        for c in cols:
            if c not in rgb2:
                x, y = next((x, y) for y in range(8) for x in range(8) if im.getpixel((cx+x, cy+y)) == c)
                raise ValueError('%s: pixel (%d,%d) colour %s is not in the item palette' % (name, cx+x, cy+y, c))
        fits = set.intersection(*[{o[0] for o in rgb2[c]} for c in cols]) if cols else {p}
        if not fits: raise ValueError('%s: cell %d,%d mixes colours of different palettes' % (name, cx//8, cy//8))
        np_ = p if p in fits else min(fits)
        cmap = {c: next(o[1] for o in rgb2[c] if o[0] == np_) for c in cols}
        rows = tuple(tuple(0 if im.getpixel((cx+x, cy+y)) == zero else cmap[im.getpixel((cx+x, cy+y))] for x in range(8))
                     for y in range(8))
        if np_ != p and mp.fmt == 'byte': raise ValueError('%s: cell %d,%d uses palette %d, byte maps are fixed to %d' % (name, cx//8, cy//8, np_, p))
        want.append((rows, np_))
    # 2. keep unchanged cells
    keep, todo = {}, []
    for k, i in enumerate(cells):
        t, p, h, v = mp.get(i)
        if t < N and flip(tile_get(d, T0+t*16), h, v) == want[k][0] and (p is None or p == want[k][1]):
            keep[i] = (t, p, h, v)
        else:
            todo.append(k)
    if not todo:
        log('%-22s unchanged' % name); return 0
    # 3. free tiles: not referenced by any cell outside the rect nor by kept cells
    # cells the game always redraws at runtime (e.g. a picture loaded over a placeholder) don't hold on to their ROM tile
    ow = set()
    for rr in meta.get('runtime_overwritten', []):
        ow |= {(rr['y']+yy)*mp.w + rr['x']+xx for yy in range(rr['h']) for xx in range(rr['w'])}
    used = set()
    for i in range(mp.w*mp.h):
        if i in inside and i not in keep: continue
        if i in ow: continue
        used.add(mp.get(i)[0])
    free = [t for t in range(N) if t not in used]
    existing = {tile_get(d, T0+t*16): t for t in sorted(used) if t < N}
    needed = len({want[k][0] for k in todo if want[k][0] not in existing})
    if needed > len(free):
        raise ValueError('%s: out of tiles: the drawing needs %d new different tiles, only %d are free (remove %d)'
                         % (name, needed, len(free), needed - len(free)))
    new = 0
    for k in todo:
        px, p = want[k]
        t = existing.get(px)
        if t is None:
            if not free: raise ValueError('%s: out of tiles (block has %d, all others in use)' % (name, N))
            t = free.pop(0); d[T0+t*16:T0+t*16+16] = tile_bytes(px); existing[px] = t; new += 1
        mp.put(cells[k], t, p if p is not None else 0, 0, 0)
    log('%-22s %d cells changed, %d new tiles, %d free tiles left' % (name, len(todo), new, len(free)))
    return len(todo)


def import_raw(d, name, log=print):
    """Items without a map (sprite frames, tiles loaded by code such as the Garou fight HUD name plates):
    the PNG's 8x8 cells are written in order over the item's tile block, same size, in place."""
    meta, im = load_item(name)
    T0, N = int(meta['tiles']['rom'], 16), meta['tiles']['count']
    w, h = meta['size_px']
    if (w // 8) * (h // 8) != N: raise ValueError('%s: %dx%d px is not %d tiles' % (name, w, h, N))
    idx = {tuple(e['rgb']): e['index'] for e in meta['palette']['png_index_map'] if 'rgb' in e}
    rgb = im.convert('RGB'); changed = 0
    for k in range(N):
        cx, cy = (k % (w // 8)) * 8, (k // (w // 8)) * 8
        rows = []
        for y in range(8):
            r = []
            for x in range(8):
                c = rgb.getpixel((cx+x, cy+y))
                if c not in idx and c != (255, 0, 255):
                    raise ValueError('%s: pixel (%d,%d) colour %s is not in the item palette' % (name, cx+x, cy+y, c))
                r.append(idx.get(c, 0))
            rows.append(tuple(r))
        b = tile_bytes(tuple(rows))
        if d[T0+k*16:T0+k*16+16] != b: d[T0+k*16:T0+k*16+16] = b; changed += 1
    log('%-22s %s' % (name, '%d tiles rewritten (raw)' % changed if changed else 'unchanged'))
    return changed


RAW = ['garou_name_terry_hud', 'garou_name_andy_hud']


def items():
    out = []
    for f in sorted(os.listdir(GFX)):
        if f.endswith('.json'):
            try:
                m = json.load(open(os.path.join(GFX, f), encoding='utf-8'))
                # sprite items ("frame", no map) are not handled here; items without a PNG in gfx/ are left as in the ROM
                if 'cells' in m and 'map' in m and os.path.exists(os.path.join(GFX, m['png'])): out.append(f[:-5])
            except ValueError:
                pass
    return out


def apply(d, names=None, log=print):
    """Import into bytearray d in place; returns number of changed cells."""
    n = 0
    for name in names or items() + [r for r in RAW if os.path.exists(os.path.join(GFX, r + '.png'))]:
        try:
            n += (import_raw if name in RAW else import_item)(d, name, log)
        except ValueError as e:
            log('SKIPPED ' + str(e))
    return n


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) < 2: sys.exit(__doc__)
    d = bytearray(open(args[0], 'rb').read())
    orig = bytes(d)
    apply(d, args[2:] or None)
    diff = sum(1 for a, b in zip(orig, d) if a != b)
    print('%d bytes differ from the input' % diff)
    if '--dry-run' not in sys.argv:
        open(args[1], 'wb').write(d); print('wrote', args[1])
