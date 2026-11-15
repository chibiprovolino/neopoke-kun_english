# Text outside the main script (graphics, tilemaps)

Survey of everything not printed by the main text routine. The patches are applied by `tools/gfx_patch.py`
(called from `tools/insert.py` before `vwf.apply`). **All English wording here is a draft for you to approve.**
**To redraw by hand:** edit the PNGs in `gfx/` (`title_logo.png` 144×40, `menu_icon_text.png` 32×7, `exit_icon.png` 16×8), using only the
4 palette colours already in each file, then rebuild with `tools/insert.py`. `python tools/gfx_export.py --original --force` resets them to the
Japanese art (for reference); without `--original` they show the current draft. The title logo must cut into at most 58 different 8×8 tiles.
Without PNGs, the build falls back to the text drafts in `DRAFT` / `EXIT_ARROW` in `tools/gfx_patch.py`.
Before/after screenshots (MAME): `build/gfx/title_compare.png`, `build/gfx/menu_compare.png`.

All patches overwrite data in place (same size), so **no free space is used**.

## Needs your approval

| # | Screen | Location (file offset) | Japanese | Meaning | Draft English | Status |
|---|---|---|---|---|---|---|
| 1 | Title logo, line 1 | tiles 0xF99E2 (58 tiles + blank 0x3A, VRAM tile 0x100+n), map 18×5 bytes at 0xDE1B2 (header `12 05` at 0xDE1B0) | ガンバレ | "Go for it!" | `GANBARE!` | **draft** — options: keep romaji, or "GO FOR IT!" |
| 2 | Title logo, line 2 | same | ねおぽけくん | "Neo Poke-kun" | `NEOPOKE-KUN` | **draft** |
| 3 | Title logo, tag | same | (仮) | "(provisional / working title)" | `(TEMP)` | **draft** — e.g. "(KARI)", "(BETA)", "(WIP)", or drop it |
| 4 | Purple minigame menu, all 5 icons | icon tiles 0x11F1F0 (4×4 tiles); text = tiles 12–15, pixel rows 1–7 | 予定地 | "planned site / reserved" | `SOON` | **draft** — 32 px wide max (~6 letters): "TBA", "SOON", "EMPTY" |
| 5 | Purple menu, EXIT button | tiles 0x1E0BE0/0x1E0BF0 **and** a copy at 0x1E3843 (the one actually loaded) | 退 (above the word EXIT) | "leave" | left arrow ← | **draft** — the word EXIT is already under it |
| 6 | Dating profile, under the photo | 9 tiles at 0x1E1430 (one row, text in pixel rows 0–5) → `gfx/profile_date_label.png` 72×8 | DATE/ メッセージ | "message" | yours to draw (e.g. `DATE/ MESSAGE`; only ~40 px for the word) | **template = original art** |
| 7 | Dating profile, top-right arrow | 3 tiles at 0x1E1260 → `gfx/profile_kore.png` 24×8 | これ | "this (one)" | yours to draw (e.g. `THIS`) | **template = original art**; one stray pixel of れ sits in tile 0x1E1320 below |

The title logo is limited to 58 unique 8×8 tiles in an 18×5 tile area (144×40 px); the draft uses 55.
Letters are the CFC2 font scaled ×2 with a 1 px outline, in the original colours (outline / line-1 fill / main fill).
The ™ mark of the original is not redrawn (it was part of the logo tiles); say if you want it back.

## Second survey (2026-11-14): minigames, catalog, shooter, B/W screen — English column is yours

Found by unlocking all minigames in MAME (RAM 0x4500–0x4557 = 0xFF), entering each of the 30, plus decoding the game's two
graphics tables (see "How the graphics are stored" below). **Every item is raw (uncompressed) 2bpp tiles.**
Each has `gfx/<file>.png` (native size, the exact in-game palette), `gfx/<file>_ref.png` (4× preview) and `gfx/<file>.json`
(ROM tile block, map location and format, the cells of the area, palette with RGB444 values, tiles shared with the rest of the screen, max size).
The PNGs hold the original Japanese art. Colour 0 = transparent (shown as the screen backdrop, or magenta when that equals an ink colour).
Items with more than one palette (marked *multi*) have 3 colours per palette in the PNG; one 8×8 cell can only use colours of one palette.

| # | Screen | File (`gfx/`) | Size px | Tiles (file offset, count) | Japanese | Literal meaning | English (yours) |
|---|---|---|---|---|---|---|---|
| 8 | Minigame menu, page E: caption under the picture | `menuE_caption` | 48×8 | 0x1E0A40, 0x26 | みんなみてね! | "Everyone, take a look!" | |
| 9 | Love Love Profile catalog: title, top line (letters inside two hearts) | `catalog_title_love` | 72×24 | 0x1E0CA0, 0x51 | ラブラブ | "Love Love" | |
| 10 | Love Love Profile catalog: title, bottom line (whole title: ラブラブプロファイル) | `catalog_title_profile` | 144×24 | same block | プロファイル | "Profile" | |
| 11 | Love Love Profile catalog: speech bubble (*multi*: text + bubble edge) | `catalog_bubble` | 72×24 | same block | あやしいカタは おことわりします。 | "Suspicious persons will be turned away." | |
| 12 | Minigame "Roswell": stage sign | `roswell_sign` | 112×16 | 0x1E555B, 0x55 | ネオカーニバル | "Neo Carnival" | |
| 13 | Minigame "Doki Doki Street" (rock-paper-scissors date): title logo (*multi*) | `doki_title` | 160×56 | 0x1E14BB, 0x86 | ドキドキストリート | "Doki Doki (heart-pounding) Street" | |
| 14 | same, title menu line 1 | `doki_menu_new` | 80×16 | same block | はじめから | "From the beginning" (new game) | |
| 15 | same, title menu line 2 | `doki_menu_continue` | 80×16 | same block | つづきから | "Continue (from where you left off)" | |
| 16–17 | Minigame "V.OFF" (the shooter): title logo, **one graphic in two layers** — back plane = textured backdrop + dark letter outline, front plane = orange letter fill, placed at x=16, y=8 inside the back one (combined preview `voff_title_ref.png`); redraw both together | `voff_logo` (back) + `voff_subtitle` (front) | 160×32 + 128×16 | 0x1E3903, 0xC4 + 0x1E5E4A, 0x9A | バーチャルオフ | "Virtual Off" (parody of *Virtual On*) | |
| 18 | same, title, 3 coloured labels next to the robot (*multi*, 7 palettes) | `voff_labels` | 88×56 | same block | approx. 射わ?天 / 従雷放光 / 超微子式 (reading uncertain) | mock "spec" labels, probably not real words | |
| 19 | Black & white NGP warning (only on a monochrome Neo Geo Pocket; captured with MAME `ngp`) | `bw_warning` | 104×112 | 0x1E88A4, 0xDD | ガンバレ ねおぽけくん(仮)は モノクロでは 遊べません カラーで ご賞味 下さい ゴメンニョ〜 | "Ganbare Neo Poke-kun (Kari) can't be played in monochrome. Please enjoy it in colour. Sorry-nyo~" | |
| 20 | Minigame "Kenka Yamete": bath-house sign (a 2nd copy at map rows 18–19 shares the tiles) | `kenka_bath_sign` | 56×16 | 0x1D92D8, 0xCE | 強力ボッキ湯 (reading uncertain) | "Super-strength erection bath" (crude joke name) | |
| 21 | same, bath-house curtain | `kenka_bath_noren` | 64×24 | same block | ゆ | "hot water" — the standard bath-house sign | |
| 22 | same, small framed tile top-left | `kenka_bath_ji` | 16×16 | same block | ぢ | "ji" (probably 痔, hemorrhoids — a joke) | |
| 23 | same, tiny notice at the right edge | `kenka_bath_notice` | 32×24 | same block | (unreadable, ~3 columns of vertical text) | bath rules / prices? | |
| 24 | Minigame "Garou": player-select background, bottom right | `garou_chinohate` | 32×8 | 0x1E47AC, 0xCB | ちのはて | "the ends of the earth" (stage name?) | |
| 25 | same, level-select heading `LEVEL設定` (LEVEL is already English) | `garou_settei` | 32×16 | 0x147400, 8 | 設定 | "setting(s)" | |
| 26 | same, player-select heading | `garou_player_select` | 104×16 | 0x10B8C9, 0x17 | ぷれいや〜せれくと | "player select" | |
| 27 | same, name plate (player select + fight HUD) | `garou_name_terry` | 32×8 | 0x12E2D1, 4 | テリ〜 | "Terry" | |
| 28 | same, name plate | `garou_name_andy` | 40×8 | 0x10014F, 5 | アンディ | "Andy" | |
| 29 | Minigame "Mr. Yabou": battle start (brush lettering) | `yabou_kassen` | 152×64 | 0x184E3D, 0x60 | 合戦!! | "Battle!!" | |
| 30 | same, battle won (not reached; palette copied from #29) | `yabou_appare` | 152×64 | 0x12EE50, 0x5C | 天晴れ!! | "Splendid!! / Bravo!!" | |
| 31 | same, battle lost | `yabou_munen` | 152×56 | 0x12F2A0, 0x61 | 無念!! | "Alas!! / How regrettable!!" | |
| 32 | same, game cleared (not reached; palette copied from #31) | `yabou_tenka_touitsu` | 152×56 | 0x10C148, 0x69 | 天下統一 | "Unification of the realm" | |
| 33 | Minigame-menu icon "under construction" (traffic cone; not seen on any page, palette is a guess) | `menu_icon_kaihatsu` | 32×32 | 0x0F9D80, 0xD | 開発中 | "Under development" | |

Notes for redrawing:
- **Size:** stay inside the PNG. The tile budget is the block's count; tiles listed under `shared_with_rest_of_screen` in the JSON
  are also used elsewhere on that screen and are never overwritten (e.g. #20's sign copy, the bubble edge of #11).
- #18 and #20–#23 are background details; you may decide to leave them in Japanese. #30, #32, #33 were never seen in MAME.
- The tiny squiggles on the unlocked minigame-menu icons (e.g. `xIxI.xIx` under each picture) are decorative greeking, not text.

### How the graphics are stored (all raw)
- **Screen table** at 0x1C0000: a list of 32-bit pointers (CPU address) to 16-byte records at 0x1C00F4–0x1C049F:
  `+0` map pointer, `+4` tile pointer (often an odd address), `+8` width, `+10` height (tiles), `+12` tile count, `+14` flags.
  Maps are 16-bit words: `tile | palette<<9 | Vflip<<14 | Hflip<<15`; the game adds a tile base when loading (base per screen in each JSON).
  59 screens; all were rendered (`work/gfxsurvey/screens/`) and checked by eye.
- **Object commands** at 0xD2E00–0xD9200: `[op16][map16][01 00][tile ptr 24][00][count16]`. The tile block of a command uses the map field
  of the **next** command (map at 0xD0000 + map16). Maps there start `[b0 b1 w h]` and hold either 16-bit words (as above) or one byte per cell
  (palette chosen by code). 156 objects; all rendered (`work/gfxsurvey/ob2_*.png`) and checked by eye.
- Other sprite tiles (minigame characters etc.) are loaded by code; everything seen in the ~1,600 VRAM dumps was checked on screen.

## Third survey (2026-11-14): sprites and missed background text
The second survey only read the two background tables and what appeared in ~10-40 s of each minigame, so sprites loaded by game code
were never checked. They are now decoded statically (`work/gfxsurvey/frames.py`, all raw 16-byte tiles):
- **Strip frames** (1,185 at 0xDE8B4-0xF2EC5): `[tiles*8 u16][tile ptr u32][x s8][y s8][rows u8][code0]{[code][dx s8]}`; a row holds (0x50-code)/5 tiles, dx shifts it.
- **Rect frames A** (853) `[tile ptr u32][x][y][w][h][tiles*8 u16]` and **B** (521) `[x][y][w][h][tiles*8 u16][tile ptr u32][w*h tile indexes]`, at 0xE1680-0xF2FDD.
All ~2,400 frames and the 59 screens were looked at again. New items (exported by `work/gfxsurvey/export_more.py`):

| # | Where | File (`gfx/`) | Japanese | Meaning |
|---|---|---|---|---|
| 34 | Garou player-select map, under the whirlpool | `garou_oouzu` | 大うず | "Great whirlpool" |
| 35 | Temple stage (g22) background, standing stone | `temple_stone_tamashii` | 魂 | "Soul" |
| 36 | Temple stage background, round wall emblem | `temple_emblem` | one character, unreadable | crest, probably decorative |
| 37 | Sprite, stone-block lettering (not seen in MAME, greys) | `sprite_genjitsu` | 現実 | "Reality" |
| 38 | Sprite, fallen figure with halo, kanji on its head (not seen, greys) | `sprite_halo_kanji` | reading uncertain (仰/抑?) | ? |
| 39 | Sprite, barrel robot with a kanji on its side (not seen, greys) | `sprite_robot_kanji` | reading uncertain (祭?) | ? |
| 40 | Garou, second copy of the Terry name plate (sprite tiles 0xFF65B) | `garou_name_terry_hud` | テリ〜 | "Terry" |

Seen and left out: tombstone scribbles on the graveyard stage (screen 0x1C0254), tiny marks on a clown's apron (frames 0xF1546...), the L/O/V/E letter sprites (English).
Still unchecked: about 68 KB of tile data in 0xF3027-0x1B0000 that none of the decoded tables point to (`work/gfxsurvey/gaps.json`; it looks like picture
fragments), about 45 small format-A frames that render scrambled (tile order unknown), and palettes for #37-#39.
`gfx_import.py` does not handle the sprite items yet.

**Review table:** `gfx/REVIEW.md` / `gfx/REVIEW.csv` (file, transcription, proposed translation, empty Revision column), built by `python tools/gfx_review_table.py`.

## Re-import plan (not wired in yet)
1. Redraw a `gfx/<file>.png` from the table above, using only its palette colours (index 0 = transparent).
2. `python tools/gfx_import.py rom/original.ngc build/gfx_test.ngc [file ...] [--dry-run]` writes the edited items into a copy of the ROM:
   unchanged cells keep their tiles (an unedited set rebuilds the ROM byte for byte; checked), changed cells reuse identical tiles or take tiles
   no cell of that screen uses any more, and the map cells are rewritten. Same size, in place, **no free space used**. It refuses an item that
   needs more distinct tiles than its block has, or a cell that mixes palettes.
3. Check in MAME (`work/gfxsurvey/batch.py` with `ROM=...` reaches each minigame; routes in `work/gfxsurvey/sel.py`). Tested on a scratch copy:
   設定 → "SETUP", the catalog bubble and the Roswell sign changed in game as drawn.
4. When the art is approved: call `gfx_import.apply(d)` from `tools/insert.py` next to `gfx_patch.apply(d)` (one line). If an item needs more
   tiles than its block, move that block to free space and change its loader pointer (screen record `+4`, or the command's tile pointer);
   both locations are in the JSON. That step is not implemented.

## Already English — no change needed
- HUD labels as 16-bit tile codes: `HUNGRYTIME` (0x51AFC), `SCORE` (0x4ABB4), `TIME` (0x4ACD4); "neopoke Escape" at 0x4ABF5.
- Room door sign "BATH ROOM", "NOW LOADING", menu numbers 1–6 and the word EXIT.
- Cartridge header title (0x24): `NEOPOKE KUN` (ASCII). Optional change only.
- Title screen "SNK / © SNK 2000".
- Minigames (second survey): PRESS A, READY, START, GO!, STAGE, SCORE, TIME, REST, LIFE, HIT, LEVEL 1–3, FLOOR/HP/ITEM, SHOT OK!,
  BEAT/COOL, DRAGON/TIGER, FIGHT!, YOU WIN, YOU LOSE, DRAW GAME, POKEKUN FIGHTERS, the D&DQ title (PLEASE PUSH A, © NEOPOKEKUN INC),
  "© 2000 NEOPOKEKUN", the hand-drawn GAME OVER animations, "A long time ago in a galaxy not far away", the SNK / NEOPOKE / OUT signs in stages.

## Leads that turned out not to be graphics text
- **"Kana name-entry grid" at 0x15C4E–0x15E60: not a name entry.** It is a table of 30-byte records
  (code at 0x2156CE: `index*0x1E + 0x215C4E`); each record starts with 7 **string IDs** (0xA4, 0xA5, …)
  that are looked up in the main pointer table 0x2CC000 and printed into 7 text boxes (0x215AD6). Those
  strings are main-script lines, so they are handled by `insert.py`. The game has no name-entry screen.
  The IDs only look like kana because string IDs 0x80+ coincide with the hiragana codes.
- The 8×8 font at 0xC2018 is handled by the font/VWF work, not here.
- Minigame names on the unlocked menu, the Mr. Yabou status labels (1576ねんなつ, ぶりょく…, さゆうキーで キャラせんたく) and the V.OFF story
  window are main-script strings (s000–s029, s069/s071, s379, shooter lines), drawn at runtime, not graphics.

## Not covered (and why)
- **Hidden debug menu** (only reachable with the tour's memory poke): its graphics come out garbled, so it could not be read. It is a developer screen.
- **Minigames** were locked on a fresh save, not missing: RAM 0x4500–0x4557 = 0xFF unlocks all 30 (with crowns). Second survey above.
- Not reached in MAME: 天晴れ!! and 天下統一 (need a Yabou win), the 開発中 icon (no page shows it), V.OFF / Doki Street endings, D&DQ past floor 1.
  The first three were exported from the ROM anyway; their palettes are guesses (noted in their JSON).
- Readings to confirm by eye: #18 (V.OFF labels), #20 (bath sign), #23 (tiny notice, unreadable at 8 px).
- A byte-by-byte visual sweep of the whole ROM was tried but is unreadable at that density; instead both graphics tables were decoded completely
  and every tile on screen in the dumps was located. Tiles on screen that are not in the ROM are runtime-drawn: in every run, the frame with
  the most of them is a VWF text window (`work/gfxsurvey/notfound.png`); the others seen are the line-drawn GAME OVER animations.

## Note for the main build
A full `insert.py` build (with the script translations, e.g. `build/tr_drafts.json`) **skips the title screen** and goes straight to the room
between frames ~1900 and ~2000 in the MAME harness. The same happens with the older `build/test_vwf.ngc`, and does not happen with
`gfx_patch` alone on the original ROM, so it comes from the script/VWF build, not from these patches. The title screenshots were therefore taken
from `build/gfx_only.ngc` (original + gfx_patch only).
