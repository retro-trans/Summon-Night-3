# Battle-map shortcut spacing — 0.1.22

Built on 0.1.21. ISO SHA-256:
`d399499f571f002fb7d3cf1d34469b479cee5ed8838f7f4d3bab79229df1893e`.

The blue shortcut panel now uses the existing proportional Latin renderer.
Prepare, Unit List, Battle Status, Start, Position, Status, and Face fit inside
the panel. The labels, button icons, panel geometry, and native text scale are
unchanged.

The shortcut object binds text at module address `0xb1d94`. Its original call to
`0x1cbdec` now calls the existing bounded VWF wrapper at `0x347b5c`. The original
delay-slot style argument and existing JAL relocation are unchanged. The wrapper
packs up to 16 cells; longer text retains the native fallback. The longest shown
label, Battle Status, has 13 cells and a predicted proportional advance of
82.5 pixels at the native 0.75 scale, within the panel's available width.

Exactly three executable bytes change, in one instruction. All other executable
bytes, resource banks, translations, font code, and prior crash fixes are
identical to 0.1.21. The reused font code is also byte-identical to the validated
0.1.20 renderer. No new font assembly or translation data is introduced.

## Verification

- Verified all historical build-input hashes and every ISO file; all 23 data
  banks are byte-identical to 0.1.21.
- Fresh launch in isolated PPSSPP 1.20.4, software renderer at 1x, using a copied
  in-game battle save. No save state used.
- Viewed both the unit-selected menu and the empty-tile menu. Battle Status and
  Unit List stay inside the blue panel; other labels and controller icons align.
- Entered Battle Prep with the Circle shortcut and returned to the map without
  a crash or spacing regression.
- Read the loaded instruction through PPSSPP's original-opcode disassembler:
  it calls `0x08b4bb5c`; its native style argument remains `a2 = 1`.
- Screenshots and the validation record are in `work/ui/map_0.1.22/runtime`.

This change concerns battle-map shortcut labels. The separate unit-status card
at the bottom left still uses its existing spacing. Hardware GPU rendering and
original PSP hardware were not tested.
