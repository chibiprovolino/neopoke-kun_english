"""Build the review table for graphics text: python tools/gfx_review_table.py
-> gfx/REVIEW.md and gfx/REVIEW.csv (file, proposed transcription, proposed translation, empty revision column).
Transcriptions come from gfx/<name>.json where it exists; proposals live in PROPOSED below. An existing REVIEW.csv keeps its revision column."""
import csv, glob, json, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); GFX = os.path.join(ROOT, 'gfx')
NOJSON = {  # first survey: PNG only
    'title_logo': 'ガンバレ ねおぽけくん(仮)™', 'menu_icon_text': '予定地', 'exit_icon': '退 (above the word EXIT)',
    'profile_date_label': 'DATE/ メッセージ', 'profile_kore': 'これ'}
KEEP = '(leave as is)'
PROPOSED = {
    'title_logo': 'GANBARE! NEOPOKE-KUN (TEMP)', 'menu_icon_text': 'SOON', 'exit_icon': '← (arrow; EXIT is already written below)',
    'profile_date_label': 'DATE/ MESSAGE', 'profile_kore': 'THIS',
    'menuE_caption': 'Take a look!', 'catalog_title_love': 'LOVE LOVE', 'catalog_title_file': 'FILE', 'catalog_bubble': 'No creeps allowed.',
    'roswell_sign': 'NEO CARNIVAL', 'doki_title': 'DOKI DOKI STREET', 'doki_menu_new': 'NEW GAME', 'doki_menu_continue': 'CONTINUE',
    'voff_logo': 'VIRTUAL OFF (one logo in two layers: outline/backdrop + orange fill; combined preview voff_title_ref.png)', 'voff_labels': KEEP + ' mock spec labels',
    'bw_warning': "GANBARE NEOPOKE-KUN (TEMP) can't be played in black & white. Please enjoy it in color. Sorry!",
    'kenka_bath_sign': 'STIFFY SPA (crude joke; or leave as is)', 'kenka_bath_noren': KEEP + ' bath-house symbol', 'kenka_bath_ji': KEEP,
    'kenka_bath_notice': KEEP + ' unreadable', 'garou_chinohate': "World's End", 'garou_oouzu': 'Maelstrom', 'garou_settei': 'SETUP',
    'garou_player_select': 'PLAYER SELECT', 'garou_name_terry': 'TERRY', 'garou_name_terry_hud': 'TERRY', 'garou_name_andy': 'ANDY',
    'yabou_kassen': 'BATTLE!!', 'yabou_appare': 'BRAVO!!', 'yabou_munen': 'DEFEAT!!', 'yabou_tenka_touitsu': 'CONQUEST!',
    'menu_icon_kaihatsu': 'WIP', 'temple_stone_tamashii': 'SOUL (or leave as is)', 'temple_emblem': KEEP,
    'sprite_genjitsu': 'REALITY', 'sprite_halo_kanji': KEEP + ' until the kanji is confirmed', 'sprite_robot_kanji': KEEP + ' until the kanji is confirmed'}
MERGE = {'voff_logo': ['voff_subtitle']}  # one graphic in several layers: one row, files listed together
ORDER = list(PROPOSED)
def rows():
    names = sorted({os.path.basename(f)[:-4] for f in glob.glob(os.path.join(GFX, '*.png')) if not f.endswith('_ref.png')},
                   key=lambda n: (ORDER.index(n) if n in ORDER else 999, n))
    out = []; skip = {x for v in MERGE.values() for x in v}
    for n in names:
        if n in skip: continue
        j = os.path.join(GFX, n + '.json')
        jp = json.load(open(j, encoding='utf-8'))['japanese'] if os.path.exists(j) else NOJSON.get(n, '')
        out.append([' + '.join(x + '.png' for x in [n] + MERGE.get(n, [])), jp, PROPOSED.get(n, '')])
    return out
if __name__ == '__main__':
    old = {}
    c = os.path.join(GFX, 'REVIEW.csv')
    if os.path.exists(c):
        for r in list(csv.reader(open(c, encoding='utf-8-sig')))[1:]:
            if len(r) > 3: old[r[0]] = r[3]
    R = [r + [old.get(r[0], '')] for r in rows()]
    head = ['File (gfx/)', 'Proposed transcription', 'Proposed translation', 'Revision']
    w = csv.writer(open(c, 'w', encoding='utf-8-sig', newline='')); w.writerow(head); w.writerows(R)
    esc = lambda s: s.replace('|', '&#124;')
    with open(os.path.join(GFX, 'REVIEW.md'), 'w', encoding='utf-8') as f:
        f.write('# Graphics text review\n\nFill in the Revision column (here or in `REVIEW.csv`, which opens in Excel). '
                'Each file has a 4x preview next to it, `<name>_ref.png`.\nRegenerate with `python tools/gfx_review_table.py` (revisions typed in the CSV are kept).\n\n')
        f.write('| ' + ' | '.join(head) + ' |\n|---|---|---|---|\n')
        for r in R: f.write('| %s | %s | %s | %s |' % (' + '.join('[`%s`](%s)' % (x, x[:-4] + '_ref.png') for x in r[0].split(' + ')), esc(r[1]), esc(r[2]), esc(r[3])) + chr(10))
    print(len(R), 'rows;', sum(1 for r in R if not r[2]), 'without a proposal;', sum(1 for r in R if not r[1]), 'without a transcription')
