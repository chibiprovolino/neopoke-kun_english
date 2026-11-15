# Ganbare Neo Poke-kun: how minigames unlock

Nov 14, 2026

## Summary

A minigame unlocks when two saved counters both reach that game's thresholds, and the check runs only when the minigame menu opens. Counter A (0–1000) grows from visitors and room events. Counter B (0–255) grows only when Poke-kun goes to work.

Poke-kun goes to work mainly when you leave the minigame menu while he is happy. The chance is at most 8 in 16 per exit, and each session spends some of his good mood.

The rule was read from the disassembly (`work/dis/code.asm`) and the ROM tables, then confirmed in MAME by setting the counters, mood and clock directly. The names "counter A", "counter B" and "mood" are labels chosen for this report; the game does not name them.

## The unlock check

Routine `0x216b46` recomputes every locked game's state each time the minigame menu opens. It is called from the menu task at `0x213390` and nowhere else, so a game never unlocks while you stay in the room.

Each game has one flag byte at RAM `0x4526`–`0x4543` (games 1–30). `0x4525` is an unused slot 0 that shares game 1's thresholds.

| Part of the byte | Meaning |
| --- | --- |
| High nibble `F` | Unlocked. Permanent: the routine skips the game from then on. |
| High nibble `0`–`9` | Construction stage, recomputed at every menu visit. |
| Bits 0–2 | Result of the last play, copied from `0x4802`. |
| Bit 3 | Cleared flag, set when the result code in `0x4802` is 2. |

The stage is the sum of two parts, one per counter:

```latex
\text{stage} = \min\left(5, \left\lfloor \frac{100 A / T_A}{20} \right\rfloor\right) + \min\left(5, \left\lfloor \frac{100 B / T_B}{20} \right\rfloor\right)
```

Stage 10 unlocks the game, which needs both counters at or above their thresholds. Each counter alone can give at most 5, so visitors without work stop at 50%.

- **Icons:** stage 0 draws the 予定地 placeholder. Stages 1–9 draw sprites `0x97`–`0x9F`, the construction art.
- **Early stop:** the loop ends at the first locked game whose stage is exactly 1. Games after it keep their old stage for that visit.
- **Stages can fall:** a locked game's stage is overwritten each visit, so it follows the counters down as well as up. Counter A and counter B have no decreases in the code read so far.

## Thresholds

Game 30 needs counter A at its maximum of 1000 and counter B at 250 of a possible 255. The table is at file offset `0x16c0a`, two 16-bit values per game.

| Game | A needed | B needed |
| --- | --- | --- |
| 1 | 10 | 1 |
| 2 | 40 | 3 |
| 3 | 70 | 5 |
| 4 | 100 | 10 |
| 5 | 130 | 15 |
| 6 | 160 | 20 |
| 7 | 190 | 28 |
| 8 | 220 | 36 |
| 9 | 250 | 42 |
| 10 | 280 | 50 |
| 11 | 310 | 60 |
| 12 | 340 | 70 |
| 13 | 370 | 80 |
| 14 | 400 | 90 |
| 15 | 430 | 100 |
| 16 | 460 | 110 |
| 17 | 490 | 120 |
| 18 | 520 | 130 |
| 19 | 550 | 140 |
| 20 | 580 | 150 |
| 21 | 610 | 160 |
| 22 | 640 | 170 |
| 23 | 690 | 180 |
| 24 | 720 | 190 |
| 25 | 750 | 200 |
| 26 | 800 | 210 |
| 27 | 850 | 220 |
| 28 | 900 | 230 |
| 29 | 950 | 240 |
| 30 | 1000 | 250 |

Counter A steps by 30 per game up to game 22, then by 30–50. Counter B steps by 10 per game from game 10 onward, which is more than one work session gives before game 10 is unlocked.

## The three saved values

Three values in the save block drive everything: two counters that only rise, and a mood value that swings both ways. A new save sets all three to zero. Routine `0x205a89` clamps them after every change.

| Value | RAM | Range | Rises from | Falls from |
| --- | --- | --- | --- | --- |
| Counter A | `0x4520` (16-bit) | 0 to 1000 | Visitors and room events, +1 or +2 each | Nothing found |
| Mood | `0x4522` (signed byte) | −100 to +100; negative is happy | Bad encounters, unhappy menu exits | Good encounters, work sessions pull it toward 0 |
| Counter B | `0x4523` (16-bit) | 0 to 255 | Work sessions, +1 to +10 each | Nothing found |

**Mood runs backwards.** A negative value means Poke-kun is happy. Only negative values produced work in testing, and the encounters the guides call positive move the value down.

**Events come from three tables** of 32-byte records at file `0x40000` (201 room events), `0x42000` (262 records, read as the visitor table) and `0x46000` (40 records). The game picks at random among the records whose conditions all pass.

| Record bytes | Field |
| --- | --- |
| 0–3 | Date range: month, day, month, day |
| 4–7 | Time range: hour, minute, hour, minute |
| 8–9 | Mood range the event needs |
| 10 | Mood change |
| 11–12 | Minimum counter A |
| 13–14 | Counter A gain |
| 15 | Chance out of 256 |

In the visitor table, records for a not-yet-happy Poke-kun (mood −67 to +100) change mood by −6 to −10 and add 1 to counter A. Records for an already very happy one (mood −100 to −68) change it by only −3 to −5 and add nothing. Bad encounters mirror this with +2 to +6. Many records also need a minimum counter A of 100 to 800, so later visitors appear only as the game progresses.

## Going to work

Leaving the minigame menu with B rolls once for a work session, and the happier Poke-kun is, the better the odds and the bigger the gain. The roll is routine `0x214ff0`, reached from the menu's exit path at `0x21407b`. It does not look at whether a minigame was played.

| Mood on exit | Chance | Counter B gain | Gain once game 10 is unlocked | Mood afterwards |
| --- | --- | --- | --- | --- |
| Below −81 | 8 in 16 | +8 | +10 | +5 |
| −81 to −62 | 6 in 16 | +6 | +8 | +4 |
| −61 to −42 | 4 in 16 | +4 | +6 | +3 |
| −41 to −22 | 2 in 16 | +2 | +4 | +2 |
| −21 to −1 | 1 in 16 | +1 | +2 | +1 |
| 0 | none |  |  |  |

When mood is positive, the same exit rolls for a bad reaction instead. It gives no counter B and pulls mood back toward zero.

| Mood on exit | Chance | Mood afterwards |
| --- | --- | --- |
| +81 or more | 8 in 16 | −30 |
| +61 to +80 | 6 in 16 | −24 |
| +41 to +60 | 4 in 16 | −18 |
| +21 to +40 | 2 in 16 | −12 |
| +1 to +20 | 1 in 16 | −6 |

- **Game 10 bonus:** the roll checks game 10's flag byte (`0x452f`). Once it is unlocked, every bracket pays 2 more, except the lowest, which pays 1 more.
- **Second route, in the room:** routine `0x215108` awards work after certain room events, using a per-event chance byte. It pays +8, +6, +4, +3, +2 or +1 by the same mood brackets (10, 8, 6, 4, 2, 2 with game 10) and always succeeds once triggered.
- **Work spends happiness:** every session moves mood up by 1–5, so a second session in a row has worse odds unless new good encounters come first.
- **Late-game branch:** with counter A at 500 or more, an exit has a 1 in 16 chance of jumping to `0x21629d` instead of rolling. That code is the staff roll (see "Traced inputs and scenes").

## Time of day

The work roll and the unlock check have no clock test, and work was awarded at 00:00 in MAME. Night is poorer, not blocked: far fewer events are valid then, so mood and counter A move more slowly.

Counts below are records whose time range covers the hour, ignoring their date, mood and counter A conditions.

| Hour | Visitor records valid | Of those, improve mood | Room events valid |
| --- | --- | --- | --- |
| 00:00–08:59 | 58 | 34 | 14–17 |
| 10:00 | 106 | 76 | 88 |
| 13:00 | 112 | 78 | 103 |
| 17:00 | 110 | 76 | 105 |
| 19:00 | 114 | 84 | 102 |
| 21:00–23:59 | 72 | 48 | 18 |

The game also sorts the day into eight numbered periods, stored at `0x451d` and chosen by routine `0x205c20` from one of three seasonal tables (pointers at `0x205cbe`). Period 6 is night and period 2 is the long daytime stretch. What periods 0, 1, 3, 4, 5 and 7 each mean on screen was not traced.

| Period | 16 Mar–15 Jun and 16 Sep–30 Nov | 16 Jun–15 Sep | 1 Dec–15 Mar |
| --- | --- | --- | --- |
| 6 (night) | 19:00–04:59 | 19:30–04:29 | 18:01–06:59 |
| 7 | 05:00–05:29 | 04:30–05:00 | 07:00–07:30 |
| 0 | 05:30–06:59 | 05:01–06:00 | 07:31–08:59 |
| 1 | 07:00–09:29 | 06:01–08:59 | 09:00–09:59 |
| 2 (day) | 09:30–16:09 | 09:00–16:39 | 10:00–15:29 |
| 3 | 16:10–16:40 | 16:40–17:09 | 15:30–16:00 |
| 4 | 16:41–18:19 | 17:10–19:00 | 16:01–17:30 |
| 5 | 18:20–18:59 | 19:01–19:29 | 17:31–18:00 |

The 10 AM start recommended by one player falls inside period 2 in every season.

## Clears and page E

Clearing minigames does not unlock other minigames. The unlock check reads only the two counters and each game's high nibble; it never looks at the result bits.

Clears matter for one thing. Routine `0x216b60` runs when the menu opens and sets `0x4803` to `0xFF` only if all 30 flag bytes have bit 3 set. While `0x4803` is non-zero the menu shows the hidden seventh page, E, which opens the Love Love File catalog.

Bit 3 is written by routine `0x213f54` after a play, when the upper nibble of the result byte `0x4802` equals 2. The lower three bits of the same byte are copied into bits 0–2. The community reports that an ordinary clear is enough for page E, which fits bit 3 being a cleared flag and bits 0–2 a separate rank. The meaning of each rank value was not traced.

## MAME tests

Every prediction from the code held in MAME on the original ROM. Each run cold-boots, enters the room, writes the starting values at frame 2250, then presses B every 350 frames to open and leave the menu. No minigame was played in any run.

| Run | Starting values | Clock | What happened |
| --- | --- | --- | --- |
| Unlock formula | A 280, B 50 | 00:00 | Games 1–10 unlocked at the first menu visit; game 11 at stage 8, game 12 at stage 7, as computed |
| 50% cap | A 100, B 0, mood +90 | 10:00 | Games 1–4 sat at stage 5 for the whole run |
| Work by day | A 280, B 50, mood held at −90 | 10:00 | 6 sessions, each +10 B |
| Work by night | A 280, B 50, mood held at −90 | 00:00 | 5 sessions, each +10 B |
| Gain before game 10 | A 100, B 0, mood −90, not held | 10:00 | Sessions of +8, +6, +6, +4; mood moved +5, +4, +4, +3; games 1–5 unlocked by the end |
| Unhappy exits | A 100, B 0, mood +90, not held | 10:00 | No B gained; mood dropped by 30, 18, 18 and 12 |

- **Success rate:** 5–6 sessions in about 25 exits is below the 8 in 16 the code gives. After a session the menu ignores input for a while, so some scripted presses were lost and the exit count is approximate.
- **Mood drift:** mood crept up by about 2 on many exits that awarded nothing. The source was not traced. Idle menu cycling therefore slowly erodes a good mood.
- **Reproducing:** `work/unlocktest/run.sh <name>` with `UT_A`, `UT_B`, `UT_MOOD`, `UT_HOLDMOOD`, `UT_HOUR` and `UT_SEQ` set. `UT_HOUR` takes the hour as it reads in BCD, so 16 means 10:00. Logs are in `work/unlocktest/out/`.

## Community guides against the code

The guides describe the right procedure, and the code explains why it works. Two claims are not supported: that clears gate new games, and that night blocks unlocks. The claims are taken from the guide notes supplied in this conversation; the guides themselves were not opened.

| Claim | Source in the notes | What the code shows | Verdict |
| --- | --- | --- | --- |
| Leaving the minigame menu triggers going to work | Japanese GeoCities guide | The exit path calls the work roll at `0x214ff0` | Confirmed in MAME |
| "High probability", not guaranteed | Same | 1 to 8 in 16 per exit, by mood | Confirmed; 50% at best |
| Repeat the menu step if nothing happens | Same | Each exit is a new roll | Confirmed, but failed exits cost about 2 mood each |
| 6–8 positive encounters first | Same | Good encounters give −6 to −10 mood; eight reach about −64, the 6 in 16 bracket | Consistent |
| Playing a minigame may not be needed | Same | The roll ignores play results | Confirmed in MAME |
| Save good encounters, reset bad ones | Both Japanese guides | Counters and mood are all in the save block `0x4520`–`0x456C` | Consistent |
| Visitors alone reach about 50% | RetroAchievements developer | Counter A supplies at most 5 of 10 stages | Confirmed in MAME |
| No unlocks at night | Same | No clock test in the roll or the check; work awarded at 00:00 | Not supported; night only has fewer events |
| Start around 10 AM | Steam discussion | 10:00 is in the daytime period in every season, with about twice the visitor records of night | Consistent |
| Sixth-generation games stick at 90% and need two more sessions | Spanish community guide | Late games need +10 B each; one session gives at most +8, or +10 with game 10 | Consistent |
| Clearing games limits how many new ones unlock | Older English review | The unlock check never reads clear bits | Not supported |
| Clearing all 30 opens page E | Several | `0x216b60` needs bit 3 on all 30 flags | Confirmed in code |

Not checked against the code: the joystick-rotation disasters, the doorbell breaking after five rings, and which named visitors are negative.

## A routine that follows from the code

The guides' loop is right; the code adds the numbers that tune it. Mood is not shown on screen, so the encounter counts below are estimates from the visitor table.

1. Play between 09:00 and 20:59 on the console clock, when most visitor records are valid.
2. Summon visitors and keep only the good outcomes by saving, as the guides describe. From a neutral mood, about 8 good encounters reach the 6 in 16 bracket and about 11 reach the 8 in 16 bracket.
3. Open the minigame menu and leave it with B. Do not play; it makes no difference to the roll.
4. If he does not go to work, repeat the exit a few times. Each failed exit costs about 2 mood, so return to visitors after three or four failures.
5. After a work session, add one good encounter before the next exit. The session itself gave back 3–5 mood.
6. Open the menu again to register progress. Stages and unlocks update only there.

- **Aim for game 10 early.** It needs A 280 and B 50, and from then on every session pays about 2 more.
- **Counter A is the long pole.** Game 30 needs 1000, and encounters and room events give 1 or 2 each. Counter B needs about 7 best-case sessions to reach 50, then 20 more to reach 250.
- **A very happy Poke-kun earns no counter A from visitors.** Below about −68 mood, the good-encounter records that apply add nothing to counter A, so alternate visitor streaks with work sessions.

## Event records decoded

Every byte of the 32-byte event records is now read, along with the four routines that pick from them. The extra bytes add position, input, chain and prerequisite conditions; none of them is a hidden rarity weight. All of this section is read from the disassembly and the ROM tables and was not run in MAME.

### Four tables, four pickers

Bytes 0–15 mean the same in every table (see "The three saved values"). Each picker refreshes the clock through `0x205acc`, filters its table, then picks one survivor at random.

| Table (file offset) | Records | Picker | When it runs |
| --- | --- | --- | --- |
| `0x40000` room events | 1–201 | `0x2054c5`, check `0x205723` | Each room event tick, called from `0x206521` |
| `0x42000` visitors | 1–262 | `0x20580e`, check `0x2058b6` | The doorbell path at `0x20407b` |
| `0x45000` | 1–16 | `0x205997`, check `0x205a1a` | From `0x205366`, after a counter at `0x4512` builds up. Byte 24 is the minimum count (9, 20 or 60). The counter measures stick wiggling (see "Traced inputs and scenes"). |
| `0x46000` | 0–39 (40, not 24) | `0x2053dc`, check `0x205468` | When `0x44fd` is 2, which a menu exit sets with a 1 in 8 chance if no work or bad reaction was triggered |

### Room records, bytes 16–24

| Byte | Meaning | Values |
| --- | --- | --- |
| 16 | Animation class returned to the caller | 1, 2, 5, 10 |
| 17 | Event id. It also selects Poke-kun's next state (0–6) from the table at `0x207c4e`. | 75 ids across 201 records |
| 18 | Where Poke-kun must stand: 0 anywhere, 1–3 left, middle or right third of the room | 67 records need a position |
| 19 | Input: 0 needs no direction held; otherwise a direction must have been pressed within that many seconds | 0 on 25 records, 1 s on 64, 5 s on 2, 10 s on 110 |
| 20 | A held-input code 1–4 at `0x44c3`. 1 Up, 2 Left, 3 Down, 4 Right, each held for 40 frames. | 64 records need one |
| 21 | Once flag: the record cannot repeat until the bitmap at `0x44cf` is cleared, which every menu exit does | 35 records |
| 22 | Chance out of 256 that the next room tick sends him to work (`0x215108`) | 50 or 80, on 18 records |
| 23 | Chance out of 256 that the next room tick gives a bad reaction (`0x21512b`) | 50 or 80, on 17 records |
| 24 | Forced follow-up: the event id that passes the next tick with no test at all | 91 records |

- **Chance-0 records are the second halves of chains.** 26 of the 28 are named by another record's byte 24, so they play right after their parent. Records 167 and 176 have no parent in the table.
- **The default event explains the +2 mood drift.** When no record passes, the game plays one of records 1–8, chosen by mood, day period and whether a direction is held. Held: records 1–4, counter A +1 or +2 and mood +1 to −1. Not held: records 5–8, mood +2 and no counter A. The MAME scripts never touched the stick, so they got records 5–8.
- **An idle player sees almost nothing.** 176 of 201 room records need a direction press in the last 1 to 10 seconds.

### Visitor records, bytes 16–28

| Byte | Meaning | Values |
| --- | --- | --- |
| 16 | Seconds since the last visit ended within which byte 17 applies | 3 on 36 records |
| 17 | Previous visitor id required: a follow-up visit | 36 records |
| 18 | Visitor id that must already be met (its Love Love bit set) | 134 records |
| 19 | Visitor id, 1–89. It cannot equal the previous visitor. | 2, 4 or 8 records per id |
| 20 | Position, as room byte 18 | Always 0 |
| 21–26 | 1 blocks the record while Poke-kun is in state 0–5 | State 5 blocks 164 of 262 |
| 27 | Room record that must have just played (index at `0x44cb`) | 44 records, tied to 14 room events |
| 28 | Reaction type, stored at `0x44fe` | 1–12 |

- **The Love Love File is the list of visitors met.** When a visitor is picked, the doorbell path sets the bit for its id at `0x4558` (code at `0x20409e`).
- **Visitor ids are stages.** 41 of the 89 ids can only appear after an earlier id is met: 2 after 1, 3 after 2, and so on, each with a higher minimum counter A, up to 800.
- **Holiday visitors** 7–10 need id 6 met, counter A at 200 and their date window (20–25 Dec, 1–5 Jan, 15 Mar–10 Apr, 25–31 Oct). Id 65 appears only from 25 Jul to 31 Aug.
- **If nobody qualifies,** a generic visit gives mood −1 and counter A +1, except in states 5 and 6.
- **Fast ringing is counted.** A ring within 120 ticks of the previous visit ending adds to `0x4507`, and the fifth such ring in a row jumps to `0x2041ed`. That code breaks the door (see "Traced inputs and scenes").

### Menu exit, step by step

1. `0x214081` clears the once-flag bitmap.
2. With counter A at 500 or more, 1 exit in 16 plays a bonus scene (`0x21629d`) and skips the work roll.
3. Otherwise the work roll at `0x214ff0` runs.
4. `0x2151e6`: if no reaction is pending, 1 exit in 8 arms an event from table `0x46000`.

The bonus scene shows three of 30 items per showing. It picks them without repeats, using a saved bitmap at `0x4568` and a count at `0x456c`, and starts over after all 30. It changes no counters. It is the staff roll: each showing is three staff credits, so all 30 take ten showings.

### Traced inputs and scenes

The five items left open above were read from the code and then triggered in MAME on the original ROM. Snapshots are in `work/trace/out/`.

| Item | What the code does | Seen in MAME |
| --- | --- | --- |
| Held direction (`0x44c3`, room byte 20) | Routine `0x203c03` counts frames while the same single direction stays held. At 40 frames it stores 1 Up, 2 Left, 3 Down or 4 Right. Diagonals and release clear it. | Holding each direction for 60 frames gave 1, 2, 3, 4 in that order. |
| Stick wiggling (`0x4512`, table `0x45000`) | Routine `0x20530d` adds up to 3 points each time the held direction changes without a release. After 78 frames, a total above 10 picks one of 16 records whose byte 24 (9, 20 or 60) the total reaches. A release resets the total. | Alternating Left and Right every 4 frames reached 60; a washtub fell on Poke-kun's head. |
| Fifth quick ring (`0x2041ed`) | The door is knocked into the room and `0x44fd` becomes 1. While it is 1 the bell only makes a noise. Each menu exit repairs it with a chance of about 1 in 3. | The door flew in, the screen faded, and the door came back boarded up. |
| Megaphone (`0x44fd` = 2, table `0x46000`) | After a menu exit with nothing pending, 1 chance in 8 arms it. The next ring then picks from the 40 megaphone records instead of calling a visitor. | A megaphone hangs on the door; pressing A blares it and startles Poke-kun. The game also starts in this state. |
| Staff roll (`0x21629d`) | Three of 30 credits per showing, without repeats, then it starts over. | Poke-kun presented credit cards such as "Minigame Designer" and "Debugger". |

Poke-kun's state (`0x44be`) is set by the last room event, through the table at `0x207c4e`. The 75 event ids in use are numbered up to 82.

| State | Room records | What it shows | What it blocks |
| --- | --- | --- | --- |
| 0 | 131 | Standing or walking | Nothing |
| 1 | 24 | Sitting on the floor | Nothing |
| 2 | 21 | Lying down | Nothing |
| 3 | 12 | Lying face down | Nothing |
| 4 | 4 | Busy: floating in the air (ids 53, 58) or crouched (id 9) | The door cannot be broken |
| 5 | 7 | Walks into the bathroom; the room is empty | The minigame menu, visitors, wiggling and megaphone events |
| 6 | 2 | Asleep in the futon (id 61, 21:00 to 08:59 only) | Visitors, megaphone events, breaking the door |

- **Buttons in the room:** A rings the bell, B opens the minigame menu, Option goes to the save prompt.
- **Staff roll cost:** ten showings at 1 exit in 16 is about 160 menu exits on average, all after counter A reaches 500. It is the slowest content in the game to see in full.
- **Broken door cost:** no visitor can come until a menu exit repairs it, so it stalls counter A.
- **Not checked:** the 1 in 3 repair chance is my reading of three random bytes compared at `0x21520e`; it was not measured.

### Scene catalogue

All 194 scenes were forced in MAME and pictured: 75 room events, 89 visitors, 16 stick-wiggle gags and 14 megaphone reactions. `work/trace/catalogue.py` builds the page (not included here, it holds game screenshots). Each entry has snapshots, one sentence on what happens, and the conditions from its records.

- **Visitors are about 30 characters, not 89.** Twenty-one characters have two to six ids each, which are stages of the same relationship, and nine appear once. Ids 70 to 89 are the same characters calling while Poke-kun is in the bathroom; their records are blocked in every other state.
- **Break-ins:** visitors with reaction type 10 or 11 knock the door down, play a longer scene inside the room, and end on a screen of static.
- **Seasonal scenes:** the girl with the bow has Christmas, New Year, blossom and Halloween outfits (visitors 7 to 10), and Poke-kun has matching room events on the same dates (64 to 67). Summer, Jul 25 to Aug 31, has its own visitor (65) and room events.
- **Limits:** the sentences are my reading of small sprites. Which dating-profile character each visitor is was guessed for 14 of them and not checked against the Love Love File.
- **Rebuilding:** `work/trace/jobs.txt` lists the MAME run for each scene, and `python work/trace/catalogue.py` rebuilds the page from the snapshots and `work/trace/catalogue_desc.py`.

### Save format

- **Slots:** the 77 saved bytes go into a 256-byte record with a checksum. There are 32 slots at file `0x1F8000`–`0x1F9FFF` (flash block `0x20`). Each save takes the next blank slot, and when none is blank the game erases the whole block (`0x20185b`).
- **Loading** takes the highest slot whose first byte is 0 and whose checksum matches (`0x201894`).
- **Spare room:** each slot has 177 unused bytes. RAM straight after `0x456C` holds the random-number state, so extra saved data needs its own copy loop.
- **Conflict with the translation build:** the VWF code and big-font glyphs sit at `0x1F8000`–`0x1FA5FF`. In `build/test_fonts3.ngc` no save slot is blank, so the first save should erase the VWF code. Four slots of blank glyph data also pass as a valid empty save. Reproduced in MAME: that build went to a white screen on its first save. Fixed in build/test\_fonts4.ngc by moving the VWF block to 0x1F5000–0x1F75FF; it saved three times with the VWF intact and loaded the save after a reset.

## Proposed redesign: "seen it once" progression

An alternative to a straight translation patch: keep the two counters, the construction icons and the work loop, but change what earns progress. Seeing something new always pays, work is never a dice roll, and the calendar comes to the player. This is a design only; nothing is built or tested.

### What makes the original frustrating

- **Hidden dice:** work is at most 8 in 16 per menu exit, on a mood value the player cannot see.
- **Repeats pay the same as new content:** counter A needs 1000 at +1 or +2 per event, and about half the records pay nothing.
- **Bad outcomes are pure loss,** which is why the guides recommend resetting after them.
- **Content is locked to the real clock:** 88 of 201 room events are seasonal, some in windows as short as 1–5 Jan, 20–25 Dec and 25–31 Oct. Almost every record also has an hour window.
- **Content is locked to a miserable Poke-kun:** 83 records need mood +68 or worse, which a player chasing unlocks never reaches.
- **Common events crowd out rare ones:** see "How events are picked" below.

### The four rules

| Rule | Original | Revised |
| --- | --- | --- |
| Counter A | +1 or +2 for some events, repeats included | +2 the first time each record is seen, good or bad; 0 for repeats. The picker offers unseen records first. |
| Work (counter B) | Random roll on menu exit, by mood | Guaranteed on menu exit whenever he is happy. Pay is proportional to the happiness spent, and mood resets to 0. |
| Clock | Console date and time | A saved virtual calendar of about 12 date stops × 7 time stops, enough to cover every window in the tables. It moves one stop each time he returns from work and skips stops with nothing unseen. |
| Mood bands | Edges at ±68 | Edges at ±34, a data-only edit, so ordinary swings reach the sulking content. |

- **Thresholds become linear:** game N needs about 10 new events and a few work sessions. With roughly 500 records, all 30 games unlock at about 60% of the content, and the calendar completes about one year over the same stretch.
- **Page E still needs 30 clears.** If a minigame proves too hard, an optional "pity clear" after five failures would cover it.
- **Estimated length:** 4–5 hours to all minigames and 7–8 hours to everything. Encounter length is unmeasured, so the thresholds need a simulation against the tables.

### How events are picked

Events are random, and some are several times rarer than others. Each picker makes two passes, read from the code at `0x2059b0`, `0x205a1a` and `0x2055eb`.

1. **Filter:** every record in the picker's range is tested for date, time, mood and minimum counter A, then rolls its own chance byte out of 256. Survivors go into a list at `0x6202`.
2. **Pick:** one survivor is chosen at random. If the list is empty, no event happens.

| Chance byte | Odds of entering the list | Room records | Visitor records |
| --- | --- | --- | --- |
| 255 | Almost always | 63 | 38 |
| 100 | 39% | 4 | 0 |
| 80 | 31% | 5 | 107 |
| 60 | 23% | 101 | 116 |
| 0 | Never | 28 | 1 |

- **Always-on records dominate:** in a simulation of the visitor table at 13:00 with counter A at 1000, each chance-255 record came up about 6% of the time and each chance-60 record about 1.4%. The simulation ignores the prerequisite bytes listed in "Event records decoded", so the figures are rough.
- **Seeing a full pool takes long:** about 50 records are eligible at once in that case, most of them at 1.4% each, with repeats in between.
- **Chance-0 room records are chain follow-ups,** not unreachable. They play straight after their parent record.
- **The random source** is a 256-byte table at `0x200e12`, indexed from three bytes at `0x456d`–`0x456f`.

### Why the redesign fits the code

- **One clock hook:** every event picker and the day-period routine read the time through `0x205acc`. Substituting the virtual calendar there covers them all.
- **One shared condition check:** all four picker loops call `0x205a1a` and build a candidate list before picking. An unseen-first filter fits in that loop.
- **Mostly table edits:** thresholds at `0x216c0a`, the work chances at `0x214ff0`, and the mood ranges in the records.
- **A fourth event table** sits at `0x245000` (16 records). It is described in "Event records decoded".

### To settle before building

- **Translation build first:** the save-area conflict in "Save format" is fixed in build/test\_fonts4.ngc; gameplay patches should start from that build.
- **Save space is settled.** Each slot has 177 spare bytes. Visitors need none, because the met bits at `0x4558` already record first meetings. Seen-flags by event id for the other three tables need about 18 bytes.
- **Love Love File is settled.** Bits are set by visitor id, in stages. An unseen-first picker must keep the stage prerequisites, which it does if it only filters the candidate list.
- **Exit branch is settled.** `0x21629d` is the staff roll, three credits per showing. The redesign should let the work roll run after it and show it far more often than 1 exit in 16.
- **Default event:** records 5–8 add +2 mood whenever the player is idle. The redesign should set that to 0, or guaranteed work is eroded by waiting.
- **Input conditions:** most room events need recent stick input, so the pacing estimate must assume an active player.
- **Traced since:** the held inputs, stick wiggling, Poke-kun's states, the broken door, the megaphone and the staff roll are in "Traced inputs and scenes". Every scene is now pictured in the scene catalogue (see "Scene catalogue").

### Prototype built (2026-11-14)

A first prototype exists: `build/proto_redesign.ngc` (on the reviewed translation) and `build/proto_redesign_jp.ngc` (on the original ROM). `python tools/redesign.py <in> <out>` builds it, and every pacing number is a constant at the top of that file. The pity unlock was left out, as decided.

| Rule | What the prototype does | Checked in MAME |
| --- | --- | --- |
| Score from new content | Counter A gains 5 the first time a scene plays and nothing after. Each picker offers unseen scenes first. A scene is an event id, a visitor id, a wiggle gag or a megaphone reaction: 194 in all, 970 points. | Yes: +5 on new room events, visitors and megaphone reactions; a repeat visitor gave 0 |
| Guaranteed work | Leaving the menu with mood below 0 always sends him to work. It pays 3 to 8 counter B by mood bracket and uses up 8 to 30 mood (retuned after the play test). | Yes: mood −50 gave work, +4 B, mood −10 |
| Game calendar | 12 dates × 7 times of day, one step per menu exit, saved with the game. The console clock is ignored. | Yes: 10:00, 12:30, 16:30 on successive exits; the room changed to daytime |
| Even unlocks | Game n needs counter A 5 + 24(n−1) and counter B n, so game 30 needs 701 (141 scenes) and 30 (retuned after the play test). | Yes: A 53 and B 5 unlocked games 1 to 3 |
| Records | "Counter A needed" values × 0.6. Mood band edges: room events ±34/35 become ±8/9 and ±67/68 become ±16/17; visitors and megaphone ±67/68 become ±8/9 (see "Loosened conditions"). | Not separately |
| Staff roll | Needs counter A 100 instead of 500, and shows on 1 exit in 4 instead of 1 in 16. | Not separately |
| Save | The new data (seen flags, calendar step) sits in 20 bytes of the saved block that the game never uses, `0x4544`–`0x4557`. The save format and size are unchanged. | Yes: seen flags and calendar step came back after save and reset |

- **Differences from the proposal:** none on idle drift any more: it is 0, as proposed. The staff roll now only shows on exits where he is not happy, so it never replaces a work session. An empty doorbell ring no longer gives counter A.
- **Not tested:** a long play session, the staff roll rate, and whether any minigame writes to `0x4544`–`0x4557`. No code reference to those bytes was found, but minigames were not played.
- **Pacing is a first guess.** About 5 new scenes and one work session per minigame. At one calendar stop the pool of new scenes runs dry quickly, and nothing on screen tells the player to leave the menu to move time on.
- **Old saves:** a save from the unpatched game loads, but its spare bytes were never cleared, so start a new game.

### Play test (2026-11-14)

An automated player ran the prototype in MAME for up to 3.7 game-hours per run. It rings the bell, holds directions, wiggles the stick and leaves the menu every six actions. It never reads mood or the seen flags, so it plays like someone who does not know the rules.

| Version | Runs | Games unlocked | Scenes seen (of 194) |
| --- | --- | --- | --- |
| First tuning | 3 × 30 min | 2 to 3 | 91 to 94 |
| Work on any happy exit, staff roll moved | 2 × 3.7 h | 28 | 133 |
| Lower thresholds (current build) | 2 | 30, at 65 and 99 min | 118 and 125 at that point |

- **No crash and no hang** in any run of the patched game, once the MAME sound problem below was worked around.
- **Counter B was the first bottleneck.** With work only at mood −21 or happier, the player went to work on about 1 exit in 10. That is why work now triggers at any mood below 0.
- **New scenes dry up near 130.** The last two games needed 141 scenes and were never reached, so the thresholds were lowered.
- **About 60 scenes were never seen.** They fall into four groups:
  - scenes that need mood above +35 or below −35, which the player almost never reaches because work resets mood to about 0;
  - seasonal visitors, which need one specific room event just before the ring;
  - follow-up events that only start from another event;
  - the 20 bathroom visitors.
- **So the goal is half met.** All minigames unlock in one to two hours without waiting on the real calendar. Seeing all the content still needs knowledge the game does not give.
- **Spare save bytes held up.** Only the BIOS, the game's boot code and the patch wrote to `0x4544`–`0x4557`. One minigame ran for three hours in a separate run without touching them; the other 29 were not tried.
- **MAME sound problem (MAME 0.277), also on the unpatched ROM.** After a voice sample (the megaphone, some gags) the sound CPU stops answering, and the next visitor jingle freezes the game. The test worked around it inside the test script. It was not checked on another emulator or on hardware.
- **Test limits:** the runs with the current thresholds stopped making progress once all 30 games were unlocked, because of how the test script detects the menu. Scene counts after that point are not meaningful.

### Loosened conditions (2026-11-14)

After the play test the conditions on the unreached scenes were loosened, and the automated player was run again after each step. Both prototype builds now carry all of it.

| Step | Scenes seen in 3 game-hours (of 194) | All 30 games at |
| --- | --- | --- |
| Before loosening | 118 to 133 | 65 to 99 min |
| Narrower mood bands, follow-ups can start alone, no room-event prerequisite | 156 to 160 | about 70 min |
| Mood rebalanced (no idle drift, work spends less mood) | 163 to 168 | about 35 min |
| Bathroom visitors allowed any time, in the room too (current build) | 181 and 184 | 39 and 42 min |

- **Mood bands:** room events now switch at ±8/9 and ±16/17 instead of ±34/35 and ±67/68. Visitors and megaphone switch at ±8/9 instead of ±67/68.
- **Follow-up events:** the 26 room records that could only start from another event can now also start alone.
- **Visitor prerequisites:** no visitor needs one particular room event just before the ring. This is what opens the seasonal visitors.
- **Seasonal room events:** Christmas, New Year, Halloween and blossom play at any mood.
- **Bathroom visitors (70 to 89):** they now call at any hour and while Poke-kun is in the room. The game blocks them in code as well as in the records, which is why a first attempt changed nothing. The joke of calling on an empty room is lost; he stands and watches instead.
- **Game data fix:** two visitor records had their mood bounds the wrong way round and could never match. They are corrected.
- **Still unseen in both final runs:** room events 4, 19, 20, 30, 33, 41, 51, 53 and 58, and megaphone reaction 3. They need a strong mood together with a narrow time of day or season.
- **Speed:** all 30 minigames in about 40 minutes may be faster than wanted. `A_STEP` in `tools/redesign.py` sets it; the player reached 180 scenes only after about two hours.
- **Not tested:** a human player, and minigames other than the first.

## Open questions

- How often room events fire, and so how much real time counter A needs. Not measured.
- Answered: the +2 mood drift on failed menu exits is the room's default idle event. See "Event records decoded".
- What the branch at `0x21629d` does (1 in 16 on menu exit once counter A is 500 or more). Answered: the staff roll, three credits per showing; it changes no counters.
- Whether table `0x42000` is only the visitor table, and how pressing A selects from it. Answered: it is the visitor table, read by the doorbell path, which also sets the Love Love bits.
- What each of the eight day periods changes on screen, and whether Poke-kun's sleep state alters the menu path.
- The meaning of result values 1–7 in bits 0–2 of a flag byte.

## Address reference

CPU addresses are file offsets plus `0x200000`.

| Address | What it is |
| --- | --- |
| `0x4520` | Counter A, 16-bit |
| `0x4522` | Mood, signed byte, negative is happy |
| `0x4523` | Counter B, 16-bit |
| `0x4525` | Unused flag slot 0 |
| `0x4526`–`0x4543` | Flag bytes for games 1–30 |
| `0x452f` | Game 10's flag byte, read by the work roll |
| `0x4558`–`0x4563` | Profile unlock bits |
| `0x4520`–`0x456C` | Saved block, 77 bytes |
| `0x4802` | Result of the last minigame played |
| `0x4803` | Non-zero shows page E |
| `0x44b6` | Pending reaction: 1 work, 2 bad reaction |
| `0x451d` | Day period 0–7 |
| `0x216b46` | Unlock check, run on menu open |
| `0x216b60` | Page E check |
| `0x216bfa` | Stage-to-nibble table, 16 bytes |
| `0x216c0a` | Threshold table, 4 bytes per game |
| `0x213f54` | Writes result bits after a play |
| `0x21407b` | Menu exit path |
| `0x214ff0` | Work roll on menu exit |
| `0x215108` | Work award after a room event |
| `0x205a89` | Clamps the three values |
| `0x205c20` | Picks the day period |
| `0x240000`, `0x242000`, `0x246000` | Event tables, 32 bytes per record |
