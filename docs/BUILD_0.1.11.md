# Build 0.1.11 — complete opening/harbor dialogue coverage

[ISO](../work/output/0.1.11/Summon_Night_3_EN_0.1.11.iso)

Adds the 17 source fragments omitted from 0.1.10. All 641 fragments in the
opening/harbor selection are now included, covering both protagonists and all
four pupil branches. This is a bounded section, not a full-game translation.
The next source row begins the cabin scene.

The user's first screenshot now reads “But this time, we cannot allow that to
happen!” The second continues the preceding sentence about admission to the
military academy: “is absolutely essential for the young lady's future!”
The young-master counterpart is included too.

## Why there were gaps

The extraction order follows compiled script references, which interleave
alternate branches and contain revisits. It is not one linear playthrough.
However, these specific omissions were build exclusions: the emphatic display
helper and music-note handling had not been accepted by the layout process.
The three quiz fragments also needed a meaning review. These exclusions should
have been resolved before describing the opening scene as covered.

The new selection has no excluded rows in this scope. Eight complete groups
are reflowed into nine pages. Original display helpers, style arguments, branch
code, continuations and the music note are retained. Strings are relocated;
the source text pool and the previous 624 translations remain intact.

## Backlog names

The history's text names are separate from the graphical portrait nameplates.
The table is child 22 in compressed resources 02:00085, 02:00086 and 02:00087.
It has 255 eight-byte records with two-byte CP932 strings. The seven existing
glossary names — Rexx, Aty, Nup, Belfrau, Alieze, Will and Salome — replace
21 exact labels in each copy. New names are appended and pointers relocated;
other names and all 22 sibling children are preserved.

## Validation and limits

- Independent meaning review examined 165 surrounding rows for the 17 additions.
  The quiz retains the literal “not listed as exceptions”; the alternative
  causal reading remains uncorroborated. No answer or explanation was invented.
- Exhaustive selection coverage, source identities, retained prior translations,
  simulated helper calls, line/page bounds and compression round trips pass.
- The decoded script is 236,820 bytes, below the 491,520-byte mapped region.
- All 34 unrelated ISO files, including audio and the executable, are identical
  to 0.1.10. All 23 bank indexes and 4,411 untouched bank resources pass checks.
- Fresh-boot final-ISO PPSSPP testing followed Rexx/Belfrau through the opening
  and harbor, observing 243 distinct physical text IDs. The full decoded script
  matches memory. Both reported emphatic groups are fully visible without
  clipping; the three-line continuation and Salome labels also display correctly
  in the backlog. Closing history returns to normal dialogue and continuation.
- All 107 nonzero name-table pointers and the entire 6,144-byte table match the
  build after normalizing the game's pointer rebasing. This includes all 21
  translated references in the loaded copy. The other two copies are identical.
- The exclamation/quiz/music-note and young-master branches have static checks;
  they were not replayed. Later scenes and audio playback were not retested.

[Runtime evidence](../work/output/0.1.11/harbor_runtime_validation.json) ·
[First reported line](../work/ui/harbor_complete_0.1.11/runtime/salome_emphasis_full.png) ·
[Second reported line](../work/ui/harbor_complete_0.1.11/runtime/salome_future.png) ·
[Backlog](../work/ui/harbor_complete_0.1.11/runtime/backlog_salome.png).
The saved workspace audit passes all 206 integrity checks.

Restart the game using this ISO. Emulator save states can restore old scripts
and name tables; use a fresh boot and normal in-game saves.

SHA-256: `5d3a7fa45ee682cb2d3dac9fa6eb2aac129852a99d8bcafbae6f0bb590279723`.
Next unused version: **0.1.12**.
