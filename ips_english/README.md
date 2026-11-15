# English patches, v1 beta

Apply one patch to an unmodified dump of the game: 2 MB, CRC32 `6DF986A3`.
Any IPS tool works (Flips, Lunar IPS, or an online patcher).

| Patch | What you get | Patched CRC32 | Patched MD5 |
| --- | --- | --- | --- |
| `neopoke_en_v1beta.ips` | The English translation | `BE0E1AB6` | `e33ca19773adf510bc73e0b947c42319` |
| `neopoke_en_fastunlock_v1beta.ips` | The translation plus the bonus patch: new events appear much faster, so minigames unlock sooner (see `docs/events-unlocks-fastunlock.md`) | `66D0C4DF` | `23b74408b4497cc3b22fefe51e0664b4` |
| `neopoke_en_v1beta_allgames.ips` | The translation with all minigames already unlocked (see below) | `1333CEE7` | `0b7ff4816a49dc0ed7819aa111d715e8` |
| `neopoke_en_fastunlock_v1beta_allgames.ips` | The translation plus the bonus patch, all minigames already unlocked | `CBED108E` | `c0fe688542f0f89180d4a904fa5daa1d` |

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
neopoke_en.e33ca19773adf510bc73e0b947c42319.flash
```

Delete or move any save Mednafen already made for that ROM first. Other emulators that use the NeoPop flash format may
read these files too; only Mednafen was tested. The page E update to the saves was checked in MAME (same save data put
into the cartridge's save area), not yet in Mednafen.
