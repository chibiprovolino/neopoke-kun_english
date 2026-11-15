"""Export graphics-text items found by the survey to gfx/<name>.png (+ _ref.png 4x preview, + .json metadata).
Run from work/gfxsurvey:  python export_items.py [--force]
Palettes come from MAME VRAM dumps (o_*/v*.bin made by batch.py / run.sh); see ITEMS for which dump each item uses."""
import json, os, struct, sys
from PIL import Image
from vram import mapent, palw, rgb
import screens

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
D = open(os.path.join(ROOT, 'rom', 'original.ngc'), 'rb').read()
GFX = os.path.join(ROOT, 'gfx')
u16 = lambda o: struct.unpack_from('<H', D, o)[0]

# kind 'screen': record in the screen table at 0x1C0000 (word map, raw tiles). kind 'object': tile-load command in 0xD2E00-0xD9200.
ITEMS = [
    dict(name='menuE_caption', screen='Minigame menu, page E (picture caption)', jp='みんなみてね!', meaning='Everyone, take a look!',
         kind='screen', rec=0x1C0414, rect=(7, 12, 6, 1), dump='o_cat/v3420.bin', plane='p2', base=1),
    dict(name='catalog_title_love', screen='Love Love Profile catalog (title, top line)', jp='ラブラブ', meaning='Love Love (letters inside two hearts)',
         kind='screen', rec=0x1C0424, rect=(2, 1, 9, 3), dump='o_cat/v4280.bin', plane='p2', base=1),
    dict(name='catalog_title_profile', screen='Love Love Profile catalog (title, bottom line)', jp='プロファイル', meaning='Profile (whole title: ラブラブプロファイル, "Love Love Profile")',
         kind='screen', rec=0x1C0424, rect=(1, 5, 18, 3), dump='o_cat/v4280.bin', plane='p2', base=1),
    dict(name='catalog_bubble', screen='Love Love Profile catalog (speech bubble)', jp='あやしいカタは おことわりします。',
         meaning='Suspicious persons will be turned away. (lit. "We decline suspicious people.")',
         kind='screen', rec=0x1C0424, rect=(3, 14, 9, 3), dump='o_cat/v4280.bin', plane='p2', base=1),
    dict(name='roswell_sign', screen='Minigame "Roswell" (stage sign)', jp='ネオカーニバル', meaning='Neo Carnival',
         kind='screen', rec=0x1C0274, rect=(3, 0, 14, 2), dump='o_g24/v4570.bin', plane='p2', base=0x160),
    dict(name='doki_title', screen='Minigame "Doki Doki Street" (title screen logo)', jp='ドキドキストリート', meaning='Doki Doki Street ("Heart-pounding Street")',
         kind='screen', rec=0x1C0384, rect=(0, 1, 20, 7), dump='o_doki/v5900.bin', plane='p2', base=0x100),
    dict(name='doki_menu_new', screen='Minigame "Doki Doki Street" (title menu, line 1)', jp='はじめから', meaning='From the beginning (New game)',
         kind='screen', rec=0x1C0384, rect=(7, 10, 10, 2), dump='o_doki/v5900.bin', plane='p2', base=0x100),
    dict(name='doki_menu_continue', screen='Minigame "Doki Doki Street" (title menu, line 2)', jp='つづきから', meaning='Continue (from where you left off)',
         kind='screen', rec=0x1C0384, rect=(7, 13, 10, 2), dump='o_doki/v5900.bin', plane='p2', base=0x100),
    dict(name='voff_logo', screen='Minigame "V.OFF" title (big logo, back plane)', jp='バーチャルオフ', meaning='Virtual Off (parody of "Virtual On")',
         kind='screen', rec=0x1C0444, rect=(0, 3, 20, 4), dump='o_g27/v4490.bin', plane='p2', base=0x138),
    dict(name='voff_subtitle', screen='Minigame "V.OFF" title (small line, front plane)', jp='バーチャル オフ', meaning='Virtual Off',
         kind='screen', rec=0x1C0454, rect=(2, 4, 16, 2), dump='o_g27/v4490.bin', plane='p1', base=0x9C),
    dict(name='voff_labels', screen='Minigame "V.OFF" title (3 labels next to the robot)', jp='(3 lines of mock-kanji, approx. 射わ?天 / 従雷放光 / 超微子式)',
         meaning='Pseudo spec labels (parody of the Virtual On title); partly not real words — check in game',
         kind='screen', rec=0x1C0454, rect=(9, 10, 11, 7), dump='o_g27/v4490.bin', plane='p1', base=0x9C),
    dict(name='bw_warning', screen='Monochrome NGP warning (shown only on a black & white Neo Geo Pocket)',
         jp='ガンバレ ねおぽけくん(仮)は モノクロでは 遊べません カラーで ご賞味 下さい ゴメンニョ〜',
         meaning='"Ganbare Neo Poke-kun (Kari)" can\'t be played in monochrome. Please enjoy it in colour. Sorry~ (nyo = character verbal tic)',
         kind='screen', rec=0x1C0484, rect=(0, 1, 13, 14), dump='o_mono/v2400.bin', plane='p2', base=1, mono=True),
    dict(name='kenka_bath_sign', screen='Minigame "Kenka Yamete" (bath-house stage, sign; a 2nd copy at rows 18-19)', jp='強力ボッキ湯 (reading uncertain)',
         meaning='"Super-strength erection bath" (crude joke name of the bath house); check the reading',
         kind='screen', rec=0x1C0394, rect=(7, 2, 7, 2), dump='o_g21/v4490.bin', plane='p2', base=0x100),
    dict(name='kenka_bath_noren', screen='Minigame "Kenka Yamete" (bath-house curtain)', jp='ゆ', meaning='"yu" = hot water / bath (standard bath-house sign)',
         kind='screen', rec=0x1C0394, rect=(17, 13, 8, 3), dump='o_g21/v4490.bin', plane='p2', base=0x100),
    dict(name='kenka_bath_ji', screen='Minigame "Kenka Yamete" (bath-house, top-left tile)', jp='ぢ', meaning='"ji" (probably 痔 = hemorrhoids, a joke)',
         kind='screen', rec=0x1C0394, rect=(2, 0, 2, 2), dump='o_g21/v4490.bin', plane='p2', base=0x100),
    dict(name='kenka_bath_notice', screen='Minigame "Kenka Yamete" (bath-house, small notice at right edge, scrolled in)', jp='(tiny vertical text, unreadable)',
         meaning='Notice board (bath rules / prices?) — too small to read', kind='screen', rec=0x1C0394, rect=(28, 17, 4, 3),
         dump='o_g21/v4490.bin', plane='p2', base=0x100),
    dict(name='garou_chinohate', screen='Minigame "Garou" (player-select background, bottom right)', jp='ちのはて', meaning='"The ends of the earth" (place name / signature?)',
         kind='screen', rec=0x1C0204, rect=(16, 18, 4, 1), dump='o_garou2/v6710.bin', plane='p2', base=0x100),
    dict(name='garou_settei', screen='Minigame "Garou" (level-select heading "LEVEL設定")', jp='設定', meaning='Setting(s) — heading reads "LEVEL setting"',
         kind='object', cmd=0xD3210, dump='o_garou2/v6110.bin'),
    dict(name='garou_player_select', screen='Minigame "Garou" (player-select heading)', jp='ぷれいや〜せれくと', meaning='Player select',
         kind='object', cmd=0xD3248, dump='o_garou2/v6710.bin'),
    dict(name='garou_name_terry', screen='Minigame "Garou" (player select + fight HUD)', jp='テリ〜', meaning='Terry',
         kind='object', cmd=0xD3256, dump='o_garou2/v6710.bin'),
    dict(name='garou_name_andy', screen='Minigame "Garou" (player select + fight HUD)', jp='アンディ', meaning='Andy',
         kind='object', cmd=0xD3264, dump='o_garou2/v6710.bin'),
    dict(name='yabou_kassen', screen='Minigame "Mr. Yabou" (battle start)', jp='合戦!!', meaning='Battle!!',
         kind='object', cmd=0xD32C6, dump='o_yabou/v6760.bin'),
    dict(name='yabou_appare', screen='Minigame "Mr. Yabou" (battle won; not reached in MAME)', jp='天晴れ!!', meaning='Splendid!! / Well done!!',
         kind='object', cmd=0xD32D4, dump='o_yabou/v6760.bin', plane='p1', pal=2, assumed='palette copied from 合戦!! (same plane/palette slot)'),
    dict(name='yabou_munen', screen='Minigame "Mr. Yabou" (battle lost)', jp='無念!!', meaning='Alas!! / How regrettable!! (defeat)',
         kind='object', cmd=0xD32E2, dump='o_yabou/v7120.bin'),
    dict(name='yabou_tenka_touitsu', screen='Minigame "Mr. Yabou" (game cleared; not reached in MAME)', jp='天下統一', meaning='Unification of the realm (Japan conquered)',
         kind='object', cmd=0xD32F0, dump='o_yabou/v7120.bin', plane='p1', pal=2, assumed='palette copied from 無念!! (same plane/palette slot)'),
    dict(name='menu_icon_kaihatsu', screen='Minigame menu icon "under construction" (traffic cone; not seen on any menu page)', jp='開発中',
         meaning='Under development', kind='object', cmd=0xD2FC8, dump='o_unl_0x4500_0x4557/v2900.bin', plane='p2',
         assumed='never shown in MAME; palette = the map\'s palette number, colours from the unlocked menu screen'),
]

def obj_rec(cmd):
    import objs2
    for o in objs2.objs:
        if o['cmd'] == cmd:
            objs2.compose(o); return o
    raise KeyError(hex(cmd))

def mono_rgb(v, plane, pal):
    b = {'p1': 0x108, 'p2': 0x110, 'spr': 0x100}[plane] + pal * 4
    return [None] + [(255*(7-(v[b+c] & 7))//7,)*3 for c in (1, 2, 3)]

def tile_px(off):
    return [[((D[off+y*2] | D[off+y*2+1] << 8) >> (14-2*x)) & 3 for x in range(8)] for y in range(8)]

def find_vram_use(v, first_vram, n):
    """-> (plane, palette) of the first map cell or sprite using a tile in [first_vram, first_vram+n)"""
    from vram import sprites
    for k in ('p1', 'p2'):
        for i in range(1024):
            e = mapent(v, k, i)
            if first_vram <= (e & 0x1ff) < first_vram+n: return k, (e >> 9) & 15
    for s in sprites(v):
        if s[7] and first_vram <= s[1] < first_vram+n: return 'spr', s[4]
    return None, None

def build(it):
    v = open(it['dump'], 'rb').read()
    if it['kind'] == 'screen':
        m, t, w, h, n, fl = screens.rec(it['rec'])
        x0, y0, rw, rh = it['rect']
        full = [u16(m+i*2) for i in range(w*h)]
        cells = []
        for r in range(rh):
            for c in range(rw):
                e = full[(y0+r)*w + x0+c]
                cells.append(dict(t=e & 0x1ff, p=(e >> 9) & 15, h=bool(e & 0x8000), v=bool(e & 0x4000)))
        inside = set((y0+r)*w+x0+c for r in range(rh) for c in range(rw))
        outside_tiles = set(full[i] & 0x1ff for i in range(w*h) if i not in inside)
        plane = it['plane']
        mapinfo = dict(rom=hex(m), cpu=hex(m+0x200000), format='word', header=None, width=w, height=h,
                       entry='VRAM map entry = ROM word + 0x%X (tile base; tile index = word & 0x1FF counts from the start of the tile block)' % it['base'],
                       loader='screen table record 0x%X (pointer list at 0x1C0000): +0 map ptr, +4 tile ptr, +8 w, +10 h, +12 tile count, +14 flags' % it['rec'],
                       record_rom=hex(it['rec']))
        tiles_rom = t
    else:
        o = obj_rec(it['cmd']); t, n = o['tiles'], o['n']
        mp = o['usemap']; w, h = o['w'], o['h']; kind = o['kind']
        ents = [u16(mp+4+i*2) for i in range(w*h)] if kind == 'word' else list(D[mp+4:mp+4+w*h])
        x0, y0, rw, rh = 0, 0, w, h
        # palette / plane from the dump
        vi = None; pat = D[t:t+16*min(n, 3)]
        i = v.find(pat, 0x2000)
        if i >= 0 and (i-0x2000) % 16 == 0: vi = (i-0x2000)//16
        plane, pal = find_vram_use(v, vi, n) if vi is not None else (None, None)
        if it.get('plane'): plane = it['plane']
        if it.get('pal') is not None: pal = it['pal']
        cells = []
        for e in ents:
            if kind == 'word': cells.append(dict(t=e & 0x1ff, p=(e >> 9) & 15, h=bool(e & 0x8000), v=bool(e & 0x4000)))
            else: cells.append(dict(t=e, p=pal if pal is not None else 0, h=False, v=False))
        outside_tiles = set()
        mapinfo = dict(rom=hex(mp), cpu=hex(mp+0x200000), format=kind, header=list(D[mp:mp+4]), width=w, height=h,
                       entry=('ROM word = tile index | palette<<9 | Vflip<<14 | Hflip<<15 (tile index counts from the start of the tile block)' if kind == 'word'
                              else 'one byte per cell = tile index into the tile block; the palette is chosen by the game code (palette %s on %s here)' % (pal, plane)),
                       loader='object command at 0x%X: [op16][map16][01 00][tile ptr 24][00][count16]; the tile block of command k uses the map field of command k+1 (map = 0xD0000 + map16)' % it['cmd'],
                       command_rom=hex(it['cmd']), vram_first_tile_in_dump=vi)
        tiles_rom = t
    pals = sorted(set(c['p'] for c in cells))
    # colours
    pal_rgb = {}
    for p in pals:
        if it.get('mono'): pal_rgb[p] = mono_rgb(v, plane, (1 if p & 0x10 else 0))
        else: pal_rgb[p] = [None] + [rgb(wd) for wd in palw(v, plane, p)[1:]]
    if it.get('mono'):
        words = {p: [v[{'p1': 0x108, 'p2': 0x110}[plane]+c] & 7 for c in range(4)] for p in pals}
    else:
        words = {p: palw(v, plane, p) for p in pals}
    bg = (rgb(v[0x3e0] | v[0x3e1] << 8) if not it.get('mono') else (109, 109, 109))
    # png palette: 0 = transparent (shown as backdrop), then 3 colours per used palette
    inks = set(pal_rgb[p][c] for p in pals for c in (1, 2, 3))
    shown0 = bg if bg not in inks else (255, 0, 255)
    png_pal = [shown0]; index_map = [dict(index=0, palette=None, colour=0, rgb=list(shown0),
                                          note='transparent (colour 0 of every palette); shown as %s' % ('the screen backdrop colour' if shown0 == bg else 'magenta, because the backdrop colour equals an ink colour'))]
    for p in pals:
        for c in (1, 2, 3):
            index_map.append(dict(index=len(png_pal), palette=p, colour=c, rgb=list(pal_rgb[p][c]), rgb444=('0x%03X' % words[p][c]) if not it.get('mono') else 'mono shade %d' % words[p][c]))
            png_pal.append(pal_rgb[p][c])
    W, H = rw*8, rh*8
    im = Image.new('P', (W, H))
    flat = [x for c in png_pal for x in c]; im.putpalette(flat)
    used = []
    for k, cdef in enumerate(cells):
        cx, cy = (k % rw)*8, (k//rw)*8
        if cdef['t'] >= n:
            continue
        px = tile_px(tiles_rom + cdef['t']*16); used.append(cdef['t'])
        base = 1 + 3*pals.index(cdef['p'])
        for y in range(8):
            for x in range(8):
                col = px[7-y if cdef['v'] else y][7-x if cdef['h'] else x]
                im.putpixel((cx+x, cy+y), 0 if col == 0 else base+col-1)
    used_set = sorted(set(used))
    shared = sorted(set(used_set) & outside_tiles)
    os.makedirs(GFX, exist_ok=True)
    png = os.path.join(GFX, it['name'] + '.png')
    if os.path.exists(png) and '--force' not in sys.argv: print('kept', png)
    else: im.save(png)
    im.resize((W*4, H*4), Image.NEAREST).save(os.path.join(GFX, it['name'] + '_ref.png'))
    meta = dict(
        name=it['name'], screen=it['screen'], japanese=it['jp'], meaning=it['meaning'],
        png=it['name'] + '.png', preview_4x=it['name'] + '_ref.png', size_px=[W, H],
        compression='none (raw NGPC 2bpp tiles, 16 bytes per 8x8 tile)',
        tiles=dict(rom=hex(tiles_rom), cpu=hex(tiles_rom+0x200000), count=n, bytes=n*16, end_rom=hex(tiles_rom+n*16),
                   odd_address=bool(tiles_rom & 1), used_by_this_item=used_set, shared_with_rest_of_screen=shared),
        map=mapinfo,
        rect_in_map=dict(x=x0, y=y0, w=rw, h=rh),
        cells=[[c['t'], c['p'], int(c['h']), int(c['v'])] for c in cells], cells_format='[tile, palette, hflip, vflip] row by row',
        palette=dict(plane=plane, png_index_map=index_map, source=it['dump'] + ' (MAME VRAM dump)', assumed=it.get('assumed')),
        max_size=dict(px=[W, H], note=('Stay inside the %dx%d px area. The tile block holds %d tiles; tiles listed in shared_with_rest_of_screen '
                                       'are also used outside this area and must not change (or the map must be repointed to free tiles).' % (W, H, n))),
    )
    json.dump(meta, open(os.path.join(GFX, it['name'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return meta

if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    for it in ITEMS:
        if only and it['name'] not in only: continue
        m = build(it)
        print('%-22s %3dx%-3d tiles %s n=%d pal=%s plane=%s shared=%s' % (it['name'], *m['size_px'], m['tiles']['rom'], m['tiles']['count'],
              [e['palette'] for e in m['palette']['png_index_map'][1::3]], m['palette']['plane'], m['tiles']['shared_with_rest_of_screen']))
