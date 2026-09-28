# Tutorial notice and Pact Ritual UI — 0.1.27

The immutable base is 0.1.26. This update gives “Tutorials: see Gallery.”
proportional spacing and translates the pictured Pact Ritual skill and help.

The notice uses individual native glyph objects. A scoped hook at module
0x1b670 adjusts their horizontal positions from the existing Latin metrics,
centering the 154-pixel ink span in the original message box. It only applies
when the source pointer matches this notice. Other messages retain their native
behavior; glyph pixels, vertical positions and the window are unchanged.

The skill becomes “Pact Ritual: Machine.” The matching Oni, Spirit, Beast and
All variants are also translated in static table 28, records 4–8. Their shared
description and dynamically assembled help use English crafting and affinity
labels. The original selection of permitted affinities and bracket controls
remain intact. All translated strings are relocated; the resident static-table
mirror is updated along with 02.DAT.

An independent meaning review accepted Pact Ritual and the summon-crafting
description. The position hook passed 50 cases at two load addresses, covering
every notice glyph, unrelated sources, invalid indexes, Y/Z coordinates and
preserved registers. Archive verification checks all bank indexes, unchanged
resources, executable structure and resident mirrors.

The executable's 15 battle-name variants are translated, including compact
combined-affinity suffixes (M=Machine, O=Oni, S=Spirit, B=Beast). The help spells
out the affinities. Three return-delay name references required control-flow
proof: their matching high instructions are in branch delay slots, beyond the
generic linear scanner's reach. Their existing relocation pairs are preserved.

The help dispatch at 0x642c0 now sends mode-6 ordinary English text through the
existing VWF renderer. A mode-6 row beginning with a native Greek stat marker
retains the native grid, preserving AT+17 spacing. The marker is read from the
inline text cells at context+0x4c. Fourteen emitted-code tests at two load bases
cover Latin, stat markers, boundary cells and other modes.

Runtime verification passed in an isolated PPSSPP 1.20.4 software-rendered
session, using a fresh launch and an in-game save (no save state):

- Gallery tutorial notice: centered proportional text.
- Pact Ritual: Machine: English name fits before MP cost 5.
- Generated Machine/Neutral help: both lines visible with proportional spacing.
- Inventory AT+17: native symbolic spacing retained.
- Closing the skill menu returns to normal map control.

Screenshots and framebuffer metadata are in
`work/ui/ui_fixes_0.1.27/runtime/final_*.png` and matching JSON files.
The tested ISO SHA-256 is
`fa0324aca46fd9029405f5c7c9e27e3cb8cfca887fe319789acb36615d49e4bb`.
The build verified 5,728 unchanged bank resources and all 23 bank indexes.
Other affinity variants were statically checked, not exercised in-game.

