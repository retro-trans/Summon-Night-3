# Summon Puppet crash - v0.1.48

## Cause and correction

The supplied v0.1.47 log reports an invalid read at 0x00000508 through the
font population routine. The private state identifies the caller as the
shared status-name field, selecting the default Rexx puppet name.

The first-build unit table still contained raw ASCII `Rexx` and `Aty`.
The renderer reads two-byte CP932 cells: Rexx's first two bytes become
0x6552, an invalid glyph code. With the captured font lookup table this
leads to the reported 0x508 address. This is a name-encoding defect, distinct
from the v0.1.47 equipment-description capacity fix.

The two default names are now appended using the established two-byte text
encoder. Eight name pointers (four unit variants each) are redirected in
both 01.DAT/1/0 and its resident 00.DAT/44/6/0 copy. Spellings remain Rexx
and Aty, consistent with the current character-name reference. Only those
pointer fields change within the previous table bytes. Player-entered
names are not rewritten. The executable is identical to v0.1.47.

## Validation

- All 753 referenced label strings / 2,312 pointers across 784 unit records
  pass two-byte CP932 cell validation after correction.
- Both resident and bank label tables are checked for exact consistency.
- All inherited build-input hashes, archive indexes, untouched resources,
  ISO file extents and final output hashes pass verification.
- In isolated PPSSPP 1.20.4 with bad-memory-access ignoring disabled, a
  private copy of the supplied state resumes after changing only the two
  name encodings. No program-counter, register or executable changes were
  required. Rexx displays after reselecting; the menu exits, reopens showing
  Aty, and the unit-creation prompt cancels normally.
- This runtime test uses the supplied state with corrected name data, not
  a fresh boot of the completed v0.1.48 ISO. The ISO contains the identical
  executable and corrected strings, with persistent pointers relocated in
  the resource tables. That fresh-boot distinction remains a test limit.
- Original incoming archives are untouched. Private state copies remain
  under ignored work/scratch. Screenshots and validation summary are in
  work/ui/puppet_0.1.48.

## Outputs and application

The local v0.1.48 test build provides the ISO and three verified xdelta
patches in work/output/0.1.48:

- SN3-English-v0.1.47-to-v0.1.48.xdelta: exact v0.1.47 ISO input.
- SN3-English-v0.1.42-to-v0.1.48.xdelta: exact v0.1.42 ISO input.
- SN3-English-v0.1.48.xdelta: original Japanese ISO input.

Each patch was applied with retro-trans-tools and reconstructed SHA-256
76d4cad7b5b8ded395b2e5601a590dce07d737a46111c430f12f3b907fe27850.
Full source and patch hashes are in XDELTA-VALIDATION.json.

Restart the updated ISO and use a normal in-game save. An old PPSSPP state
restores the old cached name table. No GitHub release was created.
