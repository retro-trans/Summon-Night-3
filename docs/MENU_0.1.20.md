# Menu translations and proportional text — 0.1.20

Built on 0.1.19. ISO SHA-256: `b4fa21ea06e344964d42e5c1d565f951bb3fa1af9c1ac859423c4c668dd4558e`.

## Changes

- Inventory labels: Key Item, None, No equippable items, No equippable goods;
  seven relocation-backed source groups, including repeated empty-list messages.
- Native Summon Index graphics: Spells, Combine, Range, Reach, Area, Up and Down.
  Six sprites in each of four matching packs; all other sprites and palettes unchanged.
- Proportional Latin ink packing in native list font objects, with centered packing
  for the empty-list message. Proportional menu strips, Type control, and per-glyph
  Battle Prep/help text. Existing Japanese/control characters retain native fallback.
- Summon default names already translated in the data tables now also resolve in
  loaded saves. Exact matching display-time substitution covers 121 unique names
  and forms (125 source records). Unmatched custom names and the save files are
  unchanged. This is not a claim that all 260 form-name records are translated.

## Why Dritol stayed Japanese

Live 0.1.19 had English Dritol in the relocated table at 0x08d2fda0, but the index
read a runtime cached name at 0x08a3da84. The detail accessor at module+0x57530
returns `pool + index*32 + 0xc34`, not the table's 52-byte record. The index binder
at module+0x1b390 and detail binder at module+0x14ecf8 consumed the cached Japanese
name. The new display wrapper substitutes only an exact known default name.
Neither save files nor that runtime cache are rewritten.

## Verification

The final ISO was freshly launched in a separate PPSSPP 1.20.4 test instance,
then loaded the user's copied Chapter 1 battle save through the normal Load menu.
No save state was loaded. Verified Battle Prep entry, inventory weapon/accessory
lists, Key Item, centered None, Dritol in both Summon Index views, spell-name/MP
separation, descriptions, and native translated controls. Screenshots and the
runtime report are in `work/ui/menu_0.1.20/runtime`.

Verified 41,200 newly loaded code/data bytes and all eight hooks; PPSSPP's 86 JIT
replacement instructions were checked through its original-opcode disassembler.
All five 0.1.17 crash-fix help blocks are identical both statically and in live RAM.
All historical build input hashes, 23 bank indexes, and 5,725 untouched resources
pass the build checks.

876 instruction-level cases cover two load bases: menu/help positions, native
32-cell packing, centered packing, mixed Japanese fallback, cache invalidation,
stack/register guards, and exact/default/custom name lookup. The actual emitted
MIPS executes in the tests; native font allocation/population boundaries are modeled.

Visual testing used PPSSPP's software renderer at 1x. Hardware rendering and
original PSP hardware were not tested. Some other UI paths, including battle-map
shortcut/status text, still use the game's original spacing.

The new prepare helpers are pipeline components guarded by source data, expected
hook instructions, and the build manifest. They are not generic patches for other
executable versions.
