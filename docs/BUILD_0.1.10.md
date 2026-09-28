# Build 0.1.10 — harbor translation gaps

[ISO](../work/output/0.1.10/Summon_Night_3_EN_0.1.10.iso) · [Introduction](../work/ui/harbor_gaps_0.1.10/runtime/introduction.png) · [Salome nameplate](../work/ui/harbor_gaps_0.1.10/runtime/salome.png)

Translated the missing centered harbor choices for both protagonists and both
pupil genders (12 source rows), plus the three-part player introduction.
The introduction now displays “Ah, yes. / My name is [player name].” on two lines.
The original player-name token, display helper, arguments and continuation are
preserved. The old source strings remain intact; English strings are relocated.

The choice shown in the report is “Surely...” followed by “Probably a refined
young lady.” and “Let's not overthink it.” The longest choice measures 251 pixels
including indentation, within the approximately 280-pixel native centered menu.
This wider menu has a separate limit from the narrower portrait speech window.

Replaced the native graphical names for Belfrau, Salome, Nup, Alieze and Will.
Built-in imagegen supplied matching cream/plum transparent lettering from original
sprite references. Generated words were cropped, uniformly downsampled and mapped
to the game's existing palettes; no rectangle was painted over the nameplate.
Both the lettering and its silhouette layer are replaced in all 10 matching packs
(20 sprite layers). Portraits, other pack children and the ornamental frame remain
unchanged. [Exact prompts and assets](../work/ui/nameplates_0.1.10/generation.json).

## Checks

- Independent meaning review covered 100 surrounding rows for the 15 gaps.
- Verified source hashes, 624 logical targets, all existing reflowed strings,
  preserved runtime token, two-line execution and unchanged helper arguments.
- Compressed script and portrait packs round-trip. The main script is 235,336 bytes,
  below its mapped 491,520-byte region. Maximum six-glyph name expansion is bounded
  at 197 pixels in a 208-pixel speech line; default Rexx was tested live.
- All 34 unrelated ISO files, including executable/audio, are byte-identical to
  0.1.9. Checked all 23 bank indexes and 4,404 untouched resources in changed banks.
- Fresh-boot PPSSPP reached the harbor naturally. Checked the boy-route choices,
  the player's substituted name, Salome's nameplate and normal continuation.
  Complete live script bytes match the build. All five native name sprites were
  visually inspected after palette conversion.

The girl-route 251-pixel choice and alternate character packs have static checks;
those routes were not replayed here. Audio playback and the full game were not
retested. This is still a partial translation: 624 of 641 source rows in this
opening/harbor scope are included; 17 remain Japanese, as does most later text.

Restart PPSSPP's game with the new ISO. Old emulator save states can restore the
old script and textures; ordinary in-game saves are preferable after a fresh boot.

SHA-256: `774c16772b035d3023665b005c6ca1b45b567aa8094ffbfe27e510581e1928ad`.
Next unused version: **0.1.11**.
