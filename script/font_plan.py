"""Which font each text uses.

- Big dialog font (the game's 16x16 font): only the strings listed in BIG below, with wording short enough for
  their window. The save/load window is 96 px wide and 2 lines tall; tools/check_fit.py measures every line.
- 8x8 font (the game's own): every other text drawn by the dialog renderer (messages, story, instructions...).
- CFC2 font: the dating-profile stat values only (tools/icon_drafts.py, tools/fields_cfc2.py).

BIG: string id -> text. "[10][3C]" moves to pixel 0x3C = 60, where the cursor expects "NO".
Candidates not switched yet (their screens have not been reached in MAME, so it is not confirmed that the dialog
renderer draws them): 94 "No data found.", 379 "L/R: Select Character"."""
BIG = {
    106: "Save game?\nYES[10][3C]NO",      # was "Save the game?" (102 px in a 96 px window)
    107: "Load game?\nYES[10][3C]NO",
    108: "Please save\nagain.",            # was "Please try saving / again."
    109: "Please load\nagain.",
}
# window width in px for big-font strings (for tools/check_fit.py)
BIG_WINDOW = {106: 96, 107: 96, 108: 96, 109: 96}
