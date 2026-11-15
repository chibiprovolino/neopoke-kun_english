# Brief for a translation agent

You are helping translate the Japanese Neo Geo Pocket game "Ganbare Neo Poke-kun" into English.
The attached `export.json` (format `neopoke-script/1`) has one entry per unique line.

For each entry:
- `jp` is the original, `draft` is an earlier draft, `en` is the current English. Rewrite `en` only.
- Keep `key`, `jp`, `maxw`, `lines`, `scene` unchanged.
- `\n` is a line break. Bracket codes like `[1C]` are screen positions; keep them exactly.
- Plain ASCII plus ♥ only (no curly quotes, no accents, no em dashes).
- The game will use a variable-width font (most letters 4-5px, screen 160px, about 35-38 characters per line).
  Aim for at most `maxw` x 8 pixels per line (roughly `maxw` x 1.8 characters) and at most `lines` lines.
  The human checks exact pixel widths in the review page.
- Tone: the game is a goofy SNK parody collection; keep jokes and puns, adapt rather than translate literally.
- Leave a remark in `note` if a line needs the human's decision. Set `status` to `flagged` for those.
- Do not set `status` to `approved`: only the human approves.

Return the whole file in the same format.
