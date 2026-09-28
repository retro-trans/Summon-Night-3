# Compact unit-status card VWF — 0.1.23

Built on 0.1.22. ISO SHA-256:
`bab9a85c9526a4c7c6e60b17516e342bec72c79daf03bda443002018e95493df`.

The compact battle-map unit card now renders the unit name, attack label, and
defense label with proportional Latin spacing. HSlash no longer crowds the
defense icon. Text is bound using its actual length instead of the previous
fixed eight-cell argument, allowing the existing bounded VWF renderer to pack
up to 16 cells. The renderer keeps its existing native fallback for longer text.

This release changes rendering only. Existing wording, level/HP/MP numbers,
icons, bars, panel dimensions, and the native 0.875 text scale are unchanged.
Longer or expanded translations can use the extra space in future edits; they
must still pass pixel-width checks for their field.

## Implementation and checks

- Three binding calls at module addresses `0xe10a8`, `0xe1268`, and `0xe1448`
  now use the released VWF wrapper at `0x347b5c`. Their arguments adapt the
  native `(object, text, count, style)` call to `(object, text, style)`.
- Exactly 12 executable bytes change, in six instructions. All other executable
  bytes, existing font code, translations, prior fixes, and all 23 data banks are
  byte-identical to 0.1.22. Existing JAL relocations are retained.
- Font metrics were checked for all 328 existing translated unit/class labels.
  Their longest entry is 10 characters. The widest measures 95.375 pixels at
  the native scale, within the approximately 115-pixel name region.
- Fresh launch in isolated PPSSPP 1.20.4 software rendering at 1x, loading a
  copied in-game battle save without a save state. Viewed Aty's name/HSlash/Guard,
  a soldier's name/VSlash/Guard, and Aty again after changing selection. Text
  updates correctly, fits beside the icons, and HP/MP numbers and bars align.
- Read the live instructions through PPSSPP's original-opcode disassembler and
  verified all three wrapper calls plus their style arguments.
- Verified historical input hashes and every ISO file. All resource banks are
  unchanged. Evidence is in `work/ui/card_0.1.23/runtime`.

The change is scoped to the compact battle-map card. Hardware GPU rendering and
original PSP hardware were not tested. Existing abbreviations are preserved;
this release does not claim that every label has been expanded to a full name.
