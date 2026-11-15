# Ganbare Neo Poke-kun: English translation

English translation of Go for it, Neo Poke-kun! (SNK, 2000) for the Neo Geo Pocket Color.
Text has been written by a non-native English speaker based on a first pass supervised by a native
Japanese speaker. Some obscure cultural references have been simplified or adapted to appropriate
Western equivalents.
Completely vibe-coded. This is a public release, but it needs further testing on real hardware.

Download the IPS patch from the Releases page and apply it to your own dump of the game (CRC32 `6DF986A3`).

All the graphics have been redrawn by a human. Some graphics have been left untranslated on purpose:
they include gibberish, traditional text or other, mainly visual elements.
Decision to translate the book cover in Neo Poke-kun's room is pending.

An experimental bonus patch provides a way to make new events appear much faster, therefore making
minigame unlocks less frustrating. An analysis of the original game's event and unlock logic
is included in the documentation.

Vibed technical specs:

## What you need

- A dump of the game you own: 2 MB, CRC32 `6DF986A3`.
- Python 3.10+ with Pillow (`pip install pillow`).
- For the research and test scripts only: MAME with the `ngpc` driver (tested with 0.277) and Git Bash on Windows.
  Set `MAME_DIR` to the MAME folder. The `-rompath` points at `$MAME_DIR/roms`, which must hold the NGPC BIOS.

## Build the English ROM

Run everything from the repository root.

```bash
python tools/setup.py path/to/your/rom.ngc
```

```bash
python tools/build.py --fastunlock --ips
```

`setup.py` checks the ROM, copies it to `rom/original.ngc` and extracts the script (`script/strings.json`) and the line list
(`review/lines.json`). `build.py` writes `build/neopoke_en.ngc`, with `--fastunlock` also `build/neopoke_en_fastunlock.ngc`,
and with `--ips` an IPS patch for each in `build/patches/`.

The English text is `script/page.json` (`en` field per line). The file carries no Japanese; the tools look it up in the
extracted script by line key.

## Revising the script (Script Desk)

`review/index.html` shows every line with the Japanese, the current English and a preview in the font the game will
really use, with a pixel counter against that line's real width limit. You can edit, approve or flag each line, and the
"V.OFF script" view lists the shooter's story in reading order.

```bash
python -m http.server 8765 --directory review
```

Then open http://localhost:8765. The page needs `review/lines.json` and `review/font.json`, which `tools/setup.py` writes.

- Edits save as you type, in your browser's local storage for that address (keep the same port).
- **Export database** downloads every saved line as `script_desk_YYYY-MM-DD.json` (or copies it). **Import…** loads such a file.
- To bring the edits into the build: `python tools/merge_page.py script_desk_YYYY-MM-DD.json`, then `python tools/build.py`.
- **Help** on the page explains the controls. The full guide, with the export format, is [docs/script-desk.md](docs/script-desk.md).

Opened as a Claude artifact, the page saves to the artifact's shared database instead; Export and Import work the same way.

## Graphics

Text drawn as tile art (title logo, minigame logos, menu labels) is not in this repository. To redraw it:

```bash
python tools/gfx_extract.py
```

This writes one editable PNG per item to `gfx/`, taken from your ROM. Edit them keeping the size and the item's colours
(the 4 palette entries for indexed PNGs, the colours listed in `gfx/<name>.json` for the others), then run `tools/build.py`.

- `tools/gfx_import.py` imports the items described by `gfx/*.json`. Unchanged cells keep their tiles, new ones take free
  tiles, and three screens get a larger tile block in free space (`GROW`).
- `tools/gfx_patch.py` handles the title logo (at most 58 distinct tiles), the menu-icon caption and two profile-screen strips.
  Without a PNG, the logo and caption get draft lettering in the CFC2 font.
- Items with no PNG in `gfx/` stay as in the ROM.
- `script/graphics_text.md` lists every item with its meaning.

The profile icons (`font/icons.png`) are original art made for this project; `tools/icons.py` imports them.

## Repository map

| Path | Contents |
| --- | --- |
| `tools/` | Extraction, build, fonts (VWF), graphics, profile icons, fast-unlock patch, IPS, MAME tour |
| `script/` | English script (`page.json`), drafts, font plan, notes |
| `gfx/*.json` | Location, tiles, map and palette of each graphics-text item |
| `font/` | `cfc2_vwf.json` (dating-profile stat font), `icons.png` |
| `review/index.html` | Script Desk, the script revision page |
| `docs/` | Event system, unlock rules and the fast-unlock patch |
| `work/` | Research scripts: MAME harnesses, graphics survey, disassembly |
| `ROADMAP.md` | Project log, with every decision and test |

## Documentation

- [docs/events-unlocks-fastunlock.md](docs/events-unlocks-fastunlock.md): tools, the event system, unlock rules and the fast-unlock patch.
- [docs/script-desk.md](docs/script-desk.md): the script revision page, its saving, export format and the merge into the build.
- [docs/how-minigames-unlock.md](docs/how-minigames-unlock.md): the full unlock write-up, with tables, MAME tests and community claims checked against the code.

To regenerate the disassembly the notes cite: `bash work/dis/make.sh` (uses MAME's `unidasm`).

## Credits

- `font/cfc2_vwf.json` is the variable-width font from the *SNK vs. Capcom Card Fighters 2 Expand Edition* English translation
  by the CFC2 Translation Team (v20170125).
- The MIT license (`LICENSE`) covers this project's own code, translation, documentation and icons. It does not cover
  `font/cfc2_vwf.json` or anything from the game.
- *Ganbare Neo Poke-kun* is © SNK. This is an unofficial fan project, not affiliated with or endorsed by SNK.
