# Stance crash fix — 0.1.28

Base: immutable 0.1.27. Opening Stance was reproduced from a fresh launch with
an in-game save in the first pirate battle. The isolated PPSSPP process exited
when the selected Guard description was constructed.

A second run stopped inside the help glyph loop at module 0x64bf0. The
single-line cursor was already at cell 44 (s0=0x58), beyond the 29-cell line
buffer. The selected description was an oversized translation from static
table 31. It also lacked an empty-line terminator, allowing the native
three-line reader to consume adjacent Riposte text.

The native layout has 29 cells per line, a 54-glyph object pool and a 174-byte
staging limit. Replacement records use at most two visible lines, <=29 cells
each and <=54 cells total, followed by an explicit empty line. Each record is
relocated and its pointer updated in both 02.DAT and the resident static-table
mirror. The executable is byte-identical to 0.1.27.

Meaning review and encoded-cell checks cover the related stance descriptions.
The verifier requires that the released Counter and Guard records fail the
capacity checks, while every replacement passes and the resident mirror agrees.

All 18 distinct stance descriptions in table 31 records 100–176 are repaired.
The replacements use at most 53 glyphs total, 29 per line and 255.5 pixels of
measured advance. Record 177 begins the separate ZOC passive category.

Runtime verification passed on PPSSPP 1.20.4 with software rendering, a fresh
launch and an in-game save:

- Opening Stance displays Guard and its two-line description without crashing.
- Moving to Counter displays its complete description.
- Confirming Counter closes the submenu and updates the unit card to Cntr.
- Reopening succeeds; switching back to Guard and returning to the map succeeds.
- No debugger breakpoints remain.

Screenshots and framebuffer metadata are under
`work/ui/ui_fixes_0.1.28/runtime`; the diagnosis is in
`work/ui/ui_fixes_0.1.28/diagnosis.json`.
Other stance variants were statically checked, not exercised in-game.

Tested ISO SHA-256:
`fac87f5d1c1c812e85236486690df0152978b0fe424fb442024c665ac97bf457`.
Archive verification checked all 23 indexes and 5,728 unchanged bank resources.

