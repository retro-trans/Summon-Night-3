# Status stance overflow - v0.1.45

The reported status card has about 70 native pixels available for the stance
name. At the existing 0.875 font scale, Mana Guard uses 85.75 pixels and
extends into the DF column. Magic Resist also exceeds this space at 93.625.

The shared labels now read **MP Guard** (69.125 pixels) and **M. Resist**
(66.5 pixels). This also keeps their names consistent in other menus that
use the same records. Stance mechanics and detailed descriptions are unchanged.

All 17 distinct stance labels were checked with the existing game font metrics;
the widest remaining label, Intimidate, uses 70 pixels. The executable is
byte-identical to v0.1.44. Only the two label pointers and appended label text
change in table 31, including its cached master copy.

Validation includes font widths, exact target labels, unchanged gameplay
fields, cumulative historical input hashes, ISO/archive structure and the
native System help/Brave Goals regression checks. Width results and the
reported screen coordinates are recorded in `work/ui/stance_width_0.1.45/`.
The reported Hasaha status screen has not been reached in a live emulator
with the available battle save; these are font-metric checks, not a claim
of in-game visual verification.

Use `work/output/0.1.45/SN3-English-v0.1.44-to-v0.1.45.xdelta` for exactly
v0.1.44, or `work/output/0.1.45/SN3-English-v0.1.45.xdelta` for the original
Japanese ISO. Both patches are round-trip verified against the final ISO;
see `XDELTA-VALIDATION.json` in the same output directory. Restart the ISO
and load a normal in-game save rather than restoring an older emulator state.

This is a local test build; no new GitHub release was published.
