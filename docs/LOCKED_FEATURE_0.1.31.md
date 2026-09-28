# Locked-feature popup — 0.1.31

Base: immutable 0.1.30. The notice shown when Party Abilities is unavailable
now reads "Not available yet." The full translation is "This feature is not
available yet." Both wordings were approved by the meaning reviewer; the
compact UI variant keeps the native popup frame within the screen.

The source literal at module 0x21e4ec is relocated into the added load segment.
Its relocation-backed reference pair at 0x165020 / 0x16502c is updated. Original
source bytes and earlier published build inputs remain unchanged.

The popup glyph-position callback recognizes only the new string address and
centers text using measured Latin glyph advances. Other messages chain into
the existing tutorial notice handler. Eighty-six emitted-MIPS cases at two
load bases cover all new glyph positions, the original tutorial notice,
unrelated text, out-of-range indices, callback behavior, preserved registers
and unchanged Y/Z coordinates.

The build checks all ISO files, 23 bank indexes and unchanged archive resources.
Runtime screenshots and framebuffer metadata are in
work/ui/ui_fixes_0.1.31/runtime.

Runtime verification passed in PPSSPP 1.20.4 with software rendering after a
fresh launch and loading an in-game save (no save state). The first battle's
locked Party Abilities popup displays the complete English text centered with
proportional spacing. Confirm dismisses it; returning to the battle map works.

Tested ISO SHA-256:
`861547abd89920165ba11096070183b77c4adba2ea3a0309524ff70eccb24784`.
All 5,729 unchanged archive resources were verified.
