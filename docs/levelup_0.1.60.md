# Level Up — local test 0.1.60

The reported Level Up screen mixes raster title artwork with a native two-row
instruction formatter. This patch translates both title states and all related
instruction states, including bonus-point allocation. It retains the saved
protagonist name, because that field may contain a player-entered name.

## English text

- Level Up
- Choose a unit to level up.
- No units can level up.
- Allocate bonus points.
- Circle: OK; Cross: End; SELECT: Learn Skills
- Circle: Confirm (bonus-point allocation)

## Scope and alignment

Six audited LUI/ADDIU pairs in the native formatter at module address `0x63b60`
reference new two-byte CP932 strings appended to the existing loaded segment.
Existing relocation records remain in place. All previous loaded segment bytes
are retained; only the six known bindings change. Other menus continue using
the previous shared Learn Skills string.

The native help-position helper gives SELECT the usual single-cell advance,
although its button artwork is wider. Five spaces after its control glyph move
the following Learn Skills label 34 pixels beyond the icon origin. The hints
use compact OK/End wording to stay within 27 cells per row and 54 total cells.
No new renderer hook or change to the shared guard is introduced.

Resource `02.DAT:1346/5/33` and `/34` receive Level Up lettering in rectangle
`(16,4)-(103,21)`. The original palette, alpha, dimensions and every pixel
outside that rectangle remain unchanged. Artwork used the built-in imagegen
editor; the exact prompt is in `work/ui/levelup_0.1.60/imagegen.json`.

## Verification

All eight available/unavailable, selection/allocation and skill-hint states
execute through the actual native formatter and staging code. Buffer guards
remain intact. The actual position helper passes 54 character cases at two
load bases, with stack guards and native metric lookup.

The candidate ISO passes all 14 regression groups. Legacy byte-exact audits
receive a historical view only after proving the complete candidate equals
the scoped Level Up patch; formatter and renderer guard execution use the
actual candidate executable. ISO archive indexes and resident caches agree,
and 5,728 unaffected bank resources remain byte-identical to 0.1.59.

Fresh-boot PPSSPP 1.20.4 with strict invalid-memory handling loads the copied
Chapter 15 battle save. The available save cannot reach Level Up, so the
reported screen has not yet been visually verified inside PPSSPP. Native
heading previews and runtime captures are under `work/ui/levelup_0.1.60`.

ISO SHA-256:
`d224734258aa6c524a6aa4d4d9296f2c41af59515b574a36b602db6a6b2e7f29`

The local upgrade source is the last published release, 0.1.55. Retro Trans
Tools validates the patch manifest and a full decode-to-target hash comparison.
This build is not published.
