# Start Battle confirmation VWF — 0.1.32

Base: immutable 0.1.31. The Start Battle confirmation now uses centered
proportional spacing for "Start battle?", "Yes" and "No". Wording, selection
order and native confirmation behavior remain unchanged.

The glyph-position callback checks the three exact relocated row addresses:
0x32e9c0, 0x32e9dc and 0x32e9e4. Measured Latin glyph advances replace fixed
cell positions. Other messages retain their existing handler chain, including
the tutorial and locked-feature popup fixes.

146 emitted-MIPS cases at two load bases verify every glyph position, both
previous popup handlers, unrelated-source fallback, out-of-range indices,
native callbacks, preserved registers and unchanged Y/Z coordinates.

The builder verifies ISO files, 23 archive bank indexes and 5,729 unchanged
resources. Runtime evidence is in work/ui/ui_fixes_0.1.32/runtime.

Runtime verification passed in PPSSPP 1.20.4 using software rendering after a
fresh launch with an in-game save. The prompt and both choices are centered
with proportional spacing. Both cursor positions remain clear. Confirming No
closes the dialog and returns to Battle Prep. Yes was highlighted but not
activated; this test covers layout and cancellation in the first battle.

Tested ISO SHA-256:
`65f17fcc38fc7facab05d2282b381c134a2aa628b249ff399f49a1d8ce06ba9d`.
