# English patches, beta 1

Apply one patch to an unmodified dump of the game: 2 MB, CRC32 `6DF986A3`.
Any IPS tool works (Flips, Lunar IPS, or an online patcher).

| Patch | What you get | Patched CRC32 | Patched MD5 |
| --- | --- | --- | --- |
| `neopoke_en_beta1.ips` | The English translation | `5889381A` | `1c31cec72d53f78386ebaf65ddfba357` |
| `neopoke_en_fastunlock_beta1.ips` | The translation plus the bonus patch: new events appear much faster, so minigames unlock sooner (see `docs/events-unlocks-fastunlock.md`) | `8057E673` | `446cdbdc189a33bfd4639b95fa11dd0a` |

## All-minigames saves

A save with all 30 minigames unlocked and cleared, for each patch. They are Mednafen flash saves (`.flash`).
Every game is marked as cleared, so the menu's hidden page E is there: Right past page 6, Up, A opens the
Love Love Profile catalog, with all profiles unlocked (A shows profile 1, Down/Up browse).

| Save | For |
| --- | --- |
| `neopoke_en_beta1_allgames.flash` | `neopoke_en_beta1.ips` |
| `neopoke_en_fastunlock_beta1_allgames.flash` | `neopoke_en_fastunlock_beta1.ips` |

Mednafen finds a save by the ROM's file name and MD5. Rename the save to `<ROM file name>.<patched MD5>.flash` and put it in
Mednafen's `sav` folder. For a patched ROM called `neopoke_en.ngc`:

```
neopoke_en.1c31cec72d53f78386ebaf65ddfba357.flash
```

Delete or move any save Mednafen already made for that ROM first. Other emulators that use the NeoPop flash format may
read these files too; only Mednafen was tested. The page E update to the saves was checked in MAME (same save data put
into the cartridge's save area), not yet in Mednafen.
