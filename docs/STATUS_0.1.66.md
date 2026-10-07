# Summon Status report: 0.1.66

Local test build on immutable published 0.1.65. No release is published by this
change.

The reported screenshot shows R's Japanese name and the shared companion class
label. SELECT overlaps Give Food because its icon uses fixed cell spacing while
the text uses proportional spacing.

The new label pool relocates R and Summon Friend and updates 17 pointer fields.
The original pool, numeric entity IDs and other label bytes remain unchanged.
Both the 01.DAT bank and the 00.DAT resident cache receive the same labels.
Summon Friend measures 110.25 native pixels in the 133-pixel class field.

The icon helper recognizes only a second-row icon immediately followed by the
existing Give Food label. It compares nine cells within the native 29-cell row,
accepts prefix indices 0–16, and uses the preceding row text's proportional
advances. Other icons fall back to the existing 0.1.65 handler. No controls or
actions change. The original added segment, including the private script arena,
remains byte-identical.

The emitted MIPS passes 18 cases across two load bases, covering matching and
nonmatching labels, row and index boundaries, saved registers and stack guards.
The exact reported MC-room screen still requires a matching normal save.
The completed ISO passes 17 cumulative regression groups. A fresh PPSSPP 1.20.4
boot loads the copied Chapter 15 normal save and opens the battle menu without
a memory fault; this does not establish the room-screen visual result.

Inputs: `work/translation/en/status_0.1.66/targets.json` and
`tools/status_fix_066.py`. Preview the builder before using `--write`.
