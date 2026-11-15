# English patches, v1 beta

Apply one patch to an unmodified dump of the game: 2 MB, CRC32 `6DF986A3`.
Any IPS tool works (Flips, Lunar IPS, or an online patcher).

| Patch | What you get | Patched CRC32 | Patched MD5 |
| --- | --- | --- | --- |
| `neopoke_en_v1beta.ips` | The English translation | `894C776B` | `8f5ccbcd58ebe5d70c104fce56e1385f` |
| `neopoke_en_fastunlock_v1beta.ips` | The translation plus the bonus patch: new events appear much faster, so minigames unlock sooner (see `docs/events-unlocks-fastunlock.md`) | `5192A902` | `f8517d652f4a6f0818b22632424ec63c` |
| `neopoke_en_v1beta_allgames.ips` | The translation with all minigames already unlocked (see below) | `2471A33A` | `7a4325adb18cdf25757ddb4b4fd28e25` |
| `neopoke_en_fastunlock_v1beta_allgames.ips` | The translation plus the bonus patch, all minigames already unlocked | `FCAF7D53` | `ccb2423f2ebddf25c5e31014c7a856b7` |

## All-minigames saves

A save with all 30 minigames unlocked and cleared. There are two ways to get it:

- **Flashcarts and other emulators:** use an `_allgames` patch. The save is built into the patched ROM's own save area,
  so the game loads it at boot with no extra file (the title screen is skipped because a save exists). Once you save,
  the game keeps your own saves after it. An emulator or flashcart that keeps a separate save file uses that file instead:
  delete it first.
- **Mednafen:** use a normal patch plus its flash save (`.flash`) below.

Every game is marked as cleared, so the menu's hidden page E is there: Right past page 6, Up, A opens the
Love Love Profile catalog, with all profiles unlocked (A shows profile 1, Down/Up browse).

| Save | For |
| --- | --- |
| `neopoke_en_v1beta_allgames.flash` | `neopoke_en_v1beta.ips` |
| `neopoke_en_fastunlock_v1beta_allgames.flash` | `neopoke_en_fastunlock_v1beta.ips` |

Mednafen finds a save by the ROM's file name and MD5. Rename the save to `<ROM file name>.<patched MD5>.flash` and put it in
Mednafen's `sav` folder. For a patched ROM called `neopoke_en.ngc`:

```
neopoke_en.8f5ccbcd58ebe5d70c104fce56e1385f.flash
```

Delete or move any save Mednafen already made for that ROM first. Other emulators that use the NeoPop flash format may
read these files too; only Mednafen was tested. The all-games save, page E included, was confirmed on real hardware
and in MAME.
