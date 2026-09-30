# Armor names and stat spacing: 0.1.51

The reported Amenokoyane armor help starts with CP932 cell `84aa`, which the
native font draws as the defense stat label. The v0.1.27 dispatcher recognized
only the Greek-code stat cells (`839f` through `83b6`). It sent this defense row
to ordinary proportional text placement, crowding its symbolic labels and values.
The equipment audit also found stat rows beginning with `84ac`.

This build adds a narrow dispatch wrapper: in renderer mode 6, rows starting
with either of those two cells use the native position callback. Every other
row follows the inherited dispatcher. It preserves callback arguments, native
floating-point positions, callee-saved registers, the previous two-row equipment
formatter, and the v0.1.49 memory guards. Description bytes and gameplay values
are unchanged.

All 92 remaining Japanese armor names are translated in table 16 and its cached
copy. The reported entries include Benimizuha, Yagurumatsubaki, Amenokoyane,
Metal Coat, Fluffy Vest, Goat Vest, Flower Vest and Mintelia. Coined and Japanese
proper names are transliterated; these are not claimed as official spellings.
Previously translated English labels are retained. The source-bound target file
is `work/translation/en/armor_0.1.51/targets.json`; historical hashed inputs are
unchanged.

Validation covers all 155 populated armor-name references, the new names' cell
and pixel bounds, exact preservation of 1,434 equipment formatter variants,
and all 65,536 prefix cells at two relocated load addresses. Non-stat renderer
modes retain their previous routing. The cumulative build audit also retains
weapon-name, two-row help, native buffer, spell, skill, Cooking, unit-label and
shared memory-guard checks.

Build and package:

```powershell
python tools/build_armor_051.py --write --destination work/output/0.1.51
python tools/package_armor_051.py
```

Runtime evidence and limitations are recorded separately in
`work/ui/armor_0.1.51/runtime-validation.json`. Start the patched game fresh and
load a normal save; an older emulator state can restore old code in memory.

Final candidate verification (2026-09-30):

- ISO SHA-256: `9bc40ad1556187abad2b4235880e316780b11841903595547a409376c91a12db`.
- All eleven cumulative audit groups passed. New armor names have at most
  15 cells and a maximum measured width of 123.375 pixels.
- Fresh-boot PPSSPP 1.20.4, JIT/software rendering with strict memory handling:
  normal Continue, armor tab, the exact Amenokoyane selection and the previous
  Black Rose Knife two-row description passed. The reported eight armor names
  were visible together in English. The log contained no bad-memory-access
  fault. Live guard counters were not collected before closing the emulator.
- Runtime testing used battle Inventory. The room context, other platforms and
  a full playthrough are not covered by this test.
- Original-to-0.1.51, 0.1.42-to-0.1.51 and 0.1.50-to-0.1.51 patches were decoded
  with the retro-trans-tools engine and matched the final ISO byte for byte.
