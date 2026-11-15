# Script Desk

`review/index.html` is the page used to revise the English script. It shows every unique line with the Japanese, the
current English and a preview drawn in the font the game will really use, with a pixel counter against that line's
real width limit. Lines are edited, approved or flagged there, and the result goes into `script/page.json` for the build.

## Starting it

The page reads two files that `tools/setup.py` generates from your ROM:

| File | Contents |
| --- | --- |
| `review/lines.json` | One entry per unique line: key, string ids, Japanese, current English, scene, width limit, font |
| `review/font.json` | The three fonts as bitmaps with their widths, for the preview and the pixel counter |

Serve the folder and open the page:

```bash
python -m http.server 8765 --directory review
```

Then go to http://localhost:8765. Opening `index.html` straight from disk does not work, because browsers block `fetch`
on `file://` pages.

## Using it

- **Left list:** lines grouped by scene. Filters: To review, Flagged, Approved, Already English, All, Too wide and V.OFF script.
- **Your English:** the text the build will use. Codes like `[1C]` set the screen position and must stay. A new line in the
  box is a line break in the game.
- **Preview and counter:** the line drawn in its real font: the big dialog font, the game's 8x8 font, the game's 8x8
  renderer (Yabou, V.OFF) or the CFC2 font (profile stat values). The counter shows pixels left, "fits with 3 px spaces"
  (8x8 renderer only) or pixels over.
- **Approve** (Ctrl+Enter) saves the line as approved and moves to the next one. **Flag for later** saves it as flagged.
  **Reset to draft** puts back the first draft. Alt+Down / Alt+Up move without changing the status.
- **Note:** a remark saved with the line; it goes into the `note` field of `script/page.json`.
- **Too wide:** lines that the build measured as wider than their window. `tools/wide_flags.py` writes these flags; they
  are separate from the review status, so a line can be approved and still too wide.
- **V.OFF script:** all 168 lines of the shooter in reading order, grouped by sentence and editable in place.
- **Help** opens a short version of this page.

## Where edits are saved

| Opened as | Saved to | Who sees it |
| --- | --- | --- |
| Local page (`http.server`) | The browser's local storage for that address (`db:rev`, `db:wide`) | Only that browser, on that host and port |
| Claude artifact | The artifact's shared database (collections `rev` and `wide`) | Everyone who can open the artifact |

Every keystroke marks the line as unsaved and saves it 700 ms later. A line never saved before gets the status "edited".
Switching lines saves at once, and closing the tab with unsaved text asks first.

Local storage is not a safe place for weeks of work: clearing site data, a private window or a different port all start
empty. Export regularly.

## Export database

**Export database** opens a summary (saved lines, approved, flagged, edited, too-wide flags) with two buttons:

- **Download** saves `script_desk_YYYY-MM-DD.json`.
- **Copy JSON** puts the same text on the clipboard, for when a download is blocked (some embedded views block them).

It works in both modes and always contains everything saved so far. Pending keystrokes are saved first.

File format:

```json
{
 "format": "neopoke-scriptdesk/1",
 "exported": "2026-11-15T10:00:00.000Z",
 "source": "browser storage",
 "lines": 587,
 "rev": {
  "s000": {"text": " [19]Shot ", "note": "", "status": "approved", "ids": [0], "updatedAt": "2026-11-15T09:58:12.000Z"}
 },
 "wide": {
  "s151": {"msg": "3 px over the window", "at": "2026-11-15T09:00:00.000Z"}
 }
}
```

- `rev`: one entry per saved line, keyed like `review/lines.json`. `status` is `approved`, `flagged` or `edited`.
- `wide`: the "Too wide" flags, keyed the same way.

## Import

**Import…** reads a file made by Export database and shows what it holds: lines in the file, how many differ from the
page, unknown keys (skipped) and too-wide flags. **Import** then writes the file's lines over the same lines on the page.
Lines that are not in the file stay as they are. Locally the page reloads afterwards; as an artifact, the lines are written
to the shared database one by one.

Use it to move work between browsers, to restore a backup, or to load work done on the artifact into a local page.

## Into the build

```bash
python tools/merge_page.py script_desk_2026-11-15.json
```

```bash
python tools/build.py
```

`merge_page.py` copies each saved line's text, status and note into `script/page.json`. Lines the file does not contain are
left alone, so running it twice with the same file changes nothing the second time. It also accepts a directory with one
JSON file per line under `rev/`, which is how the artifact database is saved with Claude's `ArtifactData` tool.

Then, optionally:

| Command | What it does |
| --- | --- |
| `python tools/check_fit.py build/tr_page.json build/fit.txt` | Measures every dialog line with its real font and lists the ones over the limit |
| `python tools/page_lines.py script/page.json review/lines.json` | Refreshes the English the page shows for lines it has never saved |
| `python tools/wide_flags.py <db dir> <out.json>` | Recomputes the "Too wide" flags from a fresh build (artifact workflow) |
| `python tools/voff_dump.py review/lines.json script/voff_script.md` | Writes the V.OFF script in reading order with widths |

Commit `script/page.json`. The export file is a working file; keep it out of the repository or not, as you prefer. It holds
only your English and notes.
