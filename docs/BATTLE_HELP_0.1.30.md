# Battle Info help wrapping — 0.1.30

The Win/Lose help text in 0.1.29 split "defeat" across rows and joined its last
letter to "conditions". The native help draw loop at module 0x64344 limits
rows to 27 encoded cells; its staging row stride is 29 cells. Earlier checks
used the storage stride instead of the display limit.

0.1.30 reflows the existing relocated Win/Lose bundle without changing its
wording. Party Abilities had the same 28-cell issue; its reviewed replacement
reads "View Party Abilities and / select them for battle." Support Skills and
Brave Goals descriptions already fit and remain unchanged. Proportional
rendering remains enabled.

The patch checks the live ELF program headers to resolve relocated addresses,
limits each line to 27 encoded cells and total glyphs to 54, retains the empty
line terminator, and asserts that only the two string spans change. It changes
45 bytes in a new copy of the executable. Published 0.1.29 is untouched.

The ISO builder verifies every file against 0.1.29: only EBOOT.BIN differs;
all 23 archive banks are byte-identical.

Runtime evidence is recorded under work/ui/ui_fixes_0.1.30/runtime.

Runtime verification passed in PPSSPP 1.20.4 with software rendering after a
fresh launch and loading an in-game save (no save state). All four Battle Info
help descriptions were visually checked. Win/Lose displays complete words
and spacing on two lines. The conditions popup opens and closes, and returning
to the battle map works. Testing covers the first battle's Battle Info menu.

Tested ISO SHA-256:
`d72901399d839284d6c26f7a4debf02ce638ce16fd4d9de0e962c9fed0a52fdb`.
