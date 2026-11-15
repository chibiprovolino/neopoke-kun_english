# Ganbare Neo Poke-kun: tools, event system, unlocks and the redesign

Technical notes for the gameplay side of the project: how the game decides what happens in the room, how minigames unlock,
what `tools/redesign.py` changes, and the tools used to find all of it. Translation work (script, fonts, VWF, graphics)
is covered in `ROADMAP.md`. Setup and build steps are in the README.

Status as of 2026-11-15. Sources: the disassembly (`work/dis/code.asm`), the ROM tables, and MAME runs on the original ROM.
The longer write-up with all the tables is [how-minigames-unlock.md](how-minigames-unlock.md). Every scene can be pictured with
`work/trace/catalogue.py` (section 1.2); the page itself is not included because it holds game screenshots.

**Conventions.** CPU address = file offset + `0x200000`. RAM addresses are below `0x8000`. "Counter A", "counter B" and "mood"
are our names; the game has none. Mood is a signed byte where **negative means happy**.

---

## 1. Tools

### 1.1 Emulator and disassembler

| Tool | Where | Used for |
| --- | --- | --- |
| MAME, `ngpc` driver | `$MAME_DIR/mame.exe` (tested with 0.277) | Running the ROM headless with Lua scripts: input, RAM pokes, read/write taps, snapshots |
| `unidasm -arch tlcs900` | same folder | Disassembly. `bash work/dis/make.sh` writes `work/dis/code.asm`, a linear dump of the first 768 KB, so data regions also appear as junk instructions |
| `work/gfxharness/dis.sh <fileoff> <len> [rom]` | | Disassembles one slice of any build at the right base address. Use it to check patched code |

There is no debugger in the loop. Everything dynamic was done with MAME's Lua API: `install_write_tap` / `install_read_tap`
on the program space to watch or replace RAM accesses, `write_u8` to poke, `video:snapshot()` for screenshots,
`soft_reset()` for save/load tests.

### 1.2 MAME harnesses

All of them cold-boot the cart with private `cfg`/`nvram` folders, press A until about frame 2100 to get past the title,
and are driven by environment variables. Output goes to `out/<name>/` beside each script.

| Harness | Run | What it does |
| --- | --- | --- |
| Unlock test | `work/unlocktest/run.sh <name> [rom]` | Sets counter A, counter B, mood and the clock hour at frame 2250 (`UT_A`, `UT_B`, `UT_MOOD`, `UT_HOLDMOOD`, `UT_HOUR` in BCD, `UT_SEQ`), presses B to cycle the menu, logs the flag bytes. Used to confirm the unlock formula and the work roll |
| Room trace | `work/trace/run.sh <name> [abs rom]` | General-purpose: `TR_SEQ` button script, `TR_POKE`/`TR_HOLD` RAM writes, `TR_WATCH` logs bytes on change, `TR_FORCE` replaces every write to a byte (used to force a given event, visitor or reaction), `TR_EVENT`, `TR_TRIG` snapshot on a value, `TR_EVERY` periodic snapshots, `TR_DUMP` finds which bytes in a range are ever non-zero, `TR_RESET` soft reset mid-run |
| Scene jobs | `work/trace/job.sh "<line>"` | One line of `jobs.txt` (194 scenes) or `jobs_v.txt` (89 visitors, longer window). Each forces one scene through `TR_FORCE` on `0x44b2` (event id), `0x44f7` (class), `0x44ff` (visitor), `0x44fe` (reaction) |
| Catalogue | `python work/trace/strip.py <names>`, `python work/trace/catalogue.py` | Builds snapshot strips and the scene catalogue page from the job output, `catalogue_desc.py` (one sentence per scene) and the ROM records |
| Bot | `work/trace/runbot.sh <name> [abs rom]` | `bot.lua`, an automated player for the redesign: rings the bell (60%), holds a direction (20%), wiggles (10%), leaves the menu every `BOT_EXIT` actions. It never reads mood or seen flags. Logs counters, games, scenes seen and who writes `0x4544`–`0x4557` to `bot.txt` |
| Save test | `work/savetest/run.sh <name> <rom>` | Saves, checks the VWF code survives, soft-resets and checks the save loads (`ST_SEQ`, `ST_CODE`, `ST_RESET`) |
| Graphics harness | `work/gfxharness/run.sh <rom> <cfg.lua> <outdir>` | Scripted routes with VRAM dumps; used to find free VRAM and compare old/new screens |
| Tour | `python tools/tour/run_tour.py <rom> [route]` | Translation coverage: logs which script ids are read on each screen. `debugmenu` route opens the hidden debug menu |

### 1.3 Python tools on the gameplay side

| Tool | Does |
| --- | --- |
| `tools/redesign.py <in> <out>` | Applies the redesign (section 4). Asserts the original bytes at every patch site |
| `tools/make_save.py <in> <out>` | Writes save slot 0 into a build's flash area: all 30 games unlocked (flag `0xF0`), counter A 1000, counter B 255, mood 0 |
| `tools/make_ips.py <build> <out.ips>` | IPS patch against the original ROM (CRC32 `6DF986A3`), with a round-trip check |
| `work/trace/make_bonus.py` | Writes the test ROM `work/trace/bonus.ngc`: file `0x14093` = 0, so every menu exit with counter A ≥ 500 plays the staff roll |

### 1.4 MAME pitfalls

- **Sound hang.** After a voice sample (megaphone, some gags) the sound CPU's heartbeat byte `0x70c3` stops changing, and the
  next sound command waits on it forever in the loop at `0x2a94df`. Happens on the unpatched ROM too. `bot.lua` works around it
  with a read tap that returns a changing value. Not checked on other emulators or hardware.
- **Flash is not kept between runs.** Cross-boot save tests must use a soft reset in the same run (`TR_RESET`, `ST_RESET`).
- **Input timing.** The room ignores input until about frame 2200. After a work scene the menu ignores presses for a while, so
  scripted exit counts are approximate.
- **Fixed builds show the title screen.** Builds before the save-area fix skipped it only because blank glyph data read as a valid save.

---

## 2. The event system

Everything that happens in the room comes from four tables of 32-byte records. A picker filters a table against the current
conditions, then picks one survivor at random.

### 2.1 Tables and pickers

| Table (file) | Records | Picker / condition check | Triggered by |
| --- | --- | --- | --- |
| `0x40000` room events | 1–201 | `0x2054c5` / `0x205723` | Room event tick, from `0x206521` |
| `0x42000` visitors | 1–262 | `0x20580e` / `0x2058b6` | Pressing A (doorbell path `0x20407b`) |
| `0x45000` stick-wiggle gags | 1–16 | `0x205997` / `0x205a1a` | Wiggle score at `0x4512`, from `0x205366` |
| `0x46000` megaphone reactions | 0–39 | `0x2053dc` / `0x205468` | Pressing A while `0x44fd` = 2 |

Each picker first refreshes the clock through `0x205acc` (reads the BIOS clock into `0x43a0`–`0x43a3`: month, day, hour, minute).

**Pick in two passes.** (1) Every record is tested for date, time, mood and minimum counter A, then rolls its own chance byte
out of 256; survivors go into a list at `0x6202` (count at `0x6201`; the visitor picker uses a word list at `0x6204`, count at
`0x6202`). (2) One entry is picked at random. Empty list means nothing happens, or the default event (2.4).

Random numbers come from a 256-byte table at `0x200e12`, indexed by three bytes at `0x456d`–`0x456f` (routine `0x200df2`).

### 2.2 Record layout

Bytes 0–15 are shared by all four tables.

| Byte | Field |
| --- | --- |
| 0–3 | Date window: month, day, month, day |
| 4–7 | Time window: hour, minute, hour, minute |
| 8–9 | Mood range (signed) |
| 10 | Mood change |
| 11–12 | Minimum counter A |
| 13–14 | Counter A gain |
| 15 | Chance out of 256 (0 = never on its own) |

Room records, bytes 16–24:

| Byte | Meaning |
| --- | --- |
| 16 | Animation class returned to the caller (1, 2, 5, 10) |
| 17 | Event id (75 ids used, numbered up to 82). Also picks Poke-kun's next state via the table at `0x207c4e` |
| 18 | Position needed: 0 anywhere, 1/2/3 left/middle/right third |
| 19 | 0 = no direction held; n = a direction pressed within the last n seconds (176 of 201 records need this) |
| 20 | Held direction code needed at `0x44c3`: 1 Up, 2 Left, 3 Down, 4 Right |
| 21 | Once flag: can't repeat until the bitmap at `0x44cf` is cleared (every menu exit clears it) |
| 22 | Chance /256 that the next tick sends him to work (`0x215108`) |
| 23 | Chance /256 that the next tick gives a bad reaction (`0x21512b`) |
| 24 | Forced follow-up: event id that plays next tick with no test |

Visitor records, bytes 16–28:

| Byte | Meaning |
| --- | --- |
| 16 | Seconds since the last visit within which byte 17 applies |
| 17 | Previous visitor id required (follow-up visit) |
| 18 | Visitor id that must already be met |
| 19 | Visitor id, 1–89. Can't repeat the previous visitor |
| 20 | Position (always 0) |
| 21–26 | 1 = blocked while Poke-kun is in state 0–5 |
| 27 | Room record that must have just played (index at `0x44cb`) |
| 28 | Reaction type, stored at `0x44fe` (1–12; 10 and 11 are break-ins) |

Wiggle records: byte 22 is the gag id, byte 23 the position (2 = middle), byte 24 the score needed (9, 20 or 60).
Megaphone records: byte 16 is the reaction id (14 distinct ids).

### 2.3 Poke-kun's state

`0x44be`, set by the last room event through `0x207c4e`.

| State | Shows | Blocks |
| --- | --- | --- |
| 0 | Standing or walking (131 records) | Nothing |
| 1 | Sitting | Nothing |
| 2 | Lying down | Nothing |
| 3 | Lying face down | Nothing |
| 4 | Busy (floating, crouched) | Breaking the door |
| 5 | In the bathroom, room empty | Minigame menu, normal visitors, wiggling, megaphone |
| 6 | Asleep in the futon (21:00–08:59 only) | Visitors, megaphone, breaking the door |

Visitor ids 70–89 are the same characters calling while he is in the bathroom. Their records allow only state 5, and the visitor
check also has a hard-coded "id ≥ 70 only in state 5" test at `0x205980`.

### 2.4 Rules that aren't in the record bytes

- **Default event.** When no room record passes, one of records 1–8 plays, chosen by mood, day period and whether a direction is
  held. Held: records 1–4, counter A +1/+2. Not held: records 5–8, **mood +2**, no counter A. This is the "idle mood drift".
- **Chains.** 26 of the 28 chance-0 room records are some other record's byte-24 follow-up. Records 167 and 176 have no parent.
- **Empty doorbell.** If no visitor qualifies, a generic visit gives mood −1 and counter A +1 (not in states 5 and 6).
- **Met bits.** Picking a visitor sets the bit for its id at `0x4558` (code `0x20409e`). These bits are the Love Love File list.
  89 ids need bits up to `0x4563`.
- **Visitor stages.** 41 of 89 ids need an earlier id already met (2 after 1, 3 after 2...), each with a higher minimum counter A,
  up to 800. About 30 characters in all; nine appear once.
- **Seasonal content.** Visitors 7–10 (the girl with the bow) need id 6 met, counter A 200 and a date window: 20–25 Dec, 1–5 Jan,
  15 Mar–10 Apr, 25–31 Oct. Room events 64–67 match those dates. Visitor 65 only comes 25 Jul–31 Aug.

### 2.5 Player input

- **Held direction** (`0x203c03`): the same single direction held for 40 frames stores 1–4 at `0x44c3`. Diagonals or release clear it.
- **Stick wiggling** (`0x20530d`): each direction change without release adds up to 3 to `0x4512`. After 78 frames a total above 10
  picks a wiggle gag whose score need it meets. Release resets the total.
- **Fast ringing:** a ring within 120 ticks of the previous visit ending adds to `0x4507`. The fifth in a row jumps to `0x2041ed`,
  which knocks the door in and sets `0x44fd` = 1. While broken the bell only makes a noise. A menu exit repairs it, about 1 in 3
  (three random bytes compared at `0x21520e`; not measured).
- **Buttons:** A rings, B opens the minigame menu, Option opens the save prompt.

### 2.6 Leaving the minigame menu

1. `0x214081` clears the once-flag bitmap `0x44cf`.
2. Counter A ≥ 500: 1 exit in 16 plays the staff roll (`0x21629d`) and skips the work roll. The roll shows 3 of 30 credits
   without repeats (bitmap `0x4568`, count `0x456c`), then starts over. It changes no counters. Seeing all 30 takes about
   160 exits after counter A reaches 500.
3. Otherwise the work roll `0x214ff0` runs (section 3.3).
4. `0x2151e6`: if nothing is pending, 1 exit in 8 sets `0x44fd` = 2 (megaphone on the door). The next A press picks from
   table `0x46000` instead of calling a visitor. A new game also starts in this state.

### 2.7 Clock and day periods

No picker blocks on the hour except through record time windows, but those are narrow: 14–17 room records are valid between
00:00 and 08:59 against about 100 in the day. Routine `0x205c20` also writes a day period 0–7 to `0x451d` from one of three
seasonal tables (pointers at `0x205cbe`); period 2 is day, 6 is night. What the other periods change on screen was not traced.

---

## 3. Unlock mechanisms

### 3.1 Saved values

All in the 77-byte saved block `0x4520`–`0x456C`. Routine `0x205a89` clamps the first three after every change.

| RAM | Value |
| --- | --- |
| `0x4520` (16-bit) | Counter A, 0–1000. Raised by visitors and room events |
| `0x4522` (s8) | Mood, −100..+100, negative = happy |
| `0x4523` (16-bit) | Counter B, 0–255. Raised only by work |
| `0x4525` | Unused flag slot 0 |
| `0x4526`–`0x4543` | Flag byte per game 1–30 |
| `0x4544`–`0x4557` | Never referenced by the game's code (used by the redesign) |
| `0x4558`– | Visitor met bits / Love Love File |
| `0x4568`, `0x456c` | Staff roll bitmap and count |

No code path was found that lowers counter A or counter B.

### 3.2 Minigames

The check `0x216b46` runs only when the minigame menu opens (called from `0x213390`). For each locked game:

```
stage = min(5, floor((100*A/T_A) / 20)) + min(5, floor((100*B/T_B) / 20))
```

Stage 10 sets the high nibble to `F` (unlocked, permanent). Stages 0–9 are stored in the high nibble and redrawn as the
construction icons (stage 0 = 予定地 placeholder, 1–9 = sprites `0x97`–`0x9F`). Consequences:

- Each counter supplies at most 5 stages, so visitors alone stop at 50%. Work is required.
- The stage is rewritten each visit, so it would fall if a counter fell.
- The loop stops at the first locked game whose stage is exactly 1.

Thresholds (`T_A`, `T_B`) are at file `0x16c0a`, two 16-bit words per game, entry 0 = slot 0. Game 1 needs 10/1, game 10 280/50,
game 30 1000/250. Full table in the unlock doc.

Flag byte low nibble: bits 0–2 = result of the last play (from `0x4802`), bit 3 = cleared (set by `0x213f54` when the result's
high nibble is 2). **Clears do not affect unlocks**; the check never reads these bits.

### 3.3 Work (counter B)

On menu exit, `0x214ff0` reads mood and the bracket tables at file `0x150B8`:

| Mood on exit | Chance | Counter B | With game 10 unlocked | Mood after |
| --- | --- | --- | --- | --- |
| below −81 | 8/16 | +8 | +10 | +5 |
| −81..−62 | 6/16 | +6 | +8 | +4 |
| −61..−42 | 4/16 | +4 | +6 | +3 |
| −41..−22 | 2/16 | +2 | +4 | +2 |
| −21..−1 | 1/16 | +1 | +2 | +1 |

Positive mood rolls for a bad reaction instead (no counter B, mood pulled down by 6–30). The roll ignores whether a minigame
was played and has no clock test. Game 10 is detected by reading `0x452f`; the two gain tables are at file `0x150CC` and `0x150E0`.

Room records with byte 22 set give a second route: `0x215108` awards work by the same brackets, always succeeding once triggered.

### 3.4 Page E and the Love Love File

`0x216b60` (on menu open) sets `0x4803` = `0xFF` only if all 30 flag bytes have bit 3 set. While `0x4803` ≠ 0 the menu shows a
hidden seventh page, E, which opens the Love Love Profile catalog. Profiles shown there depend on the met bits at `0x4558`.
Holding `0x4803` non-zero in MAME is enough to reach the catalog for testing.

### 3.5 Community claims, checked

| Claim | Result |
| --- | --- |
| Leaving the menu sends him to work, not guaranteed | True, 1–8 in 16 by mood |
| Playing minigames isn't needed | True |
| Visitors alone reach about 50% | True |
| Start around 10 AM | Consistent: day has about twice the valid visitor records |
| No unlocks at night | False: no clock test; night only has fewer events |
| Clearing games limits new unlocks | False |
| Clearing all 30 opens page E | True (code) |

### 3.6 Still open

- How often room event ticks fire in real time.
- Meaning of result values 1–7 in flag bits 0–2.
- What day periods 0, 1, 3, 4, 5, 7 change on screen.
- The 1 in 3 door repair chance is read from code, not measured.

---

## 4. The redesign ("seen it once")

An optional gameplay patch on top of the translation. Goal: every new scene pays, work is never a dice roll, and the calendar
comes to the player instead of the real clock.

```
python tools/redesign.py build/neopoke_en.ngc build/neopoke_en_redesign.ngc
```

It works on the original ROM or any translated build whose VWF block ends below `0x1F7800`. Every pacing number is a constant at
the top of the file. The tool refuses to run if a patch site doesn't hold the expected original bytes, or if the code area isn't blank.

### 4.1 What changes

| Area | Original | Redesign |
| --- | --- | --- |
| Counter A | +0/+1/+2 per event, repeats included | +5 (`GAIN`) the first time a scene plays, 0 after. Scene = room event id, visitor id, wiggle gag or megaphone reaction: 194 scenes, 970 points |
| Picking | Uniform among survivors | Survivors not yet seen are kept first; seen ones only if nothing new qualifies |
| Work | 1–8 in 16 when happy | Always when mood < 0. Pays 8/6/5/4/3 counter B by bracket and adds 30/25/20/15/8 to mood. Game 10 bonus removed (both gain tables get the same values) |
| Clock | BIOS date and time | Saved calendar of 12 dates × 7 times (84 stops), one step per menu exit |
| Thresholds | 10/1 … 1000/250 | Game n: counter A 5 + 24(n−1), counter B n. Game 30: 701 (141 scenes) and 30 |
| Record "min counter A" | as shipped | × 0.6, rounded to 5 |
| Staff roll | A ≥ 500, 1/16, replaces work | A ≥ 100, 1/4, only on exits where he isn't happy |
| Default events 1–8 | counter A +1/+2, idle mood +2 | No counter A, idle drift 0 |
| Empty doorbell | counter A +1 | 0 |

Loosened conditions (added after the first bot runs, see 4.4):

- Room mood edges ±34/35 → ±8/9 and ±67/68 → ±16/17; visitor and megaphone edges ±67/68 → ±8/9; the unhappy default-event edge
  at file `0x55CA` follows.
- Room records with chance 0 get chance 40, so follow-ups can also start alone.
- Visitors no longer need a particular room event just before (byte 27 cleared).
- Seasonal room records 65–68 accept any mood. Bathroom record 182 gets chance 255 and any mood.
- Visitors 70–89: any hour, any state (record bytes 21–25 cleared and the hard-coded test at `0x205980` widened to `0xFF`).
- Two visitor records with min/max mood swapped (could never match) are fixed.

### 4.2 Code and hooks

New code and the calendar table sit at file `0x1F7800`–`0x1F7DF4` (1525 bytes: 501 of code, 1024 of calendar table), just below the save slots at `0x1F8000`.
The assembler in the tool emits only TLCS-900 encodings copied from the game's own code.

| Routine | Role |
| --- | --- |
| `BT`, `BS` | Test / set bit A of a bitmap at XIX |
| `AWARD`, `ADD` | First time: set the seen bit and add `GAIN` to counter A |
| `AW_room/visitor/wiggle/megaphone` | Replace each picker's "add record bytes 13–14 to counter A". Visitors only test the met bit, because the game sets it itself later |
| `FI_*` | Run after each picker's filter pass: compact the candidate list to unseen entries if any exist, then redo the game's "list empty?" compare |
| `CALADV` | Advance the calendar step, then jump to the routine the hook replaced |
| `STAFFRNG` | Random number for the staff roll, forced to "no" when mood is negative |
| `INIT` | New game: clear the 20 new saved bytes |
| `CALTAB` | 256 × (month, day, hour, minute); index = step, so a stray value is harmless |

Patch sites (file offsets):

| Offset | Change |
| --- | --- |
| `0x5549`, `0x59D1`, `0x542C`, `0x584B` | Filter hooks: room, wiggle, megaphone, visitor |
| `0x5578`, `0x587E`, `0x59FC`, `0x5457` | Award hooks |
| `0x58A1` | No counter A for an empty doorbell ring |
| `0x5ACC` | Clock routine body replaced: reads `CALTAB[step]` into `0x43a0`–`0x43a3` |
| `0x14081` | Menu exit calls `CALADV` |
| `0x14085`, `0x14091`, `0x1408D` | Staff roll threshold, chance mask, `STAFFRNG` |
| `0x150B8`–`0x150F3` | Work brackets (chance bytes set to `0x0F` = always) and both gain tables |
| `0x16C0A` | Threshold table |
| `0x18EE` | New-game init calls `INIT` |
| `0x55CA`, `0x5980` | Mood edge for default events; bathroom visitor id test |
| `0x40000`, `0x42000`, `0x45000`, `0x46000` | Record edits listed in 4.1 |

New saved RAM, inside the block the game already saves:

| RAM | Size | Holds |
| --- | --- | --- |
| `0x4544` | 11 | Room event ids seen |
| `0x454F` | 3 | Wiggle gags seen |
| `0x4552` | 2 | Megaphone reactions seen |
| `0x4554` | 1 | Calendar step 0–83 |

Visitors reuse the game's met bits at `0x4558`. The save format and size are unchanged. A save from the unpatched game loads, but
its spare bytes were never cleared, so start a new game.

### 4.3 Differences from the original proposal

The proposal in the unlock doc differs from what was built in a few places: the gain is +5, not +2; the calendar steps on every
menu exit and does not skip stops with nothing new; mood edges went further than ±34; there is no pity clear for page E (user decision).
The prototype table in the doc still lists the first-pass edges (±34/±51); the code is authoritative.

### 4.4 Testing

Unit checks in MAME (`work/trace/run.sh`, runs p1–p8): +5 on new room events, visitors and megaphone reactions, 0 on a repeat
visitor; mood −50 gave work, +4 B; calendar showed 10:00, 12:30, 16:30 on successive exits and the room switched to daytime;
A 53 / B 5 unlocked games 1–3; seen flags and calendar step survived save + soft reset.

Bot runs (two seeds each, 3 game-hours):

| Build step | Scenes seen (of 194) | All 30 games at |
| --- | --- | --- |
| Before loosening | 118–133 | 65–99 min |
| Mood bands, follow-ups, no room prerequisite | 156–160 | ~70 min |
| No idle drift, work spends less mood | 163–168 | ~35 min |
| Bathroom visitors any time (current) | 181, 184 | 39, 42 min |

All 89 visitors and all 16 wiggle gags were seen in the final runs. No crash or hang. Only the BIOS, the game's boot code and the
patch wrote to `0x4544`–`0x4557`; one minigame ran for three hours in a separate run without touching them.

Never seen by the bot: room events 4, 19, 20, 30, 33, 41, 51, 53, 58 (strong mood plus a narrow hour or season) and megaphone
reaction 3.

### 4.5 Known limits

- 30 games in about 40 minutes may be too fast. `A_STEP` controls it; 180 scenes took about two hours.
- Nothing on screen tells the player that leaving the menu moves time on.
- Calling on an empty bathroom is lost as a joke: bathroom visitors now see him standing in the room.
- Not tested: a human player, minigames other than the first, the 29 other minigames' RAM use.
- The bot can't detect the menu reliably once all 30 games are unlocked (no stage byte is rewritten), so its counts after that are rough.

### 4.6 Builds

| File | Contents |
| --- | --- |
| `build/neopoke_en.ngc` | Translation + graphics |
| `build/neopoke_en_redesign.ngc` | Same + redesign |
| `build/*_allgames.ngc` | Same, with `make_save.py` slot 0 (all games unlocked) |
| `build/proto_redesign_jp.ngc` | Redesign on the original Japanese ROM, used for the MAME tests |
| `build/patches/*.ips` | IPS patches for the four English builds |
