"""Third survey (sprites + missed background text): python export_more.py [--force]
Screen items reuse export_items.build(); sprite items come from the frame tables decoded in frames.py."""
import json, os, sys
from PIL import Image
import export_items as E, frames
from vram import palw, rgb
D = frames.D; GFX = E.GFX
SCREEN = [
    dict(name='garou_oouzu', screen='Minigame "Garou" (player-select map, label under the whirlpool)', jp='大うず', meaning='Great whirlpool',
         kind='screen', rec=0x1C0204, rect=(16, 10, 3, 1), dump='o_garou2/v6710.bin', plane='p2', base=0x100),
    dict(name='temple_stone_tamashii', screen='Minigame g22 (temple stage background, standing stone on the left)', jp='魂', meaning='Soul / spirit',
         kind='screen', rec=0x1C0244, rect=(1, 11, 4, 3), dump='o_g22/v4410.bin', plane='p2', base=0x100),
    dict(name='temple_emblem', screen='Minigame g22 (temple stage background, round emblem on the wall)', jp='(one character in a circle, reading uncertain)',
         meaning='Temple crest; probably decorative', kind='screen', rec=0x1C0244, rect=(12, 10, 3, 3), dump='o_g22/v4410.bin', plane='p2', base=0x100),
]
# kind: 'F' = strip frame (frames.frames), 'A'/'B' = rectangular frame (frames.rect_frames); dump = (file, sprite/plane, palette) or None
SPRITE = [
    dict(name='sprite_genjitsu', off=0xf2bf3, screen='Sprite: stone block lettering (never seen in MAME; which minigame is unknown)', jp='現実', meaning='Reality', dump=None),
    dict(name='sprite_halo_kanji', off=0xf2a15, screen='Sprite: fallen round-headed figure with a halo, one kanji on its head (never seen in MAME)',
         jp='(one kanji on the head, reading uncertain: 仰 / 抑?)', meaning='unknown', dump=None),
    dict(name='sprite_robot_kanji', off=0xf0d89, screen='Sprite: barrel-shaped robot with a kanji painted on its side (never seen in MAME)',
         jp='(one kanji, reading uncertain: 祭?)', meaning='unknown (祭 = festival)', dump=None),
    dict(name='garou_name_terry_hud', off=0xe30c8, screen='Minigame "Garou": second copy of the Terry name plate (sprite tiles)', jp='テリ〜', meaning='Terry',
         dump=('o_garou2/v7310.bin', 'p1', 8)),
]
def sprite(it):
    F = {f['off']: f for f in frames.frames()}; R = {f['off']: f for f in frames.rect_frames()}
    if it['off'] in F:
        f = F[it['off']]; cells = frames.cells(f); fmt = 'strip frame: [tiles*8 u16][tile ptr u32][x s8][y s8][rows u8][code0]{[code][dx s8]}; a row has (0x50-code)/5 tiles'
    else:
        f = R[it['off']]; cells = [(t, (i % f['w'])*8, (i//f['w'])*8) for i, t in enumerate(f['map'])]
        fmt = ('rect frame A: [tile ptr u32][x s8][y s8][w][h][tiles*8 u16]' if f['fmt'] == 'A' else 'rect frame B: [x s8][y s8][w][h][tiles*8 u16][tile ptr u32][w*h tile indexes]')
    W = max(c[1] for c in cells)+8; H = max(c[2] for c in cells)+8
    if it['dump']:
        v = open(it['dump'][0], 'rb').read(); words = palw(v, it['dump'][1], it['dump'][2]); cols = [rgb(w) for w in words]; src = '%s, %s palette %d' % it['dump']
    else:
        words = None; cols = [None, (96, 96, 96), (176, 176, 176), (255, 255, 255)]; src = 'unknown: never on screen in MAME; greys stand for colours 1-3'
    png_pal = [(255, 0, 255)]+cols[1:]
    im = Image.new('P', (W, H)); im.putpalette([x for c in png_pal for x in c])
    for t, x, y in cells:
        tl = frames.tile(f['tiles']+t*16)
        for yy in range(8):
            for xx in range(8): im.putpixel((x+xx, y+yy), tl[yy][xx])
    png = os.path.join(GFX, it['name']+'.png')
    if os.path.exists(png) and '--force' not in sys.argv: print('kept', png)
    else: im.save(png)
    im.resize((W*4, H*4), Image.NEAREST).save(os.path.join(GFX, it['name']+'_ref.png'))
    meta = dict(name=it['name'], screen=it['screen'], japanese=it['jp'], meaning=it['meaning'], png=it['name']+'.png', preview_4x=it['name']+'_ref.png',
                size_px=[W, H], compression='none (raw NGPC 2bpp tiles, 16 bytes per 8x8 tile)',
                tiles=dict(rom=hex(f['tiles']), cpu=hex(f['tiles']+0x200000), count=f['n'], bytes=f['n']*16, end_rom=hex(f['tiles']+f['n']*16)),
                frame=dict(rom=hex(it['off']), format=fmt), cells=[list(c) for c in cells], cells_format='[tile, x px, y px] (sprites, 8x8 each)',
                palette=dict(source=src, png_index_map=[dict(index=0, note='transparent, shown as magenta')]+[
                    dict(index=i, rgb=list(png_pal[i]), **({'rgb444': '0x%03X' % words[i]} if words else {})) for i in (1, 2, 3)]),
                max_size=dict(px=[W, H], note='Sprite: keep the same cells (other frames of the animation may share these tiles).'))
    json.dump(meta, open(os.path.join(GFX, it['name']+'.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return meta
if __name__ == '__main__':
    for it in SCREEN:
        m = E.build(it); print(it['name'], m['size_px'], m['tiles']['shared_with_rest_of_screen'])
    for it in SPRITE:
        m = sprite(it); print(it['name'], m['size_px'])
