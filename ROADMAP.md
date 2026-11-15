# Ganbare Neo Poke-kun (Kari) — English translation roadmap

## What's known (phase 0 – done)
- ROM: 2 MB, Neo Geo Pocket Color, mapped at 0x200000. 0x1EA300–0x1FFFFF (87 KB) is free space.
- Font: 8×8, 2bpp, at 0xC2018 (header at 0xC2000). Tile number = character code.
  ASCII is at 0x20–0x7E, so English needs no new font.
- Text encoding: 1 byte per character; `01 xx` = character 0x100+xx (katakana, punctuation, kanji);
  `0D` = new line; `00` = end; `19`–`1F` at the start of a line = position codes; 0x1D0–0x1FA = large HUD letters.
- Script: 667 strings at 0xCCD80–0xCFB68, each pointed to by 32-bit pointers in tables at 0xCC004–0xCCD7F.
  587 unique, 519 need translation. Table: `tools/table.py`.

## Phase 1 – extraction (done)
- `tools/extract.py` → `script/strings.json` (offset, length, pointers, Japanese).
- `script/drafts.py` holds Claude's draft English.

## Phase 2 – your revision (in progress)
- Review page (`review/index.html`, a Claude artifact page; data from `tools/mklines.py` + `tools/review_fonts.py`): approve, rewrite or flag every line.
  It checks each line against the 20-column screen and the Japanese line width.
- Translation choices are yours; flagged lines come back to Claude with your note.

## Phase 3 – insertion (pipeline tested)
- `tools/merge_reviews.py` turns approved lines into `build/translations.json`.
- `tools/insert.py rom/original.ngc build/translations.json build/out.ngc` writes a line in place
  if it fits, otherwise into free space, and repoints it. The test build from all drafts used 8.6 KB of free space.

## Phase 4 – things outside the script (to do)
1. Text drawn as graphics: title screen, menus, minigame logos and any Japanese in tile art. Needs a tile/tilemap survey and redrawn art.
2. Glyphs 0x130/0x131 (shown as boxes, used for "move" in the instructions) and 0x1C0–0x1C2 (the word ロード) are special tiles; check them in an emulator.
3. Width: the narrow intro window (~12 columns) and the 8-column profile fields are tight. Options: shorter wording, or a variable-width font routine (bigger job).
4. Header: optionally change the cartridge title at 0x24 ("NEOPOKE KUN").

## Phase 5 – testing (to do)
- No emulator was found on this PC. Install one (e.g. Mednafen or ares) and play through every minigame,
  the dating profiles, the shooter story and the credits, checking overflow and position codes.
- Release as an IPS/BPS patch, never the ROM itself.

## Exchange format (done)
- `python tools/export_script.py` → `script/export.json` (format `neopoke-script/1`), with `script/AGENT_BRIEF.md` for the other agent.
- `python tools/import_script.py <file>` checks the returned file and prepares writes that Claude pushes to the review page.

## Half-width font (font done, display not yet)
- `tools/halffont.py`: 96 glyphs, 3×8 in a 4px cell (ASCII + ♥). Preview: `font/halfwidth_preview.png`.
- Pre-drawn pair tiles don't work: the script needs ~785 letter pairs, there are ~277 free tile slots,
  which leaves ~2,000 mid-word gaps even with the smart encoder in `tools/halfwidth.py`.
- Needed: a small assembly routine that draws text into tiles at runtime (2 glyphs per tile).
  That means finding the game's text-print routine, which needs an emulator with a debugger.

## Fonts: the game's own, one per renderer (replaces the CFC2 font, 2026-11-14)
The game uses several fonts and each renderer keeps its own. The CFC2 font is no longer used in text (its only remaining use is the
draft lettering fallback in `tools/gfx_patch.py`, which the hand-drawn PNGs in `gfx/` override).
- **Dialog font** (save prompt, profile messages, story, instructions...): 16x16 cells, 2bpp, file 0xC4006 (pointer chain 0x2C2004 -> +2),
  64 bytes/code in tile order TL,TR,BL,BR. Has its own full ASCII set (thin 1 px strokes, ~11 px tall). Originally drawn on a 12 px pitch.
- **8x8 font** (profile name and fields, HUD...): file 0xC2018, 16 bytes/code, its own proportional ASCII set with widths at 0x128a2,
  blanks 0x19-0x1F of 1-7 px. Left untouched now (`tools/font8.py` removed).
- Large HUD letters (0x1D0-0x1FA) and segment digits (0x1B0-0x1CF) are part of the 8x8 font, untouched.
- Graphics text (title, menu icons) is tile art, see "Graphics text".

## VWF (game's own dialog font, tested in MAME)
- `tools/vwf.py`, applied by `tools/insert.py`. Hook at 0x212428 (jp 0x3F8000). Code at file 0x1F8000 (228 bytes), widths at 0x1F8100 (512),
  left-aligned copies of dialog glyphs 0x00-0x7F at 0x1F8400-0x1FA3FF (8 KB, clear of the flash save block at 0x1FC000).
  Codes >= 0x80 (kana, kanji, heart 0x12A) are drawn straight from the ROM font, unshifted, 12 px advance (the original pitch).
- Widths = ink width + GAP (1 px; 2 px looks airier but doubles overflow, preview `build/font8/gap_compare.png`), space 5 px.
- How it works: the box is a grid of 8x16 tile columns (0x20 bytes each). Pixel offset in object byte +0x38 (12 px toggle disabled).
  Each of the glyph's 4 tiles is shifted and ORed into the current and next column, all 16 rows.
- Codes 0x19-0x1F are 4 px blanks; `10 xx` moves to pixel xx. Never use bytes 0x02-0x0F in text: the game stalls on them.
- Line fitting: the dialog font is much wider than CFC2, so drafts wrapped for CFC2 overflow. A line wider than its window spills into
  the next text row (seen on the save prompt: "e?" drawn over "YES"). List: `build/font8/overflow.txt` (57 of 607 lines, 48 strings,
  measured against the Japanese line at 12 px/char). The review page still measures with the CFC2 widths (`review/font.json`).
- YES/NO menus: the cursor expects the 12 px grid (NO at about 60 px from the line start for the save prompt); pad with spaces/blanks.
- Testing harness: `work/mame/run9/inp.lua`, `tools/tour`; MAME is the folder in $MAME_DIR. Test build: `build/test_origfonts.ngc`.

## MAME tour (tools/tour, in progress)
- `python tools/tour/run_tour.py <rom> [route...]` runs each `tools/tour/routes/*.lua` from a cold boot (private cfg/nvram per run),
  saves 3x screenshots in `build/tour/<route>/` and writes `build/tour/index.html` (ids per shot + coverage per category).
  `tools/tour/lib.lua` logs which string ids are read via MAME read taps on the text areas (no debugger needed); `idmap.py` maps addresses for the given ROM.
- `python tools/tour/show.py <rom> <id>...` previews single strings inside the save-prompt box (not its real screen, but real VWF rendering).
- Route `zz_preview` does all 667 at once: a read tap swaps the save-prompt pointer (0x2CC280) for each string in turn and Option / Right+A
  opens and closes the prompt every 150 frames. If the prompt ignores Option (Poke-kun asleep), the runner retries the missed ids automatically
  (`run_tour.py <rom> --retry none` reruns only the misses). The contact sheet groups these by category with the English and Japanese.
  Full run: about 10 minutes. Last run: all 667 ids shown (ids 30-49 and 406 are empty strings; 497 has an empty draft).
- Routes: `save` (ids 106), `menu_locked` (room A then B opens the minigame menu: on a fresh save all 6 pages are 予定地 placeholders, no script ids),
  `debugmenu` (opens the hidden debug menu by redirecting the save-prompt task's resume address, task obj = (0x482b), to 0x21783a).
- Debug menu items in order (Down to move, A to enter; cursor is not drawn moving): MAP_TEST (city map), HEYA_TEST (room), CHR_TEST (sprite on white),
  MAE_TEST (small sprites), MINIGAME (Poke-kun on black, no text yet found). B returns to the menu.
- Dating profiles reached: route `profiles` (all 34, ids 110-347) and `profile_anim` (burst frames of chosen profiles, TOUR_PROFILES="2,7").
  Path: room A, B opens the minigame menu; with RAM 0x4803 != 0 (held every frame) a hidden page "E" appears after page 6;
  Right x7, Up, A opens the "Love Love Profile" (ラブラブプロファイル) catalog, A again shows profile 1, Down/Up browse. Unlock flags are bits 1-69 at RAM 0x4558 (set all).
  Profile fields were clipped with text labels (e.g. "Hobby Pachink"); fixed with icons, see "Profile icons" below.
- Not reached yet: RPS date, Yabou, D&DQ, shooter, credits, minigame instructions (minigames are locked on a fresh save).
  Profile text is loaded through generic HL-indexed sites (e.g. 0x214939, 0x215ada, 0x215b91, 0x21674c, 0x2168f1); finding their task entry is the next lead.
- Rendering bugs seen:
  - Debug menu text is garbage under the VWF hook (it draws in a layout the hook doesn't expect).
  - Save-prompt box preview (a 96 px / 12-column, 2-line window): lines wider than 96 px are cut off: 4 profiles (116 130 200 235),
    8 RPS date (358 362 367-372), 2 D&DQ (397 405), 48 shooter story lines, 3 instructions. Real windows may be wider, so check these on their real screens.
  - Strings with more lines than the window has rows write garbage tiles over the box border and top: 12 minigame instructions
    (643 645 646 648 649 652 655 660 661 663 664 665). It's harmless if the real instruction window is tall enough, but the VWF routine doesn't stop at the window's last row.

## Profile icons (done, test build `build/test_icons.ngc`)
- The 5 profile field rows are NOT drawn by the VWF: they use the game's own proportional renderer (0x2122c3 -> 0x2124d6),
  original 8x8 font at file 0xC2018 (16 bytes/code), width table at file 0x128a2 (1 byte/code), 64 px per field.
  It only clears what it draws, so a short string leaves junk tiles: fields must be padded to the full 64 px.
- `tools/icons.py`: icons Age/Job/Income/Hobby/Appeal at codes 0x11-0x15 (blank, width 0 in the original font, so unused).
  Art comes from `font/icons.png` (40x8, five 8x8 cells, dark = ink; any whole upscale works); width = ink + 1 px gap.
  `python tools/icons.py` redraws the guide `font/icons_template.png`. `tools/insert.py` calls `icons.apply()` after the VWF.
- `tools/icon_drafts.py build/tr_drafts.json build/tr_drafts_icons.json` turns "Hobby Pachinko" into `[14]Pachinko` + padding
  (spaces = 8 px, codes 0x19-0x1F = 1-7 px blanks) and reports values wider than 64 px. With the current drafts: none.
- Checked in MAME on all 34 profiles (`profiles` and `profile_anim` routes). Room left now, so drafts shortened for
  the old labels ("Drive", "Big nose"...) can grow back. Untouched: the review page still measures these lines with the VWF font.
- Current icons (drawn by the user with tools/icon_editor.html): "YR" (Age), briefcase (Job), yen, outlined heart (Hobby), outlined star (Appeal), one colour.
- Colour icons: tried and dropped. The field tiles use plane-2 palette 3 = [transparent, cream CFF, dark, dark]; palettes 5-14 are unused
  there and the game keeps a RAM copy of the plane-2 palettes at 0x42BC. A routine hooked at 0x2122e0 that copied raw 2bpp icon tiles and
  set palettes 5-9 ran without crashing, but the icons still came out dark (the palette or map entry is probably rewritten after drawing).
- Flash save block: code put at file 0x1FF000 crashed at boot. The game saves into the last flash block (0x1FC000-0x1FFFFF), which erases it.
  So nothing that must survive may go above 0x1FC000. Note: the VWF font (0x1F8400 + 512*32) runs to 0x1FC3FF, so glyphs 0x1E0-0x1FF are in that block
  (unused by the English script so far).

## Save area fix (done 2026-11-14, build `build/test_fonts4.ngc`)
- VWF block moved down by 0x3000: code 0x1F5000, big widths 0x1F5200, big glyph copies 0x1F5400-0x1F73FF, 8x8 dialog widths 0x1F7400-0x1F75FF
  (`tools/vwf.py`; these replace every 0x1F8xxx/0x1FAxxx VWF address quoted elsewhere in this file). Relocated text now ends at 0x1F5000.
  `tools/insert.py` refuses to build if anything lands at 0x1F8000 or above.
- Reproduced in MAME (`work/savetest/run.sh <name> <rom>`, env ST_SEQ/ST_SNAPS/ST_STOP/ST_CODE/ST_RESET): `test_fonts3.ngc` erased the VWF code on
  the first save and went to a white screen; `test_fonts4.ngc` saved three times into slots 0-2 with the VWF intact, and after a soft reset
  the game loaded the save (counter A marker 123 came back).
- Side effect: fixed builds show the title screen again. Older builds "skipped" it only because blank glyph slots read as a valid save.
  `tools/tour/lib.lua` now presses A until frame 2100 to dismiss it (checked with `show.py` on ids 106 and 112); the tour read tap ends at 0x3F4FFF.
- MAME does not keep cartridge flash between runs, so cross-run loading can only be tested with ST_RESET (soft reset in one run).
- Every build made before this fix (test_fonts3, test_reviewed, test_origfonts, test_icons...) still has the bug: rebuild before play-testing.

## Save area conflict (found 2026-11-14 by reading the save code; reproduced, see the fix above)
- The game's own saves live at file 0x1F8000-0x1F9FFF (flash block 0x20), not in the last block: 32 slots of 256 bytes
  (byte 0 = 0x00, 77 bytes of RAM 0x4520-0x456C, checksum). Save routine 0x20181a takes the first slot that is all 0xFF;
  if none, it erases block 0x20 (0x20185b) and writes slot 0. Load 0x201894 takes the highest slot with byte 0 = 0 and a good checksum.
- This supersedes the "Flash save block" note under Profile icons. The last block (0x1FC000+) failing is probably the system-reserved block.
- The VWF code (0x1F8000), widths and big-glyph copies (0x1F8400-0x1F9FFF) are inside that area. In `build/test_fonts3.ngc`
  no slot is blank, so the first save should erase the VWF code; slots 8-11 (blank glyphs) also read as a valid all-zero save.
  Earlier builds had one blank slot (3), so the second save would erase.
- Fix to do: move VWF code/tables out of 0x1F8000-0x1F9FFF (and 0x1FC000+), e.g. into 0x1EA300-0x1F7FFF or 0x1FA000-0x1FBFFF, then save twice in MAME.

## 8x8 font
- Reverted to the game's own Latin glyphs and widths (see "Fonts"). `tools/icon_drafts.py` pads profile fields with the original widths:
  all 170 fields fit in 64 px. Checked in MAME on profiles 2 and 7 (`build/tour/profile_anim/`).

## Graphics text (tools/gfx_patch.py)
- Survey and drafts: `script/graphics_text.md` — title logo, minigame-menu 予定地 icons, EXIT kanji 退, profile screen これ and DATE/メッセージ.
  English wording is a draft for approval. No name-entry screen exists: the "kana grid" at 0x15C4E is a table of script string IDs.
- **Redraw by hand:** the PNGs in `gfx/` (title_logo 144x40, menu_icon_text 32x7, exit_icon 16x8, profile_date_label 72x8, profile_kore 24x8).
  Use only the 4 palette colours in each file; `*_ref.png` are 4x previews. `python tools/gfx_export.py [--original] --force` regenerates them.
  The title logo must cut into at most 58 different 8x8 tiles. The profile PNGs currently hold the original Japanese art.
- Applied by `tools/insert.py` (one line, before `vwf.apply`). All edits are in place, so **no free space is used**; 0x1EA300–0x1FC400 stays for text/VWF.
- Free space outside that range (0xFF runs in the original ROM, none used yet): 0x1C0AF–0x1E2FFF (143 KB), 0xA950B–0xBBFFF (76 KB),
  0x1AF231–0x1BFFFF (69 KB), 0x74C03–0x77FFF (13 KB). Check these are really unused before relying on them.
- Screenshots: `build/gfx/`. MAME harness with VRAM dumps: `work/gfxharness/` (`bash run.sh <rom> <cfg.lua> <outdir>`; `profile_route.lua` reaches the profile screen).
- Note: full builds skip the title screen (the older test_vwf.ngc does too; gfx_patch alone does not).

## Font plan (decided by the user 2026-11-14, supersedes the "Fonts" / "VWF" notes above where they differ)
- **Big dialog font** (16x16, file 0xC4006): only short system prompts, listed with their wording in `script/font_plan.py` (BIG).
  Now: save/load 106-109 ("Save game?", "Load game?", "Please save/load again."), tested on the save prompt.
  Candidates not switched (screens not reached, renderer unconfirmed): 94 "No data found.", 379 "L/R: Select Character".
- **8x8 font** (the game's own, file 0xC2018): everything else the dialog renderer draws (profile messages, story, instructions...),
  on rows 4-11 of the 16-row line, with the game's widths but a 4 px space (copy of the width table at 0x1FA400).
- **CFC2 font**: the dating-profile stat values only. Its letters sit in blank code slots of the 8x8 font
  (`tools/fields_cfc2.py`: 0x16-0x18, 0x12B-0x12D, 0x157-0x17F, 0x18A-0x18F, 0x19A-0x19F, 0x1DD-0x1DF = 62 slots, 61 used),
  so the game's own 8x8 glyphs are untouched. The fields may use at most 62 different characters.
- `tools/vwf.py`: font state in bits 4-5 of object byte +0x38 (bits 0-2 = sub-pixel); `[10][F1]` = big font, `[10][F0]` = 8x8,
  `[10][xx]` (xx < F0) = move to pixel xx. Layout: code 0x1F8000 (348 bytes), big widths 0x1F8200, big glyph copies 0x1F8400-0x1FA3FF,
  8x8 dialog widths 0x1FA400-0x1FA5FF. The newline handler at 0x21241a is patched to keep the font bits.
- Build from the user's revised script (`script/revised.json`, imported 2026-11-14 from ganbare_neopoke_export_2026-11-14.json):
  `python tools/build_from_revised.py` -> `python tools/icon_drafts.py build/tr_revised.json build/tr_revised_icons.json`
  -> `python tools/insert.py rom/original.ngc build/tr_revised_icons.json build/test_fonts3.ngc`. Set PYTHONIOENCODING=utf-8.
- `python tools/check_fit.py` measures every dialog line with its real font -> `build/fit.txt` (7 of 606 lines over the conservative limit).
  Stat values wider than 64 px: 252 "Umbrella Maker" (+11), 259 "Ninja Deserter" (+8), 266 "Civil Servant" (+5), 304 "Mixed heritage" (+11).
- Checked in MAME: save prompt and profiles 2 and 7 (`build/fonts3_check.png`). The review page was NOT updated with the revised text
  (batches ready in `build/import_batches/`) and still measures with CFC2 widths.
- Review page updated 2026-11-14: it now previews each line in its real font (`python tools/review_fonts.py` after `tools/mklines.py`
  writes the three fonts to `review/font.json` and `font`/`budget` per line to `review/lines.json`), and holds the revised text
  (270 docs in collection `rev`: 266 from `script/revised.json`, plus 106-109 reworded for the big font, saved as "flagged").
  Note: the build takes the wording of big-font strings from `script/font_plan.py`, not from the page; keep the two in step.

## Room trace harness (work/trace, 2026-11-14)
- `bash work/trace/run.sh <name> [absolute rom path]` runs MAME on the original ROM and logs watched RAM bytes on change. Env: `TR_SEQ "frame:Button[:hold],..."`, `TR_SNAPS`, `TR_EVERY "from:to:step"`, `TR_TRIG "addr=val:count:step"` (snapshots once a byte equals a value), `TR_POKE "frame:addr=val"`, `TR_HOLD "from:addr=val"`, `TR_WATCH "addr,addr"`, `TR_EVENT id` (forces every room event to that event id), `TR_STOP`. `python work/trace/sheet.py <name> [scale]` makes a contact sheet. Output in `work/trace/out/<name>/`.
- The room accepts input from about frame 2200. A = doorbell, B = minigame menu (B again leaves it), Option = save prompt.
- `work/trace/bonus.ngc` is the original ROM with one byte changed (file 0x14093 = 0) so every menu exit with counter A >= 500 plays the staff roll. Test use only.
- Findings (held directions, stick wiggling, broken door, megaphone, Poke-kun states, staff roll) are in the doc, section "Traced inputs and scenes".
- Scene catalogue (2026-11-14): all 194 room scenes pictured, built by `work/trace/catalogue.py` into `work/trace/catalogue.html` (not in the repository: it holds game screenshots). `work/trace/jobs.txt` holds one MAME run per scene (`bash work/trace/job.sh "<line>"`; visitors use the longer window in `jobs_v.txt`), `TR_FORCE "addr=val"` replaces writes to a RAM byte (event id 0x44b2, class 0x44f7, visitor 0x44ff, reaction 0x44fe, wiggle result 0x450a, megaphone result 0x4513). `python work/trace/strip.py <names>` makes the strips, `python work/trace/catalogue.py` rebuilds the page; descriptions live in `work/trace/catalogue_desc.py` (my reading of the sprites; profile names there are guesses).

## Redesign prototype ("seen it once", built 2026-11-14)
- `python tools/redesign.py <in.ngc> <out.ngc>`: `build/proto_redesign.ngc` (from `build/test_reviewed.ngc`) and `build/proto_redesign_jp.ngc` (from the original, used for the MAME tests). All pacing numbers are constants at the top of the tool. No pity unlock (user decision).
- New code and the calendar table sit at file 0x1F7800 (1525 bytes as of 2026-11-15: 501 of code, 1024 of calendar table; free space ends at the save area 0x1F8000). Hooks: list filters at 0x5549 / 0x584B / 0x59D1 / 0x542C, counter A awards at 0x5578 / 0x587E / 0x59FC / 0x5457, clock routine 0x5ACC replaced, calendar step at 0x14081, new-game init at 0x18EE. The tool asserts the original bytes at every site.
- New saved RAM: 0x4544 room seen bits (11 bytes), 0x454F wiggle (3), 0x4552 megaphone (2), 0x4554 calendar step. Visitors reuse the met bits at 0x4558. These 20 bytes are inside the saved block and have no reference in the game's code; not yet verified against minigame play.
- Tested in MAME with `work/trace/run.sh` (runs p1-p8): first-time +5, repeat +0, guaranteed work, calendar step, save + reset, unlock thresholds. `TR_RESET frame` does one soft reset and logs the second boot to log2.txt.
- Not tested: long play, staff roll rate, minigames. The translated build shows "Crossin&" for "Crossing" in the minigame menu (already present in test_reviewed, not caused by the prototype; not investigated).

## Redesign play test (2026-11-14)
- `bash work/trace/runbot.sh <name> [absolute rom]` runs `work/trace/bot.lua`, an automated player (rings, holds directions, wiggles, leaves the menu every 6 actions; it never reads mood or seen flags). Env: BOT_STOP frames, BOT_SEED, BOT_EXIT, BOT_FULL=1 (keep playing after 30 games; the bot then stalls because it detects the menu by a locked game's stage being rewritten), BOT_GAME=1 (starts a minigame; the bot cannot leave it again). Output `work/trace/out/<name>/bot.txt`.
- MAME problem (MAME 0.277), also on the unpatched ROM: after a voice sample (megaphone, some gags) the sound CPU's heartbeat byte 0x70c3 stops, and the next sound command waits on it forever in the loop at 0x2a94df. The bot works around it with a read tap on 0x70c3. Not a patch bug; not checked on other emulators or hardware.
- Tuning after the test (now in tools/redesign.py and both proto builds): work on any exit with mood below 0 (five brackets, pay 3-8), the staff roll no longer replaces a work exit (stub STAFFRNG, hook at 0x1408D), game n needs counter A 5+20(n-1) and counter B n.
- Results with that tuning, two seeds: all 30 games at 65 and 99 game-minutes; 118-125 of 194 scenes seen by then; no crash, no hang, and only the BIOS, the game's boot init and the patch wrote to 0x4544-0x4557 (one minigame ran for 3 hours in another run without touching them).
- Never seen by the bot: scenes that need mood above +35 or below -35 (work resets mood to about 0 and idling pushes it up), seasonal chains (visitors 7-10 and 65 need a specific room event just before), follow-up-only events, and visitors 70-89, which only come while Poke-kun is in the bathroom (records blocked in states 0-4).

## Redesign: loosened conditions (2026-11-14, user asked for it after the play test)
- All in tools/redesign.py as constants: mood band edges (room 34/35 -> 8/9 and 67/68 -> 16/17; visitors and megaphone 67/68 -> 8/9, also the default-event edge at 0x55CA), follow-up-only room records get chance 40, visitors need no particular last room event (byte 27 cleared), seasonal room records 65-68 take any mood, bathroom record 182 chance 255 and any mood, visitors 70-89 at any hour and in any state (record flags plus the hard-coded id test at 0x5980), two visitor records with reversed mood bounds fixed, idle drift 0, work spends 8-30 mood instead of resetting it, game n needs counter A 5+24(n-1) and counter B n.
- Bot results (2 seeds, 3 game-hours, runs T5/T6): all 30 games at 39 and 42 min; 181 and 184 of 194 scenes; all 89 visitors and all 16 wiggle gags; no crash or hang. Still unseen in both runs: room events 4, 19, 20, 30, 33, 41, 51, 53, 58 (strong mood plus narrow hours or season) and megaphone reaction 3.
- Earlier steps for comparison: before loosening 118-133 scenes; first loosening 156-160; mood rebalance 163-168; bathroom flags only 169-170 (the hard-coded test still blocked them).
- bot.lua now keeps playing after all 30 games are unlocked (BOT_FULL=1).

## Remade graphics (2026-11-15, build `build/test_gfxdone.ngc`)
- The user's redraws (gfxdone/) are copied into gfx/ as indexed PNGs (old files in gfx/_before_gfxdone/). `tools/insert.py` now calls
  `gfx_import.apply()` after `gfx_patch.apply()`, so every build includes them.
- Enlarged tile blocks (`GROW` in `tools/gfx_import.py`): catalog (81 -> 140 tiles, VRAM 0x001-0x08C), Doki Doki title (134 -> 170, 0x100-0x1A9),
  V.OFF logo (196 -> 200, 0x138-0x1FF). Copies sit in free space at 0x1B0000/0x1B1000/0x1B2000; the screen record's +4 pointer and +12 count
  are rewritten. VRAM ranges were chosen from dumps (nothing visible there on those screens). Checked in MAME: catalog, profile, Doki title
  and gameplay, V.OFF title and gameplay, Garou, Yabou look right (`work/gfxsurvey/cmpsheet.py <name>` compares o_<name> with n_<name>).
- Title logo: user's redraw cut to 58 tiles (r4c12=r4c9, r3c12=r3c9, r4c5=r2c4, r2c12 erased; unedited redraw kept as
  gfxdone/title_logo_62tiles.png; guide `python tools/logo_tiles.py`). Checked on the title screen in MAME.
- `menuE_caption`: user's "LOOK!" version (gfx/menuE_caption2.png, blank first/last cells) fits in the original tiles; checked on page E in MAME.
  All remade graphics are now in the build. Tile 4 of that block (blank placeholder under the page-E picture) is deliberately left alone.
- Title-screen capture: `work/gfxsurvey/run_noa.sh <rom> x_title.lua <out>` (driver without the automatic A presses).
- EXIT button: the "kanji 退" is really a pictogram of a man leaving through a door; kept as is (`patch_exit` disabled in
  `tools/gfx_patch.py`, the arrow draft moved to gfx/_before_gfxdone/). `menu_icon_text` (SOON over 予定地) is applied by gfx_patch;
  `menu_icon_kaihatsu` (cone + 開発中) is a separate icon no menu page was seen to use, left untranslated.

## Mr. Yabou stat labels (2026-11-15, build `build/test_yabou.ngc`)
- Stray coloured marks after Home, Hair, Calves, Worry and Grit were stale tiles from the previous screen, not the profile icons:
  the labels (ids 69-83) use the 8x8 proportional renderer, which only clears the tiles it draws into, and each field is
  (Japanese character count) x 8 px. `tools/icon_drafts.py` now pads these labels to the field width with blanks 0x19-0x1F.
  Checked in MAME (Tokugawa's screen). Still open: labels wider than their field are clipped (Defense, Stability,
  Dimples, Tantrums, Wabi-sabi; Loans/Purpose/Modesty by 1-2 px).
- 2026-11-15: the field is the Japanese label's pixel width rounded up to tiles (id 69 is 56 px, not 64). A label that is too wide
  gets its 8 px spaces narrowed to blanks 0x19-0x1F (min 1 px): "Summer 1576" -> `Summer[19]1576`, 56 px, checked in MAME
  (`build/test_page.ngc`, built from `script/page.json` = reviewed.json + the Script Desk page's text). Width flags for lines
  live in the page's `wide` collection ("Too wide" section), separate from the review status.

## V.OFF shooter text (2026-11-15, build `build/test_page.ngc`)
- The story (438-547) is drawn in V.OFF's text window by the game's own 8x8 proportional renderer (NOT the VWF), like the Yabou
  screen: 8 px spaces, clipped at 144 px (18 tiles), and it only clears what it draws (the Japanese strings end in spaces to wipe
  the previous page). Intro 407-437 and ending 548-574 have 104 px Japanese lines (a narrower window, not yet seen on screen).
- `tools/icon_drafts.py` (FIELDS/fit8) now handles every string of this renderer: spaces after the first word become 4 px blanks
  (narrowed to 3 px for the shooter / 1 px for Yabou labels if needed), leading spaces stay, each line is padded to the field.
  Checked in MAME: story pages 1-4 (`work/gfxsurvey/x_voff.lua` -> `p_voff`), Yabou screen (`x_yabou.lua` -> `p_yabou`).
- `python tools/merge_page.py <dir>` overlays the Script Desk page (`rev` collection saved with ArtifactData out_dir) on reviewed.json.
  Public repository (2026-11-15): reviewed.json is not included; merge_page now overlays the page's saves (a directory or the page's
  Export file) on script/page.json itself, text, status and note.
- Script Desk v7 (2026-11-15, source `review/index.html`): autosaves as you type (keeps the line's status; never-saved lines become
  "edited"), keeps unsaved text across re-renders, shows the current English (`en` in lines.json) instead of Claude's draft for
  lines never saved on the page (111 lines, mostly story 483+, had shown the draft), per-line pixel counter against the real
  limit, and a "V.OFF script" view (all 168 lines in order, grouped by sentence, editable in place).
  Refresh the page data: `tools/merge_page.py <dir>` -> `tools/page_lines.py` (-> build/page_lines.json, publish as lines.json).
  `tools/voff_dump.py` writes `script/voff_script.md` (V.OFF in reading order with widths).
- Builds 2026-11-15 from the page (59 lines taken from it): `build/neopoke_en.ngc` (translation + all graphics) and
  `build/neopoke_en_redesign.ngc` (same + `tools/redesign.py`). All lines fit except 151/200/256 (dialog, a few px over the
  cautious Japanese-width limit). Pipeline: merge_page -> build_from_revised -> check_fit -> wide_flags (page flags) ->
  page_lines/voff_dump -> icon_drafts -> insert -> redesign.
- All-games save: `python tools/make_save.py <in> <out>` writes save slot 0 into the cartridge flash area of a build (games 1-30
  flag 0xF0, counter A 1000, counter B 255, mood 0). `build/neopoke_en_allgames.ngc`, `build/neopoke_en_redesign_allgames.ngc`;
  checked in MAME: the game loads it at boot (no title screen), RAM 0x4520+ holds the values, menu page 1 shows the five games.
  To open the menu in MAME scripts with constant visitors, repeat A then B (`work/gfxsurvey/x_menusave3.lua`).
- IPS patches: `python tools/make_ips.py <build> <out.ips>` (checks the round trip) -> `build/patches/` for neopoke_en,
  neopoke_en_redesign and their _allgames variants. Base ROM CRC32 6DF986A3.
- Not reached yet: later story pages (need stage clears), intro, ending. Waiting on the V.OFF title shows no attract demo.
  Code at 0x6C4A3 loads ids 437 then 438 (ld BC,#id; call 0x212290) for the first story page.
