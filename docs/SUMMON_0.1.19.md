# Summon names and affinity icons — 0.1.19

Built on 0.1.18; all earlier translation and crash fixes are inherited.

ISO SHA-256: `b55790720f4813525c73dcd291aaa46395df4935cdb978a071c8e9b8845dd1eb`

ISO size: 1,659,924,480 bytes.

## Names

All 87 populated base summon-name records in shared table 12, slot 9, now
resolve to printable English. This adds 68 names and preserves 19 existing
translations. The table also contains entities beyond the 73 entries displayed
by the player's current Summon Index; 87 is the table count, not an unlock count.
All base pointers were read back, including Dritol and Shine Saber.

Source hashes, record indices and pointer fields are validated together. A
misaligned draft mapping at records 72–87 was rejected and corrected before
insertion. The user-selected character glossary supplies R, Onibi, Quiupy,
Teco and Falzen. Other proper-name readings may be provisional.

Unreviewed form aliases and long descriptions remain outside this batch.

## Affinity graphics

The five 16-by-16 native tiles use M for Machine, O for Oni, S for Spirit,
B for Beast and N for Neutral. Existing color associations and tile borders
are preserved. All 20 exact matching occurrences across packs 2952–2955 are
replaced. The top-right L/R control now reads Type, which fits its allotted area.

Generated with the built-in ImageGen tool. Project assets:

- `work/ui/summon_0.1.19/affinity_generated.png`: generated sprite strip.
- `work/ui/summon_0.1.19/native_icons_preview.png`: native palette conversion,
  enlarged only for inspection.
- `work/ui/summon_0.1.19/imagegen.prompt.json`: exact generation prompt,
  reference image, crop and native conversion settings.
- `work/ui/summon_0.1.19/affinity.locations.json`: exact resource occurrences.

Only crop, scale, original alpha and native palette conversion were applied
after ImageGen. Other texture pixels, palette data and resource footprints
are unchanged. Native converted icons were visually inspected.

## Checks and limits

The build verifies all historical inputs, all 23 bank indexes, unchanged ISO
files, 5,724 untouched resources in the rebuilt banks, and resident/bank table
mirrors. The five 0.1.17 crash-fix spans are unchanged and their native glyph
capacity checks pass. An independent code review found no insertion blocker.

The user corrected the screenshot's version to 0.1.17. Current 0.1.18 and this
release have English Dritol at the shared name pointer. No third raw text copy
was found; the exact runtime reason for the older screenshot is not established.
Save files were not modified. This release has not yet been verified in a live
game session; native asset inspection and static checks do not replace that test.
