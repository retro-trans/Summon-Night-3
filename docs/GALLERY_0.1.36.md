# Gallery tutorial list — 0.1.36

Based on immutable 0.1.35. This update addresses the supplied Illustrations
list screenshot and its paired Sound-mode controls.

## Changes

- Translated all 22 repeated tutorial titles as **Review Basics**, a compact
  rendering of Review the Basics. The source identities and record offsets
  are retained without copying the original text pool.
- Shortened **Attack Range and Weapons** to **Weapons & Range** so it stays
  inside the Comment column. The existing proportional renderer is retained.
- Translated the Illustrations and Sound headings and the View, Sound Mode,
  Exit, Play and Artwork mode controls in native graphics.
- Preserved the executable and unrelated table bytes, artwork sprites and
  frame pixels. Both copies of the resident text bank are updated together.

## Verification

The builder checks all 23 bank indexes, 5,727 unchanged bank resources and
unchanged files outside the selected banks. Appended strings retain native
terminators and pointer alignment; every changed pointer is checked. The
translated title measures 107.625 pixels against a 116-pixel budget, and the
shortened comment measures 133 pixels against a 148-pixel budget.

Runtime checks use a fresh PPSSPP 1.20.4 software-rendered launch, copied
in-game system data and no emulator save state. Evidence is in
`work/ui/gallery_0.1.36/runtime`. The final build is checked for list display,
scrolling and switching between Illustrations and Sound modes. Opening and
returning from a tutorial was also checked on the first candidate.

This is a list-screen update. Gallery tutorial-page artwork, music titles,
and the parent Gallery menu remain outside this patch's translation scope.
Locked entries keep their question marks. Earlier story/battle coverage and
playtesting limitations still apply; this is not a complete translation.

## Sources and artwork

`tools/gallery_036.py` patches the item-title records and help-comment table,
then converts generated artwork to native palettes. `tools/build_gallery_036.py`
creates the ISO; `tools/gallery_runtime_036.py` uses only the isolated test
emulator. English targets are in `work/translation/en/gallery_0.1.36`.

The built-in image-generation tool created the English graphics. The retained
assets and prompt summaries are in
[work/ui/gallery_0.1.36/artwork.json](../work/ui/gallery_0.1.36/artwork.json).
Meaning and layout received author review; no independent review is claimed.
