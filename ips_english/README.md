# English patches, beta 1

Apply one patch to an unmodified dump of the game: 2 MB, CRC32 `6DF986A3`.
Any IPS tool works (Flips, Lunar IPS, or an online patcher).

| Patch | What you get | Patched CRC32 | Patched MD5 |
| --- | --- | --- | --- |
| `neopoke_en_beta1.ips` | The English translation | `89FC3D29` | `579d32aa49fdf2c1ca80f7e51c32c916` |
| `neopoke_en_redesign_beta1.ips` | The translation plus the bonus patch: new events appear much faster, so minigames unlock sooner (see `docs/events-unlocks-redesign.md`) | `8CFF288E` | `f7da8b4ade4c36086dafb954238f9c54` |

## All-minigames saves

A save with all 30 minigames unlocked, for each patch. They are Mednafen flash saves (`.flash`).

| Save | For |
| --- | --- |
| `neopoke_en_beta1_allgames.flash` | `neopoke_en_beta1.ips` |
| `neopoke_en_redesign_beta1_allgames.flash` | `neopoke_en_redesign_beta1.ips` |

Mednafen finds a save by the ROM's file name and MD5. Rename the save to `<ROM file name>.<patched MD5>.flash` and put it in
Mednafen's `sav` folder. For a patched ROM called `neopoke_en.ngc`:

```
neopoke_en.579d32aa49fdf2c1ca80f7e51c32c916.flash
```

Delete or move any save Mednafen already made for that ROM first. Other emulators that use the NeoPop flash format may
read these files too; only Mednafen was tested.
