# Battle menu and saving notice — 0.1.34

Base: immutable 0.1.33. Translated the battle menu labels End Turn, Battle Info,
Unit List, Summon Index, Inventory, Options, Suspend and Retreat. Its Battle
Info submenu now uses Party Abilities, Support Skills, Brave Goals and Win/Lose,
matching the preparation menu terminology.

The labels are generated English glyph artwork converted to the original
64x16 paletted sprites in 01.DAT resource 105 children 10 through 21. Existing
frames, selection states and all other children are unchanged.

The two-line system-saving record now reads "Saving system data." / "Do not
remove the Memory Stick." The relocated bundle preserves its line boundaries
and terminating empty line. The exact two row addresses use measured proportional positions relative to the native
row anchors; unrelated notices retain their existing handler chain.
The meaning reviewer approved all labels and both message lines.

208 emitted-MIPS cases at two load bases verify the new row positions, prior
popup handlers, unrelated-source and out-of-range fallback, callbacks and
preserved registers. The builder verifies all 23 archive indexes and unchanged
archive resources. Runtime evidence is in work/ui/ui_fixes_0.1.34/runtime.

## Runtime verification

Verified the candidate in PPSSPP 1.20.4 with software rendering after a fresh
launch and loading an in-game save, using isolated copied save data. All eight
battle-menu labels and all four Battle Info entries display in English within
their buttons. Opened and closed Battle Info, then performed a Suspend save.
Both English system-saving lines display with proportional spacing inside the
message frame. The save completed and the game returned to the title screen.

Evidence: final_menu.png, final_info.png, final_saving.png and final_return.png
under work/ui/ui_fixes_0.1.34/runtime, with corresponding framebuffer reports.
Coverage is the first battle and this saving flow; other battle stages and
hardware renderers were not exercised for this change.

ISO SHA-256: 0b6b12df8c77773e85b0ad01511c94d84090998e387b716749e6c19be26b2859
