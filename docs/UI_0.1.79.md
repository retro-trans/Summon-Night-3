# Related UI categories — 0.1.79 local test

This build addresses the six screenshots reported from 0.1.77 after a fresh
boot and loading an in-game save. It includes the 0.1.78 Options selection-mask
correction.

- Restore Scarrel's Chapter 7 Night Talks caption as **An Organization's Bounds**
  for Rexx and Aty. The earlier translation existed but exceeded the renderer's
  256-pixel strip by one pixel. Compact the other caption above that limit,
  **Thunder Gen., Wind Princess**, in both caption banks.
- Scale the Night Talks title column proportionally in both dimensions, with
  the original dimensions restored after drawing. Use **OK** in its footer
  to separate the confirmation icon and text from Back.
- Translate 276 remaining attack-skill name, help and mastery fields. Preserve
  combat parameters, records, original text pools and player-entered names.
- Translate all remaining fortune evaluations and special Fariel labels,
  equipment-type labels and weapon-range help (44 native string groups).
- Translate 82 location entry title variants, including **Guardian Shrine**,
  and 30 additional Starting Beach copies. Translate 270 remaining story,
  selection and alternate speaker-name graphics, including **Misumi**.
  Exact duplicates extend the change to 526 texture leaves. Native geometry,
  palettes, flags and archive codecs are preserved; mystery-name question marks
  remain intentional.

Apply `SN3-English-v0.1.77-to-v0.1.79.xdelta` to the **published 0.1.77 ISO**
with Retro Trans Tools. The local 0.1.78 test does not count as a published
release. This ZIP contains the compatible manifest and checksums. Boot afresh
and use a normal in-game save.

- Source SHA-256: `d35b5882e5547d578776d3337909c0b2c939f7aeedb05e76f21ab2cbb4587427`
- Target SHA-256: `60231fef2cf0df4256aa47228a49d0bc2662aa85751051e624c3be49b4d12438`

Validation executes 135 translated skill help combinations through the actual
emitted help staging code, 856 gallery-strip cases, six proportional-scale cases
and two protected-tail cases at two load bases. It verifies the built ISO,
active pointers, caption termination, asset geometry and palettes, master-table
caches, all 23 bank indexes and 5,327 unchanged bank resources.

Runtime evidence uses one isolated Windows PPSSPP 1.20.4 instance, JIT and
software graphics, fresh boot and a normal Chapter 16 save. No save states or
game-memory edits are used. The reviewed frames cover Scarrel's Chapter 7 rows
for both protagonists, the Options L/R selector, the Fariel fortune label,
Misumi's fortune portrait/evaluation, and Yafha's translated attack-skill list.
Exact Guardian Shrine and Misumi story scenes are verified as native assets;
those exact scenes have not been replayed in this test. This is not an Android
device test or a full gameplay regression test. Audio is enabled; playback is
not validated.

English typography atlases were generated with the built-in imagegen tool,
with transparency enabled, then imported into the existing sprite records.
All atlas lettering was visually reviewed. Location atlases use the native
pale-blue title palette, distinct from the brown map-label palette. Speaker
variants reuse existing reviewed name atlases and a new 13-name atlas. Sources,
prompts, reviewed crop boundaries and asset metadata are recorded under
`work/ui/ui_0.1.79/`; private source-script extracts, saves and discovery images
are not included in Git or the package.

This is a local test package, not a published release.
